# Read the release number from the Python module and feed it to Inno Setup.
$ErrorActionPreference = 'Stop'
$versionFile = Join-Path $PSScriptRoot 'app/version.py'
$content = Get-Content -LiteralPath $versionFile -Raw
$match = [regex]::Match($content, '(?m)^VERSION\s*=\s*["''](\d+\.\d+\.\d+)["'']')
if (-not $match.Success) { throw 'Could not read VERSION from app/version.py' }
$version = $match.Groups[1].Value
$include = "; Generated from app/version.py; do not edit by hand.`r`n#define AppVersion `"$version`"`r`n"
Set-Content -LiteralPath (Join-Path $PSScriptRoot 'version.iss') -Value $include -Encoding ASCII -NoNewline
Write-Host "Foxbat release version: $version"
return $version
