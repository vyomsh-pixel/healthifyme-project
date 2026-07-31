import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_initialise_database_without_database_url(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SQLITE_DB_PATH", str(tmp_path / "healthio.sqlite3"))
    monkeypatch.setenv("PYTHONPATH", str(ROOT.parent))

    import backend.database as database_module
    database_module = importlib.reload(database_module)

    database_module.initialise_database()

    assert (tmp_path / "healthio.sqlite3").exists()
