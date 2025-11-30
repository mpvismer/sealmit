import pytest
import os
import shutil
from fastapi.testclient import TestClient
from main import app
from api import projects

@pytest.fixture(scope="function")
def client(tmp_path):
    """
    Fixture to provide a TestClient with a temporary PROJECTS_ROOT.
    """
    # Override PROJECTS_ROOT to use a temporary directory
    original_root = projects.PROJECTS_ROOT
    projects.PROJECTS_ROOT = str(tmp_path / "projects_data")
    os.makedirs(projects.PROJECTS_ROOT, exist_ok=True)
    
    with TestClient(app) as c:
        yield c
    
    # Restore original root
    projects.PROJECTS_ROOT = original_root
