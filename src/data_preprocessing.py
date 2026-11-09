"""
data_preprocessing.py — NIST AC Dataset Loader and Feature Engineer

Responsibilities:
  1. Discover and load CSV files from data/raw/
  2. Harmonise column names to a canonical schema
  3. Handle missing values, duplicates, and type coercion
  4. Engineer derived features (delta_t, estimated_cop, runtime_hours …)
  5. Scale numeric features and persist the fitted scaler
  6. Save the processed DataFrame to data/processed/

Canonical feature columns produced (all numeric):
  supply_air_temp       – evaporator supply air temperature (°C)
  return_air_temp       – indoor return/ambient air temperature (°C)
  outdoor_ambient_temp  – outdoor dry-bulb temperature (°C)
  setpoint_temp         – thermostat set-point temperature (°C)
  power_kw              – compressor + fan electrical draw (kW)
  delta_t               – return_air_temp − supply_air_temp (°C)
  estimated_cop         – Coefficient of Performance (dimensionless)
  runtime_hours         – cumulative operating time for the record (h)
  fault_label           – categorical fault class (string); NaN = unknown
"""

from __future__ import annotations

import logging
import warnings
from pathlib import Path
from typing import Optional, List

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

warnings.filterwarnings("ignore", category=FutureWarning)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

SCALER_PATH = MODELS_DIR / "scaler.joblib"
PROCESSED_CSV_PATH = PROCESSED_DATA_DIR / "nist_features.csv"

# ---------------------------------------------------------------------------
# NIST column-name aliases → canonical names
# Different NIST files may use varying header strings; list known aliases below.
# ---------------------------------------------------------------------------
COLUMN_ALIASES: dict[str, str] = {
    # Supply / evaporator outlet air
    "supply_air_temperature": "supply_air_temp",
    "supply_temp": "supply_air_temp",
    "T_sa": "supply_air_temp",
    "Tsa": "supply_air_temp",
    "outlet_temp": "supply_air_temp",
    "discharge_temp": "supply_air_temp",
    # Return / indoor ambient
    "return_air_temperature": "return_air_temp",
    "return_temp": "return_air_temp",
    "T_ra": "return_air_temp",
    "Tra": "return_air_temp",
    "indoor_temp": "return_air_temp",
    "inlet_temp": "return_air_temp",
    "ambient_temp": "return_air_temp",
    # Outdoor
    "outdoor_temperature": "outdoor_ambient_temp",
    "outdoor_temp": "outdoor_ambient_temp",
    "outside_temp": "outdoor_ambient_temp",
    "T_oa": "outdoor_ambient_temp",
    "Toa": "outdoor_ambient_temp",
    # Setpoint
    "setpoint": "setpoint_temp",
    "T_set": "setpoint_temp",
    "thermostat_setpoint": "setpoint_temp",
    "summer_SP_temp": "setpoint_temp",
    "summer_sp_temp": "setpoint_temp",
    "winter_SP_temp": "setpoint_temp",
    # Power
    "power": "power_kw",
    "total_power": "power_kw",
    "W_total": "power_kw",
    "power_w": "power_kw",          # watts — will be converted below
    "compressor_power": "power_kw",
    "active_power": "power_kw",
    # Fault label
    "fault": "fault_label",
    "fault_type": "fault_label",
    "condition": "fault_label",
    "label": "fault_label",
    "Fault": "fault_label",
}

# NIST fault-class label normalisation
FAULT_LABEL_MAP: dict[str, str] = {
    "0": "Normal",
    "1": "Refrigerant Undercharge",
    "2": "Refrigerant Overcharge",
    "3": "Outdoor Airflow Restriction",
    "4": "Liquid Line Restriction",
    "normal": "Normal",
    "no fault": "Normal",
    "nofault": "Normal",
    "nf": "Normal",
    "undercharge": "Refrigerant Undercharge",
    "refrigerant undercharge": "Refrigerant Undercharge",
    "rc": "Refrigerant Undercharge",
    "overcharge": "Refrigerant Overcharge",
    "refrigerant overcharge": "Refrigerant Overcharge",
    "oar": "Outdoor Airflow Restriction",
    "outdoor airflow": "Outdoor Airflow Restriction",
    "outdoor airflow restriction": "Outdoor Airflow Restriction",
    "llr": "Liquid Line Restriction",
    "liquid line": "Liquid Line Restriction",
    "liquid line restriction": "Liquid Line Restriction",
}

