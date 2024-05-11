from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class TreeTopo(Topo):
    "Simple topology example."

    def __init__(self, depth=2, fanout=2, **opts):
        "Create custom tree topo."
        super(TreeTopo, self).__init__(**opts)

        # Add initial switch
        root_switch = self.addSwitch('s1')
        self.addTree(root_switch, 1, depth, fanout)

    def addTree(self, parent, current_depth, max_depth, fanout):
        """Recursive function to generate the tree."""
        if current_depth > max_depth:
            return
        is_switch = current_depth < max_depth
        for i in range(1, fanout + 1):
            node_id = f'{parent}-{i}'
            if is_switch:
                child = self.addSwitch(f's{node_id}')
            else:
                child = self.addHost(f'h{node_id}')
            self.addLink(parent, child)
            self.addTree(child, current_depth + 1, max_depth, fanout)

def testTree():
    "Create and test a simple network"
    topo = TreeTopo(depth=5, fanout=2)
    net = Mininet(topo=topo, controller=lambda name: RemoteController(name, ip='127.0.0.1'), switch=OVSSwitch)
    net.start()

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    testTree()
