"""
Caché local de datos maestros usando SQLite.
Reduce viajes a la BD remota para catálogos que cambian poco
(clientes, productos, staff, etc.).
"""

import os
import json
import sqlite3
import time
from pathlib import Path

CACHE_DIR = Path(__file__).parent.parent / "cache"
CACHE_DB = CACHE_DIR / "local_cache.db"
CACHE_TTL = 300  # 5 minutos por defecto


def _ensure_cache_dir():
    CACHE_DIR.mkdir(exist_ok=True)


def _get_conn():
    _ensure_cache_dir()
    conn = sqlite3.connect(str(CACHE_DB))
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            data TEXT,
            expires_at REAL
        )"""
    )
    return conn


def get(key):
    """Obtiene un valor del caché. Retorna None si no existe o expiró."""
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT data, expires_at FROM cache WHERE key = ?", (key,)
        ).fetchone()
        if row:
            if time.time() < row["expires_at"]:
                return json.loads(row["data"])
            else:
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                conn.commit()
    finally:
        conn.close()
    return None


def set(key, data, ttl=CACHE_TTL):
    """Guarda un valor en el caché con tiempo de expiración."""
    conn = _get_conn()
    try:
        conn.execute(
            """INSERT OR REPLACE INTO cache (key, data, expires_at)
               VALUES (?, ?, ?)""",
            (key, json.dumps(data), time.time() + ttl),
        )
        conn.commit()
    finally:
        conn.close()


def invalidate(key):
    """Invalida una entrada del caché."""
    conn = _get_conn()
    try:
        conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        conn.commit()
    finally:
        conn.close()


def clear():
    """Limpia todo el caché."""
    conn = _get_conn()
    try:
        conn.execute("DELETE FROM cache")
        conn.commit()
    finally:
        conn.close()