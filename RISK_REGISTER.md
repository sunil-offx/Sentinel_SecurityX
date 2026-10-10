# SentinelX — Threat & Project Risk Register

This document tracks identified architectural, detection, and operational risks associated with **SentinelX**, along with mitigation strategies and current statuses.

| ID | Risk | Probability | Impact | Mitigation Strategy | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **R01** | **False positives** | Medium | High | Combine deterministic rules + multi-layer static heuristics + confidence thresholds. Never automatically delete files; isolate to user-managed quarantine with one-click restore. | In Progress |
| **R02** | **False negatives** | Medium | Critical | Implement defense-in-depth: YARA matching, Shannon entropy calculation, PE section anomalies, suspicious API imports, script cradle heuristics, and download monitoring. | In Progress |
| **R03** | **PyInstaller dependency issue** | Medium | Medium | Automated CI test and packaging runner on clean Windows runner; explicit `--add-data` bindings for YARA rules and Qt plugins. | Mitigated |
| **R04** | **Antivirus flags application (False positive on SentinelX itself)** | Medium | High | Code signing with Authenticode certificates, open transparency, least-privilege execution, absence of offensive payloads. | Open |
| **R05** | **Quarantine failure or file corruption** | Low | Critical | Use atomic file operations (`shutil.move`), sidecar `.qmeta` recovery files, safe path traversal checks, and strip execution rights (`stat.S_IREAD`). | Mitigated |
| **R06** | **ML model bias (Phase 2)** | Medium | High | 52-feature EMBER-based representation, explainable AI top-feature extraction, calibrated classification thresholds (0.65 threshold), offline baseline bootstrap, and combination with deterministic static heuristics. | Mitigated |
| **R07** | **Cloud API unavailable** | Medium | Medium | Local-first architecture: core scanning, YARA, heuristics, and quarantine run 100% offline without cloud API dependency. Threat Intel features fail gracefully with clear offline/cached indicators. | Mitigated |
| **R08** | **Performance overhead during deep scans** | Medium | High | Multi-threaded worker architecture (`QThread`), configurable file size boundaries (250MB limit), streaming hash calculations. | Mitigated |
| **R09** | **Privilege escalation risk** | Low | Critical | Strict least-privilege design. The application runs with standard user rights and does not require administrator privileges for standard file/download inspection. | Mitigated |
| **R10** | **Malicious file causes analyzer crash** | Medium | High | Bounded streaming reads, defensive exception guards around `pefile` and `yara`, structured timeouts on YARA matching (10s limit). | Mitigated |

---

*Last Reviewed: Phase 3 Release (Advanced Endpoint Security)*

