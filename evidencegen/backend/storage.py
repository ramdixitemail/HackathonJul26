"""
Tiny JSON-file storage — no database setup required for the demo.
Swap for real Postgres/SQLite later by reimplementing this module's
four functions with the same signatures.
"""
import os
import json
import threading

_LOCK = threading.Lock()
_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
_FILE = os.path.join(_DATA_DIR, "packs.json")


def _ensure_file():
    os.makedirs(_DATA_DIR, exist_ok=True)
    if not os.path.exists(_FILE):
        with open(_FILE, "w") as f:
            json.dump({}, f)


def list_packs():
    _ensure_file()
    with _LOCK, open(_FILE) as f:
        data = json.load(f)
    return sorted(data.values(), key=lambda p: p.get("created_at", ""), reverse=True)


def get_pack(pack_id):
    _ensure_file()
    with _LOCK, open(_FILE) as f:
        data = json.load(f)
    return data.get(pack_id)


def save_pack(pack):
    _ensure_file()
    with _LOCK:
        with open(_FILE) as f:
            data = json.load(f)
        data[pack["id"]] = pack
        with open(_FILE, "w") as f:
            json.dump(data, f, indent=2)
    return pack


def delete_pack(pack_id):
    _ensure_file()
    with _LOCK:
        with open(_FILE) as f:
            data = json.load(f)
        data.pop(pack_id, None)
        with open(_FILE, "w") as f:
            json.dump(data, f, indent=2)
