#!/bin/bash

# Start the IPsec connection
ipsec initnss
ipsec start --nofork &

# Wait for IPsec to initialize
sleep 10

# Start the L2TP connection
echo "c myvpn" > /var/run/xl2tpd/l2tp-control

# Keep the script running to maintain the VPN connection
sleep infinity
