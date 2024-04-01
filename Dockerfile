FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

# Update and install VPN and network diagnostic tools
RUN apt-get update && \
    apt-get install -y strongswan xl2tpd net-tools iptables ppp lsb-release iputils-ping curl vim systemd && \
    # apt-get clean

# Copy your VPN configuration files into the container
COPY ./vpn-config /etc

# Copy the entry script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
