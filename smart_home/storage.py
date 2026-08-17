from __future__ import annotations

import json
import os
import sqlite3
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet


def _base_dir() -> Path:
    """Resolve base dir compatible with both dev and PyInstaller frozen modes."""
    if getattr(sys, "frozen", False):
        # Frozen: use per-user writable data dir
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        if local_app_data:
            return Path(local_app_data) / "Brahma Echo"
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _base_dir()
CONFIG_DIR = BASE_DIR / "config"
DB_FILE = CONFIG_DIR / "smart_home.sqlite3"
KEY_FILE = CONFIG_DIR / "smart_home.key"


def _ensure_dir() -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)


def _now_ms() -> int:
    return int(time.time() * 1000)


class CredentialVault:
    def __init__(self, key_file: Path = KEY_FILE):
        _ensure_dir()
        self._key_file = Path(key_file)
        self._fernet = Fernet(self._load_or_create_key())

    def _load_or_create_key(self) -> bytes:
        if self._key_file.exists():
            return self._key_file.read_bytes().strip()
        key = Fernet.generate_key()
        self._key_file.write_bytes(key)
        return key

    def encrypt_json(self, payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        return self._fernet.encrypt(raw).decode("utf-8")

    def decrypt_json(self, payload: str | None) -> dict[str, Any]:
        if not payload:
            return {}
        try:
            data = self._fernet.decrypt(payload.encode("utf-8"))
            obj = json.loads(data.decode("utf-8"))
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return {}


class SmartHomeStorage:
    def __init__(self, db_path: Path | None = None):
        _ensure_dir()
        self._db_path = Path(db_path or DB_FILE)
        self._lock = threading.RLock()
        self._vault = CredentialVault()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, timeout=10, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self) -> None:
        with self._lock, self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS provider_accounts (
                    id TEXT PRIMARY KEY,
                    provider_key TEXT NOT NULL,
                    account_label TEXT NOT NULL,
                    credentials_encrypted TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS devices (
                    id TEXT PRIMARY KEY,
                    provider_account_id TEXT NOT NULL,
                    provider_key TEXT NOT NULL,
                    external_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    manufacturer TEXT NOT NULL,
                    room TEXT NOT NULL,
                    device_type TEXT NOT NULL,
                    image_key TEXT NOT NULL,
                    is_on INTEGER NOT NULL DEFAULT 0,
                    traits_json TEXT NOT NULL DEFAULT '{}',
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    UNIQUE(provider_account_id, external_id)
                );

                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    detail TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS scenes (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    config_json TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                );
                """
            )

    def save_provider_account(self, provider_key: str, account_label: str, credentials: dict[str, Any]) -> str:
        account_id = str(uuid.uuid4())
        stamp = _now_ms()
        enc = self._vault.encrypt_json(credentials)
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT id FROM provider_accounts WHERE provider_key = ? AND account_label = ?",
                (provider_key, account_label),
            ).fetchone()
            if row:
                account_id = row["id"]
                conn.execute(
                    """
                    UPDATE provider_accounts
                    SET credentials_encrypted = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (enc, stamp, account_id),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO provider_accounts(id, provider_key, account_label, credentials_encrypted, created_at, updated_at)
                    VALUES(?, ?, ?, ?, ?, ?)
                    """,
                    (account_id, provider_key, account_label, enc, stamp, stamp),
                )
        return account_id

    def get_provider_account(self, account_id: str) -> dict[str, Any] | None:
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT * FROM provider_accounts WHERE id = ?", (account_id,)).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "provider_key": row["provider_key"],
            "account_label": row["account_label"],
            "credentials": self._vault.decrypt_json(row["credentials_encrypted"]),
            "created_at": int(row["created_at"]),
            "updated_at": int(row["updated_at"]),
        }

    def save_devices(self, provider_account_id: str, provider_key: str, devices: list[dict[str, Any]]) -> list[str]:
        stamp = _now_ms()
        saved: list[str] = []
        with self._lock, self._connect() as conn:
            for device in devices:
                row = conn.execute(
                    "SELECT id FROM devices WHERE provider_account_id = ? AND external_id = ?",
                    (provider_account_id, str(device["external_id"])),
                ).fetchone()
                device_id = row["id"] if row else str(uuid.uuid4())
                payload = json.dumps(device.get("traits", {}), ensure_ascii=True)
                if row:
                    conn.execute(
                        """
                        UPDATE devices
                        SET name = ?, manufacturer = ?, room = ?, device_type = ?, image_key = ?, is_on = ?, traits_json = ?, updated_at = ?
                        WHERE id = ?
                        """,
                        (
                            str(device["name"]),
                            str(device.get("manufacturer", "")),
                            str(device.get("room", "Unassigned")),
                            str(device.get("device_type", "device")),
                            str(device.get("image_key", "device")),
                            1 if bool(device.get("is_on")) else 0,
                            payload,
                            stamp,
                            device_id,
                        ),
                    )
                else:
                    conn.execute(
                        """
                        INSERT INTO devices(id, provider_account_id, provider_key, external_id, name, manufacturer, room, device_type, image_key, is_on, traits_json, created_at, updated_at)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            device_id,
                            provider_account_id,
                            provider_key,
                            str(device["external_id"]),
                            str(device["name"]),
                            str(device.get("manufacturer", "")),
                            str(device.get("room", "Unassigned")),
                            str(device.get("device_type", "device")),
                            str(device.get("image_key", "device")),
                            1 if bool(device.get("is_on")) else 0,
                            payload,
                            stamp,
                            stamp,
                        ),
                    )
                saved.append(device_id)
        return saved

    def list_devices(self, search: str = "", room: str = "") -> list[dict[str, Any]]:
        where: list[str] = []
        params: list[Any] = []
        if search:
            like = f"%{search.strip()}%"
            where.append("(name LIKE ? OR manufacturer LIKE ? OR room LIKE ?)")
            params.extend([like, like, like])
        if room:
            where.append("room = ?")
            params.append(room)
        clause = f" WHERE {' AND '.join(where)}" if where else ""
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                f"SELECT * FROM devices{clause} ORDER BY updated_at DESC",
                params,
            ).fetchall()
        result: list[dict[str, Any]] = []
        for row in rows:
            d = dict(row)
            d["is_on"] = bool(d["is_on"])
            d["traits"] = json.loads(d.pop("traits_json", "{}") or "{}")
            result.append(d)
        return result

    def get_device(self, device_id: str) -> dict[str, Any] | None:
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT * FROM devices WHERE id = ?", (str(device_id),)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["is_on"] = bool(d["is_on"])
        d["traits"] = json.loads(d.pop("traits_json", "{}") or "{}")
        return d

    def update_device(self, device_id: str, **fields) -> None:
        allowed = {"name", "room", "is_on", "traits", "manufacturer", "device_type"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return
        set_parts: list[str] = []
        params: list[Any] = []
        if "traits" in updates:
            updates["traits"] = json.dumps(updates["traits"], ensure_ascii=True)
        if "is_on" in updates:
            updates["is_on"] = 1 if updates["is_on"] else 0
        for k, v in updates.items():
            set_parts.append(f"{k} = ?")
            params.append(v)
        set_parts.append("updated_at = ?")
        params.append(_now_ms())
        params.append(str(device_id))
        with self._lock, self._connect() as conn:
            conn.execute(f"UPDATE devices SET {', '.join(set_parts)} WHERE id = ?", params)

    def forget_device(self, device_id: str) -> None:
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM devices WHERE id = ?", (str(device_id),))

    def recent_activity(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM activities ORDER BY created_at DESC LIMIT ?",
                (int(limit),),
            ).fetchall()
        return [dict(row) for row in rows]

    def log_activity(self, title: str, detail: str) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO activities(created_at, title, detail) VALUES (?, ?, ?)",
                (_now_ms(), str(title), str(detail)),
            )

    def count_devices(self) -> int:
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) as cnt FROM devices").fetchone()
        return int(row["cnt"])

    def list_scenes(self) -> list[dict[str, Any]]:
        with self._lock, self._connect() as conn:
            rows = conn.execute("SELECT * FROM scenes ORDER BY name").fetchall()
        return [dict(row) for row in rows]

    def save_scene(self, scene_id: str, name: str, config: dict[str, Any]) -> None:
        stamp = _now_ms()
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT id FROM scenes WHERE id = ?", (scene_id,)).fetchone()
            payload = json.dumps(config, ensure_ascii=True)
            if row:
                conn.execute(
                    "UPDATE scenes SET name = ?, config_json = ?, updated_at = ? WHERE id = ?",
                    (name, payload, stamp, scene_id),
                )
            else:
                conn.execute(
                    "INSERT INTO scenes(id, name, config_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (scene_id, name, payload, stamp, stamp),
                )

    def delete_scene(self, scene_id: str) -> None:
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM scenes WHERE id = ?", (scene_id,))
