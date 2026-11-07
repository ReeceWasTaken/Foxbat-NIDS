"""Launch Foxbat in an embedded Edge WebView2 window.

The API stays on loopback, with one Uvicorn server and one capture worker.
"""
import socket
import os
import logging
from logging.handlers import RotatingFileHandler
import sys
import threading
import time
from urllib.error import URLError
from urllib.request import urlopen

from desktop.paths import configure_database, user_data_dir


# Keep native WinForms / WebView2 objects OUTSIDE the object pywebview
# recursively inspects when generating its JavaScript API. Previously the
# public `controls.window` attribute exposed the complete native window graph,
# causing get_functions() recursion and DefaultFont/FontFamily errors.
_native_window = None
_native_maximized = False


class WindowControls:
    """A deliberately leaf-only JS API: exactly three public methods.

    No instance attributes, especially no pywebview Window / .NET objects.
    """

    __slots__ = ()

    def minimize(self):
        if _native_window is None:
            return False
        _native_window.minimize()
        return True

    def toggle_maximize(self):
        global _native_maximized
        if _native_window is None:
            return False
        if _native_maximized:
            _native_window.restore()
        else:
            _native_window.maximize()
        _native_maximized = not _native_maximized
        return _native_maximized

    def close(self):
        if _native_window is None:
            return False
        _native_window.destroy()
        return True


def setup_logging():
    """Keep a small local log so installed builds can be diagnosed."""
    log_dir = user_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(log_dir / "desktop.log", maxBytes=1_000_000,
                                  backupCount=2, encoding="utf-8")
    logging.basicConfig(level=logging.INFO, handlers=[handler],
                        format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Foxbat v0.8.14 desktop starting")


def main():
    """Start the production desktop shell with the working leaf-only JS bridge."""
    setup_logging()
    run_application()


def run_application():
    # Must happen BEFORE app.main is imported (it reads FOXBAT_DB at import time).
    configure_database()
    # Set WebView2 flags before the Edge runtime is initialized.
    # Override with FOXBAT_DISABLE_GPU=0 to compare rendering behavior.
    disable_gpu = os.environ.get("FOXBAT_DISABLE_GPU", "1") != "0"
    if disable_gpu:
        args = os.environ.get("WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS", "")
        if "--disable-gpu" not in args.split():
            os.environ["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = (args + " --disable-gpu").strip()
    logging.info("WebView2 GPU disabled: %s", disable_gpu)
    # Production shell: integrated Foxbat title bar and native pywebview drag.
    # Do not restore the old Win32 mouse polling code.
    frameless = True
    logging.info("Frameless window enabled: %s", frameless)
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

        global _native_window, _native_maximized
        _native_maximized = False
        controls = WindowControls()
        _native_window = webview.create_window(
            "Foxbat NIDS", url + "/?foxbat_desktop=1", width=1280, height=820,
            min_size=(900, 600), background_color="#060b09",
            frameless=frameless, easy_drag=frameless, js_api=controls,
        )
        # Windows: pywebview uses Microsoft Edge WebView2 where available.
        # Keep WebView2's writable profile outside the installed application.
        # The application can be upgraded without touching browser cache files.
        webview_data = user_data_dir() / "webview2"
        webview_data.mkdir(parents=True, exist_ok=True)
        logging.info("Starting WebView2; profile directory: %s", webview_data)
        webview.start(gui="edge", debug=False, storage_path=str(webview_data))
    finally:
        # Closing the window must release the packet capture device.
        logging.info("Desktop closing")
        _native_window = None
        capture.stop()
        server.should_exit = True
        logging.info("Waiting up to 8 seconds for API thread to stop")
        thread.join(timeout=8)
        logging.info("API thread still alive: %s", thread.is_alive())
        try:
            listener.close()
        except OSError:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logging.exception("Desktop startup failed")
        # With --windowed, errors otherwise disappear without a console.
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                None, f"Foxbat could not start:\n{exc}\n\nCheck that Microsoft Edge WebView2 Runtime is installed.",
                "Foxbat startup error", 0x10)
        else:
            print(f"Foxbat startup error: {exc}", file=sys.stderr)
        sys.exit(1)
