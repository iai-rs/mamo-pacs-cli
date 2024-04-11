#!/bin/bash

case "$1" in
    start)
        echo "Starting L2TP connection"

        /usr/sbin/iptables --table nat --append POSTROUTING --jump MASQUERADE
        /usr/sbin/ipsec restart
        /usr/sbin/service xl2tpd restart

        /usr/sbin/ipsec up myvpn
        echo "c myvpn" > /var/run/xl2tpd/l2tp-control

        sleep 10

        ip_address=$(ip route | grep default | awk '{print $3}')
        /usr/sbin/route add VPN_IP_ADDRESS_PLACEHOLDER gw "$ip_address"

        public_ip=$(curl -s ifconfig.me)
        /usr/sbin/route add "$public_ip" gw "$ip_address"
        /usr/sbin/route add default dev ppp0
        ;;
    stop)
        echo "Stopping L2TP connection"
        /usr/sbin/iptables --table nat --flush
        /usr/sbin/ipsec stop
        /usr/sbin/service xl2tpd stop
        ;;
    test_connection)
        echo "TESTING: $2"
        ping_result=$(ping -c 1 "$2")

        # Check the exit status of the ping command
        if [ $? -ne 0 ]; then
            # If the ping command failed, display an error message
            echo "Ping failed: Could not reach $2"
        else
            # If the ping command succeeded, display a success message
            echo "Ping succeeded: $2 is reachable"
        fi
        ;;
    esac
    exit 0
