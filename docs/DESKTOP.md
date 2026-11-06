# Foxbat Windows Desktop (PyWebview + PyInstaller)

## Build on Windows

Requirements: Python 3.12+, Npcap for live capture, Microsoft Edge WebView2 Runtime (usually present on current Windows 10/11). The Windows executable **must be built on Windows**; PyInstaller does not cross-compile from Linux.

From PowerShell in the repository root:

```powershell
.\build-windows.ps1
```

If PowerShell script execution is restricted, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\build-windows.ps1
```

The script creates `.venv` if necessary, installs dependencies, runs tests, and builds `dist\Foxbat\Foxbat.exe`. Double-click it. **Distribute the entire `dist\Foxbat` folder**, not only the EXE. Zip that folder for a GitHub Release.

## How it works

`desktop/launcher.py` starts one Uvicorn server on a randomly assigned **127.0.0.1** port, then opens the existing dashboard in a native WebView2 window. Closing the window stops live capture and shuts down the server. No browser tab is opened. The app uses the existing FastAPI routes and Scapy detection engine.

## Data persistence and migration

The desktop application stores its database in `%LOCALAPPDATA%\Foxbat\foxbat.db`. The previous web version stored it in the project directory. **To preserve your existing alerts**, close Foxbat, then copy your existing `foxbat.db` into `%LOCALAPPDATA%\Foxbat\foxbat.db` before first launching the desktop version. Back up both files first. An explicit `FOXBAT_DB` environment variable overrides the default location.

## Troubleshooting

- **Blank window or startup error:** Install/repair Microsoft Edge WebView2 Runtime; check antivirus and local loopback restrictions.
- **Live capture fails:** Install Npcap, and run Foxbat as Administrator only if your capture permissions require it. Offline features do not require Npcap capture permissions.
- **Windows SmartScreen warning:** A self-signed build can still trigger a warning because the publisher is not publicly trusted. Do not bypass enterprise security policies; code signing is recommended for public distribution.
- **The application doesn't open:** Run `python -m desktop.launcher` from the virtual environment to see console errors.
- **Port changes each launch:** This is intentional; Foxbat is a local desktop application, not a remotely hosted service.

## Security note

The existing local API has no authentication. Binding to loopback prevents normal remote access but other local processes can reach it. This is a portfolio prototype, not a hardened multi-user endpoint security product. Only monitor traffic you are authorized to inspect.

## Release checklist

1. Build and test on a Windows machine.
2. Verify demo alerts, real packet capture, CSV export, Markdown report download, and clean shutdown.
3. Verify alerts persist after restart and inspect the new data directory.
4. Inspect `dist` for private data and secrets; do not bundle real PCAPs or databases.
5. Zip `dist\Foxbat` and attach it to GitHub Releases, alongside the source code.
