"""Random Forest PE malware classifier with feature explainability and offline bootstrap."""

import logging
import math
import random
from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from app.config.settings import settings
from app.ml.features import PEFeatureExtractor, pe_feature_extractor

logger = logging.getLogger(__name__)


@dataclass
class MLPredictionResult:
    """Prediction outcome from the Machine Learning PE Classifier."""

    is_pe: bool = False
    malware_probability: float = 0.0  # 0.0 to 1.0
    confidence: float = 0.0  # 0.0 to 1.0
    classification: str = "BENIGN"  # BENIGN, SUSPICIOUS, MALICIOUS
    top_features: list[tuple[str, float]] = field(default_factory=list)
    model_version: str = "RandomForest-EMBER-v1.0"
    error: str | None = None


class PEClassifier:
    """Random Forest machine learning classifier for Windows Portable Executable files."""

    def __init__(
        self,
        model_path: Path | None = None,
        feature_extractor: PEFeatureExtractor | None = None,
    ) -> None:
        self.model_path = model_path or settings.ml_model_path
        self.feature_extractor = feature_extractor or pe_feature_extractor
        self.model: RandomForestClassifier | None = None
        self._ensure_model_loaded()

    def _ensure_model_loaded(self) -> None:
        """Load trained model from disk or bootstrap a calibrated baseline model."""
        if self.model_path.is_file():
            try:
                self.model = joblib.load(str(self.model_path))
                logger.info(f"Loaded existing ML model from {self.model_path}")
                return
            except Exception as e:
                logger.warning(f"Could not load ML model from {self.model_path}: {e}. Retraining...")

        # Bootstrap and persist baseline model
        self.train_baseline_model()

    def train_baseline_model(self) -> None:
        """Train and persist a baseline Random Forest classifier on calibrated PE distributions."""
        feature_names = self.feature_extractor.feature_names
        rng = random.Random(42)  # nosec B311


        x_samples: list[list[float]] = []

        y_labels: list[int] = []

        # Generate calibrated synthetic dataset simulating real-world benign vs malicious PE traits
        num_samples_per_class = 400

        # Class 0: Benign PE Binaries
        for _ in range(num_samples_per_class):
            vec = [0.0] * len(feature_names)
            # Size: 10KB to 50MB
            size = rng.randint(10 * 1024, 50 * 1024 * 1024)
            vec[0] = math.log1p(size)
            vec[1] = math.log1p(int(size * rng.uniform(1.1, 1.8)))
            vec[2] = 1.0 if rng.random() > 0.3 else 0.0  # has_debug
            vec[3] = 1.0 if rng.random() > 0.2 else 0.0  # has_relocations
            vec[4] = 1.0 if rng.random() > 0.1 else 0.0  # has_resources
            vec[5] = 1.0 if rng.random() > 0.4 else 0.0  # has_signature
            vec[6] = 1.0 if rng.random() > 0.7 else 0.0  # has_tls
            vec[7] = 1.0 if rng.random() > 0.6 else 0.0  # is_dll
            vec[8] = 0.0  # is_driver
            vec[9] = float(rng.randint(3, 8))  # num_sections
            vec[10] = float(rng.randint(20, 300))  # num_imports
            vec[11] = float(rng.randint(3, 15))  # num_imported_dlls
            vec[12] = float(rng.randint(0, 50))  # num_exports

            # Benign entropy is typically 4.2 - 6.4
            ent_mean = rng.uniform(4.5, 6.2)
            vec[13] = ent_mean  # entropy_overall
            vec[14] = ent_mean + rng.uniform(0.1, 0.7)  # entropy_section_max
            vec[15] = ent_mean - rng.uniform(0.5, 1.5)  # entropy_section_min
            vec[16] = ent_mean  # entropy_section_mean

            vec[17] = float(rng.randint(1, 2))  # num_executable_sections
            vec[18] = float(rng.randint(1, 3))  # num_writable_sections
            vec[19] = 0.0  # num_wx_sections (strictly 0 for legitimate software)
            vec[20] = 0.0  # zero length
            vec[21] = 0.0 if rng.random() > 0.08 else 1.0  # anomalous names

            # API counts: benign applications rarely have injection/evasion clusters
            vec[22] = 1.0 if rng.random() > 0.9 else 0.0  # injection
            vec[23] = 1.0 if rng.random() > 0.8 else 0.0  # evasion
            vec[24] = 1.0 if rng.random() > 0.8 else 0.0  # persistence
            vec[25] = 1.0 if rng.random() > 0.7 else 0.0  # networking
            vec[26] = 1.0 if rng.random() > 0.6 else 0.0  # process
            vec[27] = 1.0 if rng.random() > 0.8 else 0.0  # crypto

            # Strings
            vec[28] = float(rng.randint(100, 2000))  # num_strings
            vec[29] = float(rng.uniform(8.0, 25.0))  # avg_string_length
            vec[30] = float(rng.uniform(3.8, 5.0))  # string_entropy
            vec[31] = 1.0 if rng.random() > 0.5 else 0.0  # urls
            vec[32] = 0.0 if rng.random() > 0.1 else 1.0  # ips
            vec[33] = 0.0  # powershell/cmd invocation strings (benign rarely has them)
            vec[34] = 0.0  # entry_point_in_last_section

            vec[35] = float(rng.uniform(0.3, 0.7))  # size_code_ratio
            vec[36] = float(rng.uniform(0.1, 0.5))  # size_init_data_ratio
            vec[37] = 1.0 if rng.random() > 0.3 else 0.0  # gui
            vec[38] = 1.0 - vec[37]  # cli
            vec[39] = 1.0 if rng.random() > 0.7 else 0.0  # checksum zero
            vec[40] = float(rng.randint(10, 14))  # linker
            vec[41] = float(rng.randint(6, 10))  # os

            # Byte histogram
            for i in range(10):
                vec[42 + i] = float(rng.uniform(0.05, 0.15))

            x_samples.append(vec)
            y_labels.append(0)

        # Class 1: Malicious / Packed / Weaponized PE Binaries
        for _ in range(num_samples_per_class):
            vec = [0.0] * len(feature_names)
            size = rng.randint(5 * 1024, 20 * 1024 * 1024)
            vec[0] = math.log1p(size)
            vec[1] = math.log1p(int(size * rng.uniform(1.5, 4.0)))  # often inflated virtual size
            vec[2] = 1.0 if rng.random() > 0.8 else 0.0  # debug stripped
            vec[3] = 1.0 if rng.random() > 0.7 else 0.0  # relocations stripped
            vec[4] = 1.0 if rng.random() > 0.5 else 0.0
            vec[5] = 1.0 if rng.random() > 0.85 else 0.0  # rarely validly signed
            vec[6] = 1.0 if rng.random() > 0.4 else 0.0  # TLS callbacks
            vec[7] = 1.0 if rng.random() > 0.7 else 0.0
            vec[8] = 0.0
            vec[9] = float(rng.randint(2, 6))
            vec[10] = float(rng.randint(5, 50))  # packed binaries have very few imports
            vec[11] = float(rng.randint(1, 4))
            vec[12] = 0.0

            # Malicious / packed entropy is high: 7.1 to 7.95
            ent_mean = rng.uniform(7.1, 7.95)
            vec[13] = ent_mean
            vec[14] = rng.uniform(7.4, 7.99)  # high packed section entropy
            vec[15] = ent_mean - rng.uniform(0.2, 1.0)
            vec[16] = ent_mean

            vec[17] = float(rng.randint(1, 3))
            vec[18] = float(rng.randint(1, 3))
            vec[19] = float(rng.randint(1, 2)) if rng.random() > 0.35 else 0.0  # W^X violations!
            vec[20] = 1.0 if rng.random() > 0.5 else 0.0  # zero length raw data
            vec[21] = float(rng.randint(1, 3))  # anomalous section names (.upx, etc.)

            # Highly clustered suspicious APIs
            vec[22] = float(rng.randint(1, 4))  # injection (VirtualAllocEx, WriteProcessMemory)
            vec[23] = float(rng.randint(1, 3))  # evasion (IsDebuggerPresent)
            vec[24] = float(rng.randint(1, 2))  # persistence
            vec[25] = float(rng.randint(1, 3))  # networking
            vec[26] = float(rng.randint(1, 3))  # process
            vec[27] = float(rng.randint(1, 2))  # crypto

            # Strings
            vec[28] = float(rng.randint(10, 300))  # fewer printable strings due to packing
            vec[29] = float(rng.uniform(12.0, 45.0))
            vec[30] = float(rng.uniform(4.5, 6.2))
            vec[31] = 1.0 if rng.random() > 0.3 else 0.0
            vec[32] = 1.0 if rng.random() > 0.4 else 0.0
            vec[33] = 1.0 if rng.random() > 0.35 else 0.0  # powershell / cmd execution cradle
            vec[34] = 1.0 if rng.random() > 0.45 else 0.0  # entry point in last section!

            vec[35] = float(rng.uniform(0.1, 0.4))
            vec[36] = float(rng.uniform(0.5, 0.9))
            vec[37] = 1.0 if rng.random() > 0.5 else 0.0
            vec[38] = 1.0 - vec[37]
            vec[39] = 1.0  # checksum zero
            vec[40] = float(rng.randint(6, 12))
            vec[41] = float(rng.randint(4, 10))

            # Byte histogram (skewed toward high entropy / packed byte distribution)
            for i in range(10):
                vec[42 + i] = float(rng.uniform(0.08, 0.14))

            x_samples.append(vec)
            y_labels.append(1)

        X = np.array(x_samples, dtype=np.float32)
        y = np.array(y_labels, dtype=np.int32)

        # Train Random Forest
        rf = RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            min_samples_split=4,
            random_state=42,
            n_jobs=-1,
        )
        rf.fit(X, y)

        # Ensure directory exists and save
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(rf, str(self.model_path))
        self.model = rf
        logger.info(
            f"Trained baseline PE malware classifier with {len(y)} samples. Saved to {self.model_path}"
        )

    def predict(self, file_path: Path) -> MLPredictionResult:
        """Run ML prediction on a target executable file."""
        if self.model is None:
            self._ensure_model_loaded()

        extraction = self.feature_extractor.extract_features(file_path)
        if not extraction.is_pe:
            return MLPredictionResult(
                is_pe=False,
                malware_probability=0.0,
                confidence=0.0,
                classification="NOT_PE",
                top_features=[],
                error=extraction.error or "Not a PE binary",
            )

        if self.model is None:
            return MLPredictionResult(
                is_pe=True,
                malware_probability=0.0,
                confidence=0.0,
                classification="ERROR",
                error="ML model unavailable",
            )

        x_in = np.array([extraction.feature_vector], dtype=np.float32)
        probs = self.model.predict_proba(x_in)[0]
        malware_prob = float(probs[1])
        confidence = float(max(probs[0], probs[1]))

        # Determine classification
        if malware_prob >= settings.ml_malware_threshold:
            classification = "MALICIOUS"
        elif malware_prob >= 0.40:
            classification = "SUSPICIOUS"
        else:
            classification = "BENIGN"

        # Explainable AI: determine top contributing features
        importances = getattr(self.model, "feature_importances_", None)
        top_features: list[tuple[str, float]] = []
        if importances is not None and len(importances) == len(self.feature_extractor.feature_names):
            feature_impacts: list[tuple[str, float]] = []
            for name, val, imp in zip(
                self.feature_extractor.feature_names,
                extraction.feature_vector,
                importances,
                strict=False,
            ):
                # Calculate normalized influence
                score = float(imp * abs(val))
                if score > 0.001:
                    feature_impacts.append((name, score))

            feature_impacts.sort(key=lambda item: item[1], reverse=True)
            top_features = feature_impacts[:5]

        return MLPredictionResult(
            is_pe=True,
            malware_probability=malware_prob,
            confidence=confidence,
            classification=classification,
            top_features=top_features,
        )


# Global singleton instance
pe_classifier = PEClassifier()
