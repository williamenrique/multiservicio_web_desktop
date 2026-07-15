"""
Controlador de Facturación.
Orquesta la creación de facturas, abonos y consultas de crédito.
"""

from models.factura_model import FacturaModel
from models.inventario_model import InventarioModel
from utils.validators import monto_valido, requerido


class FacturacionController:
    """Maneja la lógica de negocio de facturación."""

    @staticmethod
    def listar_facturas(order_by="fecha DESC", limit=None, offset=None):
        """Lista facturas."""
        return FacturaModel.get_all(order_by=order_by, limit=limit, offset=offset)

    @staticmethod
    def obtener_factura(factura_id):
        """Obtiene una factura con su detalle."""
        return FacturaModel.get_by_id(factura_id)

    @staticmethod
    def buscar_producto(termino):
        """Busca productos para agregar a la factura."""
        if not requerido(termino):
            return []
        return InventarioModel.buscar(termino)

    @staticmethod
    def crear_factura(encabezado, detalles):
        """
        Crea una factura completa.
        encabezado: dict con cliente_id, usuario_id, subtotal, iva_monto, total,
                    pago_efectivo, pago_transferencia, saldo_pendiente, status
        detalles: list de dicts con producto_id, descripcion, cantidad,
                  precio_unitario, costo_unitario, mecanico_id
        """
        errores = []

        if not detalles:
            errores.append("La factura debe tener al menos un detalle")

        if not monto_valido(encabezado.get("total", 0)):
            errores.append("El total debe ser un número válido")

        if errores:
            return {"success": False, "errors": errores}

        try:
            factura_id = FacturaModel.crear_factura(encabezado, detalles)
            return {"success": True, "factura_id": factura_id}
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Error al crear factura: {e}"}

    @staticmethod
    def registrar_abono(factura_id, monto, metodo_pago):
        """Registra un abono a una factura en crédito."""
        if not monto_valido(monto) or float(monto) <= 0:
            return {"success": False, "error": "El monto debe ser positivo"}

        if metodo_pago not in ("EFECTIVO", "TRANSFERENCIA"):
            return {"success": False, "error": "Método de pago inválido"}

        try:
            FacturaModel.registrar_abono(factura_id, float(monto), metodo_pago)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": f"Error al registrar abono: {e}"}

    @staticmethod
    def get_facturas_credito():
        """Obtiene facturas con saldo pendiente."""
        conn = None
        try:
            from utils.connection_pool import ConnectionPool
            conn = ConnectionPool.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT f.*, c.nombre as cliente_nombre
                    FROM table_facturas f
                    LEFT JOIN table_clientes c ON f.cliente_id = c.id
                    WHERE f.status = 'CREDITO' AND f.saldo_pendiente > 0
                    ORDER BY f.fecha DESC
                """)
                return cursor.fetchall()
        finally:
            if conn:
                ConnectionPool.release(conn)

    @staticmethod
    def anular_factura(factura_id):
        """Anula una factura y revierte el inventario."""
        conn = None
        try:
            from utils.connection_pool import ConnectionPool
            conn = ConnectionPool.get_connection()
            with conn.cursor() as cursor:
                # Obtener detalles para revertir stock
                cursor.execute(
                    "SELECT producto_id, cantidad FROM table_facturas_detalle WHERE factura_id = %s",
                    (factura_id,),
                )
                detalles = cursor.fetchall()

                # Revertir stock
                for det in detalles:
                    if det["producto_id"]:
                        cursor.execute(
                            "UPDATE table_inventario SET stock = stock + %s WHERE id = %s",
                            (det["cantidad"], det["producto_id"]),
                        )

                # Anular factura
                cursor.execute(
                    "UPDATE table_facturas SET status = 'ANULADO' WHERE id = %s",
                    (factura_id,),
                )

                conn.commit()
                return {"success": True}
        except Exception as e:
            if conn:
                conn.rollback()
            return {"success": False, "error": f"Error al anular factura: {e}"}
        finally:
            if conn:
                ConnectionPool.release(conn)