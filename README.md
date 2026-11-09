# AI-AC-Health-Monitor

### AI-Based Air Conditioner Health Monitoring, Fault Detection, and Climate Impact Estimation

## Overview

AI-AC-Health-Monitor is a Machine Learning and IoT-based system designed to monitor air conditioner operating conditions, detect abnormal behavior, identify potential faults, and estimate energy consumption and associated environmental impact.

The system combines Machine Learning algorithms, sensor-based data acquisition, and an interactive dashboard to support predictive maintenance and energy-efficient AC operation.

The project uses the NIST dataset for initial model development and an ESP32-based physical prototype for demonstrating real-time temperature monitoring.

## Objectives

- Detect abnormal AC operating conditions using Machine Learning.
- Identify potential faults and unhealthy operating patterns.
- Estimate AC health using a health score.
- Monitor temperature using IoT sensors.
- Estimate energy consumption and associated carbon emissions.
- Visualize monitoring results through an interactive dashboard.
- Demonstrate AI-assisted predictive maintenance.

## Key Features

- **Anomaly Detection:** Identify abnormal operating conditions using Isolation Forest.
- **Fault Diagnosis:** Predict probable fault categories using supervised Machine Learning.
- **AC Health Score:** Provide a health indicator on a scale of 0–100.
- **IoT Monitoring:** Acquire temperature readings using ESP32 and DS18B20 sensors.
- **Energy Analysis:** Estimate energy consumption using operating data.
- **Climate Impact:** Estimate carbon emissions from energy consumption.
- **Interactive Dashboard:** Display monitoring results and analytical insights.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Visualization | Matplotlib, Seaborn |
| Dashboard | Streamlit |
| Model Persistence | Joblib |
| Hardware | ESP32 |
| Temperature Sensor | DS18B20 |
| Version Control | Git, GitHub |

## System Workflow

1. Acquire AC operating data from the NIST dataset and physical sensors.
2. Preprocess and prepare the collected data.
3. Apply Machine Learning models for anomaly detection and fault diagnosis.
4. Calculate the AC health score.
5. Estimate energy consumption and climate impact.
6. Display results through the dashboard.

## Installation

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
cd AI-AC-Health-Monitor
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
streamlit run dashboard/app.py
```

## Repository Structure

```text
AI-AC-Health-Monitor/
├── data/
├── models/
├── src/
├── dashboard/
├── hardware/
├── docs/
├── README.md
├── info.md
├── design.md
├── requirements.txt
└── .gitignore
```

## Applications

- Predictive maintenance.
- AC operating condition monitoring.
- Fault detection and diagnosis.
- Energy efficiency analysis.
- Climate impact estimation.

## Future Scope

- Real-time monitoring and alerts.
- Integration of additional AC sensors.
- Cloud-based monitoring.
- Multi-AC support.
- Improved fault prediction.

## Contributors

Academic project focused on Machine Learning, IoT, predictive maintenance, and climate-conscious technology.

## License

To be determined.
