# Project Information

## 1. Project Title

**AI-AC-Health-Monitor: AI-Based Air Conditioner Health Monitoring, Fault Detection, and Climate Impact Estimation**

## 2. Problem Statement

Air conditioners are widely used for maintaining indoor comfort. However, inefficient operation and undetected faults can increase energy consumption, electricity costs, equipment deterioration, and environmental impact.

Conventional maintenance approaches often rely on periodic inspection or noticeable equipment failure.

An intelligent monitoring system is required to analyze operating conditions, identify abnormal behavior, detect potential faults, and provide insights into equipment health and energy efficiency.

## 3. Proposed Solution

The proposed system combines Machine Learning, IoT sensors, and data visualization to monitor air conditioner operating conditions.

The system analyzes AC operating data to detect anomalies and identify probable faults. It generates an estimated health score and calculates energy-related environmental impact.

An ESP32-based prototype demonstrates temperature monitoring and real-time sensor integration.

The software presents the results through an interactive dashboard.

## 4. Project Objectives

1. Analyze AC operating data using data science techniques.
2. Detect abnormal operating conditions using Isolation Forest.
3. Identify probable faults using supervised Machine Learning.
4. Generate an AC health score.
5. Monitor temperature through ESP32 sensors.
6. Estimate energy consumption.
7. Estimate associated carbon emissions.
8. Develop an interactive monitoring dashboard.
9. Demonstrate the integration of AI and IoT for predictive maintenance.

## 5. Project Scope

### Software Scope

- Dataset preparation and preprocessing.
- Exploratory data analysis.
- Machine Learning model development.
- Anomaly detection.
- Fault diagnosis.
- AC health score calculation.
- Energy and climate impact estimation.
- Dashboard development.

### Hardware Scope

- ESP32-based sensor acquisition.
- Temperature measurement using DS18B20.
- Communication between the physical prototype and software.
- Real-time monitoring demonstration.

The initial prototype focuses on monitoring rather than direct AC control.

## 6. Dataset

The NIST AC-related dataset will serve as the primary data source for model development.

The dataset will be examined for relevant operating parameters, normal conditions, and fault-related information.

Data preprocessing includes:

- Missing-value handling.
- Duplicate removal.
- Feature selection.
- Outlier analysis.
- Data type conversion.
- Feature scaling where required.

Dataset-specific details will be documented separately after verification.

## 7. Machine Learning Algorithms

### Isolation Forest

Used for unsupervised anomaly detection.

Purpose:

- Identify unusual operating conditions.
- Detect deviations from normal behavior.
- Flag potentially abnormal observations.

### Random Forest Classifier

Used for supervised fault diagnosis when appropriate fault labels are available.

Purpose:

- Predict probable fault categories.
- Analyze operating parameters associated with faults.

## 8. AC Health Score

The system will provide a project-defined health score ranging from 0 to 100.

The score will be calculated using relevant operating indicators, anomaly information, and available fault predictions.

Proposed interpretation:

| Score | Condition |
|---|---|
| 80–100 | Healthy |
| 60–79 | Moderate |
| 40–59 | Needs inspection |
| 0–39 | Poor |

The health score is an estimated monitoring indicator and not a certified diagnostic measurement.

## 9. Energy and Climate Impact

Energy consumption will be calculated using:

Energy (kWh) = Power (kW) × Operating Time (hours)

Carbon emissions will be estimated using:

Carbon Emissions (kg CO₂e) = Energy Consumption (kWh) × Emission Factor (kg CO₂e/kWh)

The emission factor and calculation assumptions will be documented.

## 10. Hardware Components

- ESP32 development board.
- DS18B20 temperature sensor.
- Breadboard.
- Jumper wires.
- USB cable.
- Power supply.

The hardware collects temperature measurements and transmits them to the software.

## 11. Software Requirements

- Python.
- Pandas.
- NumPy.
- Scikit-learn.
- Matplotlib.
- Seaborn.
- Streamlit.
- Joblib.

## 12. Functional Requirements

- Process AC operating data.
- Detect anomalies.
- Predict supported fault categories.
- Calculate AC health score.
- Estimate energy consumption.
- Estimate climate impact.
- Display results through a dashboard.
- Receive sensor measurements.

## 13. Non-Functional Requirements

- Modular software architecture.
- User-friendly interface.
- Reproducible model training.
- Reliable data processing.
- Low-cost hardware implementation.
- Clear distinction between measured and estimated values.

## 14. Expected Outcomes

- AI-based AC monitoring application.
- Anomaly detection model.
- Fault diagnosis model, subject to dataset suitability.
- Health score calculation.
- Energy and climate impact analysis.
- Interactive dashboard.
- ESP32-based temperature monitoring prototype.

## 15. Limitations

- Model performance depends on dataset quality.
- Temperature measurements alone cannot identify every AC fault.
- Health scores represent estimated conditions.
- Energy and emission estimates depend on measurement accuracy.
- The system does not replace professional AC inspection.

## 16. Future Scope

- Additional AC sensors.
- Real-time alerts.
- Cloud integration.
- Multi-AC monitoring.
- Predictive maintenance recommendations.
- Improved fault diagnosis.
