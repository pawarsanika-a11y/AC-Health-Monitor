"""
sample_data.py - Structured Data Provider for AI-AC-Health-Monitor

Provides realistic AC operating telemetry, sensor states, and time-series data
structured for seamless transition to backend ML models and ESP32 hardware streaming.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Literal, Tuple
import numpy as np
import pandas as pd


@dataclass
class ACSystemState:
    """Current live snapshot of the AC unit and IoT node."""
    health_score: int
    health_condition: Literal["Healthy", "Moderate", "Needs Inspection", "Poor Condition"]
    operating_status: str
    supply_air_temp: float
    return_air_temp: float
    setpoint_temp: float
    outdoor_ambient_temp: float
    delta_t: float
    power_kw: float
    daily_energy_kwh: float
    estimated_cop: float
    anomaly_status: Literal["Normal Operation", "Warning Anomaly", "Critical Anomaly"]
    anomaly_confidence: float
    anomaly_feature_flag: str
    esp32_connected: bool
    esp32_device_id: str
    esp32_sensor_type: str
    esp32_last_seen_sec: int
    esp32_port: str
    esp32_rssi_dbm: int
    esp32_packet_drop_rate: float
    cycle_runtime_hours: float


# Pre-configured realistic system operating scenarios
PRESET_SCENARIOS: Dict[str, Dict] = {
    "Healthy Operation (Standard)": {
        "health_score": 92,
        "health_condition": "Healthy",
        "operating_status": "Cooling (Inverter Steady State)",
        "supply_air_temp": 12.4,
        "return_air_temp": 23.2,
        "setpoint_temp": 23.0,
        "outdoor_ambient_temp": 34.5,
        "power_kw": 1.18,
        "daily_energy_kwh": 7.42,
        "estimated_cop": 3.45,
        "anomaly_status": "Normal Operation",
        "anomaly_confidence": 0.04,
        "anomaly_feature_flag": "Thermal gradient nominal (ΔT = 10.8°C)",
        "cycle_runtime_hours": 3.8,
    },
    "Moderate Operation (Minor Inefficiency)": {
        "health_score": 74,
        "health_condition": "Moderate",
        "operating_status": "Cooling (Elevated Thermal Drift)",
        "supply_air_temp": 15.6,
        "return_air_temp": 24.1,
        "setpoint_temp": 23.0,
        "outdoor_ambient_temp": 36.2,
        "power_kw": 1.48,
        "daily_energy_kwh": 9.15,
        "estimated_cop": 2.82,
        "anomaly_status": "Normal Operation",
        "anomaly_confidence": 0.18,
        "anomaly_feature_flag": "Mild delta-T reduction detected",
        "cycle_runtime_hours": 5.2,
    },
    "Needs Inspection (Air Filter / Coil Clamping)": {
        "health_score": 52,
        "health_condition": "Needs Inspection",
        "operating_status": "Cooling (Airflow Restricted)",
        "supply_air_temp": 17.8,
        "return_air_temp": 25.4,
        "setpoint_temp": 23.0,
        "outdoor_ambient_temp": 35.8,
        "power_kw": 1.76,
        "daily_energy_kwh": 11.80,
        "estimated_cop": 2.15,
        "anomaly_status": "Warning Anomaly",
        "anomaly_confidence": 0.68,
        "anomaly_feature_flag": "Restricted airflow / Low thermal heat exchange",
        "cycle_runtime_hours": 6.7,
    },
    "Poor Condition (Refrigerant Leak / Undercharge)": {
        "health_score": 28,
        "health_condition": "Poor Condition",
        "operating_status": "Cooling (Severe Undercharge Detected)",
        "supply_air_temp": 20.3,
        "return_air_temp": 26.8,
        "setpoint_temp": 23.0,
        "outdoor_ambient_temp": 37.0,
        "power_kw": 1.95,
        "daily_energy_kwh": 14.30,
        "estimated_cop": 1.42,
        "anomaly_status": "Critical Anomaly",
        "anomaly_confidence": 0.94,
        "anomaly_feature_flag": "Extreme ΔT degradation (< 3.5°C), high continuous power draw",
        "cycle_runtime_hours": 8.4,
    },
}


def get_current_system_state(
    scenario_name: str = "Healthy Operation (Standard)",
    esp32_online: bool = True
) -> ACSystemState:
    """Returns the current AC telemetry and hardware status for the selected scenario."""
    sc = PRESET_SCENARIOS.get(scenario_name, PRESET_SCENARIOS["Healthy Operation (Standard)"])
    delta_t = round(sc["return_air_temp"] - sc["supply_air_temp"], 1)

    return ACSystemState(
        health_score=sc["health_score"],
        health_condition=sc["health_condition"],
        operating_status=sc["operating_status"],
        supply_air_temp=sc["supply_air_temp"],
        return_air_temp=sc["return_air_temp"],
        setpoint_temp=sc["setpoint_temp"],
        outdoor_ambient_temp=sc["outdoor_ambient_temp"],
        delta_t=delta_t,
        power_kw=sc["power_kw"],
        daily_energy_kwh=sc["daily_energy_kwh"],
        estimated_cop=sc["estimated_cop"],
        anomaly_status=sc["anomaly_status"],
        anomaly_confidence=sc["anomaly_confidence"],
        anomaly_feature_flag=sc["anomaly_feature_flag"],
        esp32_connected=esp32_online,
        esp32_device_id="ESP32-WROOM-32D-01",
        esp32_sensor_type="DS18B20 1-Wire Digital Probe",
        esp32_last_seen_sec=1 if esp32_online else 142,
        esp32_port="COM3 (USB-UART)" if esp32_online else "Offline",
        esp32_rssi_dbm=-56 if esp32_online else 0,
        esp32_packet_drop_rate=0.0 if esp32_online else 100.0,
        cycle_runtime_hours=sc["cycle_runtime_hours"],
    )


def generate_temperature_timeseries(
    duration_hours: int = 6,
    scenario_name: str = "Healthy Operation (Standard)",
    points: int = 120
) -> pd.DataFrame:
    """
    Generates realistic time-series temperature and power telemetry.
    Simulates inverter compressor modulating behavior, supply air oscillations,
    and outdoor diurnal drift.
    """
    sc = PRESET_SCENARIOS.get(scenario_name, PRESET_SCENARIOS["Healthy Operation (Standard)"])
    base_supply = sc["supply_air_temp"]
    base_return = sc["return_air_temp"]
    base_setpoint = sc["setpoint_temp"]
    base_outdoor = sc["outdoor_ambient_temp"]
    base_power = sc["power_kw"]

    end_time = datetime.now()
    start_time = end_time - timedelta(hours=duration_hours)
    timestamps = pd.date_range(start=start_time, end=end_time, periods=points)

    # Time array for continuous sinusoidal modulation
    t = np.linspace(0, duration_hours * 2 * np.pi, points)

    # Inverter compressor cycling noise & wave pattern
    np.random.seed(42)
    noise_supply = np.random.normal(0, 0.25, points)
    noise_return = np.random.normal(0, 0.15, points)
    noise_power = np.random.normal(0, 0.05, points)

    # Realistic physical characteristics:
    # Supply oscillates gently with compressor modulation (amplitude ~0.8°C)
    supply = base_supply + 0.8 * np.sin(t * 1.5) + noise_supply
    # Return temperature tracks slowly towards setpoint
    return_temp = base_return + 0.3 * np.cos(t * 0.8) + noise_return
    # Outdoor fluctuates slightly based on time of day
    outdoor = base_outdoor + 1.2 * np.sin(t * 0.3) + np.random.normal(0, 0.1, points)
    # Power correlates with compressor load
    power = np.clip(base_power + 0.18 * np.sin(t * 1.5) + noise_power, 0.2, 3.0)

    # Delta-T
    delta_t = return_temp - supply

    # ESP32 DS18B20 Reading (measures Supply Air or Return Air with discrete 0.0625°C resolution)
    esp32_reading = np.round(supply / 0.0625) * 0.0625

    df = pd.DataFrame({
        "timestamp": timestamps,
        "supply_air_temp": np.round(supply, 2),
        "return_air_temp": np.round(return_temp, 2),
        "setpoint_temp": np.round(np.full(points, base_setpoint), 1),
        "outdoor_ambient_temp": np.round(outdoor, 2),
        "delta_t": np.round(delta_t, 2),
        "power_kw": np.round(power, 3),
        "esp32_ds18b20_temp": np.round(esp32_reading, 2),
    })

    return df


def generate_recent_telemetry_events(scenario_name: str = "Healthy Operation (Standard)") -> List[Dict]:
    """Generates recent operational event logs for anomaly tracking."""
    now = datetime.now()
    if "Healthy" in scenario_name:
        return [
            {"time": (now - timedelta(minutes=2)).strftime("%H:%M:%S"), "level": "INFO", "source": "ESP32", "message": "Telemetry heartbeat received (DS18B20 @ 12.4°C, RSSI -56dBm)"},
            {"time": (now - timedelta(minutes=7)).strftime("%H:%M:%S"), "level": "INFO", "source": "ML Core", "message": "Isolation Forest check passed: Anomaly score 0.04 (Nominal)"},
            {"time": (now - timedelta(minutes=15)).strftime("%H:%M:%S"), "level": "INFO", "source": "System", "message": "Compressor modulated to 68% inverter frequency"},
            {"time": (now - timedelta(minutes=28)).strftime("%H:%M:%S"), "level": "INFO", "source": "Thermal", "message": "Evaporator Delta-T stabilized at 10.8°C (Optimal)"},
        ]
    elif "Moderate" in scenario_name:
        return [
            {"time": (now - timedelta(minutes=1)).strftime("%H:%M:%S"), "level": "WARN", "source": "Thermal", "message": "Delta-T dropped below 8.0°C threshold (Current: 7.2°C)"},
            {"time": (now - timedelta(minutes=6)).strftime("%H:%M:%S"), "level": "INFO", "source": "ESP32", "message": "Telemetry packet received (Supply: 15.6°C)"},
            {"time": (now - timedelta(minutes=18)).strftime("%H:%M:%S"), "level": "WARN", "source": "Energy", "message": "Elevated continuous power draw (1.48 kW vs expected 1.18 kW)"},
            {"time": (now - timedelta(minutes=32)).strftime("%H:%M:%S"), "level": "INFO", "source": "System", "message": "Inverter ramped up to compensate for cooling deficit"},
        ]
    elif "Needs Inspection" in scenario_name:
        return [
            {"time": (now - timedelta(minutes=1)).strftime("%H:%M:%S"), "level": "ALERT", "source": "ML Core", "message": "Isolation Forest flagged pattern deviation (Score: 0.68)"},
            {"time": (now - timedelta(minutes=5)).strftime("%H:%M:%S"), "level": "ALERT", "source": "Airflow", "message": "Restricted airflow signature detected on evaporator return"},
            {"time": (now - timedelta(minutes=14)).strftime("%H:%M:%S"), "level": "WARN", "source": "Thermal", "message": "Delta-T suboptimal at 5.1°C (Efficiency loss ~32%)"},
            {"time": (now - timedelta(minutes=25)).strftime("%H:%M:%S"), "level": "WARN", "source": "Hardware", "message": "ESP32 node continuous duty alert logged"},
        ]
    else:
        return [
            {"time": (now - timedelta(minutes=1)).strftime("%H:%M:%S"), "level": "CRITICAL", "source": "ML Core", "message": "CRITICAL: Undercharge / Refrigerant leak signature confirmed"},
            {"time": (now - timedelta(minutes=3)).strftime("%H:%M:%S"), "level": "CRITICAL", "source": "Thermal", "message": "Evaporator Delta-T degraded to 2.8°C (Cooling failure imminent)"},
            {"time": (now - timedelta(minutes=11)).strftime("%H:%M:%S"), "level": "CRITICAL", "source": "Compressor", "message": "Continuous high-load thermal stress (1.95 kW draw)"},
            {"time": (now - timedelta(minutes=22)).strftime("%H:%M:%S"), "level": "ALERT", "source": "System", "message": "Health score fallen below 30 — Technician inspection required"},
        ]

