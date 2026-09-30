import logging
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

try:
    import pefile

    PEFILE_AVAILABLE = True
except ImportError:
    pefile = None
    PEFILE_AVAILABLE = False

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Critical Suspicious Windows APIs categorized by behavior
SUSPICIOUS_APIS: dict[str, str] = {
    # Process Injection & Memory Manipulation
    "VirtualAlloc": "Memory Allocation (often used in unpacking or staging code)",
    "VirtualAllocEx": "Remote Process Memory Allocation (Process Injection indicator)",
    "WriteProcessMemory": "Remote Process Memory Write (Process Injection indicator)",
    "CreateRemoteThread": "Remote Thread Creation (Process Injection indicator)",
    "NtCreateThreadEx": "Low-level Remote Thread Creation",
    "QueueUserAPC": "Asynchronous Procedure Call injection",
    "SetThreadContext": "Process Hollowing / Hijacking indicator",
    "ResumeThread": "Process Resumption (often paired with suspended injection)",
    "VirtualProtect": "Memory Permission Modification (enabling RWX code execution)",
    "VirtualProtectEx": "Remote Memory Permission Modification",
    # Evasion & Anti-Analysis
    "IsDebuggerPresent": "Anti-Debugging Check",
    "CheckRemoteDebuggerPresent": "Anti-Debugging Check",
    "SetWindowsHookExA": "System Hooking / Keylogging indicator",
    "SetWindowsHookExW": "System Hooking / Keylogging indicator",
    # Execution & System Tampering
    "WinExec": "Command Execution",
    "ShellExecuteA": "Shell Execution",
    "ShellExecuteW": "Shell Execution",
    "CreateProcessA": "Process Creation",
    "CreateProcessW": "Process Creation",
    "RegSetValueExA": "Registry Modification (Persistence indicator)",
    "RegSetValueExW": "Registry Modification (Persistence indicator)",
    # Network / Downloaders
    "InternetOpenA": "Network Connection Initializer",
    "InternetOpenUrlA": "URL Connection Retrieval",
    "URLDownloadToFileA": "Arbitrary File Download from Network",
    "URLDownloadToFileW": "Arbitrary File Download from Network",
}

# Suspicious keywords in script-based files (.bat, .cmd, .ps1, .vbs, .js)
SUSPICIOUS_SCRIPT_PATTERNS = [
    (r"\b(invoke-expression|iex)\b", "PowerShell Dynamic Code Execution (IEX)"),
    (r"\b(downloadstring|downloadfile)\b", "Remote Web Payload Download"),
    (r"\bnet\.webclient\b", "WebClient Remote Ingestion"),
    (r"-windowstyle\s+hidden\b", "Hidden Window Execution"),
    (r"-enc(odedcommand)?\s+[A-Za-z0-9+/=]{10,}", "Base64 Encoded PowerShell Command"),
    (r"\bcertutil(\.exe)?\s+(-urlcache|-f)\b", "Certutil Living-Off-The-Land Downloader"),
    (r"\bbitsadmin(\.exe)?\s+/transfer\b", "BITSAdmin Downloader Abuse"),
    (
        r"\bvssadmin(\.exe)?\s+delete\s+shadows\b",
        "Volume Shadow Copy Deletion (Ransomware behavior)",
    ),
    (r"\bwscript\.shell\b", "WScript Shell Script Automation"),
    (r"\bpowershell(\.exe)?\s+-[eE][nN][cC]\b", "Obfuscated PowerShell Invocation"),
]


@dataclass
class SectionInfo:
    """PE section metadata."""

    name: str
    virtual_size: int
    raw_size: int
    entropy: float
    is_readable: bool
    is_writable: bool
    is_executable: bool


@dataclass
class StaticAnalysisResult:
    """Consolidated static analysis findings."""

    entropy: float = 0.0
    entropy_level: str = "NORMAL"  # NORMAL, MEDIUM, HIGH
    is_pe: bool = False
    pe_sections: list[SectionInfo] = field(default_factory=list)
    suspicious_sections: list[str] = field(default_factory=list)
    imported_apis: list[str] = field(default_factory=list)
    suspicious_apis: list[str] = field(default_factory=list)
    script_triggers: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


def calculate_entropy(data: bytes) -> float:
    """Calculate Shannon entropy for a sequence of bytes.

    Returns:
        Entropy value between 0.0 (uniform) and 8.0 (completely random / compressed).
    """
    if not data:
        return 0.0

    length = len(data)
    frequencies = Counter(data)
    entropy = 0.0
    for count in frequencies.values():
        p = count / length
        entropy -= p * math.log2(p)
    return round(entropy, 4)


