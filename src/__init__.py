"""
AI-AC-Health-Monitor — src package

Exposes the core ML pipeline modules:
  - data_preprocessing : load, clean, feature-engineer the NIST AC dataset
  - anomaly_detection  : Isolation Forest unsupervised anomaly scorer
  - fault_diagnosis    : Random Forest supervised fault classifier
  - health_score       : composite AC health-score calculator
  - climate_impact     : energy & carbon-emission estimator
  - train_models       : end-to-end training script (run directly)
"""

