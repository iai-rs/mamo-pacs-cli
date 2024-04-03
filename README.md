# Mamo PACS cli/

## Description

## Usage
Build a container:
```bash
make build
```

Run a container:
```bash
make run vpn_user=<VPN_USER> vpn_password=<VPN_PASSWORD> vpn_ip_address=<VPN_IP_ADDRESS> vpn_psk=<VPN_PSK>
```

Destroy a container:
```bash
make_destroy
```

Check connection:
```bash
make check_connection private_ip=<PRIVATE_IP>
```

Start/stop connection:
```bash
make stop_connection
make start_connection
```
