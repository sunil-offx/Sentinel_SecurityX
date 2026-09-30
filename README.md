# SentinelX — AI-Powered Local Malware & Intrusion Detection System

[![CI/CD Pipeline](https://github.com/sunil-offx/Sentinel_SecurityX/actions/workflows/ci.yml/badge.svg)](https://github.com/sunil-offx/Sentinel_SecurityX/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform Windows](https://img.shields.io/badge/platform-Windows%2010%2F11%20x64-0078d7.svg)](https://www.microsoft.com/windows)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)

**SentinelX** is a local-first Windows malware and intrusion detection system designed for students, developers, home users, and small organizations. It inspects, scores, and quarantines suspicious files and scripts using defense-in-depth static heuristics, YARA rules, and PE structure analysis—with zero mandatory cloud dependencies.

> **Defensive Security Notice**: SentinelX is purely defensive. It analyzes, isolates, and quarantines threats; it does not perform credential theft, exploitation, persistence, or offensive actions.

---

## 🏛️ Architecture Overview

```
                      ┌───────────────────────┐
                      │     SentinelX UI      │
                      │   (PySide6 Desktop)   │
                      └───────────┬───────────┘
                                  │
                      ┌───────────▼───────────┐
                      │    Security Core      │
                      │                       │
                      │ • File Scanner        │
                      │ • Static Analyzer     │
                      │ • Cryptographic Hasher│
                      │ • Download Watcher    │
                      └───────────┬───────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
    ┌───────────┐           ┌───────────┐           ┌───────────┐
    │   YARA    │           │  Static   │           │ Extension │
    │  Engine   │           │ Heuristics│           │  Risk     │
    └─────┬─────┘           └─────┬─────┘           └─────┬─────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  ▼
                         ┌─────────────────┐
                         │  Risk Scoring   │
                         │    (0 - 100)    │
                         └────────┬────────┘
                                  │
         ┌────────────────┬───────┴────────┬────────────────┐
         ▼                ▼                ▼                ▼
       SAFE              LOW             HIGH            CRITICAL
      (0–29)           (30–59)          (60–79)          (80–100)
                                           │                │
                                           └───────┬────────┘
                                                   ▼
                                             ┌────────────┐
                                             │ Quarantine │
                                             └─────┬──────┘
                                                   ▼
                                            SQLite Database
```

---

## 🚀 Key Features (Phase 1 — MVP)

### 1. Multi-Format File Scanner
- Supports executables and scripts: `.exe`, `.dll`, `.msi`, `.bat`, `.cmd`, `.ps1`, `.vbs`, `.js`, `.scr`.
- Calculates streaming cryptographic hashes: **SHA-256**, **MD5**, and **SHA-1**.
- Extracts metadata: exact byte size, human-readable size, MIME type, creation time, and modification time.

### 2. Static Analyzer & Heuristics
- **Shannon Entropy Calculation**: Identifies packed, obfuscated, or encrypted payloads ($H \in [0.0, 8.0]$).
- **Windows PE Header Parsing** (`pefile`):
  - Section anomaly inspection (e.g. non-standard sections, `.upx`, section entropy > 7.2).
  - W^X violation detection (sections marked simultaneously **WRITABLE** and **EXECUTABLE**).
  - Suspicious Windows API import detection (e.g., `VirtualAllocEx`, `WriteProcessMemory`, `CreateRemoteThread`, `SetWindowsHookEx`, `URLDownloadToFile`).
- **Script Command Heuristics**: Detects malicious execution cradles in `.ps1`, `.bat`, `.vbs`, and `.js` (e.g., `Invoke-Expression`, `Net.WebClient.DownloadString`, `-WindowStyle Hidden`, `powershell -enc`, `certutil -urlcache`).

### 3. YARA Detection Engine
- Native YARA rule compiler and scanner.
- Pre-packaged with detection rules in `app/detection/rules/default.yar`.
- Extensible rule repository in `yara_rules/threats.yar`.

### 4. Configurable Multi-Factor Risk Engine
- Implements composite risk formula:
  $$\text{Risk Score} = \text{Entropy Score} + \text{Suspicious API Score} + \text{YARA Score} + \text{Extension Score}$$
- Classifies risk level into `SAFE`, `LOW`, `HIGH`, or `CRITICAL`.
- Generates transparent, human-readable diagnostic reasons for every detection.

### 5. Secure Quarantine Vault
- **Atomic File Move**: Segregates suspicious files to `.sentinelx/quarantine/`.
- **Privilege Stripping**: Removes execute and write permissions (`stat.S_IREAD`) to neutralize accidental launch.
- **Sidecar Metadata (`.qmeta`)**: Preserves original paths, hashes, and isolation reasons for offline recovery.
- **Safe Restoration & Secure Shredding**: One-click restore back to original directory or defensive zero-overwrite shredding.

### 6. Background Real-Time Directory Shield
- Asynchronously monitors the Windows `Downloads` directory for incoming executables or scripts.
- Automatically queues new files for scan without manual user intervention.

### 7. Modern PySide6 GUI
- **Dashboard**: Live system protection status, metric cards, threat distribution, and quick actions.
- **Threat Scanner**: Single file and recursive directory scanning, progress tracking, and side-by-side threat inspection.
- **Quarantine Vault View**: Isolated files table with instant restore and shredding actions.
- **Scan History**: Full audit trail with search and filter capabilities.
- **Settings**: Customizable risk score cutoffs, YARA reload, and monitor folder picker.

---

## 📁 Project Structure

```
sentinelx/
├── app/
│   ├── main.py                     # Application entry point & Qt loop
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py             # Application paths, thresholds, and weights
│   ├── core/
│   │   ├── __init__.py
│   │   ├── analyzer.py             # Static analysis (entropy, PE headers, scripts)
│   │   ├── hasher.py               # Streaming hashing (SHA-256, MD5, SHA-1)
│   │   ├── quarantine.py           # Atomic isolation & restoration vault
│   │   ├── risk_engine.py          # Composite risk scoring engine
│   │   └── scanner.py              # File & directory scan orchestrator
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py             # SQLite persistence & query API
│   │   └── models.py               # Data models (ScannedFile, Detection, Quarantine)
│   ├── detection/
│   │   ├── __init__.py
│   │   ├── yara_engine.py          # YARA compilation and matching engine
│   │   └── rules/
│   │       └── default.yar         # Default detection rules
│   ├── monitoring/
│   │   ├── __init__.py
│   │   └── download_monitor.py     # Background directory watcher
│   └── ui/
│       ├── __init__.py
│       ├── dashboard.py            # Dashboard view with stats & status banner
│       ├── history_view.py         # Historical scan audit log
│       ├── main_window.py          # Shell window with sidebar navigation
│       ├── quarantine_view.py      # Quarantine vault management
│       ├── scanner_view.py         # Multi-threaded file & folder scanner
│       ├── settings_view.py        # Risk thresholds & shield settings
│       └── styles.py               # Cyber dark design system & tokens
├── tests/
│   ├── fixtures/                   # Benign simulated test files (NO real malware)
│   ├── unit/                       # Unit tests for hasher, analyzer, YARA, DB, etc.
│   ├── integration/                # Pipeline tests (File -> Scanner -> DB)
│   └── e2e/                        # End-to-end acceptance tests (AT-01 to AT-05)
├── installer/
│   └── sentinelx.iss               # Inno Setup 6 compiler configuration
├── scripts/
│   ├── build.py                    # Standalone PyInstaller build script
│   └── package.py                  # Full packaging test and build pipeline
├── yara_rules/
│   └── threats.yar                 # Extended threat rule repository
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI workflow
├── requirements.txt
├── pyproject.toml
├── RISK_REGISTER.md                # Project security & operational risk register
├── LICENSE
└── README.md
```

---

## 🛠️ Getting Started

### Prerequisites
- Windows 10/11 64-bit
- Python 3.11 or 3.12
- Git

### Installation

```powershell
# 1. Clone the repository
git clone https://github.com/sentinelx/sentinelx.git
cd sentinelx

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Generate benign test fixtures
python tests/fixtures/generate_fixtures.py
```

### Launching the Application

```powershell
python app/main.py
```

---

## 🧪 Testing & Verification

SentinelX includes a complete automated test suite verifying all MVP acceptance criteria. **No real malware samples are ever used in development; benign fixtures simulate threat characteristics.**

```powershell
# Run the entire test suite
python -m pytest -v

# Run with coverage report
python -m pytest -v --cov=app

# Run Code Linter (Ruff)
python -m ruff check .

# Run Security Vulnerability Audit (Bandit)
python -m bandit -r app
```

### Acceptance Test Coverage (Section 12)
- **AT-01 (File Scanning)**: Validates metadata extraction and SHA-256 computation (`test_at_01_file_scanning`).
- **AT-02 (Detection)**: Verifies YARA and heuristic pattern identification (`test_at_02_detection`).
- **AT-03 (Quarantine)**: Verifies atomic quarantine file isolation and deprivileging (`test_at_03_quarantine`).
- **AT-04 (Scan History)**: Verifies persistence of scans and detections to SQLite (`test_at_04_history`).
- **AT-05 (Download Monitoring)**: Verifies automated queuing and analysis of new files (`test_at_05_download_monitoring`).

---

## 📦 Building Standalone Executable & Installer

### 1. Build Standalone `.exe` (PyInstaller)

```powershell
python scripts/build.py
```
Outputs standalone directory to `dist/SentinelX/SentinelX.exe`.

### 2. Generate Setup Installer (Inno Setup)

Compile `installer/sentinelx.iss` using Inno Setup 6 to produce `dist/installer/SentinelX-Setup-0.1.0-x64.exe`.

---

## 🗺️ Product Roadmap

- [x] **Phase 1: MVP (Complete)**
  - File scanner (.exe, .dll, .msi, .bat, .cmd, .ps1, .vbs, .js, .scr)
  - SHA-256, MD5, SHA-1 streaming hasher
  - Static analyzer (Shannon entropy, PE parser, script heuristics)
  - YARA rule engine
  - Risk scoring engine
  - Safe quarantine vault with restore & shred
  - SQLite database persistence & stats
  - Downloads folder monitor
  - PySide6 desktop GUI with dark cybersecurity theme
  - Automated tests (unit, integration, E2E)
- [ ] **Phase 2: AI & Real-Time Security (Upcoming)**
  - Machine learning PE malware classifier (Random Forest / XGBoost with EMBER feature set)
  - Real-time process monitor (parent-child relationship, command lines, memory injection tracking)
- [ ] **Phase 3: Advanced Endpoint Security**
  - Outbound connection inspection & network telemetry
  - Threat intelligence integrations (VirusTotal / AbuseIPDB with secure API key storage)
  - Windows Event Log telemetry ingestion

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
