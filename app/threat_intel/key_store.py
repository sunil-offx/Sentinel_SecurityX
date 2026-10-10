"""Secure API key storage for Threat Intelligence providers."""

import base64
import json
import logging
from pathlib import Path

from app.config.settings import settings

logger = logging.getLogger(__name__)


class KeyStore:
    """Manages encrypted/obfuscated credential storage for VirusTotal and AbuseIPDB."""

    def __init__(self, storage_path: Path | None = None) -> None:
        self.storage_path = storage_path or settings.threat_intel_credentials_path
        self._mask = b"SentinelX-Secured-Credential-Vault-2026"

    def _obfuscate(self, text: str) -> str:
        """Obfuscate plain text credential."""
        raw = text.encode("utf-8")
        masked = bytes(b ^ self._mask[i % len(self._mask)] for i, b in enumerate(raw))
        return base64.b64encode(masked).decode("ascii")

    def _deobfuscate(self, token: str) -> str:
        """Deobfuscate credential token."""
        try:
            masked = base64.b64decode(token.encode("ascii"))
            raw = bytes(b ^ self._mask[i % len(self._mask)] for i, b in enumerate(masked))
            return raw.decode("utf-8")
        except Exception:
            return ""

    def _load_data(self) -> dict[str, str]:
        """Read credentials dictionary from file."""
        if not self.storage_path.is_file():
            return {}
        try:
            content = self.storage_path.read_text(encoding="utf-8")
            return json.loads(content)
        except Exception as e:
            logger.warning(f"Could not read credential storage: {e}")
            return {}

    def _save_data(self, data: dict[str, str]) -> None:
        """Save credentials dictionary to file."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            self.storage_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to write credential storage: {e}")

    def get_api_key(self, service: str) -> str | None:
        """Retrieve deobfuscated API key for a service (e.g. 'virustotal', 'abuseipdb')."""
        data = self._load_data()
        token = data.get(service.lower())
        if not token:
            return None
        key = self._deobfuscate(token)
        return key if key else None

    def set_api_key(self, service: str, api_key: str) -> None:
        """Securely store an API key for a service."""
        data = self._load_data()
        clean_key = api_key.strip()
        if not clean_key:
            data.pop(service.lower(), None)
        else:
            data[service.lower()] = self._obfuscate(clean_key)
        self._save_data(data)

    def remove_api_key(self, service: str) -> None:
        """Remove API key for a service."""
        data = self._load_data()
        if service.lower() in data:
            del data[service.lower()]
            self._save_data(data)

    def has_api_key(self, service: str) -> bool:
        """Check if an API key exists for a service."""
        return self.get_api_key(service) is not None


# Global singleton instance
key_store = KeyStore()
