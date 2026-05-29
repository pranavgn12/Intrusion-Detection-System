#!/bin/bash

TARGET="192.168.122.24"

# echo "[*] TCP Connect Scan"
# nmap -sT "$TARGET"
#
# echo
# echo "[*] Fast Scan"
# nmap -F "$TARGET"

echo
echo "[*] Full Port Scan"
nmap -p- "$TARGET"

# echo
# echo "[*] Version Detection"
# nmap -sV "$TARGET"

# echo
# echo "[+] All scans completed."
