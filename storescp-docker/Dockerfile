FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y dcmtk

CMD storescp -aet PYNETDICOM 55613 --output-directory /data
