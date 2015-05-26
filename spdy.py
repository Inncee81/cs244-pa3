#!/usr/bin/python

"CS244 Spring 2015 Final Project: SPDY"

from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser

import termcolor as T

import sys
import os
import math

parser = ArgumentParser(description="Bufferbloat tests")
parser.add_argument('--bw-host', '-B',
                    type=float,
                    help="Bandwidth of host links (Mb/s)",
                    default=1000)

parser.add_argument('--bw-net', '-b',
                    type=float,
                    help="Bandwidth of bottleneck (network) link (Mb/s)",
                    required=True)

parser.add_argument('--delay',
                    type=float,
                    help="Link propagation delay (ms)",
                    required=True)

parser.add_argument('--dir', '-d',
                    help="Directory to store outputs",
                    default=".")

parser.add_argument('--time', '-t',
                    help="Duration (sec) to run the experiment",
                    type=int,
                    default=10)

parser.add_argument('--maxq',
                    type=int,
                    help="Max buffer size of network interface in packets",
                    default=100)

parser.add_argument('--loss',
                    type=int,
                    help="Packet loss rate (%)",
                    default=0)

# Linux uses CUBIC-TCP by default that doesn't have the usual sawtooth
# behaviour.  For those who are curious, invoke this script with
# --cong cubic and see what happens...
# sysctl -a | grep cong should list some interesting parameters.
parser.add_argument('--cong',
                    help="Congestion control algorithm to use",
                    default="reno")

# Expt parameters
args = parser.parse_args()

class BBTopo(Topo):
  "Simple topology for SPDY experiment."

  def build(self, n=2):
    print "Building topology..."
    h1 = self.addHost('h1')
    h2 = self.addHost('h2')

    # Here I have created a switch.  If you change its name, its
    # interface names will change from s0-eth1 to newname-eth1.
    switch = self.addSwitch('s0')

    delay = str(args.delay) + "ms"
    h1_link_opts = dict(bw=args.bw_host, delay=delay,
        max_queue_size=args.maxq)
    h2_link_opts = dict(bw=args.bw_net, delay=delay,
        max_queue_size=args.maxq)
    self.addLink(h1, switch, **h1_link_opts);
    self.addLink(h2, switch, **h2_link_opts);
    return

def spdy(net):
  h1 = net.get('h1')
  h1.cmd("./replace-spdyconf.sh nosslspdy.conf")
  h1.popen("node ~/epload/emulator/run.js spdy" +
      " ~/dependency_graphs/58.com_/ > %s/%s" % (args.dir, 1), shell=True)

def bufferbloat():
  if not os.path.exists(args.dir):
    os.makedirs(args.dir)
  os.system("sysctl -w net.ipv4.tcp_congestion_control=%s" % args.cong)
  topo = BBTopo()
  net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
  net.start()
  # This dumps the topology and how nodes are interconnected through links.
  dumpNodeConnections(net.hosts)
  # This performs a basic all pairs ping test.
  net.pingAll()
  # Run SPDY experiments.
  spdy(net)
  # Ensure that all processes you create within Mininet are killed.
  net.stop()

if __name__ == "__main__":
  bufferbloat()
