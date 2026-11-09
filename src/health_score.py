"""
health_score.py — AC Health Score Calculator

Computes a composite health score (0–100) for the monitored AC unit based on:
  1. Anomaly confidence (from Isolation Forest)        → penalty 0–30
  2. Fault severity    (from Random Forest classifier) → penalty 0–40
  3. COP efficiency deviation                          → penalty 0–20
  4. Thermal Delta-T degradation                       → penalty 0–10

Score interpretation (matches DESIGN.md):
  80–100 → Healthy
  60–79  → Moderate
  40–59  → Needs Inspection
  0–39   → Poor Condition
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Optional


# ---------------------------------------------------------------------------
# Reference constants (tunable for target AC class)
# ---------------------------------------------------------------------------

OPTIMAL_COP = 3.5          # Healthy inverter split AC coefficient of performance
OPTIMAL_DELTA_T = 10.0     # Healthy evaporator temperature split (°C)
MIN_DELTA_T = 3.0          # Delta-T below which maximum penalty applied


# ---------------------------------------------------------------------------
# Data class for structured output
# ---------------------------------------------------------------------------

@dataclass
class HealthResult:
    """Full health assessment result."""
    health_score: int
    health_condition: Literal["Healthy", "Moderate", "Needs Inspection", "Poor Condition"]
    anomaly_penalty: float
    fault_penalty: float
    efficiency_penalty: float
    delta_t_penalty: float
    total_penalty: float
    # Carry-through inputs for dashboard display
    anomaly_confidence: float
    anomaly_status: str
    predicted_fault: str
    fault_probability: float
    estimated_cop: float
    delta_t: float


# ---------------------------------------------------------------------------
# Main calculator
# ---------------------------------------------------------------------------

def calculate_health_score(
    anomaly_confidence: float,
    anomaly_status: str,
    predicted_fault: str,
    fault_probability: float,
    fault_severity: int,
    estimated_cop: float,
    delta_t: float,
) -> HealthResult:
    """
    Compute the AC health score.

    Parameters
    ----------
    anomaly_confidence : float [0.0, 1.0] — higher = more anomalous (IF output)
    anomaly_status     : str — "Normal Operation" | "Warning Anomaly" | "Critical Anomaly"
    predicted_fault    : str — fault class name from Random Forest
    fault_probability  : float [0.0, 1.0] — model confidence in fault prediction
    fault_severity     : int [0, 40] — from FAULT_SEVERITY lookup table
    estimated_cop      : float — Coefficient of Performance estimate
    delta_t            : float — evaporator temperature split (°C)

    Returns
    -------
    HealthResult dataclass
    """
    # 1. Anomaly penalty: scale linearly with confidence (max 30 pts)
    anomaly_penalty = min(30.0, anomaly_confidence * 30.0)

    # 2. Fault penalty: severity weighted by model confidence (max 40 pts)
    if predicted_fault == "Normal":
        fault_penalty = 0.0
    else:
        fault_penalty = min(40.0, fault_severity * fault_probability)

    # 3. COP efficiency penalty: deviation from optimal (max 20 pts)
    if estimated_cop <= 0 or estimated_cop != estimated_cop:  # guard NaN
        efficiency_penalty = 10.0  # moderate penalty when COP unknown
    else:
        cop_ratio = max(0.0, (OPTIMAL_COP - estimated_cop) / OPTIMAL_COP)
        efficiency_penalty = min(20.0, cop_ratio * 20.0)

    # 4. Delta-T penalty: low thermal split degrades score (max 10 pts)
    if delta_t >= OPTIMAL_DELTA_T:
        delta_t_penalty = 0.0
    elif delta_t <= MIN_DELTA_T:
        delta_t_penalty = 10.0
    else:
        # Linear interpolation between MIN_DELTA_T and OPTIMAL_DELTA_T
        span = OPTIMAL_DELTA_T - MIN_DELTA_T
        delta_t_penalty = 10.0 * (1.0 - (delta_t - MIN_DELTA_T) / span)

    total_penalty = anomaly_penalty + fault_penalty + efficiency_penalty + delta_t_penalty
    raw_score = 100.0 - total_penalty
    health_score = int(max(0, min(100, round(raw_score))))
    health_condition = score_to_condition(health_score)

    return HealthResult(
        health_score=health_score,
        health_condition=health_condition,
        anomaly_penalty=round(anomaly_penalty, 2),
        fault_penalty=round(fault_penalty, 2),
        efficiency_penalty=round(efficiency_penalty, 2),
        delta_t_penalty=round(delta_t_penalty, 2),
        total_penalty=round(total_penalty, 2),
        anomaly_confidence=anomaly_confidence,
        anomaly_status=anomaly_status,
        predicted_fault=predicted_fault,
        fault_probability=fault_probability,
        estimated_cop=estimated_cop,
        delta_t=delta_t,
    )


def score_to_condition(
    score: int,
) -> Literal["Healthy", "Moderate", "Needs Inspection", "Poor Condition"]:
    """Map numeric health score to labelled condition (per DESIGN.md)."""
    if score >= 80:
        return "Healthy"
    elif score >= 60:
        return "Moderate"
    elif score >= 40:
        return "Needs Inspection"
    else:
        return "Poor Condition"


# ---------------------------------------------------------------------------
# Convenience: score from a single telemetry record dict
# ---------------------------------------------------------------------------

def score_from_record(
    record: dict,
    anomaly_result: tuple,   # (confidence: float, status: str) from AnomalyDetector
    fault_result: dict,      # output dict from FaultDiagnoser.predict_single()
) -> HealthResult:
    """
    Convenience wrapper to compute HealthResult from pre-computed ML outputs.

    Parameters
    ----------
    record         : dict with at minimum 'estimated_cop' and 'delta_t' keys
    anomaly_result : (confidence, status) tuple from AnomalyDetector.predict_single()
    fault_result   : dict from FaultDiagnoser.predict_single()

    Returns
    -------
    HealthResult
    """
    confidence, status = anomaly_result
    return calculate_health_score(
        anomaly_confidence=confidence,
        anomaly_status=status,
        predicted_fault=fault_result.get("predicted_fault", "Normal"),
        fault_probability=fault_result.get("fault_probability", 0.0),
        fault_severity=fault_result.get("severity_score", 0),
        estimated_cop=float(record.get("estimated_cop", 0.0) or 0.0),
        delta_t=float(record.get("delta_t", 0.0) or 0.0),
    )


# ---------------------------------------------------------------------------
# Penalty breakdown for dashboard display
# ---------------------------------------------------------------------------

def penalty_breakdown_dict(result: HealthResult) -> Dict[str, float]:
    """Return a serialisable dict of the four penalty components."""
    return {
        "Anomaly Penalty": result.anomaly_penalty,
        "Fault Penalty": result.fault_penalty,
        "Efficiency Penalty": result.efficiency_penalty,
        "Delta-T Penalty": result.delta_t_penalty,
    }

