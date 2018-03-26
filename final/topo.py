#!/usr/bin/env python
# CS164 Final Project by Hanzhe Teng on 3/15/2018
# Spanning Tree Protocol - network topology

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI

class SpanningTreeTopo( Topo ):
	"Simple topology example."
	def __init__( self ):
		"Create custom topo."
		# Initialize topology
		Topo.__init__( self )
		# Add hosts and switches
		h1 = self.addHost( 'b1' )
		h2 = self.addHost( 'b2' )
		h3 = self.addHost( 'b3' )
		h4 = self.addHost( 'b4' )
		switch = self.addSwitch( 's1' )
		# Add links
		self.addLink( h1, switch )
		self.addLink( h2, switch )
		self.addLink( switch, h3 )
		self.addLink( switch, h4 )

def runExperiment():
	"Create and test a simple experiment"
	topo = SpanningTreeTopo()
	net = Mininet(topo)
	net.start()
	CLI( net )
	net.stop()

if __name__ == '__main__':
	# Tell mininet to print useful information
	setLogLevel('info')
	runExperiment()




