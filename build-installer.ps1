$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

if (-not (Test-Path '.\dist\Foxbat\Foxbat.exe')) {
    throw 'Foxbat.exe not found. Run .\build-windows.ps1 first.'
}

$isccCandidates = @(
    "$env:LOCALAPPDATA\Programs\Inno Setup 7\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 7\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 7\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
)
$iscc = $isccCandidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if (-not $iscc) {
    $cmd = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if ($cmd) { $iscc = $cmd.Source }
}
if (-not $iscc) {
    throw 'Inno Setup compiler (ISCC.exe) not found. Install Inno Setup from https://jrsoftware.org/isdl.php.'
}

# The version comes from app/version.py, not a second hard-coded value.
$version = & (Join-Path $PSScriptRoot 'sync-version.ps1')
Write-Host "Building Foxbat NIDS v$version installer..."
& $iscc '.\Foxbat-Installer.iss'
if ($LASTEXITCODE -ne 0) { throw 'Inno Setup failed.' }
Write-Host "Installer created: installer-output\Foxbat-NIDS-Setup-v$version.exe"

# Development-only Authenticode signing, if a certificate was created locally.
& (Join-Path $PSScriptRoot 'sign-foxbat.ps1') -FilePath ".\installer-output\Foxbat-NIDS-Setup-v$version.exe"
if ($LASTEXITCODE -ne 0) { throw 'Installer signing failed.' }
