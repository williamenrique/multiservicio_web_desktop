"""
Modelo base con métodos CRUD genéricos.
Todos los modelos específicos heredan de aquí.
"""

from utils.connection_pool import ConnectionPool


class BaseModel:
    """Provee operaciones CRUD genéricas para cualquier tabla."""

    TABLE = None  # Lo define cada subclase

    @classmethod
    def get_all(cls, order_by=None, limit=None, offset=None):
        """Obtiene todos los registros activos."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = f"SELECT * FROM {cls.TABLE} WHERE estado = 'ACTIVO'"
                if order_by:
                    sql += f" ORDER BY {order_by}"
                if limit:
                    sql += f" LIMIT {limit}"
                    if offset:
                        sql += f" OFFSET {offset}"
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            ConnectionPool.release(conn)

    @classmethod
    def get_by_id(cls, record_id, id_field="id"):
        """Obtiene un registro por su ID."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = f"SELECT * FROM {cls.TABLE} WHERE {id_field} = %s"
                cursor.execute(sql, (record_id,))
                return cursor.fetchone()
        finally:
            ConnectionPool.release(conn)

    @classmethod
    def search(cls, field, value, exact=False):
        """Busca registros por un campo."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                if exact:
                    sql = f"SELECT * FROM {cls.TABLE} WHERE {field} = %s"
                    cursor.execute(sql, (value,))
                else:
                    sql = f"SELECT * FROM {cls.TABLE} WHERE {field} LIKE %s"
                    cursor.execute(sql, (f"%{value}%",))
                return cursor.fetchall()
        finally:
            ConnectionPool.release(conn)

    @classmethod
    def create(cls, data):
        """Inserta un nuevo registro. Retorna el ID insertado."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                columns = ", ".join(data.keys())
                placeholders = ", ".join(["%s"] * len(data))
                sql = f"INSERT INTO {cls.TABLE} ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, list(data.values()))
                conn.commit()
                return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            ConnectionPool.release(conn)

    @classmethod
    def update(cls, record_id, data, id_field="id"):
        """Actualiza un registro existente."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
                sql = f"UPDATE {cls.TABLE} SET {set_clause} WHERE {id_field} = %s"
                cursor.execute(sql, list(data.values()) + [record_id])
                conn.commit()
                return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            ConnectionPool.release(conn)

    @classmethod
    def delete(cls, record_id, id_field="id", soft=True):
        """Elimina (soft delete por defecto) o borra físicamente."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                if soft:
                    sql = f"UPDATE {cls.TABLE} SET estado = 'INACTIVO' WHERE {id_field} = %s"
                else:
                    sql = f"DELETE FROM {cls.TABLE} WHERE {id_field} = %s"
                cursor.execute(sql, (record_id,))
                conn.commit()
                return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            ConnectionPool.release(conn)

    @classmethod
    def count(cls, condition=None):
        """Cuenta registros, opcionalmente con condición WHERE."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = f"SELECT COUNT(*) as total FROM {cls.TABLE}"
                if condition:
                    sql += f" WHERE {condition}"
                cursor.execute(sql)
                return cursor.fetchone()["total"]
        finally:
            ConnectionPool.release(conn)