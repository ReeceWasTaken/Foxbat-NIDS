import os
from desktop.paths import configure_database, user_data_dir

def test_desktop_database_path(monkeypatch, tmp_path):
    monkeypatch.delenv("FOXBAT_DB", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    path = configure_database()
    assert path == tmp_path / "Foxbat" / "foxbat.db"
    assert os.environ["FOXBAT_DB"] == str(path)
    assert path.parent.is_dir()

def test_database_override(monkeypatch, tmp_path):
    path = tmp_path / "custom.db"
    monkeypatch.setenv("FOXBAT_DB", str(path))
    assert configure_database() == path
