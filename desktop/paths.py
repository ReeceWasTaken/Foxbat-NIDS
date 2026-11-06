"""Paths used by the packaged desktop application."""
import os
from pathlib import Path

def user_data_dir():
    """Store mutable files outside the read-only PyInstaller bundle."""
    root = os.getenv("LOCALAPPDATA")
    if root:
        return Path(root) / "Foxbat"
    return Path.home() / ".foxbat"

def configure_database():
    """Respect an explicit FOXBAT_DB override; otherwise use user data."""
    if "FOXBAT_DB" not in os.environ:
        folder = user_data_dir()
        folder.mkdir(parents=True, exist_ok=True)
        os.environ["FOXBAT_DB"] = str(folder / "foxbat.db")
    return Path(os.environ["FOXBAT_DB"])
