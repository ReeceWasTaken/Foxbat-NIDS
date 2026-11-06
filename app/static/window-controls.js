// Native title-bar buttons are bridged to Python; leave dragging to the Windows worker.
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
  // Only the label region initiates movement; never the window buttons.
  // Use a non-blocking native window movement worker instead of
  // pywebview easy_drag or a modal Win32 caption message loop.
  bar.querySelector('.titlebar-ident')?.addEventListener('pointerdown', (event) => {
    if (event.button !== 0 || event.detail > 1) return;
    invoke('begin_drag');
  });
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
