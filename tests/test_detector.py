from scapy.layers.inet import IP, TCP
from app.detector import PortScanDetector


def test_port_scan_and_suppression():
    detector = PortScanDetector(threshold=3, window=10)
    alerts = []
    for i in range(4):
        p = IP(src='192.0.2.5', dst='198.51.100.8') / TCP(dport=100+i, flags='S')
        p.time = 1000 + i
        alerts.append(detector.process(p))
    assert sum(a is not None for a in alerts) == 1
    assert alerts[2]['event_type'] == 'PORT_SCAN'


def test_syn_ack_does_not_trigger():
    detector = PortScanDetector(threshold=2)
    for i in range(3):
        p = IP(src='192.0.2.5', dst='198.51.100.8') / TCP(dport=100+i, flags='SA')
        p.time = 1000+i
        assert detector.process(p) is None
