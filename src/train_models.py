"""
train_models.py — End-to-End ML Training Pipeline

Run this script after placing NIST CSV files in data/raw/ to:
  1. Load and preprocess the NIST AC dataset
  2. Train and save the Isolation Forest anomaly detector
  3. Train and save the Random Forest fault classifier (if fault labels exist)
  4. Print training metrics and model save paths

Usage
-----
  python src/train_models.py

Options (passed as environment variables or edited below):
  CONTAMINATION   : Isolation Forest contamination ratio (default 0.10)
  RF_ESTIMATORS   : Random Forest n_estimators (default 200)
  EVAL_SPLIT      : Train/test split fraction (default 0.20)
"""

from __future__ import annotations

import logging
import sys
import os
from pathlib import Path

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd

from src.data_preprocessing import (
    load_and_preprocess,
    get_feature_columns,
    MODELS_DIR,
    RAW_DATA_DIR,
)
from src.anomaly_detection import AnomalyDetector
from src.fault_diagnosis import FaultDiagnoser

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("train_models")

# ---------------------------------------------------------------------------
# Config (override via env vars or edit directly)
# ---------------------------------------------------------------------------
CONTAMINATION = float(os.environ.get("CONTAMINATION", "0.10"))
RF_ESTIMATORS = int(os.environ.get("RF_ESTIMATORS", "200"))
EVAL_SPLIT = float(os.environ.get("EVAL_SPLIT", "0.20"))


def main():
    logger.info("=" * 60)
    logger.info("AI-AC-Health-Monitor — Model Training Pipeline")
    logger.info("=" * 60)

    # ------------------------------------------------------------------
    # Step 1: Check data availability
    # ------------------------------------------------------------------
    data_files = sorted(list(RAW_DATA_DIR.glob("*.csv")) + list(RAW_DATA_DIR.glob("*.parquet")))
    if not data_files:
        logger.error(
            "No CSV or Parquet files found in %s\n"
            "Please download the NIST AC fault dataset and place the files there.\n"
            "See README.md for dataset download instructions.",
            RAW_DATA_DIR,
        )
        sys.exit(1)

    logger.info("Found %d raw data file(s): %s", len(data_files), [f.name for f in data_files])

    # ------------------------------------------------------------------
    # Step 2: Preprocess
    # ------------------------------------------------------------------
    logger.info("\n[Step 1/4] Loading and preprocessing dataset ...")
    df = load_and_preprocess(save=True, fit_scaler=True)

    if df.empty:
        logger.error("Preprocessing returned an empty DataFrame. Check your CSV files.")
        sys.exit(1)

    logger.info("Processed dataset: %d rows × %d columns", df.shape[0], df.shape[1])

    feature_cols = get_feature_columns()
    X = df[feature_cols].values

    # ------------------------------------------------------------------
    # Step 3: Train Isolation Forest
    # ------------------------------------------------------------------
    logger.info("\n[Step 2/4] Training Isolation Forest (anomaly detection) ...")
    detector = AnomalyDetector(contamination=CONTAMINATION)
    detector.fit(X)
    model_path = detector.save()
    logger.info("Isolation Forest saved → %s", model_path)

    # Optional evaluation against fault labels
    if "fault_label" in df.columns:
        y_fault = df["fault_label"].fillna("Normal")
        report = detector.evaluate(X, y_fault)
        logger.info("Anomaly Detection (vs fault labels):\n%s", report)

    # ------------------------------------------------------------------
    # Step 4: Train Random Forest (only if fault labels exist)
    # ------------------------------------------------------------------
    if "fault_label" not in df.columns or df["fault_label"].isna().all():
        logger.warning(
            "\n[Step 3/4] SKIP — No fault_label column found in dataset.\n"
            "Random Forest fault classifier will not be trained.\n"
            "Dashboard will use anomaly scores only for health assessment."
        )
        rf_trained = False
    else:
        logger.info("\n[Step 3/4] Training Random Forest (fault diagnosis) ...")
        y_fault = df["fault_label"].fillna("Normal")

        # Drop rows where fault label is NaN (keep only labelled rows for RF)
        mask = df["fault_label"].notna()
        X_rf = df.loc[mask, feature_cols].values
        y_rf = df.loc[mask, "fault_label"].values

        label_counts = pd.Series(y_rf).value_counts()
        logger.info("Fault label distribution:\n%s", label_counts.to_string())

        diagnoser = FaultDiagnoser(n_estimators=RF_ESTIMATORS)
        metrics = diagnoser.fit(X_rf, y_rf, eval_split=EVAL_SPLIT)
        diagnoser.save()

        logger.info(
            "Random Forest — Train Acc: %.3f | Test Acc: %.3f",
            metrics["train_accuracy"],
            metrics["test_accuracy"],
        )
        logger.info("Classification Report:\n%s", metrics["classification_report"])
        rf_trained = True

    # ------------------------------------------------------------------
    # Step 5: Summary
    # ------------------------------------------------------------------
    logger.info("\n[Step 4/4] Training Complete.")
    logger.info("Models directory: %s", MODELS_DIR)
    for model_file in sorted(MODELS_DIR.glob("*.joblib")):
        size_kb = model_file.stat().st_size / 1024
        logger.info("  %-45s  %.1f KB", model_file.name, size_kb)

    logger.info("\n✅ Ready. Launch the dashboard with:")
    logger.info("   streamlit run dashboard/app.py")
    if not rf_trained:
        logger.info(
            "\n⚠  Fault diagnosis is unavailable without labelled data.\n"
            "   The dashboard will display anomaly scores and health estimates only."
        )


if __name__ == "__main__":
    main()

