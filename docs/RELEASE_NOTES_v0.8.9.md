# Foxbat NIDS v0.8.11 Beta — Installer Stability Fix

This beta changes the default per-user install path to `%LOCALAPPDATA%\Foxbat NIDS` and stores the embedded WebView2 profile in `%LOCALAPPDATA%\Foxbat\webview2`. These changes address a location-specific UI freeze observed with v0.8.8 on one Windows test system. Windows validation is still required.

**Upgrade note:** Uninstall the previous v0.8.8 installation first using Windows Installed Apps. Back up `%LOCALAPPDATA%\Foxbat\foxbat.db` before making any changes to user data. The installer retains the same Inno Setup AppId, but does not automatically migrate or remove an old installation folder.

**Security:** Foxbat's self-signed development signature is not publicly trusted and does not remove SmartScreen warnings. Npcap is required for live capture. Use only on authorized networks.
