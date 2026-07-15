"""
Modelo de Clientes.
Operaciones sobre table_clientes y table_vehiculos.
"""

from models.base_model import BaseModel
from utils.connection_pool import ConnectionPool


class ClienteModel(BaseModel):
    TABLE = "table_clientes"

    @classmethod
    def buscar(cls, termino):
        """Busca clientes por nombre, cédula o teléfono."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """SELECT * FROM table_clientes
                         WHERE nombre LIKE %s
                            OR id LIKE %s
                            OR telefono LIKE %s
                         ORDER BY nombre
                         LIMIT 20"""
                like = f"%{termino}%"
                cursor.execute(sql, (like, like, like))
                return cursor.fetchall()
        finally:
            ConnectionPool.release(conn)

    @classmethod
    def get_vehiculos(cls, cliente_id):
        """Obtiene los vehículos de un cliente."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM table_vehiculos WHERE cliente_id = %s"
                cursor.execute(sql, (cliente_id,))
                return cursor.fetchall()
        finally:
            ConnectionPool.release(conn)

    @classmethod
    def crear_vehiculo(cls, data):
        """Registra un vehículo para un cliente."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                columns = ", ".join(data.keys())
                placeholders = ", ".join(["%s"] * len(data))
                sql = f"INSERT INTO table_vehiculos ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, list(data.values()))
                conn.commit()
                return True
        except Exception:
            conn.rollback()
            raise
        finally:
            ConnectionPool.release(conn)