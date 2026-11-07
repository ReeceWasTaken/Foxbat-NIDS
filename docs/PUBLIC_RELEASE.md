# Publishing Foxbat NIDS v0.8.14 to the existing GitHub repository

Repository: https://github.com/ReeceWasTaken/Foxbat-NIDS

## Before committing

1. Inspect every file and existing Git history for secrets, credentials, private IPs, sensitive screenshots, real PCAPs, and databases.
2. Add sanitized dashboard screenshots to `screenshots/` if available.
3. Choose a license if you want to authorize reuse; no open-source license is currently granted.
4. On Windows, run `./build-windows.ps1`, test the executable, and run `./build-installer.ps1`.
5. Run `./prepare-release.ps1` to stage the installer, checksum, and release notes.

## Upload to the existing repository

**Recommended:** Clone the existing repository first; do not create another repository or blindly overwrite files.

```powershell
git clone https://github.com/ReeceWasTaken/Foxbat-NIDS.git
cd Foxbat-NIDS
```

Copy the **contents** of the packaged `Foxbat-Desktop` folder into the clone (not the containing folder), review differences, and then:

```powershell
git status
git diff --check
git add .
git status
git commit -m "Prepare Foxbat NIDS v0.8.14 GitHub release"
git push origin main
```

If the existing default branch is not `main`, use its actual branch name. Review `git status` to confirm no databases, captures, build outputs, certificates, or other private files are staged.

## GitHub Release

After final Windows verification, create a release with tag `v0.8.14` and title `Foxbat NIDS v0.8.14 Beta`. Use `RELEASE-NOTES-v0.8.14.md` as the description and upload from `release-output/`:

- `Foxbat-NIDS-Setup-v0.8.14.exe`
- `SHA256SUMS.txt`
- `RELEASE_NOTES.md` (optional)

The installer is **not** included in the source ZIP. Build and test it on Windows before publishing. The optional self-signed development certificate is not publicly trusted; do not distribute private keys or tell users to trust a development root certificate.
