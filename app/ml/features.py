"""EMBER-inspired feature extraction for Windows PE binaries."""

import math
import re
from dataclasses import dataclass
from pathlib import Path

import pefile


@dataclass
class ExtractedFeatures:
    """Vector and dictionary representation of extracted PE features."""

    feature_vector: list[float]
    feature_names: list[str]
    feature_dict: dict[str, float]
    is_pe: bool
    file_size: int
    error: str | None = None


SUSPICIOUS_API_CATEGORIES: dict[str, list[str]] = {
    "injection": [
        "virtualallocex",
        "writeprocessmemory",
        "createremotethread",
        "ntcreatethreadex",
        "queueuserapc",
        "setwindowshookex",
        "resumethread",
    ],
    "evasion": [
        "isdebuggerpresent",
        "checkremotedebuggerpresent",
        "outputdebugstring",
        "ntqueryinformationprocess",
        "gettickcount",
        "sleep",
    ],
    "persistence": [
        "regsetvalueexa",
        "regsetvalueexw",
        "regcreatekeyexa",
        "regcreatekeyexw",
        "createservicea",
        "createservicew",
        "openscmanagera",
    ],
    "networking": [
        "urldownloadtofilea",
        "urldownloadtofilew",
        "internetopena",
        "internetopenw",
        "httpopenrequesta",
        "wsastartup",
        "connect",
        "socket",
    ],
    "process": [
        "shellexecutea",
        "shellexecutew",
        "winexec",
        "createprocessa",
        "createprocessw",
        "adjusttokenprivileges",
    ],
    "crypto": [
        "cryptencrypt",
        "cryptacquirecontexta",
        "cryptacquirecontextw",
        "bcryptencrypt",
    ],
}

STANDARD_SECTIONS: set[str] = {
    ".text",
    ".code",
    ".data",
    ".rdata",
    ".idata",
    ".edata",
    ".rsrc",
    ".reloc",
    ".pdata",
    ".tls",
    ".bss",
}


