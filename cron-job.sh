#!/bin/bash

# Set PATH variable
export PATH=/sbin:/usr/sbin:$PATH

command="/etc/init.d/ipsec-assist.sh start >> /cron_data/cron_logs.txt 2>&1 && \
    /etc/init.d/ipsec-assist.sh test_connection 10.1.1.130 >> /cron_data/cron_logs.txt 2>&1 && \
    /etc/init.d/ipsec-assist.sh stop >> /cron_data/cron_logs.txt 2>&1"

cron_job="*/5 * * * * $command"

# Install the cron job
echo "$cron_job" | crontab -

cron -f
service cron start

tail -f /dev/null
