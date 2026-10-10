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

    # 1. Ensure BASE_DIR in sys.path
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))

    from app.ml.classifier import pe_classifier


    if not pe_classifier.model_path.exists():
        print("Training baseline ML PE classifier...")
        pe_classifier.train_baseline_model()

    rules_source = BASE_DIR / "app" / "detection" / "rules"
    rules_arg = f"{rules_source}{os.pathsep}app/detection/rules"

    models_source = BASE_DIR / "app" / "ml" / "models"
    models_arg = f"{models_source}{os.pathsep}app/ml/models"

    is_onefile = "--onefile" in sys.argv

    excluded_modules = [
        "nltk",
        "matplotlib",
        "tkinter",
        "_tkinter",
        "cv2",
        "torch",
        "torchvision",
        "transformers",
        "IPython",
        "jupyter",
        "pandas",
        "numba",
    ]

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
        "--add-data",
        models_arg,
        "--hidden-import",
        "sklearn",
        "--hidden-import",
        "sklearn.ensemble",
        "--hidden-import",
        "sklearn.tree",
        "--hidden-import",
        "joblib",
        "--hidden-import",
        "pefile",
        "--hidden-import",
        "psutil",
        "--hidden-import",
        "yara",
        "--hidden-import",
        "pydantic",
    ]

    for mod in excluded_modules:
        cmd.extend(["--exclude-module", mod])

    cmd.append(str(BASE_DIR / "app" / "main.py"))

    if is_onefile:
        cmd.insert(6, "--onefile")

    print("Executing command:")
    print(" ".join(cmd))
    result = subprocess.run(cmd, cwd=str(BASE_DIR))
    if result.returncode == 0:
        print("\nBuild completed successfully!")
        target_out = (
            BASE_DIR / "dist" / "SentinelX.exe"
            if is_onefile
            else BASE_DIR / "dist" / "SentinelX" / "SentinelX.exe"
        )
        print(f"Artifact location: {target_out}")
    else:
        print(f"\nBuild failed with exit code: {result.returncode}")

    return result.returncode


if __name__ == "__main__":
    sys.exit(build())

