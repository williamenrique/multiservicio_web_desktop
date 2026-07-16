"""
src/models/invoice_model.py
Modelo de facturación: CRUD sobre table_facturas, table_facturas_detalle,
table_abonos_clientes, table_transacciones.
"""

from database.connection import DatabaseConnection


class InvoiceModel:
    """Gestión de facturas y transacciones contables."""

    @staticmethod
    def get_all() -> list[dict]:
        """Obtiene todas las facturas."""
        with DatabaseConnection() as db:
            return db.fetchall(
                """
                SELECT f.*, c.nombre AS cliente_nombre, u.username AS cajero
                FROM table_facturas f
                LEFT JOIN table_clientes c ON f.cliente_id = c.id
                LEFT JOIN table_usuarios u ON f.usuario_id = u.id
                ORDER BY f.fecha DESC
                """
            )

    @staticmethod
    def get_by_id(factura_id: int) -> dict | None:
        """Obtiene factura con su detalle."""
        with DatabaseConnection() as db:
            factura = db.fetchone(
                """
                SELECT f.*, c.nombre AS cliente_nombre, c.telefono AS cliente_telefono,
                       u.username AS cajero
                FROM table_facturas f
                LEFT JOIN table_clientes c ON f.cliente_id = c.id
                LEFT JOIN table_usuarios u ON f.usuario_id = u.id
                WHERE f.id = %s
                """,
                (factura_id,),
            )
            if factura:
                factura["detalle"] = db.fetchall(
                    """
                    SELECT d.*, s.nombre AS mecanico_nombre, i.nombre AS producto_nombre
                    FROM table_facturas_detalle d
                    LEFT JOIN table_staff s ON d.mecanico_id = s.id
                    LEFT JOIN table_inventario i ON d.producto_id = i.id
                    WHERE d.factura_id = %s
                    """,
                    (factura_id,),
                )
                factura["abonos"] = db.fetchall(
                    "SELECT * FROM table_abonos_clientes WHERE factura_id = %s",
                    (factura_id,),
                )
            return factura

    @staticmethod
    def create(orden_id: int, cliente_id: str, usuario_id: int,
               subtotal: float, iva_monto: float, total: float,
               pago_efectivo: float = 0, pago_transferencia: float = 0,
               placa: str = None, observaciones: str = None,
               detalle: list[dict] = None) -> int:
        """
        Crea factura con detalle.
        detalle: [{"producto_id": int, "mecanico_id": str, "descripcion": str,
                   "cantidad": int, "precio_unitario": float, "costo_unitario": float}, ...]
        """
        saldo = total - (pago_efectivo + pago_transferencia)
        status = "COMPLETADO" if saldo <= 0 else "CREDITO"

        with DatabaseConnection() as db:
            factura_id = db.insert(
                """
                INSERT INTO table_facturas
                (orden_id, cliente_id, placa, usuario_id, subtotal, iva_monto, total,
                 pago_efectivo, pago_transferencia, saldo_pendiente, status, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (orden_id, cliente_id, placa, usuario_id, subtotal, iva_monto, total,
                 pago_efectivo, pago_transferencia, saldo, status, observaciones),
            )

            if detalle:
                for d in detalle:
                    db.update(
                        """
                        INSERT INTO table_facturas_detalle
                        (factura_id, producto_id, mecanico_id, descripcion, cantidad,
                         precio_unitario, costo_unitario)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (factura_id, d.get("producto_id"), d.get("mecanico_id"),
                         d.get("descripcion"), d.get("cantidad"),
                         d.get("precio_unitario"), d.get("costo_unitario")),
                    )

            return factura_id

    @staticmethod
    def get_daily_summary() -> dict:
        """Resumen de ventas del día para el dashboard."""
        with DatabaseConnection() as db:
            return db.fetchone(
                """
                SELECT
                    COUNT(*) AS total_facturas,
                    COALESCE(SUM(total), 0) AS total_ventas,
                    COALESCE(SUM(pago_efectivo), 0) AS total_efectivo,
                    COALESCE(SUM(pago_transferencia), 0) AS total_transferencia,
                    COALESCE(SUM(saldo_pendiente), 0) AS total_credito
                FROM table_facturas
                WHERE DATE(fecha) = CURDATE() AND status != 'ANULADO'
                """
            )