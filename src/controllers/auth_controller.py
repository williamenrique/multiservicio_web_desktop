"""
src/controllers/auth_controller.py
Controlador de autenticación: login, logout, verificación de sesión.
"""

from src.models.user_model import UserModel


class AuthController:
    """Lógica de negocio para autenticación y sesiones."""

    def __init__(self):
        self._current_user: dict | None = None

    @property
    def current_user(self) -> dict | None:
        return self._current_user

    @property
    def is_authenticated(self) -> bool:
        return self._current_user is not None

    @property
    def is_admin(self) -> bool:
        return self._current_user and self._current_user.get("role_id") == 1

    @property
    def is_mecanico(self) -> bool:
        return self._current_user and self._current_user.get("role_id") == 2

    @property
    def is_cajero(self) -> bool:
        return self._current_user and self._current_user.get("role_id") == 3

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Intenta autenticar al usuario.
        Retorna (éxito, mensaje).
        """
        if not username or not password:
            return False, "Usuario y contraseña son requeridos"

        user = UserModel.authenticate(username.strip(), password)
        if user is None:
            return False, "Usuario o contraseña incorrectos"

        self._current_user = user
        return True, f"Bienvenido, {user['nombre']}"

    def logout(self) -> None:
        """Cierra la sesión activa."""
        if self._current_user:
            UserModel.end_session(self._current_user["id"])
            self._current_user = None

    def get_user_display_name(self) -> str:
        """Nombre para mostrar en la UI."""
        if self._current_user:
            return self._current_user.get("nombre", self._current_user.get("username", ""))
        return ""

    def get_user_role_name(self) -> str:
        """Nombre del rol para mostrar."""
        if self._current_user:
            role_map = {1: "Administrador", 2: "Mecánico", 3: "Cajero"}
            return role_map.get(self._current_user.get("role_id"), "Usuario")
        return ""