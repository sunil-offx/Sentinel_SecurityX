"""Windows Event Log telemetry ingestion for process creation, PowerShell script blocks, and security auditing."""

import json
import logging
import re
import subprocess  # nosec B404
import threading
import time
from collections.abc import Callable
from datetime import datetime

from app.config.settings import settings
from app.database.database import db
from app.database.models import EventLogRecord, RiskLevel

logger = logging.getLogger(__name__)

# Patterns indicative of malicious PowerShell script blocks (Event ID 4104)
SUSPICIOUS_SCRIPT_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"invoke-expression|iex\b", re.IGNORECASE), "Dynamic code execution (Invoke-Expression / IEX)"),
    (re.compile(r"downloadstring|downloaddata|downloadfile", re.IGNORECASE), "WebClient remote download cradle"),
    (re.compile(r"\[system\.reflection\.assembly\]::load", re.IGNORECASE), "In-memory assembly reflection execution"),
    (re.compile(r"bypass\s+-nop|bypass\s+-windowstyle\s+hidden", re.IGNORECASE), "Execution policy bypass with hidden window"),
    (re.compile(r"frombase64string", re.IGNORECASE), "Base64 payload decoding cradle"),
    (re.compile(r"invoke-mimikatz|sekurlsa|dumpls", re.IGNORECASE), "Credential dumping utility invocation"),
]


class EventLogMonitor:
    """Ingests Windows Event Logs (Process Creation 4688, PowerShell 4104, Service Creation 7045)."""

    def __init__(self, poll_interval: float | None = None) -> None:
        self.poll_interval = poll_interval or settings.event_log_poll_interval_sec
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._callbacks: list[Callable[[EventLogRecord], None]] = []
        self._last_checked_time = datetime.utcnow()
        self._seen_records: set[str] = set()

    @property
    def is_running(self) -> bool:
        return self._running

    def register_callback(self, cb: Callable[[EventLogRecord], None]) -> None:
        """Register callback for event log alerts."""
        with self._lock:
            self._callbacks.append(cb)

    def start(self) -> None:
        """Start background event log ingestion."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._monitor_loop, daemon=True, name="EventLogMonitorThread"
        )
        self._thread.start()
        logger.info("EventLogMonitor started.")

    def stop(self) -> None:
        """Stop background event log ingestion."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3.0)
        logger.info("EventLogMonitor stopped.")

    def _monitor_loop(self) -> None:
        """Periodic background ingestion loop."""
        while self._running:
            try:
                events = self.fetch_recent_events(max_events=20)
                for ev in events:
                    self._record_event(ev)
            except Exception as e:
                logger.error(f"Error in EventLogMonitor loop: {e}")
            time.sleep(self.poll_interval)

    def _record_event(self, ev: EventLogRecord) -> None:
        """Save event to database and notify subscribers."""
        ev_key = f"{ev.event_id}:{ev.channel}:{ev.event_time}:{ev.message[:50]}"
        with self._lock:
            if ev_key in self._seen_records:
                return
            self._seen_records.add(ev_key)

        try:
            db.add_event_log_record(ev)
        except Exception as e:
            logger.error(f"Failed to record event log to database: {e}")

        for cb in self._callbacks:
            try:
                cb(ev)
            except Exception as e:
                logger.error(f"Error invoking event log callback: {e}")

    def parse_event(
        self,
        event_id: int,
        channel: str,
        provider: str,
        message: str,
        event_time: str,
    ) -> EventLogRecord:
        """Parse raw event fields and assess threat severity."""
        severity = RiskLevel.LOW.value
        msg_clean = message.strip()

        if event_id == 4104:
            # Script Block Logging
            matched_indicators: list[str] = []
            for pattern, desc in SUSPICIOUS_SCRIPT_PATTERNS:
                if pattern.search(msg_clean):
                    matched_indicators.append(desc)

            if matched_indicators:
                severity = RiskLevel.HIGH.value
                msg_clean = f"Suspicious Script Block: {'; '.join(matched_indicators)} | Snippet: {msg_clean[:200]}"
            else:
                msg_clean = f"PowerShell Script Block executed | Snippet: {msg_clean[:200]}"

        elif event_id == 4688:
            # Process Creation
            if any(term in msg_clean.lower() for term in ("powershell.exe -enc", "cmd.exe /c start /min", "certutil -urlcache")):
                severity = RiskLevel.HIGH.value
            else:
                severity = RiskLevel.LOW.value

        elif event_id == 7045:
            # New Service Created
            severity = RiskLevel.HIGH.value
            msg_clean = f"Persistence Alert: New Windows Service Installed ({msg_clean[:200]})"

        elif event_id == 4625:
            # Failed Logon
            severity = RiskLevel.LOW.value
            msg_clean = f"Audit Alert: Account Logon Failure ({msg_clean[:150]})"

        return EventLogRecord(
            event_id=event_id,
            channel=channel,
            provider=provider,
            severity=severity,
            message=msg_clean,
            event_time=event_time,
            detected_at=datetime.utcnow().isoformat(),
        )

    def fetch_recent_events(self, max_events: int = 15) -> list[EventLogRecord]:
        """Fetch recent Windows Event Logs using PowerShell Get-WinEvent."""
        results: list[EventLogRecord] = []

        # PowerShell script querying Security, System, and PowerShell operational channels
        ps_script = f"""
        $events = @()
        $channels = @('Microsoft-Windows-PowerShell/Operational', 'System')
        foreach ($ch in $channels) {{
            try {{
                $evs = Get-WinEvent -LogName $ch -MaxEvents {max_events} -ErrorAction SilentlyContinue |
                    Select-Object Id, LogName, ProviderName, Message, TimeCreated
                if ($evs) {{ $events += $evs }}
            }} catch {{}}
        }}
        $events | ForEach-Object {{
            [PSCustomObject]@{{
                Id = $_.Id
                LogName = $_.LogName
                ProviderName = $_.ProviderName
                Message = $_.Message
                TimeCreated = $_.TimeCreated.ToString('o')
            }}
        }} | ConvertTo-Json -Compress
        """

        try:
            cmd = ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script]
            output = subprocess.run(  # nosec B603
                cmd,

                capture_output=True,
                text=True,
                timeout=8.0,
            )

            if output.returncode != 0 or not output.stdout.strip():
                return results

            raw_text = output.stdout.strip()
            data = json.loads(raw_text)

            # Convert single object to list if only one event was returned
            items = data if isinstance(data, list) else [data]

            for item in items:
                try:
                    eid = int(item.get("Id", 0))
                    ch = str(item.get("LogName", ""))
                    provider = str(item.get("ProviderName", ""))
                    msg = str(item.get("Message", ""))
                    t_str = str(item.get("TimeCreated", ""))

                    record = self.parse_event(
                        event_id=eid,
                        channel=ch,
                        provider=provider,
                        message=msg,
                        event_time=t_str,
                    )
                    results.append(record)
                except Exception as e:
                    logger.debug(f"Error parsing event log item: {e}")

        except subprocess.TimeoutExpired:
            logger.warning("PowerShell Get-WinEvent query timed out.")
        except Exception as e:
            logger.debug(f"EventLog query exception: {e}")

        return results


# Global singleton instance
event_log_monitor = EventLogMonitor()
