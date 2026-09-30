"""YARA detection engine for static signature scanning."""

import logging
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yara

    YARA_AVAILABLE = True
except ImportError:
    yara = None
    YARA_AVAILABLE = False

from app.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class YaraMatch:
    """Represents a YARA rule match result."""

    rule_name: str
    severity: str = "HIGH"
    description: str = ""
    tags: list[str] = field(default_factory=list)
    matched_strings: list[str] = field(default_factory=list)


class YaraEngine:
    """YARA compiler and scanner interface."""

    def __init__(self, rules_path: Path | None = None) -> None:
        self.rules_path = rules_path or settings.yara_rules_dir
        self.rules: yara.Rules | None = None
        self.is_loaded = False
        self.load_rules()

    def load_rules(self) -> bool:
        """Load and compile YARA rules from the designated directory or file."""
        if not YARA_AVAILABLE:
            logger.warning("yara-python is not installed. YARA engine is inactive.")
            return False

        try:
            rule_files: dict[str, str] = {}
            if self.rules_path.is_file():
                rule_files[self.rules_path.stem] = str(self.rules_path)
            elif self.rules_path.is_dir():
                for p in self.rules_path.glob("*.yar*"):
                    rule_files[p.stem] = str(p)

            if not rule_files:
                logger.warning(f"No .yar rule files found in {self.rules_path}")
                return False

            self.rules = yara.compile(filepaths=rule_files)
            self.is_loaded = True
            logger.info(f"Loaded {len(rule_files)} YARA rule source files.")
            return True
        except Exception as e:
            logger.error(f"Error compiling YARA rules from {self.rules_path}: {e}")
            self.rules = None
            self.is_loaded = False
            return False

    def scan_file(self, file_path: Path) -> list[YaraMatch]:
        """Scan a file with compiled YARA rules."""
        if not self.is_loaded or not self.rules:
            return []

        resolved_path = Path(file_path).resolve()
        if not resolved_path.is_file():
            return []

        try:
            raw_matches = self.rules.match(str(resolved_path), timeout=10)
            matches: list[YaraMatch] = []
            for match in raw_matches:
                meta = match.meta or {}
                severity = meta.get("severity", "HIGH").upper()
                desc = meta.get("description", f"Rule {match.rule} matched")

                matched_strs: list[str] = []
                for s in match.strings:
                    # In yara-python: string match items can be tuples or StringMatch objects
                    # depending on version: (offset, identifier, data)
                    try:
                        if hasattr(s, "identifier"):
                            matched_strs.append(f"{s.identifier}")
                        elif isinstance(s, (tuple, list)) and len(s) >= 2:
                            matched_strs.append(str(s[1]))
                    except Exception as parse_err:
                        logger.debug(f"Could not parse string match identifier: {parse_err}")

                matches.append(
                    YaraMatch(
                        rule_name=match.rule,
                        severity=severity,
                        description=desc,
                        tags=list(match.tags),
                        matched_strings=matched_strs[:5],  # Top 5 matched tokens
                    )
                )
            return matches
        except Exception as e:
            logger.warning(f"YARA scan error on {file_path}: {e}")
            return []


# Global YARA engine instance
yara_engine = YaraEngine()
