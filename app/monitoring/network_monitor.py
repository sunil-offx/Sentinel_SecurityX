"""Outbound connection inspection and network telemetry monitoring."""

import ipaddress
import logging
import socket
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime

import psutil

from app.config.settings import settings
from app.database.database import db
from app.database.models import NetworkAlertRecord, RiskLevel

logger = logging.getLogger(__name__)

# Known Command & Control (C2), RAT, and proxy ports
SUSPICIOUS_C2_PORTS: dict[int, str] = {
    4444: "Metasploit Default Listener",
    50050: "Cobalt Strike TeamServer Default",
    1337: "Elite Backdoor / RAT Port",
    31337: "Back Orifice Trojan Port",
    9001: "Tor Relay Port",
    9050: "Tor SOCKS Proxy Port",
    6667: "IRC Botnet Standard Port",
    6697: "IRC SSL Botnet Port",
    8000: "Common Non-Standard C2 Port",
}

# Processes that should not ordinarily initiate external internet connections
NON_NETWORK_PROCESSES: set[str] = {
    "cmd.exe",
    "powershell.exe",
    "pwsh.exe",
    "certutil.exe",
    "rundll32.exe",
    "regsvr32.exe",
    "wscript.exe",
    "cscript.exe",
    "notepad.exe",
    "calc.exe",
    "calculator.exe",
    "taskhostw.exe",
}


@dataclass
class NetworkConnectionInfo:
    """Telemetry data for an active system network socket."""

    pid: int
    process_name: str
    protocol: str
    local_address: str
    remote_address: str
    remote_port: int
    status: str
    is_public_ip: bool = False
    is_suspicious: bool = False
    risk_level: str = RiskLevel.SAFE.value
    reasons: list[str] = field(default_factory=list)


