"""Packaging pipeline running tests, PyInstaller build, and Inno Setup installer compilation."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def package() -> int:
    """Run full packaging pipeline."""
    print("Step 1: Running Automated Tests...")
    test_res = subprocess.run([sys.executable, "-m", "pytest", "-v"], cwd=str(BASE_DIR))
    if test_res.returncode != 0:
        print("Tests failed! Aborting packaging.")
        return 1

    print("\nStep 2: Building Standalone Executable...")
    build_script = BASE_DIR / "scripts" / "build.py"
    build_res = subprocess.run([sys.executable, str(build_script)], cwd=str(BASE_DIR))
    if build_res.returncode != 0:
        print("Executable build failed! Aborting packaging.")
        return 1

    print("\nStep 3: Checking Inno Setup Compiler (ISCC)...")
    iscc_path = shutil.which("ISCC") or r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    iss_file = BASE_DIR / "installer" / "sentinelx.iss"

    if os.path.exists(iscc_path) and iss_file.exists():
        print(f"Compiling installer with {iscc_path}...")
        installer_res = subprocess.run([iscc_path, str(iss_file)], cwd=str(BASE_DIR))
        if installer_res.returncode == 0:
            print("\nSetup installer compiled successfully!")
        else:
            print("Inno Setup compilation returned non-zero code.")
    else:
        print(f"Notice: Inno Setup Compiler not found at {iscc_path}. Skipping .exe installer generation.")
        print("Standalone binary directory dist/SentinelX is ready for distribution.")

    return 0


if __name__ == "__main__":
    sys.exit(package())
