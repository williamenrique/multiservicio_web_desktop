"""
Configuración de la base de datos.
Usa un pool de conexiones para evitar timeouts con BD remota.
"""

import os
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "multiservicio_2.0"),
    "cursorclass": DictCursor,
    "charset": "utf8mb4",
}


def get_connection():
    """Obtiene una conexión nueva. Se llama y se cierra por operación."""
    return pymysql.connect(**DB_CONFIG)