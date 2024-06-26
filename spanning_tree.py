from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info

if '__main__' == __name__:
    setLogLevel('info')
    net = Mininet(controller=RemoteController)

    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)

    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')

    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')

    net.addLink(s1, h1)
    net.addLink(s2, h2)
    net.addLink(s3, h3)

    net.addLink(s1, s2)
    net.addLink(s2, s3)
    net.addLink(s3, s1)

    net.build()
    c0.start()
    s1.start([c0])
    s2.start([c0])
    s3.start([c0])

    net.startTerms()

    CLI(net)

    net.stop()