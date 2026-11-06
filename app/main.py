"""Foxbat local security monitoring dashboard."""
import csv
import io
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from app.live import capture
from app.version import VERSION
from fastapi.responses import FileResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Keep the API version and dashboard footer tied to the same release value.
ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv('FOXBAT_DB', str(ROOT.parent / 'foxbat.db')))
app = FastAPI(title='Foxbat', version=VERSION)
app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')

@contextmanager
def db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            severity TEXT NOT NULL,
            event_type TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            destination_ip TEXT NOT NULL,
            description TEXT NOT NULL,
            simulated INTEGER NOT NULL DEFAULT 0
        )''')
        # Non-destructive migration for existing v0.4 databases.
        columns = {row[1] for row in conn.execute('PRAGMA table_info(alerts)')}
        if 'origin' not in columns:
            conn.execute("ALTER TABLE alerts ADD COLUMN origin TEXT NOT NULL DEFAULT 'legacy'")
            conn.execute("UPDATE alerts SET origin = 'demo' WHERE simulated = 1")
        conn.commit()
        yield conn
        conn.commit()
    finally:
        conn.close()

class AlertInput(BaseModel):
    severity: str = Field(pattern='^(LOW|MEDIUM|HIGH|CRITICAL)$')
    event_type: str = Field(min_length=1, max_length=80)
    source_ip: str = Field(min_length=1, max_length=80)
    destination_ip: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=500)

@app.get('/')
def home():
    return FileResponse(ROOT / 'static' / 'index.html')

@app.get('/api/health')
def health():
    return {'status': 'ok', 'version': VERSION, 'mode': 'live-capture-ready', 'live_capture': capture.snapshot()['running']}

def filtered_alerts(severity=None, origin=None, q=None, limit=100):
    if not 1 <= limit <= 5000:
        raise HTTPException(status_code=422, detail='limit must be 1–5000')
    if severity and severity not in ('LOW','MEDIUM','HIGH','CRITICAL'):
        raise HTTPException(status_code=422, detail='Invalid severity')
    if origin and origin not in ('demo','pcap','live','legacy'):
        raise HTTPException(status_code=422, detail='Invalid origin')
    conditions, params = [], []
    if severity:
        conditions.append('severity = ?'); params.append(severity)
    if origin:
        conditions.append('origin = ?'); params.append(origin)
    if q:
        if len(q) > 120:
            raise HTTPException(status_code=422, detail='Search too long')
        conditions.append('(source_ip LIKE ? OR destination_ip LIKE ? OR event_type LIKE ?)')
        params.extend(['%' + q + '%'] * 3)
    where = (' WHERE ' + ' AND '.join(conditions)) if conditions else ''
    with db() as conn:
        return [dict(row) for row in conn.execute(
            'SELECT * FROM alerts' + where + ' ORDER BY id DESC LIMIT ?', (*params, limit)
        )]

@app.get('/api/alerts')
def alerts(limit: int = 100, severity: str | None = None, origin: str | None = None, q: str | None = None):
    return filtered_alerts(severity, origin, q, limit)

@app.get('/api/alerts/export')
def export_alerts(severity: str | None = None, origin: str | None = None, q: str | None = None):
    records = filtered_alerts(severity, origin, q, 5000)
    fields = ['id','timestamp','severity','event_type','source_ip','destination_ip','description','origin']
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
    writer.writeheader(); writer.writerows(records)
    return StreamingResponse(iter([output.getvalue()]), media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="foxbat-alerts.csv"'})

@app.get('/api/analytics')
def analytics():
    with db() as conn:
        severities = [dict(r) for r in conn.execute('SELECT severity AS name, COUNT(*) AS count FROM alerts GROUP BY severity')]
        origins = [dict(r) for r in conn.execute('SELECT origin AS name, COUNT(*) AS count FROM alerts GROUP BY origin')]
        timeline = [dict(r) for r in conn.execute("SELECT substr(timestamp,1,10) AS day, COUNT(*) AS count FROM alerts GROUP BY substr(timestamp,1,10) ORDER BY day DESC LIMIT 14")]
    return {'severities': severities, 'origins': origins, 'timeline': list(reversed(timeline))}

@app.get('/api/alerts/{alert_id}')
def alert_detail(alert_id: int):
    with db() as conn:
        row = conn.execute('SELECT * FROM alerts WHERE id = ?', (alert_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail='Alert not found')
    result = dict(row)
    # Origin is stored per event; pre-migration events remain 'legacy'.
    return result

@app.get('/api/stats')
def stats():
    with db() as conn:
        total = conn.execute('SELECT COUNT(*) FROM alerts').fetchone()[0]
        high = conn.execute("SELECT COUNT(*) FROM alerts WHERE severity IN ('HIGH','CRITICAL')").fetchone()[0]
        sources = conn.execute('SELECT COUNT(DISTINCT source_ip) FROM alerts').fetchone()[0]
        by_type = [dict(r) for r in conn.execute('SELECT event_type AS name, COUNT(*) AS count FROM alerts GROUP BY event_type ORDER BY count DESC')]
    with db() as conn:
        try:
            packets = conn.execute('SELECT COALESCE(SUM(packets),0) FROM imports').fetchone()[0]
        except sqlite3.OperationalError:
            packets = 0
    return {'total_alerts': total, 'high_severity': high, 'unique_sources': sources, 'detections': by_type, 'packets_analyzed': packets + capture.snapshot()['live_packets']}

@app.post('/api/demo', status_code=201)
def demo():
    """Generate clearly labeled synthetic alerts; binds only to localhost by default."""
    samples = [
        ('HIGH','SYN_FLOOD','192.0.2.11','198.51.100.10','Elevated SYN rate in a 10-second window'),
        ('MEDIUM','PORT_SCAN','192.0.2.24','198.51.100.10','Multiple destination ports contacted'),
        ('LOW','DNS_ANOMALY','192.0.2.35','198.51.100.53','Unusually long DNS query'),
        ('MEDIUM','ICMP_FLOOD','192.0.2.44','198.51.100.10','High ICMP echo-request rate'),
        ('HIGH','PORT_SCAN','192.0.2.24','198.51.100.15','Rapid connection attempts across ports'),
    ]
    now = datetime.now(timezone.utc)
    with db() as conn:
        for i, row in enumerate(samples):
            conn.execute("INSERT INTO alerts (timestamp,severity,event_type,source_ip,destination_ip,description,simulated,origin) VALUES (?,?,?,?,?,?,1,'demo')",
                         ((now - timedelta(minutes=i * 3)).isoformat(), *row))
    return {'created': len(samples), 'simulated': True}

@app.delete('/api/demo')
def clear_demo():
    with db() as conn:
        count = conn.execute('DELETE FROM alerts WHERE simulated = 1').rowcount
    return {'deleted': count}


def require_local(request: Request):
    if request.client is None or request.client.host not in ('127.0.0.1', '::1', 'testclient'):
        raise HTTPException(status_code=403, detail='Local access only')

@app.get('/api/capture')
def capture_status():
    return capture.snapshot()

@app.post('/api/capture/start')
def capture_start(request: Request):
    require_local(request)
    try:
        changed = capture.start()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f'Capture unavailable: {type(exc).__name__}. Check Npcap and permissions.') from exc
    return {'started': changed, **capture.snapshot()}

@app.post('/api/capture/stop')
def capture_stop(request: Request):
    require_local(request)
    changed = capture.stop()
    return {'stopped': changed, **capture.snapshot()}


@app.get('/api/alerts/{alert_id}/report')
def incident_report(alert_id: int):
    """Export a single event as a Markdown investigation worksheet."""
    record = alert_detail(alert_id)
    def safe(value):
        # Prevent user-controlled alert text from injecting Markdown structure.
        return str(value).replace('\r', ' ').replace('\n', ' ').replace('|', '\\|').replace('`', "'")
    fields = [('Event ID', record['id']), ('Timestamp (UTC)', record['timestamp']),
              ('Detection', record['event_type']), ('Severity', record['severity']),
              ('Source IP', record['source_ip']), ('Destination IP', record['destination_ip']),
              ('Origin', record['origin']), ('Description', record['description'])]
    lines = ['# Foxbat Incident Report', '', '> Automated heuristic detection; not a confirmed security incident.', '',
             '## Evidence summary', '', '| Field | Value |', '| --- | --- |']
    lines.extend(f'| {label} | {safe(value)} |' for label, value in fields)
    lines += ['', '## Analyst assessment', '', '- **Disposition:** Pending review',
              '- **Evidence reviewed:**', '- **False-positive considerations:**',
              '- **Recommended follow-up:**', '', '## Limitations', '',
              'Foxbat does not independently verify malicious intent. Preserve original PCAPs separately when authorized.', '']
    return Response('\n'.join(lines), media_type='text/markdown; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename="foxbat-incident-{alert_id}.md"',
                 'X-Content-Type-Options': 'nosniff'})
