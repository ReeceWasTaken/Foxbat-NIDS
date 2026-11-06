import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from app import main


def test_report_download_and_missing_event(monkeypatch):
    with tempfile.TemporaryDirectory() as folder:
        monkeypatch.setattr(main, 'DB_PATH', Path(folder) / 'test.db')
        client = TestClient(main.app)
        assert client.get('/api/alerts/999/report').status_code == 404
        assert client.post('/api/demo').status_code == 201
        alert_id = client.get('/api/alerts').json()[0]['id']
        response = client.get(f'/api/alerts/{alert_id}/report')
        assert response.status_code == 200
        assert 'Foxbat Incident Report' in response.text
        assert 'Pending review' in response.text
        assert 'attachment;' in response.headers['content-disposition']
        assert 'DEMO' not in response.text or 'demo' in response.text
