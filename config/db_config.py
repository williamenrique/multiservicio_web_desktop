"""
config/db_config.py
Configuración de conexión a la base de datos MySQL.
Lee credenciales desde variables de entorno (.env).
"""

import os
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "multiservicio_2.0"),
    "charset": "utf8mb4",
    "autocommit": False,
    "pool_size": 5,
}