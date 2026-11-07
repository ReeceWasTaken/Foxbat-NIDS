# Foxbat NIDS v0.8.14 — Frameless release candidate

## Changes
- Frameless desktop window with custom Foxbat title bar and standard window actions.
- Retains v0.8.13 JavaScript bridge recursion fix. The native pywebview window is held in module-private state, not on the JS API object.
- Diagnostic modes and periodic faulthandler snapshots removed; rotating desktop log retained.
- Dashboard, packet capture, alert history and API retained.

## Windows validation
1. From `Foxbat-Desktop`, run `./build-windows.ps1` in PowerShell.
2. Run `./dist/Foxbat/Foxbat.exe` (no diagnostic mode arguments).
3. Drag the custom title bar repeatedly for 2–5 minutes; maximize, restore, minimize, resize and close/reopen.
4. Engage and disengage sensor; check alerts, analytics, scrolling and export.
5. If all pass, run `./build-installer.ps1` and repeat with the installed app.

Not verified on Windows by the authoring environment. If the frameless build freezes, use the known-working v0.8.13 build and provide `%LOCALAPPDATA%\Foxbat\logs\desktop.log`.
