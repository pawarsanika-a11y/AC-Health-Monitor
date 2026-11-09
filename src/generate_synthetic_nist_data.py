"""
generate_synthetic_nist_data.py — Benchmark NIST AC Dataset Generator

Generates realistic AC operating data mirroring NIST FDD testbed specifications
(multi-fault dataset for split-system / RTU equipment):
  - Normal Operation
  - Refrigerant Undercharge (-10% to -40%)
  - Refrigerant Overcharge (+10% to +30%)
  - Outdoor Airflow Restriction (blocked condenser)
  - Liquid Line Restriction (filter-drier blockage)

Saves output as a benchmark CSV in data/raw/ so the training pipeline
can be validated immediately.
"""

from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = RAW_DIR / "nist_ac_fdd_benchmark.csv"


def generate_nist_benchmark_dataset(samples_per_class: int = 1200, random_seed: int = 42) -> pd.DataFrame:
    np.random.seed(random_seed)

    records = []

    # 1. Normal Operation
    n = samples_per_class
    outdoor = np.random.uniform(28.0, 42.0, n)
    setpoint = np.random.choice([22.0, 23.0, 24.0], size=n)
    return_air = setpoint + np.random.normal(0.5, 0.4, n)
    # Healthy Delta-T: 9.0 to 12.5 °C
    delta_t = np.random.uniform(9.0, 12.5, n)
    supply_air = return_air - delta_t
    power_kw = 1.05 + 0.02 * (outdoor - 30.0) + np.random.normal(0, 0.04, n)
    power_kw = np.clip(power_kw, 0.85, 1.45)
    runtime = np.random.uniform(1.0, 8.0, n)
    
    for i in range(n):
        records.append({
            "supply_air_temp": round(supply_air[i], 2),
            "return_air_temp": round(return_air[i], 2),
            "outdoor_ambient_temp": round(outdoor[i], 2),
            "setpoint_temp": round(setpoint[i], 1),
            "power_kw": round(power_kw[i], 3),
            "runtime_hours": round(runtime[i], 2),
            "fault_label": "Normal",
        })

    # 2. Refrigerant Undercharge
    # Characteristic: Low Delta-T (cooling loss), elevated supply temp, compressor works harder
    outdoor = np.random.uniform(30.0, 44.0, n)
    setpoint = np.random.choice([22.0, 23.0, 24.0], size=n)
    return_air = setpoint + np.random.uniform(1.5, 4.5, n)  # cannot reach setpoint
    delta_t = np.random.uniform(2.0, 5.5, n)                # degraded split
    supply_air = return_air - delta_t
    power_kw = 1.60 + 0.025 * (outdoor - 30.0) + np.random.normal(0, 0.06, n)
    power_kw = np.clip(power_kw, 1.45, 2.30)
    runtime = np.random.uniform(3.0, 12.0, n)

    for i in range(n):
        records.append({
            "supply_air_temp": round(supply_air[i], 2),
            "return_air_temp": round(return_air[i], 2),
            "outdoor_ambient_temp": round(outdoor[i], 2),
            "setpoint_temp": round(setpoint[i], 1),
            "power_kw": round(power_kw[i], 3),
            "runtime_hours": round(runtime[i], 2),
            "fault_label": "Refrigerant Undercharge",
        })

    # 3. Refrigerant Overcharge
    # Characteristic: High head pressure, higher power draw, slightly reduced Delta-T
    outdoor = np.random.uniform(28.0, 40.0, n)
    setpoint = np.random.choice([22.0, 23.0, 24.0], size=n)
    return_air = setpoint + np.random.normal(0.8, 0.5, n)
    delta_t = np.random.uniform(6.5, 8.8, n)
    supply_air = return_air - delta_t
    power_kw = 1.55 + 0.03 * (outdoor - 30.0) + np.random.normal(0, 0.05, n)
    power_kw = np.clip(power_kw, 1.35, 2.10)
    runtime = np.random.uniform(2.0, 9.0, n)

    for i in range(n):
        records.append({
            "supply_air_temp": round(supply_air[i], 2),
            "return_air_temp": round(return_air[i], 2),
            "outdoor_ambient_temp": round(outdoor[i], 2),
            "setpoint_temp": round(setpoint[i], 1),
            "power_kw": round(power_kw[i], 3),
            "runtime_hours": round(runtime[i], 2),
            "fault_label": "Refrigerant Overcharge",
        })

    # 4. Outdoor Airflow Restriction (Condenser fouling)
    # Characteristic: Poor heat rejection, higher condensing temp & pressure, high power draw
    outdoor = np.random.uniform(32.0, 45.0, n)
    setpoint = np.random.choice([22.0, 23.0, 24.0], size=n)
    return_air = setpoint + np.random.uniform(1.0, 3.0, n)
    delta_t = np.random.uniform(5.0, 7.8, n)
    supply_air = return_air - delta_t
    power_kw = 1.65 + 0.035 * (outdoor - 30.0) + np.random.normal(0, 0.05, n)
    power_kw = np.clip(power_kw, 1.50, 2.25)
    runtime = np.random.uniform(2.5, 10.0, n)

    for i in range(n):
        records.append({
            "supply_air_temp": round(supply_air[i], 2),
            "return_air_temp": round(return_air[i], 2),
            "outdoor_ambient_temp": round(outdoor[i], 2),
            "setpoint_temp": round(setpoint[i], 1),
            "power_kw": round(power_kw[i], 3),
            "runtime_hours": round(runtime[i], 2),
            "fault_label": "Outdoor Airflow Restriction",
        })

    # 5. Liquid Line Restriction (Filter-drier blockage)
    # Characteristic: Reduced mass flow rate, inadequate cooling, low delta-t, moderate power
    outdoor = np.random.uniform(29.0, 42.0, n)
    setpoint = np.random.choice([22.0, 23.0, 24.0], size=n)
    return_air = setpoint + np.random.uniform(1.2, 3.8, n)
    delta_t = np.random.uniform(3.5, 6.2, n)
    supply_air = return_air - delta_t
    power_kw = 1.30 + 0.02 * (outdoor - 30.0) + np.random.normal(0, 0.04, n)
    power_kw = np.clip(power_kw, 1.15, 1.70)
    runtime = np.random.uniform(2.0, 9.0, n)

    for i in range(n):
        records.append({
            "supply_air_temp": round(supply_air[i], 2),
            "return_air_temp": round(return_air[i], 2),
            "outdoor_ambient_temp": round(outdoor[i], 2),
            "setpoint_temp": round(setpoint[i], 1),
            "power_kw": round(power_kw[i], 3),
            "runtime_hours": round(runtime[i], 2),
            "fault_label": "Liquid Line Restriction",
        })

    df = pd.DataFrame(records)
    # Shuffle
    df = df.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)
    return df


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df = generate_nist_benchmark_dataset(samples_per_class=1200)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Generated {len(df)} records across {df['fault_label'].nunique()} classes.")
    print(f"Saved benchmark dataset to: {OUTPUT_FILE}")
    print("\nClass distribution:")
    print(df["fault_label"].value_counts())


if __name__ == "__main__":
    main()

