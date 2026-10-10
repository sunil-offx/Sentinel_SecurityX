"""Integration test verifying Phase 2 & Phase 3 end-to-end pipelines."""

from pathlib import Path

from app.core.scanner import FileScanner
from app.database.database import db
from app.database.models import (
    EventLogRecord,
    NetworkAlertRecord,
    ProcessAlertRecord,
    RiskLevel,
)


def test_phase2_phase3_full_pipeline() -> None:
    # 1. Reset database state
    db.clear_all()

    # 2. Run file scan with ML classification
    scanner = FileScanner(save_to_db=True)
    sample_path = Path("tests/fixtures/clean_sample.exe")
    assert sample_path.exists()

    scan_result = scanner.scan_file(sample_path)
    assert scan_result.metadata.sha256 != ""
    assert scan_result.assessment is not None
    assert scan_result.ml_prediction is not None
    assert scan_result.ml_prediction.is_pe
    assert 0.0 <= scan_result.ml_prediction.malware_probability <= 1.0

    # 3. Simulate Process Alert (Phase 2)
    p_alert = ProcessAlertRecord(
        pid=5555,
        process_name="powershell.exe",
        ppid=1234,
        parent_name="winword.exe",
        command_line="powershell.exe -enc SQBFAFgA...",
        severity=RiskLevel.CRITICAL.value,
        reason="Suspicious Process Spawn: Document 'winword.exe' spawned 'powershell.exe'",
        status="ACTIVE",
    )
    p_id = db.add_process_alert(p_alert)
    assert p_id is not None
    assert p_id > 0

    retrieved_procs = db.get_process_alerts(status="ACTIVE")
    assert len(retrieved_procs) == 1
    assert retrieved_procs[0].process_name == "powershell.exe"
    assert retrieved_procs[0].parent_name == "winword.exe"

    # 4. Simulate Network Telemetry Alert (Phase 3)
    n_alert = NetworkAlertRecord(
        pid=5555,
        process_name="powershell.exe",
        local_addr="192.168.1.10:49200",
        remote_addr="198.51.100.23",
        remote_port=4444,
        protocol="TCP",
        severity=RiskLevel.CRITICAL.value,
        reason="Connection to Suspicious Port 4444 (Metasploit Default Listener)",
    )
    n_id = db.add_network_alert(n_alert)
    assert n_id is not None
    assert n_id > 0

    retrieved_net = db.get_network_alerts()
    assert len(retrieved_net) == 1
    assert retrieved_net[0].remote_port == 4444

    # 5. Simulate Windows Event Log (Phase 3)
    ev_record = EventLogRecord(
        event_id=4104,
        channel="Microsoft-Windows-PowerShell/Operational",
        provider="Microsoft-Windows-PowerShell",
        severity=RiskLevel.HIGH.value,
        message="Suspicious Script Block: WebClient remote download cradle",
        event_time="2026-10-07T08:30:00Z",
    )
    e_id = db.add_event_log_record(ev_record)
    assert e_id is not None
    assert e_id > 0

    retrieved_evs = db.get_event_log_records()
    assert len(retrieved_evs) == 1
    assert retrieved_evs[0].event_id == 4104

    # 6. Verify Dashboard Metrics
    stats = db.get_stats()
    assert stats["total_scanned"] == 1
    assert stats["active_process_alerts"] == 1
    assert stats["total_network_alerts"] == 1
    assert stats["total_event_logs"] == 1

    # Clean up after test
    db.clear_all()
