import os
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def client():
    # IMPORTANT : set env BEFORE importing app/services
    os.environ["DATA_DIR"] = "tests/data"
    os.environ["PYTHONPATH"] = "."

    from banking_api.main import app  # import after env set
    return TestClient(app)
