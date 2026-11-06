from scapy.layers.inet import IP, TCP, ICMP, UDP
from scapy.layers.dns import DNS, DNSQR
from app.detector import ThreatDetector


def test_syn_flood():
    d = ThreatDetector(port_threshold=999, syn_threshold=3)
    found = []
    for i in range(3):
        p = IP(src='192.0.2.1', dst='198.51.100.1') / TCP(dport=443, flags='S', sport=2000+i)
        p.time = 1000 + i
        found.extend(d.process_all(p))
    assert [a['event_type'] for a in found] == ['SYN_FLOOD']


def test_icmp_flood():
    d = ThreatDetector(icmp_threshold=3)
    found = []
    for i in range(3):
        p = IP(src='192.0.2.1', dst='198.51.100.1') / ICMP(type=8)
        p.time = 1000 + i
        found.extend(d.process_all(p))
    assert any(a['event_type'] == 'ICMP_FLOOD' for a in found)


def test_dns_anomalies():
    d = ThreatDetector(dns_threshold=2, dns_length=30)
    found = []
    for i in range(2):
        p = IP(src='192.0.2.1', dst='198.51.100.53') / UDP(dport=53) / DNS(rd=1, qd=DNSQR(qname='a'*40+'.example.test'))
        p.time = 1000 + i
        found.extend(d.process_all(p))
    assert {'DNS_LONG_QUERY', 'DNS_RATE'} <= {a['event_type'] for a in found}
