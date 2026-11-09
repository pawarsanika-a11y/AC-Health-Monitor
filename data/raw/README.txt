# Place NIST AC fault dataset CSV files in this directory.
#
# Expected files:
#   - Any CSV file(s) containing AC operating parameters.
#     The preprocessing module (src/data_preprocessing.py) will auto-discover
#     all *.csv files in this directory.
#
# NIST AC-FDD Dataset sources:
#   https://www.nist.gov/el/energy-and-environment-division-73200/air-conditioning-systems
#   Or search: "NIST AC fault detection dataset" on data.gov or ResearchGate
#
# After placing your data here, run:
#   python src/train_models.py

