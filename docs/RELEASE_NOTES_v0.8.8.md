# Foxbat NIDS v0.8.8 Beta

Foxbat is a Windows desktop network intrusion detection prototype built with Python, Scapy, FastAPI, SQLite, and PyWebview. Its interface uses a retro military radar-inspired design.

## Features

- Local live packet monitoring with Npcap and Scapy
- Offline PCAP analysis
- Rule-based alerts for port scanning, SYN floods, ICMP floods, and DNS anomalies
- Searchable alert history, analytics, CSV export, and Markdown incident reports
- Windows installer, custom application icon, and desktop interface

## Install

1. Download `Foxbat-NIDS-Setup-v0.8.8.exe` from this release.
2. Compare its SHA-256 digest against `SHA256SUMS.txt`.
3. Install Npcap for live capture, and ensure Microsoft Edge WebView2 Runtime is available.
4. Run Foxbat from the Start Menu or desktop shortcut. Capture may require elevated privileges.

## Important limitations

**Beta / educational software.** Not suitable as a sole security control. Monitor only networks you are authorized to inspect. The local API has no authentication and must not be exposed beyond localhost.

**Signing:** The installer may be signed with a *self-signed development certificate*, which is not publicly trusted. Windows SmartScreen or publisher warnings may appear. Do not disable Windows security protections or install an unknown certificate as a trusted root.

**Privacy:** Alerts and reports may contain IP addresses and network metadata. Keep these files private.

## Source and license

The source is available in this repository. No open-source license has been selected yet; public visibility does not grant redistribution or modification rights.
