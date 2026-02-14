import os
import sys
from pathlib import Path

# Add project root to PYTHONPATH so "import banking_api" works
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Force test dataset directory if you created tests/data
os.environ.setdefault("DATA_DIR", str(ROOT / "tests" / "data"))
