from scapy.all import *
from collections import defaultdict, Counter
import pandas as pd

# =========================
# CONFIGURATION
# =========================

WINDOW_SIZE = 2

MONITORED_IP = "192.168.122.24"

PCAP_FILES = [
    "ntg.pcap"
]

LABEL = "Nothing"

OUTPUT_FILE = "Nothing.csv"

# =========================
# WINDOW STRUCTURE
# =========================

def new_window():
    return {
        "packet_count": 0,
        "byte_count": 0,

        "tcp_count": 0,
        "udp_count": 0,
        "icmp_count": 0,
        "arp_count": 0,

        "syn_count": 0,
        "ack_count": 0,
        "rst_count": 0,

        "dst_ports": set(),
        "dst_ips": set(),

        "connections": set(),

        "dns_query_count": 0,
        "dns_query_lengths": [],

        "ssh_connections": 0,
        "ftp_connections": 0,

        "outbound_bytes": 0,
        "inbound_bytes": 0,

        "port_counter": Counter(),

        "arp_ip_to_macs": defaultdict(set)
    }


windows = defaultdict(new_window)

# =========================
# PROCESS PCAPS
# =========================

for pcap in PCAP_FILES:

    print(f"Reading {pcap}")

    with PcapReader(pcap) as reader:

        for pkt in reader:

            ts = float(pkt.time)

            window_id = int(ts // WINDOW_SIZE)

            w = windows[window_id]

            if IP in pkt:

                size = len(pkt)

                src_ip = pkt[IP].src
                dst_ip = pkt[IP].dst

                w["packet_count"] += 1
                w["byte_count"] += size

                # Direction-aware bytes
                if dst_ip == MONITORED_IP:
                    w["inbound_bytes"] += size

                if src_ip == MONITORED_IP:
                    w["outbound_bytes"] += size

                w["dst_ips"].add(dst_ip)

                # ---------------------
                # TCP
                # ---------------------

                if TCP in pkt:

                    sport = pkt[TCP].sport
                    dport = pkt[TCP].dport

                    w["tcp_count"] += 1

                    w["dst_ports"].add(dport)
                    w["port_counter"][dport] += 1

                    conn = (
                        src_ip,
                        dst_ip,
                        sport,
                        dport
                    )

                    w["connections"].add(conn)

                    flags = int(pkt[TCP].flags)

                    if flags & 0x02:
                        w["syn_count"] += 1

                    if flags & 0x10:
                        w["ack_count"] += 1

                    if flags & 0x04:
                        w["rst_count"] += 1

                    if dport == 22:
                        w["ssh_connections"] += 1

                    if dport == 21:
                        w["ftp_connections"] += 1

                # ---------------------
                # UDP
                # ---------------------

                elif UDP in pkt:

                    w["udp_count"] += 1

                    dport = pkt[UDP].dport

                    w["dst_ports"].add(dport)
                    w["port_counter"][dport] += 1

                # ---------------------
                # ICMP
                # ---------------------

                elif ICMP in pkt:

                    w["icmp_count"] += 1

                # ---------------------
                # DNS
                # ---------------------

                if DNS in pkt and DNSQR in pkt:

                    try:

                        qname = pkt[DNSQR].qname.decode(
                            errors="ignore"
                        )

                        w["dns_query_count"] += 1

                        w["dns_query_lengths"].append(
                            len(qname)
                        )

                    except:
                        pass

            # =====================
            # ARP
            # =====================

            elif ARP in pkt:

                w["arp_count"] += 1

                w["arp_ip_to_macs"][
                    pkt[ARP].psrc
                ].add(
                    pkt[ARP].hwsrc
                )

# =========================
# BUILD DATAFRAME
# =========================

rows = []

for _, w in windows.items():

    packet_count = w["packet_count"]

    if packet_count == 0:
        continue

    byte_count = w["byte_count"]

    packets_per_second = (
        packet_count / WINDOW_SIZE
    )

    bytes_per_second = (
        byte_count / WINDOW_SIZE
    )

    new_connections = len(
        w["connections"]
    )

    failed_connections = max(
        w["syn_count"] -
        w["ack_count"],
        0
    )

    syn_ack_ratio = (
        w["syn_count"]
        /
        max(
            w["ack_count"],
            1
        )
    )

    avg_dns_query_length = (
        sum(
            w["dns_query_lengths"]
        )
        /
        len(
            w["dns_query_lengths"]
        )
        if w["dns_query_lengths"]
        else 0
    )

    top_destination_port_count = (
        max(
            w["port_counter"].values()
        )
        if w["port_counter"]
        else 0
    )

    max_macs = 0

    for macs in w[
        "arp_ip_to_macs"
    ].values():

        max_macs = max(
            max_macs,
            len(macs)
        )

    outbound_inbound_ratio = (
        (w["outbound_bytes"] + 1)
        /
        (w["inbound_bytes"] + 1)
    )

    row = {

        "packet_count":
            packet_count,

        "byte_count":
            byte_count,

        "packets_per_second":
            packets_per_second,

        "bytes_per_second":
            bytes_per_second,

        "tcp_count":
            w["tcp_count"],

        "udp_count":
            w["udp_count"],

        "icmp_count":
            w["icmp_count"],

        "arp_count":
            w["arp_count"],

        "syn_count":
            w["syn_count"],

        "ack_count":
            w["ack_count"],

        "rst_count":
            w["rst_count"],

        "unique_destination_ports":
            len(
                w["dst_ports"]
            ),

        "unique_destination_ips":
            len(
                w["dst_ips"]
            ),

        "new_connections":
            new_connections,

        "failed_connections":
            failed_connections,

        "syn_ack_ratio":
            syn_ack_ratio,

        "dns_query_count":
            w["dns_query_count"],

        "avg_dns_query_length":
            avg_dns_query_length,

        "ssh_connections":
            w["ssh_connections"],

        "ftp_connections":
            w["ftp_connections"],

        "outbound_bytes":
            w["outbound_bytes"],

        "inbound_bytes":
            w["inbound_bytes"],

        "outbound_inbound_ratio":
            outbound_inbound_ratio,

        "top_destination_port_count":
            top_destination_port_count,

        "unique_macs_claiming_same_ip":
            max_macs,

        "label":
            LABEL
    }

    rows.append(row)

# =========================
# SAVE CSV
# =========================

df = pd.DataFrame(rows)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"Saved {len(df)} rows to {OUTPUT_FILE}"
)
