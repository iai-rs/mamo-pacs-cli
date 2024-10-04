#!/bin/bash

echo $ITE_VPN_PASSWORD | openconnect $ITE_VPN_URL --user=$ITE_VPN_USER --passwd-on-stdin --script "vpn-slice 10.0.0.0/8" &
sleep infinity
