#!/bin/bash

echo $ITE_VPN_PASSWORD | openconnect $ITE_VPN_URL --user=$ITE_VPN_USER --passwd-on-stdin &
sleep infinity
