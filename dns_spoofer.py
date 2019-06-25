#!/usr/bin/env python


# start intercepting packets into queue
# iptables -I FORWARD -j NFQUEUE --queue-num 0

# clear queue
# iptables --flush