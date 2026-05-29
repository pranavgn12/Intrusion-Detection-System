#!/bin/bash

WEB_SERVER="192.168.122.24"
DNS_SERVER="192.168.122.24"
SSH_HOST="192.168.122.24"

SSH_USER="vtm"
SSH_PASS="vtm12"

# Random float between MIN and MAX
rand_sleep() {
    awk -v min="$1" -v max="$2" \
        'BEGIN{srand(); print min + rand() * (max - min)}'
}

# DNS traffic
dns_worker() {
    while true; do
        nslookup example.com "$DNS_SERVER" >/dev/null 2>&1
        sleep "$(rand_sleep 0.50 0.55)"
    done
}

# HTTP/API traffic
http_worker() {
    while true; do
        curl -s "http://${WEB_SERVER}/api/status" >/dev/null 2>&1
        sleep "$(rand_sleep 0.80 1.80)"
    done
}

# ICMP traffic
ping_worker() {
    while true; do
        ping -c 2 "$WEB_SERVER" >/dev/null 2>&1
        sleep "$(rand_sleep 0.50 0.55)"
    done
}

# SSH command traffic
ssh_worker() {
    while true; do
        sshpass -p "$SSH_PASS" ssh \
            -o ConnectTimeout=3 \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null \
            "${SSH_USER}@${SSH_HOST}" "date" \
            >/dev/null 2>&1

        sleep "$(rand_sleep 1.00 1.20)"
    done
}

echo "Starting traffic generators..."

dns_worker &
http_worker &
ping_worker &
ssh_worker &

wait
