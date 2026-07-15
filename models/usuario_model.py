"""
Modelo de Usuarios.
Operaciones sobre table_usuarios, table_staff, table_roles.
Usa bcrypt para verificación segura de contraseñas.
"""

import bcrypt
from models.base_model import BaseModel
from utils.connection_pool import ConnectionPool


class UsuarioModel(BaseModel):
    TABLE = "table_usuarios"

    @staticmethod
    def verificar_credenciales(username, password):
        """
        Verifica credenciales contra la BD.
        Soporta tanto contraseñas con hash bcrypt como texto plano
        (para compatibilidad con el sistema web existente).
        """
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """SELECT u.id, u.username, u.password, u.role_id, r.nombre_rol,
                                u.staff_id, s.nombre as staff_nombre
                         FROM table_usuarios u
                         LEFT JOIN table_roles r ON u.role_id = r.id
                         LEFT JOIN table_staff s ON u.staff_id = s.id
                         WHERE u.username = %s AND u.estado = 'ACTIVO'"""
                cursor.execute(sql, (username,))
                user = cursor.fetchone()

                if not user:
                    return None

                # Intentar verificar con bcrypt primero
                stored_pw = user["password"]
                if stored_pw.startswith("$2b$") or stored_pw.startswith("$2a$"):
                    if bcrypt.checkpw(password.encode("utf-8"), stored_pw.encode("utf-8")):
                        return user
                else:
                    # Compatibilidad: contraseña en texto plano (sistema web actual)
                    if password == stored_pw:
                        return user

                return None
        except Exception as e:
            print(f"Error en verificar_credenciales: {e}")
            return None
        finally:
            ConnectionPool.release(conn)

    @staticmethod
    def hash_password(password):
        """Genera un hash bcrypt de la contraseña."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def cambiar_password(usuario_id, nueva_password):
        """Actualiza la contraseña de un usuario con hash bcrypt."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                hashed = UsuarioModel.hash_password(nueva_password)
                cursor.execute(
                    "UPDATE table_usuarios SET password = %s WHERE id = %s",
                    (hashed, usuario_id),
                )
                conn.commit()
                return True
        except Exception:
            conn.rollback()
            raise
        finally:
            ConnectionPool.release(conn)

    @staticmethod
    def get_usuarios_con_staff():
        """Lista todos los usuarios con información del staff."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """SELECT u.*, s.nombre as staff_nombre, s.cedula,
                                r.nombre_rol
                         FROM table_usuarios u
                         LEFT JOIN table_staff s ON u.staff_id = s.id
                         LEFT JOIN table_roles r ON u.role_id = r.id
                         ORDER BY s.nombre"""
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            ConnectionPool.release(conn)