"""Launch Foxbat in an embedded Edge WebView2 window.

The API stays on loopback, with one Uvicorn server and one capture worker.
"""
import socket
import os
import sys
import threading
import time
from urllib.error import URLError
from urllib.request import urlopen

from desktop.paths import configure_database


class WindowControls:
    """Limited native-window actions exposed to the trusted local dashboard."""

    def __init__(self):
        self.window = None
        self.maximized = False
        self._drag_lock = threading.Lock()
        self._dragging = False

    def begin_drag(self):
        """Move the native top-level window from a background worker.

        WebView2's JS bridge is asynchronous; posting a non-client mouse-down
        from that bridge does not reliably start a native Windows drag. Instead
        we track the left mouse button and move the HWND directly. No blocking
        Win32 modal message loop runs on the bridge or WebView2 UI thread.
        """
        if sys.platform != "win32":
            return False
        with self._drag_lock:
            if self._dragging:
                return False
            self._dragging = True
        threading.Thread(target=self._drag_worker, name="foxbat-window-drag",
                         daemon=True).start()
        return True

    def _drag_worker(self):
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.EnumWindows.argtypes = [ctypes.c_void_p, wintypes.LPARAM]
        user32.EnumWindows.restype = wintypes.BOOL
        user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        user32.GetWindowThreadProcessId.restype = wintypes.DWORD
        user32.IsWindowVisible.argtypes = [wintypes.HWND]
        user32.IsWindowVisible.restype = wintypes.BOOL
        user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
        user32.GetWindowTextLengthW.restype = ctypes.c_int
        user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        user32.GetWindowTextW.restype = ctypes.c_int
        user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
        user32.GetCursorPos.restype = wintypes.BOOL
        user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        user32.GetWindowRect.restype = wintypes.BOOL
        user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
        user32.GetAsyncKeyState.restype = ctypes.c_short
        user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND,
                                       ctypes.c_int, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_int, wintypes.UINT]
        user32.SetWindowPos.restype = wintypes.BOOL
        callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        try:
            handles = []
            @callback_type
            def visit(hwnd, _):
                owner = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
                if owner.value != os.getpid() or not user32.IsWindowVisible(hwnd):
                    return True
                size = user32.GetWindowTextLengthW(hwnd)
                if size:
                    buf = ctypes.create_unicode_buffer(size + 1)
                    user32.GetWindowTextW(hwnd, buf, size + 1)
                    if buf.value == "Foxbat NIDS":
                        handles.append(hwnd)
                return True
            user32.EnumWindows(visit, 0)
            if not handles:
                return
            hwnd = handles[0]
            cursor = wintypes.POINT()
            rect = wintypes.RECT()
            if not user32.GetCursorPos(ctypes.byref(cursor)) or not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                return
            start_x, start_y = cursor.x, cursor.y
            left, top = rect.left, rect.top
            # Wait only while the physical left mouse button remains pressed.
            # SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE.
            flags = 0x0001 | 0x0004 | 0x0010
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline and user32.GetAsyncKeyState(0x01) & 0x8000:
                if not user32.GetCursorPos(ctypes.byref(cursor)):
                    break
                x, y = left + cursor.x - start_x, top + cursor.y - start_y
                user32.SetWindowPos(hwnd, None, x, y, 0, 0, flags)
                time.sleep(0.016)
        finally:
            with self._drag_lock:
                self._dragging = False

    def minimize(self):
        self.window.minimize()
        return True

    def toggle_maximize(self):
        if self.maximized:
            self.window.restore()
        else:
            self.window.maximize()
        self.maximized = not self.maximized
        return self.maximized

    def close(self):
        self.window.destroy()
        return True


def main():
    # Must happen BEFORE app.main is imported (it reads FOXBAT_DB at import time).
    configure_database()
    import uvicorn
    import webview
    from app.main import app
    from app.live import capture

    # Bind to an OS-selected loopback port. Pass the bound socket to Uvicorn to
    # avoid a race with another application claiming the port.
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(128)
    port = listener.getsockname()[1]
    config = uvicorn.Config(app, host="127.0.0.1", port=port,
                            log_level="warning", access_log=False,
                            lifespan="off")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]},
                              name="foxbat-api", daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{port}"

    try:
        # Wait for the server rather than opening a blank window.
        ready = False
        for _ in range(100):
            if not thread.is_alive():
                break
            try:
                with urlopen(url + "/api/health", timeout=0.2) as response:
                    if response.status == 200:
                        ready = True
                        break
            except (OSError, URLError):
                pass
            time.sleep(0.1)
        if not ready:
            raise RuntimeError("Foxbat local API did not start")

        controls = WindowControls()
        controls.window = webview.create_window(
            "Foxbat NIDS", url + "/?foxbat_desktop=1", width=1280, height=820,
            min_size=(900, 600), background_color="#060b09",
            frameless=True, easy_drag=False, js_api=controls,
        )
        # Windows: pywebview uses Microsoft Edge WebView2 where available.
        webview.start(gui="edge", debug=False)
    finally:
        # Closing the window must release the packet capture device.
        capture.stop()
        server.should_exit = True
        thread.join(timeout=8)
        try:
            listener.close()
        except OSError:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # With --windowed, errors otherwise disappear without a console.
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                None, f"Foxbat could not start:\n{exc}\n\nCheck that Microsoft Edge WebView2 Runtime is installed.",
                "Foxbat startup error", 0x10)
        else:
            print(f"Foxbat startup error: {exc}", file=sys.stderr)
        sys.exit(1)
