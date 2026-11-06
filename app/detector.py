"""Heuristic detections for authorized network traffic; not a signature IDS."""
from collections import defaultdict, deque
from datetime import datetime, timezone
from scapy.layers.inet import IP, TCP, ICMP, UDP
from scapy.layers.dns import DNS, DNSQR


class ThreatDetector:
    def __init__(self, port_threshold=10, syn_threshold=100, icmp_threshold=50,
                 dns_threshold=40, dns_length=90, window=10.0):
        self.window = window
        self.thresholds = {'PORT_SCAN': port_threshold, 'SYN_FLOOD': syn_threshold,
                           'ICMP_FLOOD': icmp_threshold, 'DNS_RATE': dns_threshold}
        self.dns_length = dns_length
        self.events = defaultdict(deque)
        self.last_alert = {}

    def process_all(self, packet):
        if IP not in packet:
            return []
        src, dst = packet[IP].src, packet[IP].dst
        now = float(packet.time)
        alerts = []
        # Each rule keeps a short rolling window, so old packets do not trigger new alerts.
        def check(kind, key, value, threshold, description, severity):
            token = (kind, key)
            entries = self.events[token]
            entries.append((now, value))
            while entries and (now - entries[0][0] > self.window or now < entries[0][0]):
                entries.popleft()
            count = len({v for _, v in entries}) if kind == 'PORT_SCAN' else len(entries)
            if count < threshold or now - self.last_alert.get(token, float('-inf')) < self.window:
                return
            self.last_alert[token] = now
            alerts.append({'timestamp': datetime.fromtimestamp(now, timezone.utc).isoformat(),
                           'severity': severity, 'event_type': kind, 'source_ip': src,
                           'destination_ip': dst, 'description': description.format(count=count, window=self.window)})

        if TCP in packet:
            flags = int(packet[TCP].flags)
            if flags & 0x02 and not flags & 0x10:
                check('PORT_SCAN', (src, dst), int(packet[TCP].dport),
                      self.thresholds['PORT_SCAN'], '{count} distinct TCP SYN ports in {window:g}s', 'MEDIUM')
                check('SYN_FLOOD', (src, dst), None, self.thresholds['SYN_FLOOD'],
                      '{count} initial TCP SYN packets in {window:g}s', 'HIGH')
        if ICMP in packet and int(packet[ICMP].type) == 8:
            check('ICMP_FLOOD', (src, dst), None, self.thresholds['ICMP_FLOOD'],
                  '{count} ICMP echo requests in {window:g}s', 'HIGH')
        if UDP in packet and DNS in packet and DNSQR in packet and int(packet[DNS].qr) == 0:
            qname = bytes(packet[DNSQR].qname)
            if len(qname) >= self.dns_length:
                token = ('DNS_LONG_QUERY', src)
                if now - self.last_alert.get(token, float('-inf')) >= self.window:
                    self.last_alert[token] = now
                    alerts.append({'timestamp': datetime.fromtimestamp(now, timezone.utc).isoformat(),
                                   'severity': 'LOW', 'event_type': 'DNS_LONG_QUERY',
                                   'source_ip': src, 'destination_ip': dst,
                                   'description': f'DNS query name length {len(qname)} bytes (heuristic)'})
            check('DNS_RATE', src, None, self.thresholds['DNS_RATE'],
                  '{count} DNS queries in {window:g}s', 'MEDIUM')
        return alerts

    def process(self, packet):
        """Backward-compatible single-alert interface."""
        results = self.process_all(packet)
        return results[0] if results else None


class PortScanDetector(ThreatDetector):
    def __init__(self, threshold=10, window=10.0):
        super().__init__(port_threshold=threshold, window=window,
                         syn_threshold=10**9, icmp_threshold=10**9, dns_threshold=10**9)

    def process_all(self, packet):
        return [a for a in super().process_all(packet) if a['event_type'] == 'PORT_SCAN']
