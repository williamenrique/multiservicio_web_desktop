"""
Modelo de Inventario.
Operaciones sobre table_inventario y table_kardex.
Incluye actualización de Costo Promedio Ponderado (CPP).
"""

from models.base_model import BaseModel
from utils.connection_pool import ConnectionPool


class InventarioModel(BaseModel):
    TABLE = "table_inventario"

    @classmethod
    def buscar(cls, termino):
        """Busca productos por nombre o categoría."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """SELECT * FROM table_inventario
                         WHERE (nombre LIKE %s OR categoria LIKE %s)
                           AND estado = 'ACTIVO'
                         ORDER BY nombre
                         LIMIT 30"""
                like = f"%{termino}%"
                cursor.execute(sql, (like, like))
                return cursor.fetchall()
        finally:
            ConnectionPool.release(conn)

    @classmethod
    def get_stock_bajo(cls):
        """Productos con stock por debajo del mínimo."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """SELECT * FROM table_inventario
                         WHERE stock <= stock_minimo AND estado = 'ACTIVO'
                         ORDER BY (stock_minimo - stock) DESC"""
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            ConnectionPool.release(conn)

    @classmethod
    def registrar_movimiento(cls, producto_id, tipo, cantidad, referencia_id, usuario_id, observacion=None):
        """
        Registra un movimiento en el kardex y actualiza stock + CPP.
        tipos: ENTRADA_COMPRA, SALIDA_VENTA, AJUSTE_MANUAL, DEVOLUCION
        """
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. Obtener estado actual del producto
                cursor.execute(
                    "SELECT stock, costo_promedio, ultimo_costo FROM table_inventario WHERE id = %s FOR UPDATE",
                    (producto_id,),
                )
                prod = cursor.fetchone()
                if not prod:
                    raise ValueError("Producto no encontrado")

                stock_anterior = prod["stock"]
                costo_promedio_actual = prod["costo_promedio"] or 0

                # 2. Calcular nuevo stock
                if tipo in ("ENTRADA_COMPRA", "DEVOLUCION"):
                    stock_nuevo = stock_anterior + cantidad
                else:  # SALIDA_VENTA, AJUSTE_MANUAL (negativo)
                    stock_nuevo = stock_anterior - cantidad
                    if stock_nuevo < 0:
                        raise ValueError("Stock insuficiente")

                # 3. Actualizar CPP si es compra
                if tipo == "ENTRADA_COMPRA" and cantidad > 0:
                    nuevo_costo_total = (costo_promedio_actual * stock_anterior) + (prod["ultimo_costo"] * cantidad)
                    nuevo_cpp = nuevo_costo_total / stock_nuevo if stock_nuevo > 0 else 0
                else:
                    nuevo_cpp = costo_promedio_actual

                # 4. Actualizar inventario
                cursor.execute(
                    """UPDATE table_inventario
                       SET stock = %s, costo_promedio = %s
                       WHERE id = %s""",
                    (stock_nuevo, nuevo_cpp, producto_id),
                )

                # 5. Insertar en kardex
                cursor.execute(
                    """INSERT INTO table_kardex
                       (producto_id, tipo_movimiento, cantidad, stock_anterior, stock_actual,
                        referencia_id, usuario_id, observacion)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (producto_id, tipo, cantidad, stock_anterior, stock_nuevo,
                     referencia_id, usuario_id, observacion),
                )

                conn.commit()
                return True
        except Exception:
            conn.rollback()
            raise
        finally:
            ConnectionPool.release(conn)

    @classmethod
    def get_kardex(cls, producto_id, limite=50):
        """Historial de movimientos de un producto."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """SELECT k.*, u.username
                         FROM table_kardex k
                         LEFT JOIN table_usuarios u ON k.usuario_id = u.id
                         WHERE k.producto_id = %s
                         ORDER BY k.fecha DESC
                         LIMIT %s"""
                cursor.execute(sql, (producto_id, limite))
                return cursor.fetchall()
        finally:
            ConnectionPool.release(conn)