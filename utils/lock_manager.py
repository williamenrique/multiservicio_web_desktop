"""
Control de concurrencia para operaciones críticas.
Evita condiciones de carrera cuando la app desktop y la web
acceden a la misma BD simultáneamente.
"""

from contextlib import contextmanager
from utils.connection_pool import ConnectionPool


class LockManager:
    """
    Maneja locks optimistas y pesimistas a nivel de aplicación.
    Usa tablas de la BD o un archivo de lock local.
    """

    @staticmethod
    @contextmanager
    def pessimistic_lock(table_name, record_id):
        """
        Lock pesimista usando SELECT ... FOR UPDATE.
        Bloquea el registro hasta que se complete la transacción.
        Uso: with LockManager.pessimistic_lock('table_inventario', 5): ...
        """
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"SELECT id FROM {table_name} WHERE id = %s FOR UPDATE",
                    (record_id,),
                )
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            ConnectionPool.release(conn)

    @staticmethod
    def optimistic_lock(conn, table_name, record_id, expected_version, new_data):
        """
        Lock optimista: actualiza solo si la versión no ha cambiado.
        Retorna True si se actualizó, False si hubo conflicto.
        """
        with conn.cursor() as cursor:
            cursor.execute(
                f"SELECT version FROM {table_name} WHERE id = %s FOR UPDATE",
                (record_id,),
            )
            row = cursor.fetchone()
            if not row or row["version"] != expected_version:
                return False  # Conflicto: otro proceso modificó el registro

            set_clause = ", ".join([f"{k} = %s" for k in new_data.keys()])
            values = list(new_data.values()) + [record_id]
            cursor.execute(
                f"UPDATE {table_name} SET {set_clause} WHERE id = %s",
                values,
            )
        return True