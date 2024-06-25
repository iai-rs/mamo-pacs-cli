FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV VPN_IP_ADDRESS=vpnipaddress
ENV VPN_USER=vpnuser
ENV VPN_PASSWORD=vpnpassword
ENV VPN_PRE_SHARED_KEY=vpnpresharedkey

# Update and install VPN and network diagnostic tools
RUN apt-get update && \
    apt-get install -y strongswan xl2tpd net-tools iptables ppp lsb-release iputils-ping curl pip && \
    pip install pynetdicom
    # apt-get clean


# Copy your VPN configuration files into the container
COPY ./vpn-config /etc

# Copy the entry script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy the ipsec-assist script
COPY ipsec-assist.sh /etc/init.d/ipsec-assist.sh
RUN chmod +x /etc/init.d/ipsec-assist.sh

ENTRYPOINT ["/entrypoint.sh"]
