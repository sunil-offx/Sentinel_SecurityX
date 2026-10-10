"""Risk scoring engine computing multi-layer threat scores and risk classifications."""

from dataclasses import dataclass, field
from typing import Any

from app.config.settings import settings
from app.core.analyzer import StaticAnalysisResult
from app.core.hasher import FileMetadata
from app.database.models import DetectionRecord, DetectionType, RiskLevel
from app.detection.yara_engine import YaraMatch


@dataclass
class RiskBreakdown:
    """Individual component scores contributing to total risk score."""

    entropy_score: int = 0
    suspicious_api_score: int = 0
    yara_score: int = 0
    extension_score: int = 0
    ml_score: int = 0


@dataclass
class RiskAssessmentResult:
    """Comprehensive risk assessment outcome."""

    risk_score: int = 0
    risk_level: RiskLevel = RiskLevel.SAFE
    breakdown: RiskBreakdown = field(default_factory=RiskBreakdown)
    reasons: list[str] = field(default_factory=list)
    detections: list[DetectionRecord] = field(default_factory=list)
    ml_prediction: Any = None


class RiskEngine:
    """Calculates risk scores based on static analysis, YARA matches, and file properties."""

    def __init__(
        self,
        weight_entropy: int | None = None,
        weight_suspicious_api: int | None = None,
        weight_yara: int | None = None,
        weight_extension: int | None = None,
        weight_ml: int | None = None,
    ) -> None:
        self.weight_entropy = (
            weight_entropy if weight_entropy is not None else settings.weight_entropy
        )
        self.weight_suspicious_api = (
            weight_suspicious_api
            if weight_suspicious_api is not None
            else settings.weight_suspicious_api
        )
        self.weight_yara = weight_yara if weight_yara is not None else settings.weight_yara
        self.weight_extension = (
            weight_extension if weight_extension is not None else settings.weight_extension
        )
        self.weight_ml = weight_ml if weight_ml is not None else settings.weight_ml

    def evaluate(
        self,
        metadata: FileMetadata,
        static_analysis: StaticAnalysisResult,
        yara_matches: list[YaraMatch],
        ml_prediction: Any = None,
    ) -> RiskAssessmentResult:

        """Calculate the composite risk score and generate detection records."""
        reasons: list[str] = []
        detections: list[DetectionRecord] = []

        # 1. Calculate Entropy Score
        entropy_score = 0
        if static_analysis.entropy >= settings.entropy_threshold_high:
            entropy_score = self.weight_entropy
            detections.append(
                DetectionRecord(
                    detection_type=DetectionType.ENTROPY.value,
                    severity=RiskLevel.HIGH.value,
                    reason=f"High file entropy ({static_analysis.entropy:.2f}/8.0)",
                )
            )
        elif static_analysis.entropy >= settings.entropy_threshold_medium:
            entropy_score = int(self.weight_entropy * 0.6)
            detections.append(
                DetectionRecord(
                    detection_type=DetectionType.ENTROPY.value,
                    severity=RiskLevel.LOW.value,
                    reason=f"Elevated file entropy ({static_analysis.entropy:.2f}/8.0)",
                )
            )

        # Check section entropy / anomalies
        if static_analysis.suspicious_sections:
            sec_boost = 10
            entropy_score = min(self.weight_entropy, entropy_score + sec_boost)
            for sec in static_analysis.suspicious_sections:
                detections.append(
                    DetectionRecord(
                        detection_type=DetectionType.SUSPICIOUS_SECTION.value,
                        severity=RiskLevel.HIGH.value,
                        reason=f"Abnormal or packed section: {sec}",
                    )
                )

        # 2. Calculate Suspicious API / Script Score
        api_score = 0
        api_count = len(static_analysis.suspicious_apis)
        if api_count > 0:
            if api_count >= 3:
                api_score = self.weight_suspicious_api
                severity = RiskLevel.HIGH.value
            elif api_count == 2:
                api_score = int(self.weight_suspicious_api * 0.75)
                severity = RiskLevel.HIGH.value
            else:
                api_score = int(self.weight_suspicious_api * 0.5)
                severity = RiskLevel.LOW.value

            detections.append(
                DetectionRecord(
                    detection_type=DetectionType.SUSPICIOUS_IMPORT.value,
                    severity=severity,
                    reason=f"Detected {api_count} suspicious API imports ({', '.join(static_analysis.suspicious_apis[:4])})",
                )
            )

        # Script execution triggers
        if static_analysis.script_triggers:
            script_score = self.weight_suspicious_api
            api_score = max(api_score, script_score)
            for trig in static_analysis.script_triggers:
                detections.append(
                    DetectionRecord(
                        detection_type=DetectionType.SUSPICIOUS_SCRIPT.value,
                        severity=RiskLevel.HIGH.value,
                        reason=f"Malicious script pattern: {trig}",
                    )
                )

        # 3. Calculate YARA Score
        yara_score = 0
        if yara_matches:
            has_critical = any(m.severity == "CRITICAL" for m in yara_matches)
            has_high = any(m.severity == "HIGH" for m in yara_matches)
            if has_critical:
                yara_score = self.weight_yara
            elif has_high:
                yara_score = self.weight_yara
            else:
                yara_score = int(self.weight_yara * 0.6)

            for match in yara_matches:
                detections.append(
                    DetectionRecord(
                        detection_type=DetectionType.YARA.value,
                        severity=RiskLevel.HIGH.value
                        if match.severity in ("HIGH", "CRITICAL")
                        else RiskLevel.LOW.value,
                        reason=f"YARA Match: {match.rule_name} - {match.description}",
                    )
                )

        # 4. Calculate Extension Score
        ext_score = 0
        ext = metadata.extension.lower()
        high_risk_scripts = {".scr", ".vbs", ".ps1", ".bat", ".cmd", ".js"}
        executable_binaries = {".exe", ".dll", ".msi"}

        if ext in high_risk_scripts:
            ext_score = self.weight_extension
            detections.append(
                DetectionRecord(
                    detection_type=DetectionType.EXTENSION.value,
                    severity=RiskLevel.LOW.value,
                    reason=f"High-risk script extension: {ext}",
                )
            )
        elif ext in executable_binaries:
            ext_score = int(self.weight_extension * 0.5)

        # 5. Calculate Machine Learning Malware Score
        ml_score = 0
        if ml_prediction and getattr(ml_prediction, "is_pe", False):
            prob = getattr(ml_prediction, "malware_probability", 0.0)
            if prob >= settings.ml_malware_threshold:
                ml_score = self.weight_ml
                detections.append(
                    DetectionRecord(
                        detection_type=DetectionType.ML_MALWARE.value,
                        severity=RiskLevel.HIGH.value,
                        reason=f"AI/ML Classifier: High malware probability ({prob:.1%})",
                    )
                )
                reasons.append(f"AI/ML Malware Prediction: High Probability ({prob:.1%})")
            elif prob >= 0.40:
                ml_score = int(self.weight_ml * 0.5)
                detections.append(
                    DetectionRecord(
                        detection_type=DetectionType.ML_MALWARE.value,
                        severity=RiskLevel.LOW.value,
                        reason=f"AI/ML Classifier: Elevated malware probability ({prob:.1%})",
                    )
                )
                reasons.append(f"AI/ML Malware Prediction: Suspicious ({prob:.1%})")

        # Composite risk score calculation
        raw_score = entropy_score + api_score + yara_score + ext_score + ml_score
        risk_score = max(0, min(100, raw_score))

        # Categorize Level based on configurable thresholds
        if risk_score <= settings.threshold_safe_max:
            risk_level = RiskLevel.SAFE
        elif risk_score <= settings.threshold_low_max:
            risk_level = RiskLevel.LOW
        elif risk_score <= settings.threshold_high_max:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL

        # Consolidate human readable reasons
        if static_analysis.is_pe:
            reasons.append("Executable file (PE)")
        elif ext in high_risk_scripts:
            reasons.append(f"Script file ({ext})")

        reasons.extend(static_analysis.reasons)
        for m in yara_matches:
            reasons.append(f"YARA Rule matched: {m.rule_name} ({m.description})")

        if not reasons:
            reasons.append("No suspicious traits or anomalous signatures detected.")

        return RiskAssessmentResult(
            risk_score=risk_score,
            risk_level=risk_level,
            breakdown=RiskBreakdown(
                entropy_score=entropy_score,
                suspicious_api_score=api_score,
                yara_score=yara_score,
                extension_score=ext_score,
                ml_score=ml_score,
            ),
            reasons=reasons,
            detections=detections,
            ml_prediction=ml_prediction,
        )


# Global risk engine instance
risk_engine = RiskEngine()

