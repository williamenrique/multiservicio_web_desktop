"""
config/settings.py
Constantes globales, rutas de recursos, colores y estilos de la UI (Flet).
"""

import os

# ── Rutas base ──────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")

# ── Dimensiones de la ventana ───────────────────────────
APP_NAME = "Taller Multiservicio PRO"
APP_VERSION = "2.0"
APP_TITLE = APP_NAME
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 680

# ── Colores corporativos (paleta taller automotriz) ─────
COLOR_PRIMARY = "#1A237E"
COLOR_PRIMARY_LIGHT = "#3949AB"
COLOR_ACCENT = "#FF6F00"
COLOR_BG = "#F5F5F5"
COLOR_BACKGROUND = COLOR_BG
COLOR_SURFACE = "#FFFFFF"
COLOR_TEXT = "#212121"
COLOR_TEXT_PRIMARY = COLOR_TEXT
COLOR_TEXT_SECONDARY = "#757575"
COLOR_SUCCESS = "#2E7D32"
COLOR_WARNING = "#F57F17"
COLOR_ERROR = "#C62828"
COLOR_DIVIDER = "#BDBDBD"

# ── Estados de órdenes de servicio ──────────────────────
ESTADOS_ORDEN = [
    "RECIBIDO",
    "DIAGNOSTICANDO",
    "EN_REPARACION",
    "LISTO",
    "ENTREGADO",
    "CANCELADO",
]

# ── Roles del sistema ───────────────────────────────────
ROLES = {
    1: "ADMINISTRADOR",
    2: "MECANICO",
    3: "CAJERO",
}

# ── Configuración de sesión ─────────────────────────────
SESSION_TIMEOUT_MINUTES = 30
MAX_LOGIN_ATTEMPTS = 5