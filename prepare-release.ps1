# Stage the installer and checksum after a successful Windows build.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$versionLine = Get-Content '.\app\version.py' | Where-Object { $_ -match '^VERSION\s*=' } | Select-Object -First 1
if (-not $versionLine -or $versionLine -notmatch '"([0-9]+\.[0-9]+\.[0-9]+)"') { throw 'Cannot read version from app/version.py.' }
$version = $Matches[1]
$installer = ".\installer-output\Foxbat-NIDS-Setup-v$version.exe"
if (-not (Test-Path $installer)) { throw "Installer not found: $installer. Run .\build-installer.ps1 first." }
$signature = Get-AuthenticodeSignature $installer
if (-not $signature.SignerCertificate) { Write-Warning 'Installer is not signed. Do not claim it is signed in release notes.' }
else { Write-Host "Installer signer: $($signature.SignerCertificate.Subject) (trust status: $($signature.Status))" }
$out = Join-Path $PSScriptRoot 'release-output'
New-Item -ItemType Directory -Path $out -Force | Out-Null
Get-ChildItem $out -File | Remove-Item -Force
Copy-Item $installer $out
$staged = Join-Path $out (Split-Path $installer -Leaf)
$hash = (Get-FileHash $staged -Algorithm SHA256).Hash.ToLowerInvariant()
"$hash  $(Split-Path $staged -Leaf)" | Set-Content (Join-Path $out 'SHA256SUMS.txt') -Encoding ascii
Copy-Item '.\RELEASE-NOTES-v0.8.14.md' (Join-Path $out 'RELEASE_NOTES.md')
Write-Host "Release assets staged in $out"
Write-Host "SHA256: $hash"
