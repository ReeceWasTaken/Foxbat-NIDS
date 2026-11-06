"""Import a local PCAP into Foxbat's database; no live sniffing required."""
import argparse
from pathlib import Path

from scapy.utils import PcapReader
from app.detector import ThreatDetector
from app.main import db


def import_pcap(path, threshold=10, window=10.0):
    detector = ThreatDetector(port_threshold=threshold, window=window)
    analyzed = 0
    found = []
    with PcapReader(str(path)) as reader:
        for packet in reader:
            analyzed += 1
            found.extend(detector.process_all(packet))
    with db() as conn:
        for a in found:
            conn.execute('''INSERT INTO alerts
                (timestamp,severity,event_type,source_ip,destination_ip,description,simulated,origin)
                VALUES (?,?,?,?,?,?,0,'pcap')''',
                (a['timestamp'], a['severity'], a['event_type'], a['source_ip'], a['destination_ip'], a['description']))
        conn.execute('''CREATE TABLE IF NOT EXISTS imports
            (id INTEGER PRIMARY KEY, filename TEXT NOT NULL, packets INTEGER NOT NULL, alerts INTEGER NOT NULL)''')
        conn.execute('INSERT INTO imports (filename,packets,alerts) VALUES (?,?,?)',
                     (Path(path).name, analyzed, len(found)))
    return analyzed, len(found)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import an authorized PCAP into Foxbat')
    parser.add_argument('pcap', type=Path)
    parser.add_argument('--threshold', type=int, default=10)
    parser.add_argument('--window', type=float, default=10.0)
    args = parser.parse_args()
    if args.threshold < 2 or args.window <= 0:
        parser.error('--threshold must be >= 2 and --window > 0')
    packets, alerts = import_pcap(args.pcap, args.threshold, args.window)
    print(f'Imported {packets} packets; created {alerts} security alerts.')
