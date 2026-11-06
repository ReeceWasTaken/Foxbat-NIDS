# Foxbat — Python Network Intrusion Detection System

Foxbat is a **local-first, educational NIDS** featuring Scapy packet capture, offline PCAP inspection, rule-based detection, a FastAPI REST API, SQLite alert history, and a responsive security dashboard.

> **Status: v0.8.8.** This is a portfolio prototype, **not** a production IDS. Detections are heuristics and require analyst validation.

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

## GitHub publishing

Run tests, add screenshots in `screenshots/`, and publish **source code only**. `.gitignore` excludes virtual environments, SQLite databases, and PCAPs. Review logs, screenshots, and commit history for private addresses or sensitive data before publishing. GitHub Actions runs pytest on pushes and pull requests.

## Security limitations

- Keep the web server bound to `127.0.0.1`. The development API is not authenticated and should not be exposed publicly.
- Monitor only interfaces and traffic you are authorized to inspect. Normal Wi-Fi capture does not provide visibility into all other clients.
- Detection thresholds are static heuristics, not validated signatures; false positives and false negatives are expected.
- Alerts store IP addresses and descriptions; treat exported reports as potentially sensitive.
- Older migrated events may have `legacy` origin; sample PCAP events are not live captures.
- A database backup is recommended before updating.

## Portfolio showcase

Add sanitized screenshots under `screenshots/` before publishing. Recommended images: `dashboard.png`, `investigation.png`, and `traffic.png`. See [release checklist](docs/RELEASE_CHECKLIST.md).

**Tech stack:** Python, Scapy, FastAPI, SQLite, HTML/CSS/JavaScript, pytest, GitHub Actions.

**License:** No license is included in this release-ready package; choose one before inviting external reuse.

## Windows desktop edition (PyWebview)

Build a native Windows app window using `build-windows.ps1`. The resulting folder is `dist\Foxbat`, containing `Foxbat.exe` and bundled dependencies. See [desktop instructions](docs/DESKTOP.md). A local build can be self-signed with the development certificate (not publicly trusted) and still requires Npcap for live capture and Edge WebView2 Runtime for the window. The desktop database lives under `%LOCALAPPDATA%\Foxbat`.

## Releasing a new version

Change **only** `VERSION` in `app/version.py` (for example, `0.8.8`). The API's OpenAPI metadata, `/api/health`, and the dashboard footer use that value automatically. The build scripts regenerate `version.iss` so Inno Setup uses the same version and installer filename. Avoid editing `version.iss` manually.

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\build-windows.ps1
.\build-installer.ps1
```

`create-dev-certificate.ps1` sets up an optional **local-only** signing identity. The signing step is skipped with a warning if it is absent. Self-signed releases remain untrusted by other computers.

## Source layout

- `app/`: API, packet capture, detection logic, and dashboard assets
- `desktop/`: WebView2 desktop launcher and local data paths
- `assets/`: selected Foxbat logo and Windows icon
- `tests/`: automated checks for detection, APIs, and version consistency
- `docs/`: desktop instructions and release checklist
- `build-*.ps1`, `Foxbat-Installer.iss`: Windows packaging

Historical patch notes were consolidated into this README and `docs/` to keep the repository tidy.
