import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from app import main

def test_filters_export_and_migration():
    with tempfile.TemporaryDirectory() as folder:
        main.DB_PATH = Path(folder) / 'test.db'
        client = TestClient(main.app)
        assert client.post('/api/demo').status_code == 201
        alerts = client.get('/api/alerts?origin=demo&severity=HIGH').json()
        assert len(alerts) == 2
        assert all(a['origin'] == 'demo' for a in alerts)
        assert len(client.get('/api/alerts?q=192.0.2.24').json()) == 2
        assert client.get('/api/alerts?origin=invalid').status_code == 422
        csv_response = client.get('/api/alerts/export?severity=HIGH')
        assert csv_response.status_code == 200
        assert csv_response.text.count('\n') == 3
        analytics = client.get('/api/analytics').json()
        assert sum(x['count'] for x in analytics['origins']) == 5
        assert client.get('/api/alerts/1').json()['origin'] == 'demo'
