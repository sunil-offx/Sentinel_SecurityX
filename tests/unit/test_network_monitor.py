"""Unit tests for Phase 3 Outbound Connection Inspection and Network Telemetry."""

from app.database.models import RiskLevel
from app.monitoring.network_monitor import NetworkMonitor


def test_public_ip_classification() -> None:
    monitor = NetworkMonitor()
    assert not monitor.is_public_ip("127.0.0.1")
    assert not monitor.is_public_ip("192.168.1.100")
    assert not monitor.is_public_ip("10.0.0.1")
    assert not monitor.is_public_ip("172.16.0.5")
    assert monitor.is_public_ip("8.8.8.8")
    assert monitor.is_public_ip("1.1.1.1")


def test_inspect_benign_connection() -> None:
    monitor = NetworkMonitor()
    conn = monitor.inspect_connection(
        pid=1000,
        proc_name="chrome.exe",
        proto="TCP",
        laddr_str="192.168.1.50:54321",
        raddr_ip="142.250.190.46",
        raddr_port=443,
        status="ESTABLISHED",
    )
    assert not conn.is_suspicious
    assert conn.risk_level == RiskLevel.SAFE.value


def test_detect_suspicious_c2_port() -> None:
    monitor = NetworkMonitor()
    conn = monitor.inspect_connection(
        pid=2000,
        proc_name="unknown.exe",
        proto="TCP",
        laddr_str="192.168.1.50:54322",
        raddr_ip="203.0.113.5",
        raddr_port=4444,  # Metasploit default
        status="ESTABLISHED",
    )
    assert conn.is_suspicious
    assert conn.risk_level == RiskLevel.CRITICAL.value
    assert any("Metasploit" in r for r in conn.reasons)


def test_detect_non_network_process_outbound() -> None:
    monitor = NetworkMonitor()
    conn = monitor.inspect_connection(
        pid=3000,
        proc_name="cmd.exe",
        proto="TCP",
        laddr_str="192.168.1.50:54323",
        raddr_ip="198.51.100.99",
        raddr_port=8080,
        status="SYN_SENT",
    )
    assert conn.is_suspicious
    assert conn.risk_level == RiskLevel.HIGH.value
    assert any("Suspicious Outbound Process" in r for r in conn.reasons)


def test_get_active_connections() -> None:
    monitor = NetworkMonitor()
    conns = monitor.get_active_connections()
    assert isinstance(conns, list)

