# Foxbat — Python Network Intrusion Detection System

Foxbat is a **local-first, educational NIDS** featuring Scapy packet capture, offline PCAP inspection, rule-based detection, a FastAPI REST API, SQLite alert history, and a responsive security dashboard.

> **Status: v0.8.8.** This is a portfolio prototype, detections require analyst validation.

## Features

- Live IP packet monitoring with Scapy + Npcap (Windows)
- Offline PCAP import, with repeat imports counted again
- TCP port scan, SYN flood, ICMP flood, DNS rate and long-query heuristics
- SQLite persistence with event origin (`live`, `pcap`, `demo`, `legacy`)
- Searchable alerts, severity/origin filters, CSV export, charts and investigation details
- Per-alert Markdown incident report download and GitHub Actions test workflow

## Run locally (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. Install [Npcap](https://npcap.com/) for live capture. Do not use `--reload` while capturing; use one server worker. Windows may require elevated permissions.

To test offline analysis:

```powershell
.\.venv\Scripts\python.exe samples\generate_demo_pcap.py
.\.venv\Scripts\python.exe -m app.pcap samples\demo_scan.pcap
```

To export a report, open an alert in the dashboard and click **Download incident report (.md)**. The report is an analyst worksheet, not a verified incident conclusion.

## Architecture

```text
Authorized Wi-Fi traffic --> Scapy AsyncSniffer --+
                                                +--> ThreatDetector --> SQLite --> FastAPI --> Dashboard
Authorized PCAP file --> Scapy PcapReader -------+
```

## API highlights

| Endpoint | Purpose |
| --- | --- |
| `GET /api/health` | Health check |
| `GET /api/capture` | Live capture state |
| `POST /api/capture/start` / `stop` | Local capture control |
| `GET /api/alerts` | Search/filter alert history |
| `GET /api/alerts/{id}` | Event evidence |
| `GET /api/alerts/{id}/report` | Markdown incident worksheet |
| `GET /api/alerts/export` | CSV export |
| `GET /api/analytics` | Alert aggregates |

## First public beta release

See [public release instructions](docs/PUBLIC_RELEASE.md), [release notes](docs/RELEASE_NOTES_v0.8.8.md), [security policy](SECURITY.md), and [changelog](CHANGELOG.md). After building the Windows installer, run `./prepare-release.ps1` to stage the installer and SHA-256 checksum. No public-trust code-signing certificate is provided.

## Security limitations

- Keep the web server bound to `127.0.0.1`. The development API is not authenticated and should not be exposed publicly.
- Monitor only interfaces and traffic you are authorized to inspect. Normal Wi-Fi capture does not provide visibility into all other clients.
- Detection thresholds are static heuristics, not validated signatures; false positives and false negatives are expected.
- Alerts store IP addresses and descriptions; treat exported reports as potentially sensitive.
- Older migrated events may have `legacy` origin; sample PCAP events are not live captures.
- A database backup is recommended before updating.


## Source layout

- `app/`: API, packet capture, detection logic, and dashboard assets
- `desktop/`: WebView2 desktop launcher and local data paths
- `assets/`: selected Foxbat logo and Windows icon
- `tests/`: automated checks for detection, APIs, and version consistency
- `docs/`: desktop instructions and release checklist
- `build-*.ps1`, `Foxbat-Installer.iss`: Windows packaging

Historical patch notes were consolidated into this README and `docs/` to keep the repository tidy.
