#!/bin/bash

case "$1" in
    start)
        echo "Starting L2TP connection"

        iptables --table nat --append POSTROUTING --jump MASQUERADE
        ipsec restart
        /usr/sbin/service xl2tpd restart

        ipsec up myvpn
        echo "c myvpn" > /var/run/xl2tpd/l2tp-control

        sleep 10

        ip_address=$(ip route | grep default | awk '{print $3}')
        route add VPN_IP_ADDRESS_PLACEHOLDER gw "$ip_address"

        public_ip=$(curl -s ifconfig.me)
        route add "$public_ip" gw "$ip_address"
        route add default dev ppp0
        ;;
    stop)
        echo "Stopping L2TP connection"
        iptables --table nat --flush
        ipsec stop
        /usr/sbin/service xl2tpd stop
        ;;
    test_connection)
        ping_result=$(ping -c 1 PRIVATE_IP_PLACEHOLDER)

        # Check the exit status of the ping command
        if [ $? -ne 0 ]; then
            # If the ping command failed, display an error message
            echo "Ping failed: Could not reach PRIVATE_IP_PLACEHOLDER"
            # exit 1
        else
            # If the ping command succeeded, display a success message
            echo "Ping succeeded: PRIVATE_IP_PLACEHOLDER is reachable"
        fi
        ;;
    esac
    exit 0
