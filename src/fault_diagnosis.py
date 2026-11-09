"""
fault_diagnosis.py — Random Forest Fault Classifier

Wraps scikit-learn's RandomForestClassifier with:
  - Multi-class training (5 NIST fault categories)
  - LabelEncoder for string class labels
  - Fit / save / load workflow
  - Single-record and batch inference APIs
  - Full evaluation suite (accuracy, classification report, confusion matrix)

Fault classes (NIST-aligned):
  0 — Normal
  1 — Refrigerant Undercharge
  2 — Refrigerant Overcharge
  3 — Outdoor Airflow Restriction
  4 — Liquid Line Restriction
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
import joblib

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "random_forest_classifier.joblib"
ENCODER_PATH = MODELS_DIR / "label_encoder.joblib"

# Fault severity weights used by health_score.py
FAULT_SEVERITY: Dict[str, int] = {
    "Normal": 0,
    "Refrigerant Undercharge": 35,
    "Refrigerant Overcharge": 25,
    "Outdoor Airflow Restriction": 20,
    "Liquid Line Restriction": 30,
}

# Maintenance recommendations per fault class
FAULT_RECOMMENDATIONS: Dict[str, str] = {
    "Normal": "No action required. Continue routine maintenance schedule.",
    "Refrigerant Undercharge": (
        "Inspect refrigerant charge level. "
        "Check for leaks in refrigerant lines and service valves. "
        "Contact certified HVAC technician for refrigerant top-up."
    ),
    "Refrigerant Overcharge": (
        "Refrigerant charge is above rated capacity. "
        "Risk of liquid slugging and compressor damage. "
        "Contact certified HVAC technician to bleed excess refrigerant."
    ),
    "Outdoor Airflow Restriction": (
        "Clean outdoor condenser coil fins and fan blades. "
        "Ensure 60 cm clearance around outdoor unit. "
        "Check for blocked air intake or recirculation."
    ),
    "Liquid Line Restriction": (
        "Inspect liquid line filter-drier for blockage or saturation. "
        "Check expansion valve / capillary tube for ice or debris. "
        "Replace filter-drier if pressure drop is confirmed."
    ),
}


class FaultDiagnoser:
    """
    Random Forest multi-class fault classifier for NIST AC fault categories.

    Usage (training)
    ----------------
    diagnoser = FaultDiagnoser()
    diagnoser.fit(X_train, y_train)   # y_train: array of string class labels
    diagnoser.save()

    Usage (inference)
    -----------------
    diagnoser = FaultDiagnoser.load()
    result = diagnoser.predict_single(feature_vector)
    """

    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: Optional[int] = None,
        min_samples_leaf: int = 2,
        random_state: int = 42,
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.random_state = random_state
        self._model: Optional[RandomForestClassifier] = None
        self._encoder: Optional[LabelEncoder] = None

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def fit(
        self,
        X: np.ndarray | pd.DataFrame,
        y: np.ndarray | pd.Series,
        eval_split: float = 0.20,
    ) -> Dict:
        """
        Fit the Random Forest classifier.

        Parameters
        ----------
        X          : Feature matrix (n_samples, n_features)
        y          : Target fault labels — string class names
        eval_split : Fraction held out for evaluation logging

        Returns
        -------
        dict with train_accuracy, test_accuracy, and classification_report string
        """
        X = _to_array(X)
        y = np.array(y, dtype=str)

        # Encode string labels → integers
        self._encoder = LabelEncoder()
        y_enc = self._encoder.fit_transform(y)

        logger.info(
            "Training Random Forest on %d samples, %d features, %d classes: %s",
            X.shape[0], X.shape[1],
            len(self._encoder.classes_), list(self._encoder.classes_),
        )

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_enc, test_size=eval_split, random_state=self.random_state, stratify=y_enc
        )

        self._model = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_leaf=self.min_samples_leaf,
            class_weight="balanced",
            random_state=self.random_state,
            n_jobs=-1,
        )
        self._model.fit(X_train, y_train)

        # Evaluate on held-out split
        y_pred_test = self._model.predict(X_test)
        test_acc = accuracy_score(y_test, y_pred_test)
        train_acc = accuracy_score(y_train, self._model.predict(X_train))
        report = classification_report(
            y_test, y_pred_test,
            target_names=self._encoder.classes_,
            zero_division=0,
        )
        logger.info(
            "Random Forest — Train acc: %.3f | Test acc: %.3f\n%s",
            train_acc, test_acc, report,
        )
        return {
            "train_accuracy": train_acc,
            "test_accuracy": test_acc,
            "classification_report": report,
            "classes": list(self._encoder.classes_),
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, model_path: Optional[Path] = None, encoder_path: Optional[Path] = None):
        model_path = model_path or MODEL_PATH
        encoder_path = encoder_path or ENCODER_PATH
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._model, model_path)
        joblib.dump(self._encoder, encoder_path)
        logger.info("Random Forest saved → %s", model_path)
        logger.info("LabelEncoder saved  → %s", encoder_path)

    @classmethod
    def load(
        cls,
        model_path: Optional[Path] = None,
        encoder_path: Optional[Path] = None,
    ) -> "FaultDiagnoser":
        model_path = model_path or MODEL_PATH
        encoder_path = encoder_path or ENCODER_PATH
        if not model_path.exists():
            raise FileNotFoundError(
                f"Random Forest model not found at {model_path}. "
                "Run train_models.py first."
            )
        if not encoder_path.exists():
            raise FileNotFoundError(
                f"LabelEncoder not found at {encoder_path}. "
                "Run train_models.py first."
            )
        instance = cls()
        instance._model = joblib.load(model_path)
        instance._encoder = joblib.load(encoder_path)
        logger.info("Random Forest loaded from %s", model_path)
        return instance

    @staticmethod
    def is_trained() -> bool:
        return MODEL_PATH.exists() and ENCODER_PATH.exists()

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict_single(self, feature_vector: np.ndarray) -> Dict:
        """
        Classify a single (1 x n_features) sample.

        Returns
        -------
        dict with:
          predicted_fault   : str (class name)
          fault_probability : float (confidence for predicted class)
          all_probabilities : dict {class_name: probability}
          severity_score    : int (0-40 health penalty from FAULT_SEVERITY)
          recommendation    : str (maintenance advisory)
        """
        self._check_fitted()
        feature_vector = _to_array(feature_vector).reshape(1, -1)
        encoded_pred = self._model.predict(feature_vector)[0]
        proba = self._model.predict_proba(feature_vector)[0]

        predicted_fault = self._encoder.inverse_transform([encoded_pred])[0]
        fault_probability = float(proba[encoded_pred])

        all_probs = {
            self._encoder.inverse_transform([i])[0]: float(p)
            for i, p in enumerate(proba)
        }

        return {
            "predicted_fault": predicted_fault,
            "fault_probability": fault_probability,
            "all_probabilities": all_probs,
            "severity_score": FAULT_SEVERITY.get(predicted_fault, 0),
            "recommendation": FAULT_RECOMMENDATIONS.get(predicted_fault, ""),
        }

    def predict_batch(self, X: np.ndarray | pd.DataFrame) -> pd.DataFrame:
        """
        Classify a batch of samples.

        Returns
        -------
        DataFrame with columns:
          predicted_fault, fault_probability, severity_score, recommendation
        """
        self._check_fitted()
        X = _to_array(X)
        encoded_preds = self._model.predict(X)
        probas = self._model.predict_proba(X)

        predicted_faults = self._encoder.inverse_transform(encoded_preds)
        fault_probabilities = probas[np.arange(len(X)), encoded_preds]

        return pd.DataFrame({
            "predicted_fault": predicted_faults,
            "fault_probability": fault_probabilities.round(4),
            "severity_score": [FAULT_SEVERITY.get(f, 0) for f in predicted_faults],
            "recommendation": [FAULT_RECOMMENDATIONS.get(f, "") for f in predicted_faults],
        })

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(
        self,
        X: np.ndarray | pd.DataFrame,
        y_true: np.ndarray | pd.Series,
    ) -> Dict:
        """
        Full evaluation suite.

        Returns
        -------
        dict with accuracy, classification_report, confusion_matrix, feature_importances
        """
        self._check_fitted()
        X = _to_array(X)
        y_true_enc = self._encoder.transform(np.array(y_true, dtype=str))
        y_pred_enc = self._model.predict(X)

        acc = accuracy_score(y_true_enc, y_pred_enc)
        report = classification_report(
            y_true_enc, y_pred_enc,
            target_names=self._encoder.classes_,
            zero_division=0,
        )
        cm = confusion_matrix(y_true_enc, y_pred_enc)
        fi = dict(zip(
            [f"feature_{i}" for i in range(X.shape[1])],
            self._model.feature_importances_.round(4),
        ))

        logger.info("Fault Diagnosis Evaluation — Accuracy: %.3f\n%s", acc, report)
        return {
            "accuracy": acc,
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
            "feature_importances": fi,
            "classes": list(self._encoder.classes_),
        }

    def cross_validate(self, X: np.ndarray | pd.DataFrame, y: np.ndarray | pd.Series, cv: int = 5) -> Dict:
        """k-fold cross-validation accuracy."""
        self._check_fitted()
        X = _to_array(X)
        y_enc = self._encoder.transform(np.array(y, dtype=str))
        scores = cross_val_score(self._model, X, y_enc, cv=cv, scoring="accuracy", n_jobs=-1)
        logger.info(
            "Cross-validation (%d-fold) accuracy: %.3f ± %.3f",
            cv, scores.mean(), scores.std(),
        )
        return {"cv_scores": scores.tolist(), "mean": float(scores.mean()), "std": float(scores.std())}

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def classes(self) -> List[str]:
        self._check_fitted()
        return list(self._encoder.classes_)

    @property
    def feature_importances(self) -> np.ndarray:
        self._check_fitted()
        return self._model.feature_importances_

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _check_fitted(self):
        if self._model is None or self._encoder is None:
            raise RuntimeError(
                "FaultDiagnoser is not fitted. Call .fit() or .load() first."
            )


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------

def diagnose_realtime_record(record: dict, feature_columns: list) -> Dict:
    """
    Diagnose a single live telemetry record for dashboard use.

    Parameters
    ----------
    record          : dict of feature_name → value
    feature_columns : ordered list matching training features

    Returns
    -------
    dict from FaultDiagnoser.predict_single()
    """
    diagnoser = FaultDiagnoser.load()
    vec = np.array([[record.get(col, 0.0) for col in feature_columns]], dtype=float)
    return diagnoser.predict_single(vec)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_array(X) -> np.ndarray:
    if isinstance(X, pd.DataFrame):
        return X.values.astype(float)
    return np.array(X, dtype=float)

