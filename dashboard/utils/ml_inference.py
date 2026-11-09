"""
ml_inference.py — ML Model Loader and Real-Time Inference Bridge

This module is the single integration point between the Streamlit dashboard
and the trained ML models. It provides:

  - Model availability detection (graceful degradation to demo mode if untrained)
  - Cached model loading (using st.cache_resource for Streamlit)
  - Full ML inference pipeline for real-time telemetry records
  - Feature vector construction from ACSystemState or raw dicts

Usage in dashboard:
    from dashboard.utils.ml_inference import run_inference, models_available

    if models_available():
        result = run_inference(state)   # returns MLInferenceResult
    else:
        # fall back to simulated preset data
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "models"


# ---------------------------------------------------------------------------
# Output data class
# ---------------------------------------------------------------------------

@dataclass
class MLInferenceResult:
    """Full real-time ML inference output."""
    # Anomaly Detection (Isolation Forest)
    anomaly_confidence: float          # [0.0, 1.0]
    anomaly_status: str                # "Normal Operation" | "Warning Anomaly" | "Critical Anomaly"
    # Fault Diagnosis (Random Forest) — None if model not trained
    predicted_fault: Optional[str]
    fault_probability: Optional[float]
    all_fault_probabilities: Optional[dict]
    fault_severity: int
    recommendation: str
    # Health Score
    health_score: int
    health_condition: str
    anomaly_penalty: float
    fault_penalty: float
    efficiency_penalty: float
    delta_t_penalty: float
    # Input echo
    estimated_cop: float
    delta_t: float
    # Source
    source: str                        # "ml_model" | "demo_fallback"


# ---------------------------------------------------------------------------
# Model availability check
# ---------------------------------------------------------------------------

def models_available() -> bool:
    """
    Return True if at minimum the Isolation Forest model is present on disk.
    Random Forest is optional (not all NIST files have fault labels).
    """
    if_path = MODELS_DIR / "isolation_forest.joblib"
    return if_path.exists()


def fault_model_available() -> bool:
    """Return True if the Random Forest fault classifier is present."""
    rf_path = MODELS_DIR / "random_forest_classifier.joblib"
    enc_path = MODELS_DIR / "label_encoder.joblib"
    return rf_path.exists() and enc_path.exists()


# ---------------------------------------------------------------------------
# Cached model loading (lazy, Streamlit-compatible)
# ---------------------------------------------------------------------------

def _load_anomaly_detector():
    """Load and cache the Isolation Forest model."""
    try:
        from src.anomaly_detection import AnomalyDetector
        return AnomalyDetector.load()
    except Exception as exc:
        logger.error("Failed to load AnomalyDetector: %s", exc)
        return None


def _load_fault_diagnoser():
    """Load and cache the Random Forest model (returns None if unavailable)."""
    if not fault_model_available():
        return None
    try:
        from src.fault_diagnosis import FaultDiagnoser
        return FaultDiagnoser.load()
    except Exception as exc:
        logger.error("Failed to load FaultDiagnoser: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Feature vector construction
# ---------------------------------------------------------------------------

FEATURE_COLUMNS = [
    "supply_air_temp",
    "return_air_temp",
    "outdoor_ambient_temp",
    "setpoint_temp",
    "power_kw",
    "delta_t",
    "estimated_cop",
    "runtime_hours",
]


def build_feature_vector(state_or_dict) -> np.ndarray:
    """
    Convert an ACSystemState object or plain dict into a feature numpy array.

    Accepts both dataclass objects (with attribute access) and dicts.
    """
    def _get(key, default=0.0):
        if hasattr(state_or_dict, key):
            return float(getattr(state_or_dict, key) or default)
        return float(state_or_dict.get(key, default) or default)

    vec = np.array([[
        _get("supply_air_temp"),
        _get("return_air_temp"),
        _get("outdoor_ambient_temp"),
        _get("setpoint_temp"),
        _get("power_kw"),
        _get("delta_t"),
        _get("estimated_cop"),
        _get("cycle_runtime_hours", 1.0),   # maps to runtime_hours
    ]], dtype=float)
    return vec


# ---------------------------------------------------------------------------
# Main inference pipeline
# ---------------------------------------------------------------------------

def run_inference(state_or_dict) -> MLInferenceResult:
    """
    Run the full ML inference pipeline on a telemetry record.

    Parameters
    ----------
    state_or_dict : ACSystemState dataclass or dict with telemetry fields

    Returns
    -------
    MLInferenceResult with all predictions and health score.
    Falls back to demo_fallback source if models are unavailable.
    """
    if not models_available():
        return _demo_fallback(state_or_dict)

    feature_vec = build_feature_vector(state_or_dict)

    # 1. Anomaly Detection
    detector = _load_anomaly_detector()
    if detector is None:
        return _demo_fallback(state_or_dict)

    try:
        anomaly_confidence, anomaly_status = detector.predict_single(feature_vec)
    except Exception as exc:
        logger.error("Anomaly detection failed: %s", exc)
        return _demo_fallback(state_or_dict)

    # 2. Fault Diagnosis (optional)
    diagnoser = _load_fault_diagnoser()
    if diagnoser is not None:
        try:
            fault_result = diagnoser.predict_single(feature_vec)
            predicted_fault = fault_result["predicted_fault"]
            fault_probability = fault_result["fault_probability"]
            all_probs = fault_result["all_probabilities"]
            fault_severity = fault_result["severity_score"]
            recommendation = fault_result["recommendation"]
        except Exception as exc:
            logger.error("Fault diagnosis failed: %s", exc)
            predicted_fault = None
            fault_probability = None
            all_probs = None
            fault_severity = 0
            recommendation = "Fault model unavailable."
    else:
        predicted_fault = None
        fault_probability = None
        all_probs = None
        fault_severity = 0
        recommendation = "Fault diagnosis model not yet trained."

    # 3. Health Score
    from src.health_score import calculate_health_score
    def _get(key, default=0.0):
        if hasattr(state_or_dict, key):
            return float(getattr(state_or_dict, key) or default)
        return float(state_or_dict.get(key, default) or default)

    health = calculate_health_score(
        anomaly_confidence=anomaly_confidence,
        anomaly_status=anomaly_status,
        predicted_fault=predicted_fault or "Normal",
        fault_probability=fault_probability or 0.0,
        fault_severity=fault_severity,
        estimated_cop=_get("estimated_cop"),
        delta_t=_get("delta_t"),
    )

    return MLInferenceResult(
        anomaly_confidence=anomaly_confidence,
        anomaly_status=anomaly_status,
        predicted_fault=predicted_fault,
        fault_probability=fault_probability,
        all_fault_probabilities=all_probs,
        fault_severity=fault_severity,
        recommendation=recommendation,
        health_score=health.health_score,
        health_condition=health.health_condition,
        anomaly_penalty=health.anomaly_penalty,
        fault_penalty=health.fault_penalty,
        efficiency_penalty=health.efficiency_penalty,
        delta_t_penalty=health.delta_t_penalty,
        estimated_cop=_get("estimated_cop"),
        delta_t=_get("delta_t"),
        source="ml_model",
    )


def _demo_fallback(state_or_dict) -> MLInferenceResult:
    """Return a placeholder result sourced from the preset scenario state."""
    def _get(key, default=0.0):
        if hasattr(state_or_dict, key):
            return float(getattr(state_or_dict, key) or default)
        return float(state_or_dict.get(key, default) or default)

    def _gets(key, default=""):
        if hasattr(state_or_dict, key):
            return str(getattr(state_or_dict, key) or default)
        return str(state_or_dict.get(key, default) or default)

    return MLInferenceResult(
        anomaly_confidence=_get("anomaly_confidence"),
        anomaly_status=_gets("anomaly_status", "Normal Operation"),
        predicted_fault=None,
        fault_probability=None,
        all_fault_probabilities=None,
        fault_severity=0,
        recommendation="Train models using src/train_models.py for real fault diagnosis.",
        health_score=int(_get("health_score", 85)),
        health_condition=_gets("health_condition", "Healthy"),
        anomaly_penalty=_get("anomaly_confidence") * 30,
        fault_penalty=0.0,
        efficiency_penalty=max(0, (3.5 - _get("estimated_cop")) / 3.5 * 20),
        delta_t_penalty=max(0, (10 - _get("delta_t")) / 7 * 10),
        estimated_cop=_get("estimated_cop"),
        delta_t=_get("delta_t"),
        source="demo_fallback",
    )

