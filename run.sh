#!/bin/bash

# Note: Mininet must be run as root.  So invoke this shell script
# using sudo.

bwnet=10
delay=50
timestamp=$(date +%s)
sep=_loss_

for loss in 0 0.5 1 2; do
  dir=loss/$timestamp$sep$loss
  # Run spdy.py here...
  python spdy.py -b $bwnet -d $dir --delay $delay --loss $loss

  # Graphs go in the root folder, based on names in the assignment
  # python plot_tcpprobe.py -f $dir/cwnd.txt -o cwnd-q$qsize.png -p $iperf_port
  # python plot_queue.py -f $dir/q.txt -o buffer-q$qsize.png
  # python plot_ping.py -f $dir/ping.txt -o rtt-q$qsize.png
done