class StaticAnalyzer:
    """Static file inspector evaluating entropy, PE headers, imports, and scripts."""

    def __init__(self) -> None:
        self.entropy_high = settings.entropy_threshold_high
        self.entropy_medium = settings.entropy_threshold_medium

    def analyze(self, file_path: Path) -> StaticAnalysisResult:
        """Perform full static analysis on the target file."""
        resolved = Path(file_path).resolve()
        result = StaticAnalysisResult()

        if not resolved.is_file():
            return result

        file_size = resolved.stat().st_size
        ext = resolved.suffix.lower()

        # Read content (bounded by max_scan_size_bytes to avoid OOM)
        max_bytes = min(file_size, settings.max_scan_size_bytes)
        try:
            with open(resolved, "rb") as f:
                data = f.read(max_bytes)
        except Exception as e:
            result.reasons.append(f"Could not read file for static analysis: {e}")
            return result

        # 1. Entropy calculation
        result.entropy = calculate_entropy(data)
        if result.entropy >= self.entropy_high:
            result.entropy_level = "HIGH"
            result.reasons.append(
                f"High entropy ({result.entropy:.2f}/8.0): Likely packed, encrypted, or obfuscated"
            )
        elif result.entropy >= self.entropy_medium:
            result.entropy_level = "MEDIUM"
            result.reasons.append(f"Elevated entropy ({result.entropy:.2f}/8.0)")
        else:
            result.entropy_level = "NORMAL"

        # 2. Executable / PE Header analysis
        if PEFILE_AVAILABLE and data.startswith(b"MZ"):
            self._analyze_pe(resolved, data, result)

        # 3. Script inspection (.bat, .cmd, .ps1, .vbs, .js, or small text files)
        if ext in {".bat", ".cmd", ".ps1", ".vbs", ".js"}:
            self._analyze_script(data, result)

        # 4. Dangerous Extension Note
        if ext in {".scr", ".vbs", ".ps1", ".bat", ".cmd"}:
            result.reasons.append(
                f"High-risk file extension ({ext}) frequently leveraged in attacks"
            )

        return result

    def _analyze_pe(self, path: Path, data: bytes, result: StaticAnalysisResult) -> None:
        """Inspect PE structures, sections, and import tables."""
        try:
            pe = pefile.PE(data=data, fast_load=True)
            result.is_pe = True
            result.reasons.append("Valid Windows Portable Executable (PE)")

            # Parse directory entries (imports)
            pe.parse_data_directories(
                directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                ]
            )

            # Analyze sections
            for section in pe.sections:
                sec_name = section.Name.decode("latin-1", errors="ignore").strip("\x00")
                sec_entropy = section.get_entropy()
                chars = section.Characteristics
                is_write = bool(chars & 0x80000000)
                is_exec = bool(chars & 0x20000000)
                is_read = bool(chars & 0x40000000)

                sec_info = SectionInfo(
                    name=sec_name,
                    virtual_size=section.Misc_VirtualSize,
                    raw_size=section.SizeOfRawData,
                    entropy=round(sec_entropy, 3),
                    is_readable=is_read,
                    is_writable=is_write,
                    is_executable=is_exec,
                )
                result.pe_sections.append(sec_info)

                # Anomaly: Writable AND Executable section
                if is_write and is_exec:
                    result.suspicious_sections.append(sec_name)
                    result.reasons.append(
                        f"Suspicious section '{sec_name}': Marked both WRITABLE and EXECUTABLE (W^X violation)"
                    )

                # Anomaly: Abnormally high section entropy (packed section)
                if sec_entropy >= 7.2:
                    result.suspicious_sections.append(sec_name)
                    result.reasons.append(
                        f"Suspicious section '{sec_name}': High entropy ({sec_entropy:.2f}/8.0), likely packed"
                    )

                # Anomaly: Known packer section names
                known_packer_prefixes = ("upx", ".vmp", "aspack", ".nsp", ".themida")
                if any(sec_name.lower().startswith(p) for p in known_packer_prefixes):
                    result.suspicious_sections.append(sec_name)
                    result.reasons.append(
                        f"Known packer signature detected in section name: '{sec_name}'"
                    )

            # Analyze imports
            if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    for imp in entry.imports:
                        if imp.name:
                            api_name = imp.name.decode("latin-1", errors="ignore")
                            result.imported_apis.append(api_name)

                            if api_name in SUSPICIOUS_APIS:
                                desc = SUSPICIOUS_APIS[api_name]
                                result.suspicious_apis.append(api_name)
                                result.reasons.append(f"Suspicious API import: {api_name} ({desc})")

            pe.close()
        except Exception as e:
            # Not a fatal failure, could be corrupted PE or raw binary
            result.reasons.append(f"PE parsing notice: {e}")

    def _analyze_script(self, data: bytes, result: StaticAnalysisResult) -> None:
        """Scan text and script contents for malicious automation keywords."""
        try:
            content = data.decode("utf-8", errors="ignore")
            for pattern, description in SUSPICIOUS_SCRIPT_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    result.script_triggers.append(description)
                    result.reasons.append(f"Script security trigger: {description}")
        except Exception as e:
            logger.debug(f"Script inspection skipped for non-text data: {e}")


# Global static analyzer instance
static_analyzer = StaticAnalyzer()
