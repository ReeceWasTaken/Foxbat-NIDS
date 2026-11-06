# Foxbat public release checklist

- [ ] Confirm `VERSION` in `app/version.py` is `0.8.8` and UI/API/installer agree.
- [ ] Select a LICENSE if you intend to permit third-party reuse.
- [ ] Run Windows build and tests; confirm the installer launches and uninstalls.
- [ ] Test Npcap capture, PCAP import, alerts, exports, window dragging, and shortcut icons.
- [ ] Add sanitized screenshots; review files and Git history for secrets and personal network data.
- [ ] Verify the installer signature is present, and disclose that self-signed certificates are not publicly trusted.
- [ ] Run `./prepare-release.ps1` and verify its SHA-256 checksum.
- [ ] Publish GitHub tag `v0.8.8` with installer, checksums, and release notes.
- [ ] Download the public release and test it on a clean Windows system or VM.
