"""
database/connection.py
Gestor de conexiones MySQL usando context manager y pool de conexiones.
Usa pymysql (ya listado en requirements.txt).
"""

import pymysql
from config.db_config import DB_CONFIG


class DatabaseConnection:
    """Context manager para conexiones MySQL con pymysql."""

    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            charset=DB_CONFIG["charset"],
            autocommit=DB_CONFIG.get("autocommit", False),
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
        else:
            self.conn.commit()
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute(self, query: str, params: tuple = None):
        """Ejecuta una consulta SQL con parámetros."""
        self.cursor.execute(query, params or ())
        return self.cursor

    def fetchone(self, query: str, params: tuple = None):
        """Ejecuta y retorna un solo registro como dict."""
        self.execute(query, params)
        return self.cursor.fetchone()

    def fetchall(self, query: str, params: tuple = None):
        """Ejecuta y retorna todos los registros como lista de dicts."""
        self.execute(query, params)
        return self.cursor.fetchall()

    def insert(self, query: str, params: tuple = None):
        """Ejecuta INSERT y retorna el último ID."""
        self.execute(query, params)
        return self.cursor.lastrowid

    def update(self, query: str, params: tuple = None):
        """Ejecuta UPDATE/DELETE y retorna filas afectadas."""
        self.execute(query, params)
        return self.cursor.rowcount