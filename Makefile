IMAGE_NAME = l2tp-ipsec-vpn
CONTAINER_NAME = myvpncontainer

.PHONY: build run destroy start_connection stop_connection check_connection

build:
	docker build -t $(IMAGE_NAME) .

run:
	@if [ -z "$(vpn_user)" ]; then \
		echo "ERROR: 'vpn_user' is not provided"; \
		exit 1; \
	fi
	@if [ -z "$(vpn_password)" ]; then \
		echo "ERROR: 'vpn_password' is not provided"; \
		exit 1; \
	fi
	@if [ -z "$(vpn_ip_address)" ]; then \
		echo "ERROR: 'vpn_ip_address' is not provided"; \
		exit 1; \
	fi
	@if [ -z "$(vpn_psk)" ]; then \
		echo "ERROR: 'vpn_psk' is not provided"; \
		exit 1; \
	fi
	docker run \
		-e VPN_USER=$(vpn_user) \
		-e VPN_PASSWORD=$(vpn_password) \
		-e VPN_IP_ADDRESS=$(vpn_ip_address) \
		-e VPN_PRE_SHARED_KEY=$(vpn_psk) \
		-e PRIVATE_IP=10.1.1.130  \
		--privileged --cap-add NET_ADMIN -d --name=myvpncontainer l2tp-ipsec-vpn

destroy:
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)

start_connection:
	docker exec $(CONTAINER_NAME) /etc/init.d/ipsec-assist.sh start

stop_connection:
	docker exec $(CONTAINER_NAME) /etc/init.d/ipsec-assist.sh stop

check_connection:
	@if [ -z "$(private_ip)" ]; then \
		echo "ERROR: 'private_ip' is not provided"; \
		exit 1; \
	fi
	docker exec $(CONTAINER_NAME) /etc/init.d/ipsec-assist.sh test_connection $(private_ip)
