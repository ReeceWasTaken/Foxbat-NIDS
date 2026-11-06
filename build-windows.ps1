$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
# Make sure the installer metadata is ready before packaging.
$version = & (Join-Path $PSScriptRoot 'sync-version.ps1')
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
}
$python = ".\.venv\Scripts\python.exe"
& $python -m pip install -r requirements-desktop.txt
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed" }
& $python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed; build cancelled" }
& $python -m PyInstaller --noconfirm --clean --onedir --windowed --name Foxbat `
    --paths . `
    --icon "assets/foxbat.ico" `
    --add-data "app/static;app/static" `
    --collect-all scapy `
    --collect-all webview `
    --hidden-import app.main `
    --hidden-import app.live `
    desktop/launcher.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed" }
Write-Host "Foxbat v$version build complete: dist\Foxbat\Foxbat.exe"

# Sign the built executable with the local development certificate when available.
& (Join-Path $PSScriptRoot 'sign-foxbat.ps1') -FilePath '.\dist\Foxbat\Foxbat.exe'
if ($LASTEXITCODE -ne 0) { throw 'Executable signing failed.' }
