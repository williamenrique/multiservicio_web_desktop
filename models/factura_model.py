"""
Modelo de Facturación.
Operaciones sobre table_facturas, table_facturas_detalle, table_abonos_clientes
y table_transacciones (Libro Mayor).
"""

from models.base_model import BaseModel
from utils.connection_pool import ConnectionPool


class FacturaModel(BaseModel):
    TABLE = "table_facturas"

    @classmethod
    def crear_factura(cls, encabezado, detalles):
        """
        Crea una factura completa con su detalle en una transacción.
        Actualiza inventario y registra en el libro mayor.
        """
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. Insertar encabezado
                cols = ", ".join(encabezado.keys())
                placeholders = ", ".join(["%s"] * len(encabezado))
                sql = f"INSERT INTO table_facturas ({cols}) VALUES ({placeholders})"
                cursor.execute(sql, list(encabezado.values()))
                factura_id = cursor.lastrowid

                # 2. Insertar detalles y descontar inventario
                for det in detalles:
                    d_cols = ", ".join(det.keys())
                    d_phs = ", ".join(["%s"] * len(det))
                    cursor.execute(
                        f"INSERT INTO table_facturas_detalle ({d_cols}) VALUES ({d_phs})",
                        list(det.values()),
                    )

                    # Descontar stock si es producto
                    if det.get("producto_id"):
                        cursor.execute(
                            """UPDATE table_inventario
                               SET stock = stock - %s
                               WHERE id = %s AND stock >= %s""",
                            (det["cantidad"], det["producto_id"], det["cantidad"]),
                        )
                        if cursor.rowcount == 0:
                            raise ValueError(f"Stock insuficiente para producto ID {det['producto_id']}")

                # 3. Registrar en libro mayor (ingreso)
                cursor.execute(
                    """INSERT INTO table_transacciones
                       (cuenta_id, tipo, categoria, monto, referencia_id, descripcion, usuario_id)
                       VALUES (%s, 'INGRESO', 'VENTA', %s, %s, %s, %s)""",
                    (1, encabezado["total"], factura_id,
                     f"Factura #{factura_id}", encabezado.get("usuario_id")),
                )

                conn.commit()
                return factura_id
        except Exception:
            conn.rollback()
            raise
        finally:
            ConnectionPool.release(conn)

    @classmethod
    def registrar_abono(cls, factura_id, monto, metodo_pago):
        """Registra un abono a una factura en crédito."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                # Insertar abono
                cursor.execute(
                    """INSERT INTO table_abonos_clientes (factura_id, monto, metodo_pago)
                       VALUES (%s, %s, %s)""",
                    (factura_id, monto, metodo_pago),
                )

                # Actualizar saldo pendiente en factura
                cursor.execute(
                    """UPDATE table_facturas
                       SET saldo_pendiente = saldo_pendiente - %s
                       WHERE id = %s""",
                    (monto, factura_id),
                )

                # Si quedó en 0, marcar como COMPLETADO
                cursor.execute(
                    """UPDATE table_facturas
                       SET status = 'COMPLETADO'
                       WHERE id = %s AND saldo_pendiente <= 0""",
                    (factura_id,),
                )

                conn.commit()
                return True
        except Exception:
            conn.rollback()
            raise
        finally:
            ConnectionPool.release(conn)

    @classmethod
    def get_historial(cls, limite=50):
        """Obtiene las últimas facturas con información del cliente."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """SELECT f.*, c.nombre as cliente_nombre
                         FROM table_facturas f
                         LEFT JOIN table_clientes c ON f.cliente_id = c.id
                         ORDER BY f.fecha DESC
                         LIMIT %s"""
                cursor.execute(sql, (limite,))
                return cursor.fetchall()
        finally:
            ConnectionPool.release(conn)

    @classmethod
    def get_detalles(cls, factura_id):
        """Obtiene el detalle de una factura."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """SELECT fd.*, i.nombre as producto_nombre
                         FROM table_facturas_detalle fd
                         LEFT JOIN table_inventario i ON fd.producto_id = i.id
                         WHERE fd.factura_id = %s"""
                cursor.execute(sql, (factura_id,))
                return cursor.fetchall()
        finally:
            ConnectionPool.release(conn)

    @classmethod
    def get_abonos(cls, factura_id):
        """Obtiene los abonos de una factura."""
        conn = ConnectionPool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM table_abonos_clientes WHERE factura_id = %s ORDER BY fecha"
                cursor.execute(sql, (factura_id,))
                return cursor.fetchall()
        finally:
            ConnectionPool.release(conn)