"""
Pool de conexiones MySQL con reconexión automática.
Ideal para app desktop que conecta a BD remota.
"""

import time
import pymysql
from pymysql.cursors import DictCursor
from config.database import DB_CONFIG


class ConnectionPool:
    """Pool simple de conexiones MySQL con reintentos."""

    _pool = []
    _max_connections = 5
    _retry_attempts = 3
    _retry_delay = 1  # segundos

    @classmethod
    def get_connection(cls):
        """Obtiene una conexión del pool o crea una nueva."""
        if cls._pool:
            conn = cls._pool.pop()
            try:
                conn.ping(reconnect=True)
                return conn
            except pymysql.Error:
                pass  # La conexión murió, crear una nueva
        return cls._create_connection()

    @classmethod
    def _create_connection(cls):
        """Crea una nueva conexión con reintentos."""
        for attempt in range(1, cls._retry_attempts + 1):
            try:
                return pymysql.connect(**DB_CONFIG)
            except pymysql.Error as e:
                if attempt == cls._retry_attempts:
                    raise ConnectionError(
                        f"No se pudo conectar a la BD tras {cls._retry_attempts} intentos: {e}"
                    )
                time.sleep(cls._retry_delay)

    @classmethod
    def release(cls, conn):
        """Devuelve la conexión al pool si está viva."""
        if conn:
            try:
                conn.ping(reconnect=True)
                if len(cls._pool) < cls._max_connections:
                    cls._pool.append(conn)
                else:
                    conn.close()
            except pymysql.Error:
                conn.close()

    @classmethod
    def close_all(cls):
        """Cierra todas las conexiones del pool."""
        for conn in cls._pool:
            try:
                conn.close()
            except pymysql.Error:
                pass
        cls._pool.clear()