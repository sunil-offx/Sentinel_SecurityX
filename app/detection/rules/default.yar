/*
    SentinelX Default YARA Rules (Phase 1 MVP)
    Used for local static inspection and benign testing.
*/

rule SentinelX_Test_Rule {
    meta:
        description = "Benign rule for SentinelX testing and verification"
        author = "SentinelX Core Team"
        severity = "HIGH"
        date = "2026-09-30"
    strings:
        $test_token = "SENTINELX_MALWARE_TEST_STRING_9988" ascii wide nocase
        $test_sig   = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*" ascii
    condition:
        any of them
}

rule Suspicious_PowerShell_Download_Cradle {
    meta:
        description = "Detects in-memory execution and download cradle invocations in scripts"
        author = "SentinelX Core Team"
        severity = "HIGH"
    strings:
        $s1 = "Net.WebClient" ascii wide nocase
        $s2 = "DownloadString(" ascii wide nocase
        $s3 = "DownloadFile(" ascii wide nocase
        $s4 = "Invoke-Expression" ascii wide nocase
        $s5 = "IEX(" ascii wide nocase
        $s6 = "Start-Process" ascii wide nocase
        $s7 = "-WindowStyle Hidden" ascii wide nocase
    condition:
        ($s1 and ($s2 or $s3) and ($s4 or $s5)) or ($s6 and $s7)
}

rule Suspicious_Ransomware_Note_Keywords {
    meta:
        description = "Detects strings frequently used in ransom notes and extortion notices"
        author = "SentinelX Core Team"
        severity = "CRITICAL"
    strings:
        $r1 = "your files have been encrypted" ascii wide nocase
        $r2 = "send bitcoin to" ascii wide nocase
        $r3 = "pay the ransom" ascii wide nocase
        $r4 = "decrypt your files" ascii wide nocase
        $r5 = "all your documents, photos, databases" ascii wide nocase
    condition:
        2 of ($r*)
}

rule Suspicious_Process_Injection_Indicators {
    meta:
        description = "Detects process injection and remote thread API string patterns"
        author = "SentinelX Core Team"
        severity = "HIGH"
    strings:
        $api1 = "CreateRemoteThread" ascii wide
        $api2 = "WriteProcessMemory" ascii wide
        $api3 = "VirtualAllocEx" ascii wide
        $api4 = "QueueUserAPC" ascii wide
        $api5 = "SetWindowsHookEx" ascii wide
    condition:
        2 of ($api*)
}

rule Suspicious_Script_Obfuscation_Indicator {
    meta:
        description = "Detects common script-based evasion and obfuscation commands"
        author = "SentinelX Core Team"
        severity = "MEDIUM"
    strings:
        $cmd1 = "powershell -enc" ascii wide nocase
        $cmd2 = "powershell -encodedcommand" ascii wide nocase
        $cmd3 = "certutil -urlcache" ascii wide nocase
        $cmd4 = "bitsadmin /transfer" ascii wide nocase
        $cmd5 = "vssadmin delete shadows" ascii wide nocase
    condition:
        any of them
}
