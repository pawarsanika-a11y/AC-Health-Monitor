"""
climate_impact.py — Energy Consumption & Carbon Emission Estimator

Implements the formulas defined in DESIGN.md sections 6, INFO.md sections 9:

  Energy (kWh)        = Power (kW) × Operating Time (hours)
  Carbon (kg CO₂e)    = Energy (kWh) × Emission Factor (kg CO₂e/kWh)
  Excess Carbon       = Carbon_actual − Carbon_at_nominal_efficiency

Emission factors (CEA / IEA reference values):
  India grid average  : 0.82  kg CO₂e / kWh  (CEA CO₂ Baseline 2023)
  World average       : 0.49  kg CO₂e / kWh  (IEA 2022)
  EU grid             : 0.28  kg CO₂e / kWh  (EEA 2022)
  US average          : 0.39  kg CO₂e / kWh  (EPA 2022)
  Renewable (solar)   : 0.04  kg CO₂e / kWh  (lifecycle estimate)

All monetary/cost estimates are optional and use an INR tariff by default.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Emission factors (kg CO₂e per kWh)
# ---------------------------------------------------------------------------

EMISSION_FACTORS: Dict[str, float] = {
    "India Grid (CEA 2023)": 0.82,
    "World Average (IEA 2022)": 0.49,
    "EU Grid (EEA 2022)": 0.28,
    "US Average (EPA 2022)": 0.39,
    "Renewable / Solar": 0.04,
}

DEFAULT_EMISSION_FACTOR_KEY = "India Grid (CEA 2023)"
NOMINAL_COP = 3.5          # Healthy reference COP for excess calculation
DEFAULT_TARIFF_INR_PER_KWH = 7.50  # Approximate Indian residential tariff


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

@dataclass
class ClimateResult:
    """Full energy and climate impact result for one AC unit over a period."""
    energy_kwh: float                # Actual energy consumed
    carbon_kg_co2e: float            # Actual carbon emissions
    nominal_energy_kwh: float        # What energy should have been at nominal COP
    excess_energy_kwh: float         # Energy wasted due to degradation
    excess_carbon_kg_co2e: float     # Extra carbon from excess energy
    cost_inr: float                  # Actual electricity cost (INR)
    excess_cost_inr: float           # Excess cost from inefficient operation
    emission_factor_key: str         # Label of emission factor used
    emission_factor_value: float     # Numeric emission factor (kg/kWh)
    runtime_hours: float             # Total operating duration
    power_kw: float                  # Average power draw
    estimated_cop: float             # Actual/estimated COP
    is_power_estimated: bool         # True if power was not directly measured


# ---------------------------------------------------------------------------
# Main estimator
# ---------------------------------------------------------------------------

def estimate_climate_impact(
    power_kw: float,
    runtime_hours: float,
    estimated_cop: float = NOMINAL_COP,
    emission_factor_key: str = DEFAULT_EMISSION_FACTOR_KEY,
    tariff_inr_per_kwh: float = DEFAULT_TARIFF_INR_PER_KWH,
    is_power_estimated: bool = False,
) -> ClimateResult:
    """
    Calculate energy consumption and associated carbon emissions.

    Parameters
    ----------
    power_kw            : Average electrical draw of the AC unit (kW)
    runtime_hours       : Total operating time for the period (hours)
    estimated_cop       : Coefficient of Performance (dimensionless)
    emission_factor_key : Key from EMISSION_FACTORS dict
    tariff_inr_per_kwh  : Electricity tariff in INR per kWh
    is_power_estimated  : Flag — True when power is derived, not measured

    Returns
    -------
    ClimateResult dataclass
    """
    factor = EMISSION_FACTORS.get(emission_factor_key, EMISSION_FACTORS[DEFAULT_EMISSION_FACTOR_KEY])

    # Actual energy and carbon
    energy_kwh = power_kw * runtime_hours
    carbon_kg_co2e = energy_kwh * factor

    # Nominal reference: what energy would have been at NOMINAL_COP
    if estimated_cop > 0 and estimated_cop == estimated_cop:  # guard NaN / zero
        # Thermal load is fixed; at higher COP the same load needs less power
        # Nominal power = actual_power × (actual_cop / nominal_cop)
        nominal_power_kw = power_kw * (estimated_cop / NOMINAL_COP)
    else:
        nominal_power_kw = power_kw  # cannot determine excess

    nominal_energy_kwh = nominal_power_kw * runtime_hours
    excess_energy_kwh = max(0.0, energy_kwh - nominal_energy_kwh)
    excess_carbon_kg_co2e = excess_energy_kwh * factor

    # Cost
    cost_inr = energy_kwh * tariff_inr_per_kwh
    excess_cost_inr = excess_energy_kwh * tariff_inr_per_kwh

    return ClimateResult(
        energy_kwh=round(energy_kwh, 3),
        carbon_kg_co2e=round(carbon_kg_co2e, 4),
        nominal_energy_kwh=round(nominal_energy_kwh, 3),
        excess_energy_kwh=round(excess_energy_kwh, 3),
        excess_carbon_kg_co2e=round(excess_carbon_kg_co2e, 4),
        cost_inr=round(cost_inr, 2),
        excess_cost_inr=round(excess_cost_inr, 2),
        emission_factor_key=emission_factor_key,
        emission_factor_value=factor,
        runtime_hours=round(runtime_hours, 2),
        power_kw=round(power_kw, 3),
        estimated_cop=round(estimated_cop, 3),
        is_power_estimated=is_power_estimated,
    )


# ---------------------------------------------------------------------------
# Batch estimation from time-series DataFrame
# ---------------------------------------------------------------------------

def estimate_from_timeseries(
    df: pd.DataFrame,
    power_col: str = "power_kw",
    cop_col: str = "estimated_cop",
    emission_factor_key: str = DEFAULT_EMISSION_FACTOR_KEY,
    tariff_inr_per_kwh: float = DEFAULT_TARIFF_INR_PER_KWH,
) -> ClimateResult:
    """
    Aggregate a time-series DataFrame into a single ClimateResult.

    Parameters
    ----------
    df              : DataFrame with at least a power column; timestamps inferred from row count
    power_col       : Name of power column (kW)
    cop_col         : Name of COP column (optional, used for excess calculation)
    emission_factor_key : Emission factor to use
    tariff_inr_per_kwh  : Electricity tariff in INR/kWh

    Returns
    -------
    ClimateResult aggregated over the full time-series
    """
    if power_col not in df.columns:
        raise ValueError(f"Column '{power_col}' not found in DataFrame.")

    avg_power = float(df[power_col].mean())
    # Infer runtime from timestamp range if available, else assume 1 record = 1 hour
    if "timestamp" in df.columns:
        ts = pd.to_datetime(df["timestamp"])
        runtime_hours = (ts.max() - ts.min()).total_seconds() / 3600.0
        runtime_hours = max(runtime_hours, 1 / 60)  # minimum 1 minute
    else:
        runtime_hours = len(df) / 60.0  # assume 1-minute interval

    avg_cop = float(df[cop_col].mean()) if cop_col in df.columns else NOMINAL_COP
    if np.isnan(avg_cop) or avg_cop <= 0:
        avg_cop = NOMINAL_COP

    return estimate_climate_impact(
        power_kw=avg_power,
        runtime_hours=runtime_hours,
        estimated_cop=avg_cop,
        emission_factor_key=emission_factor_key,
        tariff_inr_per_kwh=tariff_inr_per_kwh,
        is_power_estimated=True,
    )


# ---------------------------------------------------------------------------
# Utility: compare across emission factor regions
# ---------------------------------------------------------------------------

def compare_emission_factors(energy_kwh: float) -> Dict[str, float]:
    """
    Return carbon emissions (kg CO₂e) for a given energy consumption
    across all available emission factors.

    Useful for dashboard regional comparison cards.
    """
    return {key: round(energy_kwh * factor, 4) for key, factor in EMISSION_FACTORS.items()}


def get_available_emission_factors() -> List[str]:
    """Return list of emission factor keys for dashboard dropdowns."""
    return list(EMISSION_FACTORS.keys())


# ---------------------------------------------------------------------------
# Convenience: build a human-readable summary string
# ---------------------------------------------------------------------------

def format_summary(result: ClimateResult) -> str:
    """Return a concise multi-line summary suitable for dashboard display."""
    lines = [
        f"Energy Consumed  : {result.energy_kwh:.2f} kWh",
        f"Carbon Footprint : {result.carbon_kg_co2e:.3f} kg CO₂e",
        f"Electricity Cost : ₹{result.cost_inr:.2f}",
        f"Excess Energy    : {result.excess_energy_kwh:.2f} kWh (inefficiency waste)",
        f"Excess Emissions : {result.excess_carbon_kg_co2e:.3f} kg CO₂e (avoidable)",
        f"Excess Cost      : ₹{result.excess_cost_inr:.2f} (recoverable savings)",
        f"Emission Factor  : {result.emission_factor_value} kg CO₂e/kWh ({result.emission_factor_key})",
    ]
    if result.is_power_estimated:
        lines.append("⚠  Power is estimated — install a smart meter for measured values.")
    return "\n".join(lines)

