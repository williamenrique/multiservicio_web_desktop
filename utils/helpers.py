"""
Funciones auxiliares de formateo y utilidades.
Equivalentes a utils.js del sistema web.
"""

import re
from datetime import datetime


def formatear_moneda(monto):
    """Formatea un número como moneda: 1,234.56 Bs."""
    if monto is None:
        return "0,00 Bs"
    try:
        return f"{float(monto):,.2f} Bs".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "0,00 Bs"


def formatear_fecha(fecha, formato="%d/%m/%Y"):
    """Formatea una fecha a string. Acepta datetime, timestamp o string ISO."""
    if fecha is None:
        return ""
    if isinstance(fecha, datetime):
        return fecha.strftime(formato)
    if isinstance(fecha, str):
        try:
            dt = datetime.fromisoformat(fecha)
            return dt.strftime(formato)
        except ValueError:
            return fecha
    return str(fecha)


def formatear_fecha_hora(fecha):
    """Formatea fecha y hora: 14/07/2026 03:45 PM."""
    return formatear_fecha(fecha, "%d/%m/%Y %I:%M %p")


def formatear_cedula(cedula):
    """Formatea cédula: V-12345678."""
    if not cedula:
        return ""
    cedula = cedula.strip().upper()
    if re.match(r"^[VEJPG]", cedula):
        return cedula
    return f"V-{cedula}"


def formatear_telefono(telf):
    """Formatea teléfono: 0412-1234567."""
    if not telf:
        return ""
    telf = re.sub(r"[^\d]", "", telf)
    if len(telf) == 11:
        return f"{telf[:4]}-{telf[4:]}"
    return telf


def generar_id_tabla(prefijo, ultimo_id):
    """Genera un ID secuencial: STAFF-001, CLIENTE-042."""
    if ultimo_id is None:
        return f"{prefijo}-001"
    try:
        num = int(str(ultimo_id).split("-")[-1]) + 1
        return f"{prefijo}-{num:03d}"
    except (ValueError, IndexError):
        return f"{prefijo}-001"