"""Unit tests for Phase 2 Machine Learning PE Malware Classifier."""

from pathlib import Path

from app.ml.classifier import PEClassifier, pe_classifier
from app.ml.features import PEFeatureExtractor


def test_feature_extractor_on_non_pe(tmp_path: Path) -> None:
    txt_file = tmp_path / "plain.txt"
    txt_file.write_text("Hello SentinelX test string")

    extractor = PEFeatureExtractor()
    features = extractor.extract_features(txt_file)

    assert not features.is_pe
    assert len(features.feature_vector) == len(extractor.feature_names)
    assert features.file_size > 0


def test_feature_extractor_on_pe_sample() -> None:
    pe_sample = Path("tests/fixtures/clean_sample.exe")
    assert pe_sample.exists()

    extractor = PEFeatureExtractor()
    features = extractor.extract_features(pe_sample)

    assert features.is_pe
    assert len(features.feature_vector) == len(extractor.feature_names)
    assert features.feature_dict["num_sections"] > 0
    assert "entropy_overall" in features.feature_dict


def test_pe_classifier_predict_benign() -> None:
    pe_sample = Path("tests/fixtures/clean_sample.exe")
    res = pe_classifier.predict(pe_sample)

    assert res.is_pe
    assert 0.0 <= res.malware_probability <= 1.0
    assert res.confidence >= 0.5
    assert res.classification in ("BENIGN", "SUSPICIOUS", "MALICIOUS")


def test_pe_classifier_predict_non_pe(tmp_path: Path) -> None:
    dummy = tmp_path / "script.bat"
    dummy.write_text("echo hello")

    res = pe_classifier.predict(dummy)
    assert not res.is_pe
    assert res.malware_probability == 0.0


def test_pe_classifier_bootstrap_and_retrain(tmp_path: Path) -> None:
    custom_model_path = tmp_path / "test_model.joblib"
    classifier = PEClassifier(model_path=custom_model_path)

    assert custom_model_path.exists()
    assert classifier.model is not None
