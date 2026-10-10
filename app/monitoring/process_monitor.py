"""Real-time process monitor tracking process hierarchies, LOLBins, and anomalous behaviors."""

import logging
import os
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime

import psutil

from app.config.settings import settings
from app.database.database import db
from app.database.models import ProcessAlertRecord, RiskLevel

logger = logging.getLogger(__name__)

# Living Off the Land Binaries (LOLBins) & Shells
SHELL_EXECUTABLES = {
    "cmd.exe",
    "powershell.exe",
    "pwsh.exe",
    "wscript.exe",
    "cscript.exe",
    "mshta.exe",
    "certutil.exe",
    "regsvr32.exe",
    "rundll32.exe",
    "bitsadmin.exe",
    "curl.exe",
    "vssadmin.exe",
}

# Office, Document Readers & Web Browsers prone to weaponization
SUSPICIOUS_PARENTS = {
    "winword.exe",
    "excel.exe",
    "powerpnt.exe",
    "outlook.exe",
    "acrord32.exe",
    "acrobat.exe",
    "foxitreader.exe",
    "chrome.exe",
    "msedge.exe",
    "firefox.exe",
    "brave.exe",
}

# Critical Windows binaries expected to run strictly from System32
SYSTEM32_SYSTEM_BINARIES = {
    "svchost.exe",
    "csrss.exe",
    "lsass.exe",
    "services.exe",
    "smss.exe",
    "winlogon.exe",
    "wininit.exe",
}


@dataclass
class ProcessInfo:
    """Snapshot data of an active operating system process."""

    pid: int
    name: str
    ppid: int = 0
    parent_name: str = ""
    exe_path: str = ""
    cmdline: str = ""
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    username: str = ""
    create_time: float = 0.0
    status: str = "running"
    is_suspicious: bool = False
    risk_level: str = RiskLevel.SAFE.value
    reasons: list[str] = field(default_factory=list)


