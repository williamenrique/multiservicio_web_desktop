"""
Controlador de Login.
Maneja la autenticación de usuarios y gestión de sesión.
"""

from models.usuario_model import UsuarioModel


class LoginController:
    """Orquesta la autenticación y el estado de sesión."""

    _current_user = None

    @classmethod
    def login(cls, username, password):
        """
        Intenta autenticar al usuario.
        Retorna dict con datos del usuario o None si falla.
        """
        user = UsuarioModel.verificar_credenciales(username, password)
        if user:
            cls._current_user = {
                "id": user["id"],
                "username": user["username"],
                "role_id": user["role_id"],
                "nombre_rol": user["nombre_rol"],
                "staff_id": user["staff_id"],
                "staff_nombre": user["staff_nombre"],
            }
        return cls._current_user

    @classmethod
    def logout(cls):
        """Cierra la sesión del usuario actual."""
        cls._current_user = None

    @classmethod
    def get_current_user(cls):
        """Retorna el usuario autenticado o None."""
        return cls._current_user

    @classmethod
    def is_authenticated(cls):
        """Verifica si hay un usuario autenticado."""
        return cls._current_user is not None

    @classmethod
    def has_role(cls, role_name):
        """Verifica si el usuario tiene un rol específico."""
        if not cls._current_user:
            return False
        return cls._current_user.get("nombre_rol") == role_name

    @classmethod
    def cambiar_password(cls, usuario_id, nueva_password):
        """Cambia la contraseña del usuario."""
        return UsuarioModel.cambiar_password(usuario_id, nueva_password)