class NetworkMonitor:
    """Inspects active network sockets and flags C2 beacons and abnormal outbound connections."""

    def __init__(self, poll_interval: float | None = None) -> None:
        self.poll_interval = poll_interval or settings.network_poll_interval_sec
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._callbacks: list[Callable[[NetworkAlertRecord], None]] = []
        self._seen_alert_keys: set[str] = set()

    @property
    def is_running(self) -> bool:
        return self._running

    def register_callback(self, cb: Callable[[NetworkAlertRecord], None]) -> None:
        """Register callback for network alerts."""
        with self._lock:
            self._callbacks.append(cb)

    def start(self) -> None:
        """Start background network monitoring thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._monitor_loop, daemon=True, name="NetworkMonitorThread"
        )
        self._thread.start()
        logger.info("NetworkMonitor started.")

    def stop(self) -> None:
        """Stop background network monitoring."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3.0)
        logger.info("NetworkMonitor stopped.")

    def _monitor_loop(self) -> None:
        """Periodic background network inspection."""
        while self._running:
            try:
                conns = self.get_active_connections()
                for conn in conns:
                    if conn.is_suspicious:
                        self._handle_suspicious_conn(conn)
            except Exception as e:
                logger.error(f"Error in NetworkMonitor loop: {e}")
            time.sleep(self.poll_interval)

    def _handle_suspicious_conn(self, conn: NetworkConnectionInfo) -> None:
        """Record and dispatch detected network anomaly."""
        alert_key = f"{conn.pid}:{conn.process_name}:{conn.remote_address}:{conn.remote_port}"
        with self._lock:
            if alert_key in self._seen_alert_keys:
                return
            self._seen_alert_keys.add(alert_key)

        reason_str = "; ".join(conn.reasons)
        record = NetworkAlertRecord(
            pid=conn.pid,
            process_name=conn.process_name,
            local_addr=conn.local_address,
            remote_addr=conn.remote_address,
            remote_port=conn.remote_port,
            protocol=conn.protocol,
            severity=conn.risk_level,
            reason=reason_str,
            detected_at=datetime.utcnow().isoformat(),
        )

        try:
            db.add_network_alert(record)
        except Exception as e:
            logger.error(f"Failed to record network alert to database: {e}")

        for cb in self._callbacks:
            try:
                cb(record)
            except Exception as e:
                logger.error(f"Error invoking network alert callback: {e}")

    def is_public_ip(self, ip_str: str) -> bool:
        """Check if an IP address is a public routable WAN address."""
        if not ip_str or ip_str in ("127.0.0.1", "0.0.0.0", "::1", "localhost"):  # nosec B104
            return False

        try:
            ip = ipaddress.ip_address(ip_str)
            return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast)
        except ValueError:
            return False

    def inspect_connection(
        self,
        pid: int,
        proc_name: str,
        proto: str,
        laddr_str: str,
        raddr_ip: str,
        raddr_port: int,
        status: str,
    ) -> NetworkConnectionInfo:
        """Evaluate behavioral network rules on a socket connection."""
        proc_name_lower = proc_name.lower()
        reasons: list[str] = []
        risk_level = RiskLevel.SAFE.value
        is_public = self.is_public_ip(raddr_ip)

        # 1. Suspicious C2 / RAT port connection
        if raddr_port in SUSPICIOUS_C2_PORTS:
            desc = SUSPICIOUS_C2_PORTS[raddr_port]
            reasons.append(f"Connection to Suspicious Port {raddr_port} ({desc})")
            risk_level = RiskLevel.CRITICAL.value

        # 2. Non-network process initiating external connection
        if proc_name_lower in NON_NETWORK_PROCESSES and (is_public or raddr_port not in (80, 443)):
            reasons.append(
                f"Suspicious Outbound Process: '{proc_name}' establishing external network connection to {raddr_ip}:{raddr_port}"
            )
            risk_level = RiskLevel.HIGH.value

        # 3. Direct Public IP connection outside of web ports
        if is_public and raddr_port not in (80, 443, 8080, 8443, 53):
            reasons.append(f"Direct Public IP Connection on non-standard port: {raddr_ip}:{raddr_port}")
            if risk_level == RiskLevel.SAFE.value:
                risk_level = RiskLevel.LOW.value

        is_suspicious = len(reasons) > 0

        return NetworkConnectionInfo(
            pid=pid,
            process_name=proc_name,
            protocol=proto,
            local_address=laddr_str,
            remote_address=raddr_ip,
            remote_port=raddr_port,
            status=status,
            is_public_ip=is_public,
            is_suspicious=is_suspicious,
            risk_level=risk_level,
            reasons=reasons,
        )

    def get_active_connections(self) -> list[NetworkConnectionInfo]:
        """Collect current system network connections."""
        results: list[NetworkConnectionInfo] = []

        # Cache pid -> name to avoid repeated lookups
        pid_names: dict[int, str] = {}
        for p in psutil.process_iter(attrs=["pid", "name"]):
            try:
                pid_names[p.info["pid"]] = p.info["name"] or "unknown"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        try:
            connections = psutil.net_connections(kind="inet")
        except (psutil.AccessDenied, PermissionError):
            logger.warning("Access denied reading net_connections. Elevate privileges for full telemetry.")
            return results
        except Exception as e:
            logger.error(f"Error querying net_connections: {e}")
            return results

        for c in connections:
            pid = c.pid or 0
            proc_name = pid_names.get(pid, "System / Unknown" if pid == 0 else f"PID {pid}")
            proto = "TCP" if c.type == socket.SOCK_STREAM else "UDP"

            laddr_str = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else ""
            raddr_ip = c.raddr.ip if c.raddr else ""
            raddr_port = c.raddr.port if c.raddr else 0
            status = c.status or "NONE"

            # Filter out local loopback listening sockets if not suspicious
            if not raddr_ip and status == "LISTEN":
                continue

            conn_info = self.inspect_connection(
                pid=pid,
                proc_name=proc_name,
                proto=proto,
                laddr_str=laddr_str,
                raddr_ip=raddr_ip,
                raddr_port=raddr_port,
                status=status,
            )
            results.append(conn_info)

        return results


# Global singleton instance
network_monitor = NetworkMonitor()
