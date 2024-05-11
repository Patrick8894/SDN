from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class TreeTopo(Topo):
    "Custom topology for SDN project with tree structure."

    def build(self, depth=3, fanout=2):
        # Recursive function to create the topology
        def addTree(parent, depth, fanout):
            isSwitch = depth > 0
            if isSwitch:
                for i in range(fanout):
                    child = self.addSwitch('s%s' % self.switchCount)
                    self.switchCount += 1
                    self.addLink(parent, child)
                    addTree(child, depth - 1, fanout)
            else:
                child = self.addHost('h%s' % self.hostCount)
                self.hostCount += 1
                self.addLink(parent, child)

        self.switchCount = 1
        self.hostCount = 1
        root = self.addSwitch('s0')
        addTree(root, depth, fanout)

class LinearTopo(Topo):
    def build(self, numSwitches=3, numHostsPerSwitch=2, linkSpeed=1):
        lastSwitch = None
        for i in range(numSwitches):
            switch = self.addSwitch('s%s' % i, cls=OVSSwitch, failMode='standalone')
            for j in range(numHostsPerSwitch):
                host = self.addHost('h%s' % (i * numHostsPerSwitch + j))
                self.addLink(switch, host, bw=linkSpeed, delay='10ms')
            if lastSwitch:
                self.addLink(switch, lastSwitch, bw=linkSpeed, delay='10ms')
            lastSwitch = switch

def testTree():
    "Create network and run simple performance test"
    topo = TreeTopo(depth=2, fanout=2)
    # topo = LinearTopo(numSwitches=6, numHostsPerSwitch=3)
    net = Mininet(topo=topo, controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6633))
    net.start()

    # Start an iperf server on the last host
    last_host = net.hosts[-1]
    last_host.cmd('iperf -s &')

    # Run iperf client on the first host
    first_host = net.hosts[0]
    result = first_host.cmd('iperf -c %s -t 15' % last_host.IP())

    info("Iperf Results:\n")
    info(result)

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    testTree()