"""Threat Intelligence client for VirusTotal and AbuseIPDB with caching and offline resilience."""

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from app.config.settings import settings
from app.database.database import db
from app.database.models import ThreatIntelRecord
from app.threat_intel.key_store import key_store

logger = logging.getLogger(__name__)


@dataclass
class ThreatReport:
    """Consolidated threat intelligence report for a hash or IP."""

    indicator: str
    indicator_type: str  # "SHA256" or "IP"
    status: str = "SUCCESS"  # SUCCESS, NOT_FOUND, NO_API_KEY, OFFLINE, ERROR
    score: int = 0  # 0 to 100
    malicious_count: int = 0
    suspicious_count: int = 0
    harmless_count: int = 0
    total_engines: int = 0
    threat_label: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    is_cached: bool = False
    message: str = ""


class ThreatIntelClient:
    """Client for external threat intelligence providers."""

    def __init__(self) -> None:
        self.vt_base_url = "https://www.virustotal.com/api/v3"
        self.abuseipdb_base_url = "https://api.abuseipdb.com/api/v2"

    def _get_cached_report(self, indicator: str) -> ThreatReport | None:
        """Retrieve valid cached threat intel report from database."""
        try:
            record = db.get_threat_intel_cache(indicator)
            if not record:
                return None

            cached_time = datetime.fromisoformat(record.cached_at)
            ttl = timedelta(hours=settings.threat_intel_cache_ttl_hours)
            if datetime.utcnow() - cached_time > ttl:
                return None  # Cache expired

            details = json.loads(record.details_json) if record.details_json else {}
            return ThreatReport(
                indicator=record.indicator_value,
                indicator_type=record.indicator_type,
                status="SUCCESS",
                score=record.score,
                malicious_count=record.malicious_count,
                suspicious_count=details.get("suspicious_count", 0),
                harmless_count=details.get("harmless_count", 0),
                total_engines=record.total_count,
                threat_label=details.get("threat_label", ""),
                details=details,
                is_cached=True,
                message=f"Retrieved from local cache (cached at {record.cached_at})",
            )
        except Exception as e:
            logger.debug(f"Cache lookup failed for {indicator}: {e}")
            return None

    def _save_to_cache(self, report: ThreatReport) -> None:
        """Save a successful threat report to local SQLite cache."""
        try:
            record = ThreatIntelRecord(
                indicator_type=report.indicator_type,
                indicator_value=report.indicator,
                score=report.score,
                malicious_count=report.malicious_count,
                total_count=report.total_engines,
                details_json=json.dumps(report.details),
                cached_at=datetime.utcnow().isoformat(),
            )
            db.set_threat_intel_cache(record)
        except Exception as e:
            logger.error(f"Failed to cache threat intel result: {e}")

    def lookup_file_hash(self, sha256: str) -> ThreatReport:
        """Query VirusTotal v3 for a file hash (SHA-256)."""
        clean_hash = sha256.strip().lower()

        # 1. Check local cache first
        cached = self._get_cached_report(clean_hash)
        if cached:
            return cached

        # 2. Check API key
        api_key = key_store.get_api_key("virustotal")
        if not api_key:
            return ThreatReport(
                indicator=clean_hash,
                indicator_type="SHA256",
                status="NO_API_KEY",
                message="VirusTotal API key not configured. Enter an API key in Settings to enable cloud reputation checks.",
            )

        url = f"{self.vt_base_url}/files/{clean_hash}"
        req = urllib.request.Request(
            url,
            headers={
                "x-apikey": api_key,
                "Accept": "application/json",
                "User-Agent": "SentinelX/0.1.0",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=10.0) as resp:  # nosec B310
                data = json.loads(resp.read().decode("utf-8"))

            attributes = data.get("data", {}).get("attributes", {})
            stats = attributes.get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            harmless = stats.get("harmless", 0)
            undetected = stats.get("undetected", 0)
            total = malicious + suspicious + harmless + undetected

            threat_class = attributes.get("popular_threat_classification", {})
            threat_label = threat_class.get("suggested_threat_label", "")

            # Calculate composite threat score (0 to 100)
            score = 0
            if total > 0:
                score = min(100, int((malicious * 100 + suspicious * 50) / total))

            report = ThreatReport(
                indicator=clean_hash,
                indicator_type="SHA256",
                status="SUCCESS",
                score=score,
                malicious_count=malicious,
                suspicious_count=suspicious,
                harmless_count=harmless,
                total_engines=total,
                threat_label=threat_label,
                details={
                    "meaningful_name": attributes.get("meaningful_name", ""),
                    "reputation": attributes.get("reputation", 0),
                    "type_description": attributes.get("type_description", ""),
                    "suspicious_count": suspicious,
                    "harmless_count": harmless,
                    "threat_label": threat_label,
                },
                is_cached=False,
                message=f"{malicious}/{total} security vendors flagged this file as malicious.",
            )
            self._save_to_cache(report)
            return report

        except urllib.error.HTTPError as e:
            if e.code == 404:
                report = ThreatReport(
                    indicator=clean_hash,
                    indicator_type="SHA256",
                    status="NOT_FOUND",
                    message="Hash not found in VirusTotal database (unseen sample).",
                )
                return report
            elif e.code == 401 or e.code == 403:
                return ThreatReport(
                    indicator=clean_hash,
                    indicator_type="SHA256",
                    status="ERROR",
                    message="Invalid VirusTotal API key or quota exceeded.",
                )
            else:
                return ThreatReport(
                    indicator=clean_hash,
                    indicator_type="SHA256",
                    status="ERROR",
                    message=f"VirusTotal API HTTP error: {e.code}",
                )
        except urllib.error.URLError as e:
            return ThreatReport(
                indicator=clean_hash,
                indicator_type="SHA256",
                status="OFFLINE",
                message=f"Network unreachable: {e.reason}. Operating in local offline mode.",
            )
        except Exception as e:
            return ThreatReport(
                indicator=clean_hash,
                indicator_type="SHA256",
                status="ERROR",
                message=f"Unexpected error: {e}",
            )

    def lookup_ip_address(self, ip_address: str) -> ThreatReport:
        """Query AbuseIPDB or VirusTotal for IP reputation."""
        clean_ip = ip_address.strip()

        # 1. Check local cache
        cached = self._get_cached_report(clean_ip)
        if cached:
            return cached

        # Check AbuseIPDB key first, fallback to VirusTotal
        abuse_key = key_store.get_api_key("abuseipdb")
        if abuse_key:
            return self._lookup_abuseipdb(clean_ip, abuse_key)

        vt_key = key_store.get_api_key("virustotal")
        if vt_key:
            return self._lookup_virustotal_ip(clean_ip, vt_key)

        return ThreatReport(
            indicator=clean_ip,
            indicator_type="IP",
            status="NO_API_KEY",
            message="No API key configured for AbuseIPDB or VirusTotal. Enter keys in Settings.",
        )

    def _lookup_abuseipdb(self, ip: str, api_key: str) -> ThreatReport:
        """Query AbuseIPDB API v2."""
        url = f"{self.abuseipdb_base_url}/check?ipAddress={ip}&maxAgeInDays=90"
        req = urllib.request.Request(
            url,
            headers={
                "Key": api_key,
                "Accept": "application/json",
                "User-Agent": "SentinelX/0.1.0",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=10.0) as resp:  # nosec B310
                data = json.loads(resp.read().decode("utf-8")).get("data", {})

            abuse_score = data.get("abuseConfidenceScore", 0)
            total_reports = data.get("totalReports", 0)
            country = data.get("countryCode", "")
            isp = data.get("isp", "")

            report = ThreatReport(
                indicator=ip,
                indicator_type="IP",
                status="SUCCESS",
                score=abuse_score,
                malicious_count=total_reports,
                total_engines=100,
                threat_label=f"ISP: {isp} ({country})" if isp else "",
                details={
                    "country": country,
                    "isp": isp,
                    "domain": data.get("domain", ""),
                    "is_whitelisted": data.get("isWhitelisted", False),
                },
                is_cached=False,
                message=f"Abuse Confidence Score: {abuse_score}% ({total_reports} abuse reports).",
            )
            self._save_to_cache(report)
            return report
        except Exception as e:
            logger.warning(f"AbuseIPDB query error: {e}")
            return ThreatReport(
                indicator=ip,
                indicator_type="IP",
                status="ERROR",
                message=f"AbuseIPDB lookup failed: {e}",
            )

    def _lookup_virustotal_ip(self, ip: str, api_key: str) -> ThreatReport:
        """Query VirusTotal v3 for IP address reputation."""
        url = f"{self.vt_base_url}/ip_addresses/{ip}"
        req = urllib.request.Request(
            url,
            headers={
                "x-apikey": api_key,
                "Accept": "application/json",
                "User-Agent": "SentinelX/0.1.0",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=10.0) as resp:  # nosec B310
                data = json.loads(resp.read().decode("utf-8"))

            attributes = data.get("data", {}).get("attributes", {})
            stats = attributes.get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            harmless = stats.get("harmless", 0)
            undetected = stats.get("undetected", 0)
            total = malicious + suspicious + harmless + undetected

            score = 0
            if total > 0:
                score = min(100, int((malicious * 100 + suspicious * 50) / total))

            report = ThreatReport(
                indicator=ip,
                indicator_type="IP",
                status="SUCCESS",
                score=score,
                malicious_count=malicious,
                suspicious_count=suspicious,
                harmless_count=harmless,
                total_engines=total,
                threat_label=attributes.get("as_owner", ""),
                details={
                    "country": attributes.get("country", ""),
                    "as_owner": attributes.get("as_owner", ""),
                },
                is_cached=False,
                message=f"{malicious}/{total} security vendors flagged this IP address.",
            )
            self._save_to_cache(report)
            return report
        except Exception as e:
            return ThreatReport(
                indicator=ip,
                indicator_type="IP",
                status="ERROR",
                message=f"VirusTotal IP lookup failed: {e}",
            )


# Global singleton instance
threat_client = ThreatIntelClient()
