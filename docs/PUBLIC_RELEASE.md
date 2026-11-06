# First public GitHub release — v0.8.8 Beta

## Before publishing

1. Choose a license deliberately. **No open-source license is included.** Public GitHub visibility alone does not grant reuse rights. If you want open-source contributions, add an appropriate LICENSE file before inviting reuse.
2. Check all files and Git history for secrets, personal data, internal IP addresses, and PCAP contents. Do not commit certificate private keys or `.pfx` files.
3. Add real, sanitized dashboard screenshots to `screenshots/`.
4. On Windows, run `./build-windows.ps1` and `./build-installer.ps1` in PowerShell. Verify tests, app startup, window movement, taskbar icon, shortcuts, capture, PCAP import, alerts, and installer/uninstaller.
5. Run `./prepare-release.ps1` to generate a SHA-256 checksum and a release staging folder.
6. Review `release-output/` before uploading. Only upload the installer, checksums, and relevant notes as release assets. Do not upload your development certificate private key.

## GitHub setup

Create a repository called `Foxbat-NIDS` under your GitHub account (if it does not already exist). From the extracted `Foxbat-Desktop` directory:

```powershell
git init
git add .
git status
git commit -m "Prepare Foxbat NIDS v0.8.8 public beta"
git branch -M main
git remote add origin https://github.com/ReeceWasTaken/Foxbat-NIDS.git
git push -u origin main
```

If the repository already exists, clone it and copy these files into the clone, or use its existing Git remote rather than running `git init` or adding a duplicate remote. Review `git status` before committing.

Create a GitHub Release with tag `v0.8.8`, title `Foxbat NIDS v0.8.8 Beta`, and paste `docs/RELEASE_NOTES_v0.8.8.md`. Attach `Foxbat-NIDS-Setup-v0.8.8.exe` and `SHA256SUMS.txt` from `release-output/`.

## Distribution disclosure

The Windows installer is self-signed for development. Other PCs do not automatically trust that signature; Windows may warn. Users should verify the SHA-256 checksum and obtain the installer only from the official repository release. Do not instruct users to disable antivirus or install your development certificate as a trusted root.

## After publishing

Test the published download on a separate clean Windows system or VM. Ensure the GitHub download checksum matches `SHA256SUMS.txt`. Only then link the release from your portfolio.
