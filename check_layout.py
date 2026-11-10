import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dashboard.utils.theme import get_plot_layout
pl = get_plot_layout('dark')
print('Keys in plot_layout:', list(pl.keys()))
print('Full layout:', pl)

