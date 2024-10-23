FROM python:3.12.4

RUN apt-get update && apt-get install openconnect socat -y 
RUN yes | apt-get install vim
RUN pip install vpn-slice
COPY . .
ENTRYPOINT ./vpn.sh
