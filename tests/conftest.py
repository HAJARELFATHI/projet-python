import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add project root to PYTHONPATH so "import banking_api" works
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def client():
    # Force the API to use the small test dataset
    os.environ["DATA_DIR"] = str(ROOT / "tests" / "data")

    # Import AFTER setting env
    from banking_api.main import app

    return TestClient(app)
