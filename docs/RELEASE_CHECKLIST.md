# Foxbat v0.8.14 release checklist

- [ ] Review the existing Git repository and its history for sensitive data.
- [ ] Confirm `app/version.py`, UI, and installer all show `0.8.14`.
- [ ] Decide whether to add an open-source license.
- [ ] Add sanitized screenshots.
- [ ] Build on Windows and run automated tests.
- [ ] Test frameless dragging, resizing, minimize/maximize, and close/reopen.
- [ ] Test live capture, offline PCAP import, alerts, exports, and SQLite persistence.
- [ ] Test installer and uninstaller on Windows; back up existing database before upgrade.
- [ ] Confirm only intended source files are committed; exclude generated binaries and signing secrets.
- [ ] Run `./prepare-release.ps1` and verify SHA-256 checksum.
- [ ] Publish tag `v0.8.14` and attach installer and checksum.
- [ ] Test the published installer on a clean Windows environment.
