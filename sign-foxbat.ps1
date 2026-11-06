param([Parameter(Mandatory=$true)][string]$FilePath)
$ErrorActionPreference = 'Stop'
$target = (Resolve-Path $FilePath -ErrorAction Stop).Path
$subject = 'CN=Foxbat NIDS Development'
$cert = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert | Where-Object { $_.Subject -eq $subject -and $_.HasPrivateKey -and $_.NotAfter -gt (Get-Date) } | Sort-Object NotAfter -Descending | Select-Object -First 1
if (-not $cert) {
    Write-Warning 'No Foxbat development certificate found. Output remains unsigned. Run .\create-dev-certificate.ps1 to enable signing.'
    exit 0
}
$signature = Set-AuthenticodeSignature -FilePath $target -Certificate $cert -HashAlgorithm SHA256
if ($signature.Status -eq 'NotSigned' -or -not $signature.SignerCertificate -or $signature.SignerCertificate.Thumbprint -ne $cert.Thumbprint) {
    throw "Signing failed: $($signature.Status) - $($signature.StatusMessage)"
}
Write-Host "Signed $target with development certificate $($cert.Thumbprint)"
Write-Host "Signature status: $($signature.Status) (untrusted self-signed certificates can report UnknownError or NotTrusted)"
