from mininet.net import Mininet
from mininet.node import Node, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.topo import Topo

class OSPFRouter(Node):
    "A Node with IP forwarding and OSPF enabled."

    def config(self, **params):
        super(OSPFRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')
        self.cmd('sysctl net.ipv4.conf.all.rp_filter=0')
        self.cmd('sysctl net.ipv4.conf.default.rp_filter=0')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(OSPFRouter, self).terminate()

class TreeTopo(Topo):
    def build(self, depth=3, fanout=2, linkSpeed=1):
        def addTree(parent, depth, fanout):
            isSwitch = depth > 0
            if isSwitch:
                for i in range(fanout):
                    child = self.addSwitch('s%s' % self.switchCount, cls=OVSSwitch, failMode='standalone')
                    self.switchCount += 1
                    self.addLink(parent, child, bw=linkSpeed, delay='10ms')
                    addTree(child, depth - 1, fanout)
            else:
                child = self.addHost('h%s' % self.hostCount, cls=OSPFRouter)
                self.hostCount += 1
                self.addLink(parent, child, bw=linkSpeed, delay='10ms')

        self.switchCount = 1
        self.hostCount = 1
        root = self.addSwitch('s0', cls=OVSSwitch, failMode='standalone')
        addTree(root, depth, fanout)

class LinearTopo(Topo):
    def build(self, numSwitches=3, numHostsPerSwitch=2, linkSpeed=1):
        lastSwitch = None
        for i in range(numSwitches):
            switch = self.addSwitch('s%s' % i, cls=OVSSwitch, failMode='standalone')
            for j in range(numHostsPerSwitch):
                host = self.addHost('h%s' % (i * numHostsPerSwitch + j), cls=OSPFRouter)
                self.addLink(switch, host, bw=linkSpeed, delay='10ms')
            if lastSwitch:
                self.addLink(switch, lastSwitch, bw=linkSpeed, delay='10ms')
            lastSwitch = switch

def testNetwork():
    topo = TreeTopo(depth=3, fanout=3)
    # topo = LinearTopo(numSwitches=16, numHostsPerSwitch=1)
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None)
    net.start()

    for router in net.hosts:
        router.cmd('zebra -d -f /etc/quagga/zebra.conf')
        router.cmd('ospfd -d -f /etc/quagga/ospfd.conf')

    last_host = net.hosts[-1]
    last_host.cmd('iperf -s &')

    first_host = net.hosts[0]
    result = first_host.cmd('iperf -c %s -t 10' % last_host.IP())

    info("Iperf Results:\n")
    info(result)

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    testNetwork()
