"""Generate synthetic, offline packets using documentation IP addresses."""
from pathlib import Path
from scapy.layers.inet import IP, TCP
from scapy.utils import wrpcap

packets = []
for i in range(15):
    p = IP(src='192.0.2.24', dst='198.51.100.10') / TCP(sport=40000+i, dport=1000+i, flags='S')
    p.time = 1700000000 + i * 0.2
    packets.append(p)
output = Path(__file__).with_name('demo_scan.pcap')
wrpcap(str(output), packets)
print(f'Created {output}')
