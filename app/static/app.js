const $ = id => document.getElementById(id);
let currentAlerts = [];
const escapeHtml = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
// Poll the local sensor; the UI keeps working even when no capture is running.
async function refresh() {
  try {
    const [health, stats, alerts, capture] = await Promise.all(['/api/health','/api/stats','/api/alerts?limit=500','/api/capture'].map(async path => {const response = await fetch(path); if (!response.ok) throw new Error(path); return response.json()}));
    // The footer follows the backend release, so an old cached HTML page won't show the wrong version.
    $('appVersion').textContent = `v${health.version}`;
    $('captureState').textContent = capture.running ? '● Monitoring' : 'Stopped';
    $('consoleCapture').textContent = capture.running ? 'ACTIVE' : 'STANDBY';
    $('startCapture').disabled = capture.running;
    $('stopCapture').disabled = !capture.running;
    $('protocols').textContent = Object.entries(capture.protocols).map(([k,v])=>`${k}: ${v}`).join('  ·  ') || 'No traffic captured';
    const values = capture.traffic.map(x=>x.packets);
    const peak = Math.max(1,...values);
    const points = values.map((v,i)=>`${15+i*570/Math.max(1,values.length-1)},${115-v*95/peak}`).join(' ');
    $('trafficChart').innerHTML = values.length ? `<line x1="15" y1="115" x2="590" y2="115" stroke="#315a3b"/><polyline fill="none" stroke="#86f5a3" stroke-width="3" points="${points}"/><text x="15" y="15" fill="#8fe9a6" font-family="Consolas, Courier New, monospace" font-size="12">Peak: ${peak} packets/sec</text>` : '<text x="300" y="59" text-anchor="middle" fill="#91f7ab" font-family="Consolas, Courier New, monospace" font-size="13" letter-spacing="1">AWAITING SENSOR ACTIVATION</text><text x="300" y="83" text-anchor="middle" fill="#719d7b" font-family="Consolas, Courier New, monospace" font-size="10">ENGAGE SENSOR TO DISPLAY LIVE TRAFFIC</text>';
    $('api').textContent = health.status === 'ok' ? '● Online' : 'Offline';
    $('consoleApi').textContent = health.status === 'ok' ? 'ONLINE' : 'OFFLINE';
    $('total').textContent = stats.total_alerts;
    $('high').textContent = stats.high_severity;
    $('sources').textContent = stats.unique_sources;
    $('packets').textContent = stats.packets_analyzed || '—';
    $('count').textContent = `${alerts.length} events`;
    const max = Math.max(1, ...stats.detections.map(x=>x.count));
    $('breakdown').innerHTML = stats.detections.length ? stats.detections.map(x=>`<div class="barrow"><div class="barlabel"><span>${escapeHtml(x.name.replaceAll('_',' '))}</span><b>${x.count}</b></div><div class="track"><div class="fill" style="width:${100*x.count/max}%"></div></div></div>`).join('') : '<p class="empty">No detections yet. Generate demo alerts to preview.</p>';
    const analyticsResponse = await fetch('/api/analytics');
    if (analyticsResponse.ok) {
      const analytics = await analyticsResponse.json();
      renderBars('severityBars', analytics.severities);
      renderBars('originBars', analytics.origins);
    }
    currentAlerts = alerts;
    updateRadar(alerts);
    renderAlerts();
  } catch (error) { $('api').textContent = '● Offline'; $('consoleApi').textContent = 'OFFLINE'; console.error(error); }
}
$('demo').addEventListener('click', async()=>{await fetch('/api/demo',{method:'POST'});await refresh()});
$('clear').addEventListener('click', async()=>{await fetch('/api/demo',{method:'DELETE'});await refresh()});
refresh();setInterval(refresh,5000);

async function captureAction(action) {
  try {
    const response = await fetch(`/api/capture/${action}`, {method:'POST'});
    if (!response.ok) {const data = await response.json(); throw new Error(data.detail || 'Capture request failed')}
    await refresh();
  } catch (error) {alert(error.message)}
}
$('startCapture').addEventListener('click',()=>captureAction('start'));
$('stopCapture').addEventListener('click',()=>captureAction('stop'));

