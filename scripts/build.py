"""Build script packaging SentinelX into a standalone Windows executable using PyInstaller."""

import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def build() -> int:
    """Run PyInstaller build."""
    print("=" * 60)
    print("SentinelX Executable Build Script")
    print("=" * 60)

    rules_source = BASE_DIR / "app" / "detection" / "rules"
    rules_arg = f"{rules_source}{os.pathsep}app/detection/rules"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        "SentinelX",
        "--add-data",
        rules_arg,
        str(BASE_DIR / "app" / "main.py"),
    ]

    print("Executing command:")
    print(" ".join(cmd))
    result = subprocess.run(cmd, cwd=str(BASE_DIR))
    if result.returncode == 0:
        print("\nBuild completed successfully!")
        print(f"Artifact location: {BASE_DIR / 'dist' / 'SentinelX' / 'SentinelX.exe'}")
    else:
        print(f"\nBuild failed with exit code: {result.returncode}")

    return result.returncode


if __name__ == "__main__":
    sys.exit(build())
