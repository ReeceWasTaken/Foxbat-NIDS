import os
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient
from app import main


def test_demo_and_stats():
    with tempfile.TemporaryDirectory() as folder:
        main.DB_PATH = Path(folder) / 'test.db'
        client = TestClient(main.app)
        assert client.get('/api/health').json()['live_capture'] is False
        assert client.get('/api/stats').json()['total_alerts'] == 0
        assert client.post('/api/demo').status_code == 201
        assert client.get('/api/stats').json()['total_alerts'] == 5
        assert all(a['simulated'] for a in client.get('/api/alerts').json())
        assert client.delete('/api/demo').json()['deleted'] == 5
        assert client.get('/api/stats').json()['total_alerts'] == 0
