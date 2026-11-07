<div align="center">
  <img src="assets/Foxbat-logo.png" alt="Foxbat NIDS Logo" width="260">

  <h1>Foxbat NIDS</h1>

  <p><strong>Network Intrusion Detection System</strong></p>

  <p>Network Visibility • Threat Detection • Defensive Research</p>
</div>


**Foxbat NIDS v0.8.14** is an experimental Windows network intrusion detection system featuring a retro terminal-style dashboard, local alert history, packet analysis, and an embedded Microsoft Edge WebView2 desktop interface.

> **Status:** Beta / portfolio project. Detection is heuristic and may produce false positives or miss threats. Foxbat is not a substitute for production security monitoring.

## Features

- Live network packet capture and analysis using Scapy and Npcap
- Offline PCAP analysis, alerts, severity summaries, and dashboard analytics
- FastAPI backend bound to the local loopback interface
- Windows desktop interface using pywebview and WebView2
- Frameless window with custom title bar and native drag behavior
- Local SQLite persistence of detection history
- Windows installer built with PyInstaller and Inno Setup

## Screenshots

Add sanitized screenshots to [`screenshots/`](screenshots/) before publishing. Do not publish private IP addresses, real packet captures, credentials, or other sensitive network data.

## Install on Windows

Download `Foxbat-NIDS-Setup-v0.8.14.exe` from the **Releases** section after a release has been published. Verify its SHA-256 checksum against `SHA256SUMS.txt`. Install [Npcap](https://npcap.com/) separately for live packet capture. Microsoft Edge WebView2 Runtime is required for the desktop interface.

Foxbat stores mutable application data in `%LOCALAPPDATA%\Foxbat` and installs by default to `%LOCALAPPDATA%\Foxbat NIDS`. **Before upgrading from older releases, back up `%LOCALAPPDATA%\Foxbat\foxbat.db`.** Older installer versions may require uninstalling first.

The installer is signed only with a self-signed development certificate when one is available. This does **not** establish a publicly trusted publisher; Windows may display a warning.

## Build from source

Requires Windows, Python, PowerShell, and Inno Setup (to build the installer). From the repository root:

```powershell
.\build-windows.ps1
& .\dist\Foxbat\Foxbat.exe
.\build-installer.ps1
.\prepare-release.ps1
```

`build-windows.ps1` creates a virtual environment, installs dependencies, runs tests, and packages the desktop executable. `build-installer.ps1` requires Inno Setup and produces `installer-output\Foxbat-NIDS-Setup-v0.8.14.exe`. `prepare-release.ps1` stages the installer, checksum, and release notes in `release-output/`. These generated directories are excluded from Git.

For development or tests:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-desktop.txt
.\.venv\Scripts\python.exe -m pytest -q
```

## Project layout

| Path | Purpose |
| --- | --- |
| `app/` | FastAPI application, detection logic, packet capture, dashboard assets |
| `desktop/` | pywebview launcher and local data paths |
| `tests/` | Automated tests |
| `assets/` | Foxbat icon and artwork |
| `samples/` | Demo PCAP generation script |
| `docs/` | Windows build, release, and security documentation |
| `.github/workflows/` | GitHub Actions test workflow |

## Security and privacy

Foxbat is intended for **authorized network monitoring only**. The API is loopback-only and unauthenticated; do not expose it on public interfaces. Captures and alert records may contain sensitive network details. Do not commit local databases, PCAP files, signing keys, or certificates. See [SECURITY.md](SECURITY.md).

## License

No open-source license has been selected yet. Source visibility on GitHub does not itself grant permission to copy, modify, or redistribute the code. A license can be added later by the repository owner.

## Release history

See [CHANGELOG.md](CHANGELOG.md) and [v0.8.14 release notes](RELEASE-NOTES-v0.8.14.md).
