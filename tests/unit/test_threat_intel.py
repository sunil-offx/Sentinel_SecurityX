"""Unit tests for Phase 3 Threat Intelligence and Secure Key Store."""

from pathlib import Path

from app.threat_intel.key_store import KeyStore
from app.threat_intel.threat_client import ThreatIntelClient, ThreatReport


def test_key_store_operations(tmp_path: Path) -> None:
    vault_file = tmp_path / "creds.json"
    store = KeyStore(storage_path=vault_file)

    assert not store.has_api_key("virustotal")

    test_key = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    store.set_api_key("virustotal", test_key)

    assert store.has_api_key("virustotal")
    assert store.get_api_key("virustotal") == test_key

    # Ensure obfuscation on disk
    raw_disk = vault_file.read_text()
    assert test_key not in raw_disk

    # Remove
    store.remove_api_key("virustotal")
    assert not store.has_api_key("virustotal")
    assert store.get_api_key("virustotal") is None


def test_threat_client_no_api_key() -> None:
    client = ThreatIntelClient()
    report = client.lookup_file_hash("275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f")

    # When no key is set or cached, it gracefully returns NO_API_KEY without exceptions
    assert report.status in ("NO_API_KEY", "SUCCESS")
    assert report.indicator_type == "SHA256"


def test_threat_report_caching(tmp_path: Path) -> None:
    client = ThreatIntelClient()
    test_hash = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

    report = ThreatReport(
        indicator=test_hash,
        indicator_type="SHA256",
        status="SUCCESS",
        score=85,
        malicious_count=42,
        total_engines=70,
        threat_label="Trojan.Generic",
        details={"reputation": -50},
    )

    client._save_to_cache(report)
    cached = client._get_cached_report(test_hash)

    assert cached is not None
    assert cached.indicator == test_hash
    assert cached.score == 85
    assert cached.malicious_count == 42
    assert cached.is_cached
