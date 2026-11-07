# v0.8.11 Windows verification

1. Back up `%LOCALAPPDATA%\Foxbat\foxbat.db` if necessary.
2. Uninstall the existing Foxbat v0.8.8 using Windows Installed Apps.
3. Build with `build-windows.ps1` and `build-installer.ps1`.
4. Install v0.8.11 and verify the installed executable is at `%LOCALAPPDATA%\Foxbat NIDS\Foxbat.exe`.
5. Launch from the desktop shortcut and directly from the installed executable.
6. Confirm window drag, scrolling, navigation, monitoring, and clean shutdown.
7. Confirm WebView2 profile is created under `%LOCALAPPDATA%\Foxbat\webview2`.
8. Only publish the release after confirming the freeze no longer reproduces.

This is a location-specific mitigation, not a proven root-cause fix. If the freeze persists, inspect WebView2 runtime logs, Windows Event Viewer, and security software policies.
