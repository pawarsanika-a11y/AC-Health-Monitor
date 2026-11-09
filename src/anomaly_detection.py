"""
anomaly_detection.py — Isolation Forest Anomaly Detector

Wraps scikit-learn's IsolationForest with:
  - Fit / save / load workflow
  - Anomaly score normalisation to [0.0, 1.0] confidence scale
  - Single-record and batch inference APIs
  - Evaluation helper (against available fault labels)

Anomaly confidence interpretation:
  < 0.30  → Normal Operation
  0.30–0.65 → Warning Anomaly
  > 0.65  → Critical Anomaly
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report
import joblib

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "isolation_forest.joblib"

# Thresholds for label assignment
WARNING_THRESHOLD = 0.30
CRITICAL_THRESHOLD = 0.65


class AnomalyDetector:
    """
    Isolation Forest anomaly detector for AC operating data.

    Usage (training)
    ----------------
    detector = AnomalyDetector()
    detector.fit(X_train)          # X_train: np.ndarray or pd.DataFrame
    detector.save()

    Usage (inference)
    -----------------
    detector = AnomalyDetector.load()
    confidence, label = detector.predict_single(feature_vector)
    """

    def __init__(
        self,
        n_estimators: int = 100,
        contamination: float = 0.10,
        max_samples: str | int = "auto",
        random_state: int = 42,
    ):
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.max_samples = max_samples
        self.random_state = random_state
        self._model: Optional[IsolationForest] = None

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def fit(self, X: np.ndarray | pd.DataFrame) -> "AnomalyDetector":
        """
        Fit the Isolation Forest on normal (or mixed) operating data.

        Parameters
        ----------
        X : Feature matrix — shape (n_samples, n_features).
            Use FEATURE_COLUMNS from data_preprocessing.py.

        Returns
        -------
        self (for chaining)
        """
        X = _to_array(X)
        logger.info(
            "Training Isolation Forest on %d samples (%d features), "
            "contamination=%.2f",
            X.shape[0], X.shape[1], self.contamination,
        )
        self._model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            max_samples=self.max_samples,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self._model.fit(X)
        logger.info("Isolation Forest training complete.")
        return self

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: Optional[Path] = None) -> Path:
        """Persist the fitted model to disk."""
        path = path or MODEL_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._model, path)
        logger.info("Isolation Forest model saved → %s", path)
        return path

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "AnomalyDetector":
        """Load a saved Isolation Forest from disk."""
        path = path or MODEL_PATH
        if not path.exists():
            raise FileNotFoundError(
                f"Isolation Forest model not found at {path}. "
                "Run train_models.py first."
            )
        instance = cls()
        instance._model = joblib.load(path)
        logger.info("Isolation Forest loaded from %s", path)
        return instance

    @staticmethod
    def is_trained() -> bool:
        """Return True if a saved model file exists."""
        return MODEL_PATH.exists()

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict_single(self, feature_vector: np.ndarray) -> Tuple[float, str]:
        """
        Score a single (1 x n_features) sample.

        Returns
        -------
        confidence : float in [0.0, 1.0]  — higher = more anomalous
        label      : "Normal Operation" | "Warning Anomaly" | "Critical Anomaly"
        """
        self._check_fitted()
        feature_vector = _to_array(feature_vector).reshape(1, -1)
        confidence = self._score_to_confidence(feature_vector)[0]
        label = _confidence_to_label(confidence)
        return float(confidence), label

    def predict_batch(self, X: np.ndarray | pd.DataFrame) -> pd.DataFrame:
        """
        Score a batch of samples.

        Returns
        -------
        DataFrame with columns:
          anomaly_confidence : float [0, 1]
          anomaly_status     : str label
          anomaly_flag       : int (1 = anomaly, 0 = normal)
        """
        self._check_fitted()
        X = _to_array(X)
        confidences = self._score_to_confidence(X)
        labels = [_confidence_to_label(c) for c in confidences]
        flags = [1 if c >= WARNING_THRESHOLD else 0 for c in confidences]
        return pd.DataFrame({
            "anomaly_confidence": confidences,
            "anomaly_status": labels,
            "anomaly_flag": flags,
        })

    # ------------------------------------------------------------------
    # Evaluation (optional — requires fault labels)
    # ------------------------------------------------------------------

    def evaluate(self, X: np.ndarray | pd.DataFrame, y_true_fault_labels: pd.Series) -> str:
        """
        Compare Isolation Forest predictions against available ground-truth
        fault labels (treats non-'Normal' as anomaly).

        Returns a classification report string.
        """
        self._check_fitted()
        results = self.predict_batch(X)
        predicted_binary = results["anomaly_flag"].values
        # True: 0 = Normal, 1 = any fault
        true_binary = (y_true_fault_labels != "Normal").astype(int).values
        report = classification_report(
            true_binary, predicted_binary,
            target_names=["Normal", "Anomaly"],
            zero_division=0,
        )
        logger.info("Anomaly Detection Evaluation:\n%s", report)
        return report

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _check_fitted(self):
        if self._model is None:
            raise RuntimeError(
                "AnomalyDetector is not fitted. Call .fit() or .load() first."
            )

    def _score_to_confidence(self, X: np.ndarray) -> np.ndarray:
        """
        Convert raw Isolation Forest decision_function scores to [0, 1] confidence.

        IsolationForest.decision_function returns values roughly in [-0.5, 0.5]:
          - Positive   → inlier (normal)
          - Negative   → outlier (anomaly)
        We invert and min-max scale to [0, 1] where 1 = most anomalous.
        """
        raw_scores = self._model.decision_function(X)   # higher = more normal
        # Invert so higher = more anomalous, then clip to typical range
        inverted = -raw_scores
        # Normalise using fitted training score extremes (approximation)
        confidence = np.clip((inverted + 0.5) / 1.0, 0.0, 1.0)
        return confidence


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------

def score_realtime_record(record: dict, feature_columns: list) -> Tuple[float, str]:
    """
    Score a single telemetry record dict for dashboard real-time use.

    Parameters
    ----------
    record          : dict of feature_name → value
    feature_columns : ordered list of feature column names

    Returns
    -------
    (confidence: float, label: str)
    """
    detector = AnomalyDetector.load()
    vec = np.array([[record.get(col, 0.0) for col in feature_columns]], dtype=float)
    return detector.predict_single(vec)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_array(X) -> np.ndarray:
    if isinstance(X, pd.DataFrame):
        return X.values.astype(float)
    return np.array(X, dtype=float)


def _confidence_to_label(confidence: float) -> str:
    if confidence < WARNING_THRESHOLD:
        return "Normal Operation"
    elif confidence < CRITICAL_THRESHOLD:
        return "Warning Anomaly"
    else:
        return "Critical Anomaly"

