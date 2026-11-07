// Native title-bar buttons use the Python bridge; pywebview handles dragging.
/* Desktop shell is explicitly enabled by the local launcher, not by an asynchronous API event. */
(() => {
  const bar = document.getElementById('militaryTitlebar');
  const desktop = new URLSearchParams(window.location.search).get('foxbat_desktop') === '1';
  if (!desktop || !bar) return;
  document.documentElement.classList.add('desktop-shell');
  bar.hidden = false;
  const invoke = async (method) => {
    try {
      if (!window.pywebview?.api?.[method]) {
        console.warn('Native window API unavailable:', method);
        return;
      }
      return await window.pywebview.api[method]();
    } catch (error) { console.error('Window control failed:', method, error); }
  };
  // The label uses pywebview's native drag region. No JS mouse bridge
  // is involved in dragging, so clicks remain responsive in WebView2.
  document.getElementById('windowMinimize')?.addEventListener('click', (event) => {
    event.stopPropagation(); invoke('minimize');
  });
  document.getElementById('windowMaximize')?.addEventListener('click', async (event) => {
    event.stopPropagation();
    const maximized = await invoke('toggle_maximize');
    if (typeof maximized === 'boolean')
      document.getElementById('windowMaximize').textContent = maximized ? '❐' : '□';
  });
  document.getElementById('windowClose')?.addEventListener('click', (event) => {
    event.stopPropagation(); invoke('close');
  });
})();
