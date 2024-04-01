#!/bin/bash

# Set environment variables
sed -i "s/VPN_USER_PLACEHOLDER/$VPN_USER/g" /etc/ppp/options.l2tpd.client
sed -i "s/VPN_IP_ADDRESS_PLACEHOLDER/$VPN_IP_ADDRESS/g" /etc/ipsec.conf
sed -i "s/VPN_IP_ADDRESS_PLACEHOLDER/$VPN_IP_ADDRESS/g" /etc/xl2tpd/xl2tpd.conf
sed -i "s/VPN_IP_ADDRESS_PLACEHOLDER/$VPN_IP_ADDRESS/g" /etc/init.d/ipsec-assist.sh
sed -i "s/VPN_PASSWORD_PLACEHOLDER/$VPN_PASSWORD/g" /etc/ppp/options.l2tpd.client
sed -i "s/VPN_PRE_SHARED_KEY_PLACEHOLDER/$VPN_PRE_SHARED_KEY/g" /etc/ipsec.secrets
sed -i "s/PRIVATE_IP_PLACEHOLDER/$PRIVATE_IP/g" /etc/init.d/ipsec-assist.sh

# Start the IPsec connection
ipsec initnss
ipsec start --nofork &

# Wait for IPsec to initialize
sleep 10

/etc/init.d/ipsec-assist.sh start
/etc/init.d/ipsec-assist.sh test_connection

# Keep the script running to maintain the VPN connection
sleep infinity
