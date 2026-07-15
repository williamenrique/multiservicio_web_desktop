# config/settings.py
import os
import customtkinter as ctk

# ==========================================
# 1. RUTAS DEL SISTEMA (Gestión de Rutas)
# ==========================================
# Obtiene la ruta base del proyecto para evitar errores de archivos no encontrados
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")

# ==========================================
# 2. CONFIGURACIÓN DEL MOTOR VISUAL
# ==========================================
APP_THEME = "dark"          # Opciones globales: "system", "dark", "light"
COLOR_THEME = "blue"        # Esquema base predefinido de CustomTkinter (blue, green, dark-blue)

# ==========================================
# 3. PALETA DE COLORES PERSONALIZADA (Premium Slate)
# ==========================================
# Formato: ("Color en Modo Claro", "Color en Modo Oscuro")
BG_PRINCIPAL = ("#F1F5F9", "#0F172A")       # Fondos de ventanas principales
BG_TARJETAS = ("#FFFFFF", "#1E293B")        # Contenedores, páneles y formularios
BG_NAVEGACION = ("#E2E8F0", "#0B0F19")      # Barra lateral o menú superior

# Colores de Acento y Estados del Taller
ACCENTO_TALLER = "#3B82F6"                  # Azul Eléctrico (Botones principales, selección)
ACCENTO_HOVER = "#2563EB"                   # Azul más oscuro para efecto hover al pasar el mouse
ACCENTO_EXITO = "#10B981"                   # Verde (Servicios listos, pagos procesados)
ACCENTO_ALERTA = "#F59E0B"                  # Naranja (Vehículos en espera de repuesto)
ACCENTO_PELIGRO = "#EF4444"                 # Rojo (Vehículos críticos, deudas, eliminar)

# Tipografías y Textos
TEXTO_PRINCIPAL = ("#0F172A", "#F8FAFC")
TEXTO_MUTED = ("#64748B", "#94A3B8")        # Para subtítulos o texto secundario

# ==========================================
# 4. TIPOGRAFÍAS CORPORATIVAS
# ==========================================
FONT_FAMILY = "Segoe UI"  # Altamente legible en Windows/Linux. Cambiar a "San Francisco" en macOS si se prefiere.

FONT_TITULO_PRINCIPAL = (FONT_FAMILY, 28, "bold")
FONT_TITULO_MODULO = (FONT_FAMILY, 22, "bold")
FONT_SUBTITULO = (FONT_FAMILY, 14, "medium")
FONT_BODY = (FONT_FAMILY, 13, "normal")
FONT_BODY_BOLD = (FONT_FAMILY, 13, "bold")
FONT_BOTONES = (FONT_FAMILY, 13, "medium")

# ==========================================
# 5. FUNCIÓN DE INICIALIZACIÓN
# ==========================================
def aplicar_configuracion_visual():
    """
    Aplica las configuraciones globales de apariencia y tema al motor de CustomTkinter.
    Debe llamarse en el arranque de la app (main.py) antes de inicializar el CTk.
    """
    ctk.set_appearance_mode(APP_THEME)
    ctk.set_default_color_theme(COLOR_THEME)