class PEFeatureExtractor:
    """Extracts numeric feature vectors from Windows Portable Executable files."""

    def __init__(self) -> None:
        self.feature_names = self._build_feature_names()

    def _build_feature_names(self) -> list[str]:
        names = [
            "log_file_size",
            "log_virtual_size",
            "has_debug",
            "has_relocations",
            "has_resources",
            "has_signature",
            "has_tls",
            "is_dll",
            "is_driver",
            "num_sections",
            "num_imports",
            "num_imported_dlls",
            "num_exports",
            "entropy_overall",
            "entropy_section_max",
            "entropy_section_min",
            "entropy_section_mean",
            "num_executable_sections",
            "num_writable_sections",
            "num_wx_sections",
            "num_zero_length_sections",
            "num_anomalous_section_names",
            "import_suspicious_injection",
            "import_suspicious_evasion",
            "import_suspicious_persistence",
            "import_suspicious_networking",
            "import_suspicious_process",
            "import_suspicious_crypto",
            "num_strings",
            "avg_string_length",
            "string_entropy",
            "contains_url_strings",
            "contains_ip_strings",
            "contains_ps_cmd_strings",
            "entry_point_in_last_section",
            "size_code_ratio",
            "size_init_data_ratio",
            "subsystem_gui",
            "subsystem_cli",
            "header_checksum_zero",
            "major_linker_version",
            "major_os_version",
        ]
        # 10 byte-frequency histogram bins
        for i in range(10):
            names.append(f"byte_hist_bin_{i}")
        return names

    def calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy for raw bytes."""
        if not data:
            return 0.0
        length = len(data)
        counts = [0] * 256
        for b in data:
            counts[b] += 1
        entropy = 0.0
        for count in counts:
            if count > 0:
                p = count / length
                entropy -= p * math.log2(p)
        return float(entropy)

    def extract_features(self, file_path: Path) -> ExtractedFeatures:
        """Extract EMBER-like feature representations from a PE file.

        Returns ExtractedFeatures with is_pe=False if not a valid PE.
        """
        path = Path(file_path).resolve()
        if not path.is_file():
            empty_vec = [0.0] * len(self.feature_names)
            return ExtractedFeatures(
                feature_vector=empty_vec,
                feature_names=self.feature_names,
                feature_dict=dict(zip(self.feature_names, empty_vec, strict=False)),
                is_pe=False,
                file_size=0,
                error="File does not exist",
            )

        try:
            file_bytes = path.read_bytes()
        except Exception as e:
            empty_vec = [0.0] * len(self.feature_names)
            return ExtractedFeatures(
                feature_vector=empty_vec,
                feature_names=self.feature_names,
                feature_dict=dict(zip(self.feature_names, empty_vec, strict=False)),
                is_pe=False,
                file_size=0,
                error=f"Could not read file: {e}",
            )

        file_size = len(file_bytes)
        overall_entropy = self.calculate_entropy(file_bytes)

        # Quick check for MZ signature
        if len(file_bytes) < 64 or file_bytes[:2] != b"MZ":
            empty_vec = [0.0] * len(self.feature_names)
            empty_vec[0] = math.log1p(file_size)
            empty_vec[13] = overall_entropy
            return ExtractedFeatures(
                feature_vector=empty_vec,
                feature_names=self.feature_names,
                feature_dict=dict(zip(self.feature_names, empty_vec, strict=False)),
                is_pe=False,
                file_size=file_size,
                error="Not a Windows PE binary (Missing MZ header)",
            )

        try:
            pe = pefile.PE(data=file_bytes, fast_load=False)
        except Exception as e:
            empty_vec = [0.0] * len(self.feature_names)
            empty_vec[0] = math.log1p(file_size)
            empty_vec[13] = overall_entropy
            return ExtractedFeatures(
                feature_vector=empty_vec,
                feature_names=self.feature_names,
                feature_dict=dict(zip(self.feature_names, empty_vec, strict=False)),
                is_pe=False,
                file_size=file_size,
                error=f"Malformed PE header: {e}",
            )

        try:
            features = self._parse_pe(pe, file_bytes, file_size, overall_entropy)
            vec = [features.get(name, 0.0) for name in self.feature_names]
            return ExtractedFeatures(
                feature_vector=vec,
                feature_names=self.feature_names,
                feature_dict=features,
                is_pe=True,
                file_size=file_size,
            )
        finally:
            pe.close()

    def _parse_pe(
        self, pe: pefile.PE, file_bytes: bytes, file_size: int, overall_entropy: float
    ) -> dict[str, float]:
        feat: dict[str, float] = {}

        # 1. General properties
        feat["log_file_size"] = float(math.log1p(file_size))
        virtual_size = (
            getattr(pe.OPTIONAL_HEADER, "SizeOfImage", 0) if hasattr(pe, "OPTIONAL_HEADER") else 0
        )
        feat["log_virtual_size"] = float(math.log1p(virtual_size))

        # Directories
        has_debug = 0.0
        has_relocs = 0.0
        has_rsrc = 0.0
        has_security = 0.0
        has_tls = 0.0

        if hasattr(pe, "OPTIONAL_HEADER") and hasattr(pe.OPTIONAL_HEADER, "DATA_DIRECTORY"):
            for entry in pe.OPTIONAL_HEADER.DATA_DIRECTORY:
                if entry.name == "IMAGE_DIRECTORY_ENTRY_DEBUG" and entry.VirtualAddress != 0:
                    has_debug = 1.0
                elif entry.name == "IMAGE_DIRECTORY_ENTRY_BASERELOC" and entry.VirtualAddress != 0:
                    has_relocs = 1.0
                elif entry.name == "IMAGE_DIRECTORY_ENTRY_RESOURCE" and entry.VirtualAddress != 0:
                    has_rsrc = 1.0
                elif entry.name == "IMAGE_DIRECTORY_ENTRY_SECURITY" and entry.VirtualAddress != 0:
                    has_security = 1.0
                elif entry.name == "IMAGE_DIRECTORY_ENTRY_TLS" and entry.VirtualAddress != 0:
                    has_tls = 1.0

        feat["has_debug"] = has_debug
        feat["has_relocations"] = has_relocs
        feat["has_resources"] = has_rsrc
        feat["has_signature"] = has_security
        feat["has_tls"] = has_tls

        # Characteristics
        is_dll = 0.0
        if hasattr(pe, "FILE_HEADER") and (pe.FILE_HEADER.Characteristics & 0x2000):
            is_dll = 1.0
        feat["is_dll"] = is_dll

        subsystem = getattr(pe.OPTIONAL_HEADER, "Subsystem", 0)
        feat["is_driver"] = 1.0 if subsystem == 1 else 0.0
        feat["subsystem_gui"] = 1.0 if subsystem == 2 else 0.0
        feat["subsystem_cli"] = 1.0 if subsystem == 3 else 0.0

        # Linker / OS versions
        feat["major_linker_version"] = float(
            getattr(pe.OPTIONAL_HEADER, "MajorLinkerVersion", 0)
        )
        feat["major_os_version"] = float(
            getattr(pe.OPTIONAL_HEADER, "MajorOperatingSystemVersion", 0)
        )
        feat["header_checksum_zero"] = (
            1.0 if getattr(pe.OPTIONAL_HEADER, "CheckSum", 0) == 0 else 0.0
        )

        # 2. Sections
        sections = getattr(pe, "sections", [])
        feat["num_sections"] = float(len(sections))

        sec_entropies: list[float] = []
        num_exec = 0
        num_write = 0
        num_wx = 0
        num_zero = 0
        num_anomalous_names = 0
        last_section = sections[-1] if sections else None

        for s in sections:
            ent = s.get_entropy()
            sec_entropies.append(ent)

            name = ""
            try:
                name = s.Name.decode("latin-1", errors="ignore").rstrip("\x00").lower()
            except Exception:  # nosec B110
                name = ""


            if name not in STANDARD_SECTIONS:
                num_anomalous_names += 1

            chars = s.Characteristics
            is_e = bool(chars & 0x20000000)
            is_w = bool(chars & 0x80000000)
            if is_e:
                num_exec += 1
            if is_w:
                num_write += 1
            if is_e and is_w:
                num_wx += 1

            if s.SizeOfRawData == 0 or s.Misc_VirtualSize == 0:
                num_zero += 1

        feat["entropy_overall"] = overall_entropy
        feat["entropy_section_max"] = max(sec_entropies) if sec_entropies else 0.0
        feat["entropy_section_min"] = min(sec_entropies) if sec_entropies else 0.0
        feat["entropy_section_mean"] = (
            sum(sec_entropies) / len(sec_entropies) if sec_entropies else 0.0
        )
        feat["num_executable_sections"] = float(num_exec)
        feat["num_writable_sections"] = float(num_write)
        feat["num_wx_sections"] = float(num_wx)
        feat["num_zero_length_sections"] = float(num_zero)
        feat["num_anomalous_section_names"] = float(num_anomalous_names)

        # Check if entry point is in last section
        ep_rva = getattr(pe.OPTIONAL_HEADER, "AddressOfEntryPoint", 0)
        ep_in_last = 0.0
        if last_section and last_section.VirtualAddress <= ep_rva < (
            last_section.VirtualAddress + last_section.Misc_VirtualSize
        ):
            ep_in_last = 1.0
        feat["entry_point_in_last_section"] = ep_in_last

        # Code and data ratios
        size_code = getattr(pe.OPTIONAL_HEADER, "SizeOfCode", 0)
        size_init = getattr(pe.OPTIONAL_HEADER, "SizeOfInitializedData", 0)
        feat["size_code_ratio"] = float(size_code / virtual_size) if virtual_size > 0 else 0.0
        feat["size_init_data_ratio"] = float(size_init / virtual_size) if virtual_size > 0 else 0.0

        # 3. Imports and Exports
        total_imports = 0
        total_dlls = 0
        imported_apis: set[str] = set()

        if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
            total_dlls = len(pe.DIRECTORY_ENTRY_IMPORT)
            for imp in pe.DIRECTORY_ENTRY_IMPORT:
                for func in imp.imports:
                    total_imports += 1
                    if func.name:
                        try:
                            fn_str = func.name.decode("latin-1", errors="ignore").lower()
                            imported_apis.add(fn_str)
                        except Exception:  # nosec B110
                            pass


        feat["num_imports"] = float(total_imports)
        feat["num_imported_dlls"] = float(total_dlls)

        total_exports = 0
        if hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
            total_exports = len(pe.DIRECTORY_ENTRY_EXPORT.symbols)
        feat["num_exports"] = float(total_exports)

        # Suspicious API counts per category
        for cat, api_list in SUSPICIOUS_API_CATEGORIES.items():
            cnt = sum(1 for target in api_list if any(target in api for api in imported_apis))
            feat[f"import_suspicious_{cat}"] = float(cnt)

        # 4. String features
        # Extract ASCII strings >= 4 chars
        strings = re.findall(b"[ -~]{4,}", file_bytes[:1024 * 1024])  # sample first 1MB
        feat["num_strings"] = float(len(strings))
        if strings:
            avg_len = sum(len(s) for s in strings) / len(strings)
            feat["avg_string_length"] = float(avg_len)
            # Sampled string entropy
            joined_str = b"".join(strings[:200])
            feat["string_entropy"] = self.calculate_entropy(joined_str)
        else:
            feat["avg_string_length"] = 0.0
            feat["string_entropy"] = 0.0

        # Indicators in strings
        has_url = 0.0
        has_ip = 0.0
        has_ps_cmd = 0.0
        for s in strings:
            s_lower = s.lower()
            if b"http://" in s_lower or b"https://" in s_lower or b".onion" in s_lower:
                has_url = 1.0
            if re.search(rb"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", s):
                has_ip = 1.0
            if (
                b"powershell" in s_lower
                or b"cmd.exe" in s_lower
                or b"invoke-expression" in s_lower
                or b"-enc" in s_lower
                or b"wscript" in s_lower
            ):
                has_ps_cmd = 1.0

        feat["contains_url_strings"] = has_url
        feat["contains_ip_strings"] = has_ip
        feat["contains_ps_cmd_strings"] = has_ps_cmd

        # 5. 10-bin byte histogram
        hist = [0] * 256
        for b in file_bytes[:256 * 1024]:  # Sample up to 256KB
            hist[b] += 1
        sample_len = min(len(file_bytes), 256 * 1024)
        if sample_len > 0:
            bin_size = 25.6
            for i in range(10):
                start = int(i * bin_size)
                end = int((i + 1) * bin_size)
                feat[f"byte_hist_bin_{i}"] = float(sum(hist[start:end]) / sample_len)
        else:
            for i in range(10):
                feat[f"byte_hist_bin_{i}"] = 0.0

        return feat


# Global instance
pe_feature_extractor = PEFeatureExtractor()