function renderBars(id, values) {
  const max = Math.max(1, ...values.map(x=>x.count));
  $(id).innerHTML = values.length ? values.map(x=>`<div class="barrow"><div class="barlabel"><span>${escapeHtml(x.name.toUpperCase())}</span><b>${x.count}</b></div><div class="track"><div class="fill" style="width:${100*x.count/max}%"></div></div></div>`).join('') : '<p class="empty">No alerts yet</p>';
}
function renderAlerts() {
  const severity = $('severityFilter').value;
  const origin = $('originFilter').value;
  const query = $('alertSearch').value.trim().toLowerCase();
  const alerts = currentAlerts.filter(a => (severity === 'ALL' || a.severity === severity) && (origin === 'ALL' || a.origin === origin) && (!query || [a.source_ip,a.destination_ip,a.event_type].some(x=>x.toLowerCase().includes(query))));
  $('rows').innerHTML = alerts.length ? alerts.map(a => `<tr class="alertrow" data-id="${Number(a.id)}" tabindex="0"><td>${escapeHtml(a.timestamp)}</td><td>${escapeHtml(a.event_type.replaceAll('_',' '))}</td><td><span class="sev ${escapeHtml(a.severity)}">${escapeHtml(a.severity)}</span></td><td>${escapeHtml(a.source_ip)}</td><td>${escapeHtml(a.destination_ip)}</td><td>${escapeHtml(a.origin.toUpperCase())}</td></tr>`).join('') : '<tr><td colspan="6" class="empty">No matching alerts.</td></tr>';
}
$('severityFilter').addEventListener('change', renderAlerts);
$('originFilter').addEventListener('change', renderAlerts);
$('alertSearch').addEventListener('input', renderAlerts);
$('exportCsv').addEventListener('click', () => {
  const params = new URLSearchParams();
  if ($('severityFilter').value !== 'ALL') params.set('severity', $('severityFilter').value);
  if ($('originFilter').value !== 'ALL') params.set('origin', $('originFilter').value);
  if ($('alertSearch').value.trim()) params.set('q', $('alertSearch').value.trim());
  window.location.href = '/api/alerts/export?' + params.toString();
});
$('rows').addEventListener('click', async e => {
  const row = e.target.closest('tr[data-id]');
  if (!row) return;
  const response = await fetch(`/api/alerts/${row.dataset.id}`);
  if (!response.ok) return;
  const alertData = await response.json();
  $('alertEvidence').textContent = JSON.stringify(alertData, null, 2);
  $('downloadReport').href = `/api/alerts/${Number(alertData.id)}/report`;
  $('investigation').showModal();
});
$('closeInvestigation').addEventListener('click', () => $('investigation').close());

// Client-side sidebar navigation. All sections remain in the DOM so existing
// live refresh, filters, alert investigation and capture controls keep working.
const views = {
  overview: {title:'Network Defense Console', eyebrow:'SECURITY OPERATIONS / OVERVIEW', description:'LIVE TELEMETRY / THREAT DETECTION / INCIDENT REVIEW'},
  alerts: {title:'Security Alerts', eyebrow:'SECURITY OPERATIONS / SECURITY ALERTS', description:'Search, filter, export, and investigate recorded security detections.'},
  analytics: {title:'Network Analytics', eyebrow:'SECURITY OPERATIONS / NETWORK ANALYTICS', description:'Review live traffic activity, severity distribution, and alert origins.'}
};
function setView(view) {
  if (!Object.prototype.hasOwnProperty.call(views, view)) view = 'overview';
  document.querySelectorAll('[data-section]').forEach(section => {
    section.hidden = section.dataset.section !== view;
  });
  document.querySelectorAll('[data-view]').forEach(button => {
    const active = button.dataset.view === view;
    button.classList.toggle('active', active);
    if (active) button.setAttribute('aria-current', 'page');
    else button.removeAttribute('aria-current');
  });
  $('viewTitle').textContent = views[view].title;
  $('viewEyebrow').textContent = views[view].eyebrow;
  $('viewDescription').textContent = views[view].description;
  window.location.hash = view === 'overview' ? '' : view;
}
document.querySelectorAll('[data-view]').forEach(button => {
  button.addEventListener('click', () => setView(button.dataset.view));
});
window.addEventListener('hashchange', () => setView(window.location.hash.slice(1)));
setView(window.location.hash.slice(1));

// Radar is an illustrative event projection, not geographic IP geolocation.
// Deterministic positions keep contacts stable across the 5-second API refresh.
function radarHash(value) {
  let hash = 2166136261;
  for (const char of String(value)) { hash ^= char.charCodeAt(0); hash = Math.imul(hash, 16777619); }
  return hash >>> 0;
}
function updateRadar(alerts) {
  const recent = alerts.slice(0, 28);
  $('radarContactCount').textContent = `CONTACTS: ${String(recent.length).padStart(3, '0')}`;
  $('consoleDetections').textContent = String(alerts.length).padStart(4, '0');
  const high = alerts.some(a => a.severity === 'HIGH' || a.severity === 'CRITICAL');
  const medium = alerts.some(a => a.severity === 'MEDIUM');
  $('threatCondition').textContent = high ? 'ELEVATED' : medium ? 'CAUTION' : 'NORMAL';
  $('threatCondition').style.color = high ? '#ff8b7d' : medium ? '#efc572' : '#a9ffb8';
  $('radarBlips').innerHTML = recent.map(a => {
    const seed = radarHash(`${a.id}|${a.source_ip}|${a.event_type}`);
    const angle = (seed % 360) * Math.PI / 180;
    const radius = 26 + ((seed >>> 9) % 138);
    const x = 280 + Math.cos(angle) * radius;
    const y = 190 + Math.sin(angle) * radius;
    const color = ['HIGH', 'CRITICAL'].includes(a.severity) ? '#ff8174' : a.severity === 'MEDIUM' ? '#efc36d' : '#9dffb1';
    return `<g class="radar-blip" style="color:${color}"><circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="4" fill="${color}"/><circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="8" fill="none" stroke="${color}" opacity=".55"/></g>`;
  }).join('');
}
function updateConsoleClock() {
  $('consoleClock').textContent = new Date().toLocaleTimeString('en-GB', {timeZone:'UTC', hour12:false}) + ' UTC';
}
updateConsoleClock();
setInterval(updateConsoleClock, 1000);
