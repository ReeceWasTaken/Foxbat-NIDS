"""Single local-only Scapy capture worker. No arbitrary interface selection via API."""
import threading
from collections import Counter, deque
from datetime import datetime, timezone
from scapy.all import AsyncSniffer, IP, IPv6, TCP, UDP, ICMP
from app.detector import ThreatDetector

class CaptureManager:
    def __init__(self):
        self.lock = threading.RLock()
        self.sniffer = None
        self.running = False
        self.interface = None
        self.total = 0
        self.protocols = Counter()
        self.buckets = deque(maxlen=60)
        self.detector = ThreatDetector()

    def _packet(self, packet):
        if TCP in packet: proto = 'TCP'
        elif UDP in packet: proto = 'UDP'
        elif ICMP in packet: proto = 'ICMP'
        else: proto = 'OTHER'
        # Group packets into one-second buckets for the live traffic chart.
        second = datetime.now(timezone.utc).strftime('%H:%M:%S')
        with self.lock:
            self.total += 1
            self.protocols[proto] += 1
            if self.buckets and self.buckets[-1][0] == second:
                self.buckets[-1] = (second, self.buckets[-1][1] + 1)
            else:
                self.buckets.append((second, 1))
            alerts = self.detector.process_all(packet)
        if alerts:
            # Import lazily to avoid circular imports.
            from app.main import db
            with db() as conn:
              for alert in alerts:
                conn.execute("""INSERT INTO alerts
                  (timestamp,severity,event_type,source_ip,destination_ip,description,simulated,origin)
                  VALUES (?,?,?,?,?,?,0,'live')""",
                  (alert['timestamp'], alert['severity'], alert['event_type'],
                   alert['source_ip'], alert['destination_ip'], alert['description']))

    def start(self):
        with self.lock:
            if self.running:
                return False
            # Default interface is Scapy's system-selected route; no remote interface parameter.
            sniffer = AsyncSniffer(prn=self._packet, store=False, filter='ip or ip6')
            try:
                sniffer.start()
            except Exception:
                self.sniffer = None
                raise
            self.sniffer = sniffer
            self.running = True
            return True

    def stop(self):
        with self.lock:
            if not self.running:
                return False
            sniffer = self.sniffer
            self.running = False
            self.sniffer = None
        try:
            sniffer.stop(join=True)
        except Exception:
            # A failed capture can stop on its own before the stop request.
            pass
        return True

    def snapshot(self):
        with self.lock:
            if self.running and self.sniffer and not self.sniffer.running:
                self.running = False
            return {'running': self.running, 'live_packets': self.total,
                    'protocols': dict(self.protocols),
                    'traffic': [{'time': t, 'packets': n} for t,n in self.buckets]}

capture = CaptureManager()
