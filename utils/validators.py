"""
Validadores de datos.
Equivalentes a Validator.php del sistema web.
"""

import re


def cedula_valida(cedula):
    """Valida cédula venezolana (V-12345678 o 12345678)."""
    if not cedula:
        return False
    cedula = cedula.strip().upper()
    return bool(re.match(r"^[VEJPG]?-?\d{5,10}$", cedula))


def nit_valido(nit):
    """Valida NIT básico."""
    if not nit:
        return False
    return bool(re.match(r"^\d{6,15}(-\d{1})?$", nit.strip()))


def email_valido(email):
    """Valida formato de email."""
    if not email:
        return False
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email.strip()))


def telefono_valido(telefono):
    """Valida teléfono venezolano (0412-1234567 o +584121234567)."""
    if not telefono:
        return False
    telefono = telefono.strip()
    return bool(re.match(r"^(\+?\d{1,3})?[\s-]?\d{3,4}[\s-]?\d{7}$", telefono))


def monto_valido(monto):
    """Valida que un monto sea un número positivo."""
    try:
        return float(monto) >= 0
    except (ValueError, TypeError):
        return False


def requerido(valor):
    """Valida que un campo no esté vacío."""
    return valor is not None and str(valor).strip() != ""