"""Release metadata should agree across the app and installer."""
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.version import VERSION


def test_api_and_health_use_release_version():
    assert app.version == VERSION
    assert TestClient(app).get('/api/health').json()['version'] == VERSION


def test_installer_version_matches_release():
    include = Path(__file__).resolve().parents[1] / 'version.iss'
    assert f'#define AppVersion "{VERSION}"' in include.read_text()