# Columns used by ML models (must all be present after preprocessing)
FEATURE_COLUMNS: List[str] = [
    "supply_air_temp",
    "return_air_temp",
    "outdoor_ambient_temp",
    "setpoint_temp",
    "power_kw",
    "delta_t",
    "estimated_cop",
    "runtime_hours",
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_and_preprocess(
    raw_dir: Optional[Path] = None,
    save: bool = True,
    fit_scaler: bool = True,
) -> pd.DataFrame:
    """
    Full preprocessing pipeline.

    Parameters
    ----------
    raw_dir   : directory containing raw NIST CSV files; defaults to data/raw/
    save      : persist processed CSV and scaler artefacts
    fit_scaler: fit a fresh StandardScaler (True when training)

    Returns
    -------
    DataFrame with canonical feature columns + optional fault_label column.
    """
    raw_dir = raw_dir or RAW_DATA_DIR

    # 1. Discover & load -------------------------------------------------
    df = _load_csv_files(raw_dir)
    if df.empty:
        logger.warning("No CSV data found in %s. Returning empty DataFrame.", raw_dir)
        return df

    logger.info("Loaded %d rows from %s", len(df), raw_dir)

    # 2. Rename columns to canonical schema ------------------------------
    df = _harmonise_columns(df)

    # 3. Basic data quality ----------------------------------------------
    df = _clean(df)

    # 4. Unit normalisation ---------------------------------------------
    df = _fix_units(df)

    # 5. Feature engineering --------------------------------------------
    df = _engineer_features(df)

    # 6. Drop rows still missing required features ----------------------
    df = df.dropna(subset=FEATURE_COLUMNS)
    df = df.reset_index(drop=True)

    logger.info("After preprocessing: %d clean rows, columns: %s", len(df), df.columns.tolist())

    # 7. Scale -----------------------------------------------------------
    if fit_scaler:
        scaler = _fit_and_save_scaler(df[FEATURE_COLUMNS], save=save)
    else:
        scaler = _load_scaler()

    # Attach scaled copies with suffix _scaled (kept alongside originals)
    df_scaled = df.copy()
    if scaler is not None:
        df_scaled[FEATURE_COLUMNS] = scaler.transform(df[FEATURE_COLUMNS])

    # 8. Persist ---------------------------------------------------------
    if save:
        PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(PROCESSED_CSV_PATH, index=False)
        logger.info("Processed dataset saved → %s", PROCESSED_CSV_PATH)

    return df


def load_processed() -> pd.DataFrame:
    """Load the already-processed feature CSV (skips raw pipeline)."""
    if not PROCESSED_CSV_PATH.exists():
        raise FileNotFoundError(
            f"Processed data not found at {PROCESSED_CSV_PATH}. "
            "Run load_and_preprocess() first."
        )
    return pd.read_csv(PROCESSED_CSV_PATH)


def get_feature_columns() -> List[str]:
    """Return the ordered list of ML feature column names."""
    return list(FEATURE_COLUMNS)


def preprocess_single_record(record: dict) -> np.ndarray:
    """
    Scale a single live telemetry record for real-time inference.

    Parameters
    ----------
    record : dict with keys matching FEATURE_COLUMNS (at minimum)

    Returns
    -------
    2-D numpy array shaped (1, n_features), scaled.
    """
    scaler = _load_scaler()
    row = np.array([[record.get(col, 0.0) for col in FEATURE_COLUMNS]], dtype=float)
    if scaler is not None:
        row = scaler.transform(row)
    return row


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_csv_files(raw_dir: Path) -> pd.DataFrame:
    """Read all CSV and Parquet files in raw_dir and concatenate them."""
    data_files = sorted(list(raw_dir.glob("*.csv")) + list(raw_dir.glob("*.parquet")))
    if not data_files:
        logger.warning("No .csv or .parquet files found in %s", raw_dir)
        return pd.DataFrame()

    frames: List[pd.DataFrame] = []
    for f in data_files:
        try:
            if f.suffix == ".parquet":
                chunk = pd.read_parquet(f)
            else:
                chunk = pd.read_csv(f, low_memory=False)
            chunk["_source_file"] = f.name
            frames.append(chunk)
            logger.debug("Read %d rows from %s", len(chunk), f.name)
        except Exception as exc:
            logger.error("Failed to read %s: %s", f.name, exc)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


def _harmonise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns using canonical priorities without creating duplicate columns."""
    df.columns = [c.strip() for c in df.columns]

    PRIORITY = {
        "supply_air_temp": ["supply_air_temp", "outlet_temp", "discharge_temp", "supply_air_temperature", "supply_temp", "T_sa", "Tsa"],
        "return_air_temp": ["return_air_temp", "inlet_temp", "return_air_temperature", "return_temp", "indoor_temp", "ambient_temp", "T_ra", "Tra"],
        "outdoor_ambient_temp": ["outdoor_ambient_temp", "outside_temp", "outdoor_temperature", "outdoor_temp", "T_oa", "Toa"],
        "setpoint_temp": ["setpoint_temp", "summer_SP_temp", "summer_sp_temp", "winter_SP_temp", "setpoint", "T_set", "thermostat_setpoint"],
        "power_kw": ["power_kw", "active_power", "total_power", "compressor_power", "power", "W_total", "power_w"],
        "fault_label": ["fault_label", "fault", "fault_type", "condition", "label", "Fault"],
    }

    col_lower = {c.lower(): c for c in df.columns}
    rename_dict = {}
    used_sources = set()

    for canonical, candidates in PRIORITY.items():
        if canonical in df.columns:
            continue
        for cand in candidates:
            if cand in df.columns and cand not in used_sources:
                rename_dict[cand] = canonical
                used_sources.add(cand)
                break
            elif cand.lower() in col_lower and col_lower[cand.lower()] not in used_sources:
                actual_name = col_lower[cand.lower()]
                rename_dict[actual_name] = canonical
                used_sources.add(actual_name)
                break

    df = df.rename(columns=rename_dict)
    # Drop any duplicate column names if created
    df = df.loc[:, ~df.columns.duplicated()]
    return df


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates; coerce numerics; normalise fault labels; filter active states."""
    # If on_off indicator exists, filter for active operational records
    if "on_off" in df.columns:
        active_mask = (df["on_off"] == 1.0) | (df["on_off"].isna())
        df = df[active_mask]

    # Drop exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    logger.debug("Dropped %d duplicate rows", before - len(df))

    # Coerce all feature columns to numeric (non-parseable → NaN)
    numeric_candidates = [
        "supply_air_temp", "return_air_temp", "outdoor_ambient_temp",
        "setpoint_temp", "power_kw", "runtime_hours",
    ]
    for col in numeric_candidates:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Normalise fault labels
    if "fault_label" in df.columns:
        df["fault_label"] = (
            df["fault_label"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map(lambda v: FAULT_LABEL_MAP.get(v, None))
        )

    return df


def _fix_units(df: pd.DataFrame) -> pd.DataFrame:
    """Convert power from Watts to kW if the values suggest W-scale."""
    if "power_kw" in df.columns:
        col = df["power_kw"].dropna()
        if len(col) > 0 and col.median() > 100:
            # Likely in Watts — convert
            df["power_kw"] = df["power_kw"] / 1000.0
            logger.info("power_kw column converted from W to kW (median was %.1f W)", col.median())
    return df


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns: delta_t, estimated_cop, runtime_hours defaults."""
    # Delta-T: temperature split across evaporator
    if "return_air_temp" in df.columns and "supply_air_temp" in df.columns:
        df["delta_t"] = df["return_air_temp"] - df["supply_air_temp"]

    # Estimated COP: rough proxy — thermal load / electrical input
    # COP ≈ delta_t * airflow_factor / power; without airflow we use a heuristic
    if "delta_t" in df.columns and "power_kw" in df.columns:
        # Avoid divide-by-zero; COP capped at physically reasonable [0.5, 8.0]
        df["estimated_cop"] = np.where(
            df["power_kw"] > 0.1,
            np.clip(df["delta_t"] * 0.35 / df["power_kw"].replace(0, np.nan), 0.5, 8.0),
            np.nan,
        )

    # Setpoint: fill missing with return_air_temp (assumption)
    if "setpoint_temp" not in df.columns:
        df["setpoint_temp"] = df.get("return_air_temp", 23.0)
    df["setpoint_temp"] = df["setpoint_temp"].fillna(23.0)

    # Runtime hours: if not present in raw data, default to NaN then impute as 1.0
    if "runtime_hours" not in df.columns:
        df["runtime_hours"] = 1.0
    df["runtime_hours"] = df["runtime_hours"].fillna(1.0)

    # Clip physically implausible values
    if "supply_air_temp" in df.columns:
        df["supply_air_temp"] = df["supply_air_temp"].clip(-10, 40)
    if "return_air_temp" in df.columns:
        df["return_air_temp"] = df["return_air_temp"].clip(10, 50)
    if "outdoor_ambient_temp" in df.columns:
        df["outdoor_ambient_temp"] = df["outdoor_ambient_temp"].clip(-20, 55)
    if "power_kw" in df.columns:
        df["power_kw"] = df["power_kw"].clip(0.0, 10.0)

    return df


def _fit_and_save_scaler(features_df: pd.DataFrame, save: bool) -> StandardScaler:
    scaler = StandardScaler()
    scaler.fit(features_df)
    if save:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(scaler, SCALER_PATH)
        logger.info("Scaler saved → %s", SCALER_PATH)
    return scaler


def _load_scaler() -> Optional[StandardScaler]:
    if SCALER_PATH.exists():
        return joblib.load(SCALER_PATH)
    logger.warning("Scaler not found at %s — returning None", SCALER_PATH)
    return None