class ProcessMonitor:
    """Monitors live Windows processes and flags malicious hierarchies and LOLBin abuse."""

    def __init__(self, poll_interval: float | None = None) -> None:
        self.poll_interval = poll_interval or settings.process_poll_interval_sec
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._callbacks: list[Callable[[ProcessAlertRecord], None]] = []
        self._seen_alert_keys: set[str] = set()

    @property
    def is_running(self) -> bool:
        return self._running

    def register_callback(self, cb: Callable[[ProcessAlertRecord], None]) -> None:
        """Register a callback invoked when a suspicious process is detected."""
        with self._lock:
            self._callbacks.append(cb)

    def start(self) -> None:
        """Start the background monitoring thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True, name="ProcessMonitorThread")
        self._thread.start()
        logger.info("ProcessMonitor started.")

    def stop(self) -> None:
        """Stop the background monitoring thread."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3.0)
        logger.info("ProcessMonitor stopped.")

    def _monitor_loop(self) -> None:
        """Periodic background inspection loop."""
        while self._running:
            try:
                processes = self.get_process_snapshot()
                for proc in processes:
                    if proc.is_suspicious:
                        self._process_suspicious_event(proc)
            except Exception as e:
                logger.error(f"Error in ProcessMonitor loop: {e}")
            time.sleep(self.poll_interval)

    def _process_suspicious_event(self, proc: ProcessInfo) -> None:
        """Handle a detected suspicious process."""
        alert_key = f"{proc.pid}:{proc.name}:{proc.create_time}"
        with self._lock:
            if alert_key in self._seen_alert_keys:
                return
            self._seen_alert_keys.add(alert_key)

        reason_str = "; ".join(proc.reasons)
        record = ProcessAlertRecord(
            pid=proc.pid,
            process_name=proc.name,
            ppid=proc.ppid,
            parent_name=proc.parent_name,
            command_line=proc.cmdline,
            severity=proc.risk_level,
            reason=reason_str,
            detected_at=datetime.utcnow().isoformat(),
            status="ACTIVE",
        )

        try:
            db.add_process_alert(record)
        except Exception as e:
            logger.error(f"Failed to record process alert to database: {e}")

        # Notify callbacks
        for cb in self._callbacks:
            try:
                cb(record)
            except Exception as e:
                logger.error(f"Error invoking process alert callback: {e}")

    def inspect_process(self, proc_dict: dict) -> ProcessInfo:
        """Inspect a single process dictionary and evaluate behavioral rules."""
        pid = proc_dict.get("pid", 0)
        name = (proc_dict.get("name") or "").lower()
        ppid = proc_dict.get("ppid", 0)
        exe = proc_dict.get("exe") or ""
        cmdline_list = proc_dict.get("cmdline") or []
        cmdline = " ".join(cmdline_list) if isinstance(cmdline_list, list) else str(cmdline_list)
        cmdline_lower = cmdline.lower()

        mem_info = proc_dict.get("memory_info")
        memory_mb = (mem_info.rss / (1024 * 1024)) if mem_info else 0.0
        cpu_percent = proc_dict.get("cpu_percent") or 0.0
        username = proc_dict.get("username") or ""
        create_time = proc_dict.get("create_time") or 0.0
        status = proc_dict.get("status") or "running"

        # Resolve parent process name defensively
        parent_name = ""
        if ppid > 0:
            try:
                parent_proc = psutil.Process(ppid)
                parent_name = parent_proc.name().lower()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        reasons: list[str] = []
        risk_level = RiskLevel.SAFE.value

        # --- Rule 1: Suspicious Parent-Child Process Spawning ---
        if parent_name in SUSPICIOUS_PARENTS and name in SHELL_EXECUTABLES:
            reasons.append(
                f"Suspicious Process Spawn: Document/Browser '{parent_name}' spawned shell/LOLBin '{name}'"
            )
            risk_level = RiskLevel.CRITICAL.value

        # --- Rule 2: Living Off The Land Binaries (LOLBins) Abuse ---
        if name in ("powershell.exe", "pwsh.exe"):
            ps_cradles = [
                ("-enc" in cmdline_lower or "-encodedcommand" in cmdline_lower, "Encoded PowerShell payload (-enc)"),
                ("-w hidden" in cmdline_lower or "-windowstyle hidden" in cmdline_lower, "Hidden PowerShell window execution"),
                ("downloadstring" in cmdline_lower, "WebClient.DownloadString execution cradle"),
                ("invoke-expression" in cmdline_lower or "iex(" in cmdline_lower or "iex " in cmdline_lower, "Invoke-Expression dynamic code execution"),
                ("bypass" in cmdline_lower and "-executionpolicy" in cmdline_lower, "ExecutionPolicy bypass"),
            ]
            for triggered, msg in ps_cradles:
                if triggered:
                    reasons.append(f"PowerShell Abuse: {msg}")
                    risk_level = RiskLevel.HIGH.value

        if name == "certutil.exe":
            if any(arg in cmdline_lower for arg in ("-urlcache", "-split", "-decode", "-f")):
                reasons.append("CertUtil Ingress Tool: Attempted remote download or binary decode (-urlcache/-decode)")
                risk_level = RiskLevel.HIGH.value

        if name == "mshta.exe":
            if any(proto in cmdline_lower for proto in ("http:", "https:", "javascript:", "vbscript:")):
                reasons.append("MSHTA Remote Scriptlet Execution (Living Off The Land)")
                risk_level = RiskLevel.HIGH.value

        if name == "regsvr32.exe":
            if "/i:http" in cmdline_lower or "/i:https" in cmdline_lower or "/s" in cmdline_lower:
                reasons.append("Regsvr32 Squiblydoo Scriptlet execution")
                risk_level = RiskLevel.HIGH.value

        if name == "bitsadmin.exe":
            if any(arg in cmdline_lower for arg in ("/transfer", "/download", "/addfile")):
                reasons.append("Bitsadmin Outbound Transfer Tool abuse")
                risk_level = RiskLevel.HIGH.value

        if name == "vssadmin.exe":
            if "delete shadows" in cmdline_lower:
                reasons.append("Ransomware Indicator: vssadmin delete shadows invoked")
                risk_level = RiskLevel.CRITICAL.value

        # --- Rule 3: Process Masquerading & Non-System Path Anomalies ---
        if exe:
            exe_norm = os.path.normpath(exe).lower()
            system32_path = os.path.normpath(os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32")).lower()
            windows_path = os.path.normpath(os.environ.get("SystemRoot", "C:\\Windows")).lower()

            if name in SYSTEM32_SYSTEM_BINARIES:
                if not exe_norm.startswith(system32_path):
                    reasons.append(
                        f"Masquerading Binary: '{name}' running from abnormal path '{exe}' (Expected System32)"
                    )
                    risk_level = RiskLevel.CRITICAL.value

            if name == "explorer.exe":
                if not (exe_norm == os.path.join(windows_path, "explorer.exe").lower() or exe_norm.startswith(windows_path)):
                    reasons.append(
                        f"Masquerading Explorer: 'explorer.exe' running from abnormal location '{exe}'"
                    )
                    risk_level = RiskLevel.HIGH.value

        is_suspicious = len(reasons) > 0
        if is_suspicious and risk_level == RiskLevel.SAFE.value:
            risk_level = RiskLevel.LOW.value

        return ProcessInfo(
            pid=pid,
            name=proc_dict.get("name") or "",
            ppid=ppid,
            parent_name=parent_name,
            exe_path=exe,
            cmdline=cmdline,
            cpu_percent=cpu_percent,
            memory_mb=round(memory_mb, 2),
            username=username,
            create_time=create_time,
            status=status,
            is_suspicious=is_suspicious,
            risk_level=risk_level,
            reasons=reasons,
        )

    def get_process_snapshot(self) -> list[ProcessInfo]:
        """Collect current system processes and evaluate threat heuristics."""
        results: list[ProcessInfo] = []
        attrs = ["pid", "name", "ppid", "exe", "cmdline", "memory_info", "cpu_percent", "username", "create_time", "status"]

        for proc in psutil.process_iter(attrs=attrs):
            try:
                proc_info = proc.info
                results.append(self.inspect_process(proc_info))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                logger.debug(f"Error inspecting process: {e}")

        return results

    def terminate_process(self, pid: int) -> tuple[bool, str]:
        """Safely terminate a targeted process by PID."""
        try:
            if pid <= 4:
                return False, "Cannot terminate critical system process (PID <= 4)."

            target = psutil.Process(pid)
            proc_name = target.name()

            # Defensive safety check: do not terminate SentinelX itself
            current_pid = os.getpid()
            if pid == current_pid:
                return False, "Cannot terminate SentinelX itself."

            target.terminate()
            gone, alive = psutil.wait_procs([target], timeout=3.0)
            if alive:
                target.kill()

            # Mark status in database
            db.update_process_alert_status(pid, "TERMINATED")
            return True, f"Process '{proc_name}' (PID: {pid}) successfully terminated."
        except psutil.NoSuchProcess:
            return False, f"Process PID {pid} no longer exists."
        except psutil.AccessDenied:
            return False, f"Access denied terminating PID {pid}. (Requires administrator privileges)."
        except Exception as e:
            return False, f"Failed to terminate process PID {pid}: {e}"


# Global singleton instance
process_monitor = ProcessMonitor()
