# Create a local development-only Authenticode certificate. Never export the private key to the repo.
$ErrorActionPreference = 'Stop'
$subject = 'CN=Foxbat NIDS Development'
$existing = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert | Where-Object { $_.Subject -eq $subject -and $_.NotAfter -gt (Get-Date) } | Sort-Object NotAfter -Descending | Select-Object -First 1
if ($existing) {
    Write-Host "Existing development certificate: $($existing.Thumbprint)"
    exit 0
}
$cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject $subject -CertStoreLocation 'Cert:\CurrentUser\My' -KeyAlgorithm RSA -KeyLength 3072 -HashAlgorithm SHA256 -NotAfter (Get-Date).AddYears(3) -KeyExportPolicy NonExportable
Write-Host "Created local development certificate: $($cert.Thumbprint)"
Write-Warning 'Self-signed certificates are not trusted on other machines and do not eliminate SmartScreen warnings.'
