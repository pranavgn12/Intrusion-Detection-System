#!/bin/bash

WEB_SERVER="192.168.122.24"
DNS_SERVER="192.168.122.24"
SSH_HOST="192.168.122.24"

SSH_USER="vtm"
SSH_PASS="vtm12"

# DNS traffic
dns_worker() {
    while true; do
        sleep $((RANDOM % 120 + 30))
        nslookup example.com "$DNS_SERVER" >/dev/null 2>&1
    done
}

# HTTP/API traffic
http_worker() {
    while true; do
        pages=(
            "/"
            "/about"
            "/products"
            "/contact"
            "/api/status"
        )

        page=${pages[$RANDOM % ${#pages[@]}]}

        curl -s "http://${WEB_SERVER}${page}" >/dev/null 2>&1

        sleep $((RANDOM % 60 + 10))
    done
}

# ICMP traffic
ping_worker() {
    while true; do
        sleep $((RANDOM % 300 + 60))
        ping -c 3 "$WEB_SERVER" >/dev/null 2>&1
    done
}

# SSH traffic
ssh_worker() {
    while true; do
        sleep $((RANDOM % 180 + 60))

        sshpass -p "$SSH_PASS" ssh \
            -o ConnectTimeout=3 \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null \
            "${SSH_USER}@${SSH_HOST}" "date" \
            >/dev/null 2>&1
    done
}

echo "Starting normal traffic generators..."

dns_worker &
http_worker &
ping_worker &
ssh_worker &

wait
