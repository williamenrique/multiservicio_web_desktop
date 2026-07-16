"""
src/models/user_model.py
Modelo de usuarios: autenticación, CRUD de usuarios, sesiones.
Acoplado a: table_usuarios, table_staff, table_roles, table_usuario_sessions
"""

import hashlib
import bcrypt
from database.connection import DatabaseConnection


class UserModel:
    """Gestión de usuarios y autenticación."""

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hashea contraseña con bcrypt (compatible con password_hash de PHP)."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def _verify_password(password: str, stored: str) -> bool:
        """
        Verifica contraseña:
        - Si stored empieza con $2y$ o $2b$ → bcrypt, comparar con bcrypt.
        - Si no → texto plano, comparar directo.
        """
        if stored.startswith("$2y$") or stored.startswith("$2b$") or stored.startswith("$2a$"):
            # Compatibilidad PHP: $2y$ → $2b$ en Python bcrypt
            stored_fixed = stored.replace("$2y$", "$2b$")
            return bcrypt.checkpw(password.encode("utf-8"), stored_fixed.encode("utf-8"))
        else:
            # Texto plano: comparación directa
            return password == stored

    @staticmethod
    def authenticate(username: str, password: str) -> dict | None:
        """
        Autentica usuario contra table_usuarios.
        Retorna dict con datos del usuario o None si falla.
        Si la contraseña estaba en texto plano, la actualiza a bcrypt.
        """
        with DatabaseConnection() as db:
            user = db.fetchone(
                """
                SELECT u.id, u.username, u.password, u.role_id, u.estado,
                       s.id AS staff_id, s.nombre, s.cedula, s.cargo, s.foto
                FROM table_usuarios u
                LEFT JOIN table_staff s ON u.staff_id = s.id
                WHERE u.username = %s
                """,
                (username,),
            )

            if not user:
                return None

            if user["estado"] != "ACTIVO":
                return None

            if not UserModel._verify_password(password, user["password"]):
                return None

            # Si la contraseña estaba en texto plano, la hasheamos ahora
            if not user["password"].startswith("$2"):
                new_hash = UserModel._hash_password(password)
                db.update(
                    "UPDATE table_usuarios SET password = %s WHERE id = %s",
                    (new_hash, user["id"]),
                )

            # Registrar sesión activa (single session)
            db.update(
                """
                INSERT INTO table_usuario_sessions (usuario_id, session_id, ip_address)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE session_id = VALUES(session_id),
                                        ip_address = VALUES(ip_address),
                                        last_activity = CURRENT_TIMESTAMP
                """,
                (user["id"], f"sess_{user['id']}_{hashlib.md5(username.encode()).hexdigest()[:8]}", "127.0.0.1"),
            )

            return {
                "id": user["id"],
                "username": user["username"],
                "role_id": user["role_id"],
                "staff_id": user["staff_id"],
                "nombre": user["nombre"],
                "cedula": user["cedula"],
                "cargo": user["cargo"],
                "foto": user["foto"],
            }

    @staticmethod
    def get_all_users() -> list[dict]:
        """Obtiene todos los usuarios activos con su staff y rol."""
        with DatabaseConnection() as db:
            return db.fetchall(
                """
                SELECT u.id, u.username, u.estado, u.role_id, r.nombre_rol,
                       s.id AS staff_id, s.nombre, s.cedula, s.cargo
                FROM table_usuarios u
                LEFT JOIN table_staff s ON u.staff_id = s.id
                LEFT JOIN table_roles r ON u.role_id = r.id
                ORDER BY u.id
                """
            )

    @staticmethod
    def create_user(staff_id: str, username: str, password: str, role_id: int) -> int:
        """Crea un nuevo usuario con contraseña hasheada."""
        hashed = UserModel._hash_password(password)
        with DatabaseConnection() as db:
            return db.insert(
                """
                INSERT INTO table_usuarios (staff_id, username, password, role_id, estado)
                VALUES (%s, %s, %s, %s, 'ACTIVO')
                """,
                (staff_id, username, hashed, role_id),
            )

    @staticmethod
    def update_password(user_id: int, new_password: str) -> bool:
        """Actualiza la contraseña de un usuario."""
        hashed = UserModel._hash_password(new_password)
        with DatabaseConnection() as db:
            rows = db.update(
                "UPDATE table_usuarios SET password = %s WHERE id = %s",
                (hashed, user_id),
            )
            return rows > 0

    @staticmethod
    def get_user_by_id(user_id: int) -> dict | None:
        """Obtiene datos completos de un usuario por ID."""
        with DatabaseConnection() as db:
            return db.fetchone(
                """
                SELECT u.id, u.username, u.role_id, u.estado,
                       s.id AS staff_id, s.nombre, s.cedula, s.cargo,
                       s.telefono, s.email, s.direccion, s.foto
                FROM table_usuarios u
                LEFT JOIN table_staff s ON u.staff_id = s.id
                WHERE u.id = %s
                """,
                (user_id,),
            )

    @staticmethod
    def end_session(user_id: int) -> None:
        """Cierra la sesión activa del usuario."""
        with DatabaseConnection() as db:
            db.update(
                "DELETE FROM table_usuario_sessions WHERE usuario_id = %s",
                (user_id,),
            )