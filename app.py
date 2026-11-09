"""
Root entry point for AI-AC-Health-Monitor Dashboard.
Delegates to dashboard/app.py.
"""

import sys
from pathlib import Path

# Add project root to python path for modular imports
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dashboard.app import main

if __name__ == "__main__":
    main()

