/*
    SentinelX Threat Signatures - Extended Rules Repository
    Contains extended threat indicators for Windows PE and script threats.
*/

rule Windows_Suspicious_Downloader {
    meta:
        description = "Detects scripts or binaries with embedded multi-source downloader calls"
        severity = "HIGH"
        date = "2026-09-30"
    strings:
        $d1 = "URLDownloadToFile" ascii wide
        $d2 = "powershell -WindowStyle Hidden -Command (New-Object System.Net.WebClient)" ascii wide nocase
        $d3 = "certutil.exe -urlcache -split -f" ascii wide nocase
    condition:
        any of them
}

rule Windows_Ransom_Note_Pattern {
    meta:
        description = "Detects generic ransomware ransom notes and extortion demands"
        severity = "CRITICAL"
        date = "2026-09-30"
    strings:
        $m1 = "All your files have been encrypted with strong algorithms" ascii wide nocase
        $m2 = "To recover your data you need a private key" ascii wide nocase
        $m3 = "Send payment to the following Bitcoin address" ascii wide nocase
        $m4 = "Any attempt to decrypt files with third party software will damage them" ascii wide nocase
    condition:
        2 of them
}
