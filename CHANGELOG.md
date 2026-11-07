# Changelog

## v0.8.14 — Frameless stable release candidate

- Restored the integrated Foxbat frameless title bar and native pywebview dragging.
- Retained the v0.8.13 leaf-only JavaScript bridge fix; native window references remain outside the bridge.
- Removed the temporary minimal/dashboard/full diagnostic modes and periodic thread snapshots.
- Retained rotating desktop error logging, API shutdown, detection engine, and dashboard.
- Windows drag/resize behavior and installer must be verified on the target PC.

## v0.8.12 — Installer stability beta

- Changed the default installation directory to `%LOCALAPPDATA%\Foxbat NIDS` after location-based Windows testing.
- Moved WebView2 browser data to `%LOCALAPPDATA%\Foxbat\webview2`.
- Disabled Inno Setup's reuse of the previous installation path.
- Updated release notes and version metadata.

## v0.8.8 — Public beta release preparation

- Added public release documentation, security guidance, and a repeatable release packaging script.
- Added SHA-256 checksum generation and a release asset verification checklist.
- Updated the application version to 0.8.8.
- Kept the existing detection engine, dashboard, icon, desktop window, and Windows installer build flow.

## v0.8.7

- Centralized version management and cleaned source tree.
- Added Foxbat icon assets and development-only signing scripts in preceding releases.

Earlier versions were iterative development builds.
