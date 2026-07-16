"""
src/controllers/workshop_controller.py
Controlador principal del taller: dashboard, órdenes, facturación.
"""

from src.models.order_model import OrderModel
from src.models.invoice_model import InvoiceModel
from src.models.inventory_model import InventoryModel
from src.models.client_model import ClientModel
from src.models.vehicle_model import VehicleModel
from database.connection import DatabaseConnection


class WorkshopController:
    """Lógica de negocio para operaciones del taller."""

    def __init__(self, auth_controller):
        self.auth = auth_controller

    # ── Dashboard ────────────────────────────────────────

    def get_dashboard_data(self) -> dict:
        """Datos para el panel principal."""
        return {
            "ordenes_activas": OrderModel.get_active_orders_count(),
            "ventas_hoy": InvoiceModel.get_daily_summary(),
            "stock_bajo": InventoryModel.get_low_stock(),
        }

    # ── Órdenes de servicio ──────────────────────────────

    def get_ordenes(self, estado: str = None) -> list[dict]:
        return OrderModel.get_all(estado)

    def buscar_ordenes(self, cliente_id: str = None, placa: str = None) -> list[dict]:
        """Busca órdenes por cliente o placa."""
        return OrderModel.search(cliente_id=cliente_id, placa=placa)

    def get_orden(self, orden_id: int) -> dict | None:
        return OrderModel.get_by_id(orden_id)

    def crear_orden(self, cliente_id: str, placa: str, mecanico_id: str = None,
                    kilometraje: str = "", nivel_combustible: str = "",
                    diagnostico: str = "", observaciones: str = "",
                    checklist: list[dict] = None) -> tuple[bool, str]:
        """Crea una nueva orden de servicio."""
        try:
            orden_id = OrderModel.create(
                cliente_id, placa, mecanico_id, kilometraje,
                nivel_combustible, diagnostico, observaciones, checklist,
            )
            return True, f"Orden #{orden_id} creada exitosamente"
        except Exception as e:
            return False, f"Error al crear orden: {str(e)}"

    def cambiar_estado_orden(self, orden_id: int, nuevo_estado: str,
                             comentario: str = None) -> tuple[bool, str]:
        """Cambia el estado de una orden."""
        if not self.auth.is_authenticated:
            return False, "Debe iniciar sesión"
        try:
            ok = OrderModel.update_estado(
                orden_id, nuevo_estado, self.auth.current_user["id"], comentario,
            )
            return (True, "Estado actualizado") if ok else (False, "Orden no encontrada")
        except Exception as e:
            return False, f"Error: {str(e)}"

    # ── Clientes y vehículos ─────────────────────────────

    def buscar_cliente(self, term: str) -> list[dict]:
        return ClientModel.search(term)

    def get_vehiculos_cliente(self, cliente_id: str) -> list[dict]:
        return VehicleModel.get_by_cliente(cliente_id)

    def get_vehiculo(self, placa: str) -> dict | None:
        return VehicleModel.get_by_placa(placa)

    # ── Inventario ───────────────────────────────────────

    def buscar_producto(self, term: str) -> list[dict]:
        return InventoryModel.search(term)

    def get_producto(self, producto_id: int) -> dict | None:
        return InventoryModel.get_by_id(producto_id)

    # ── Facturación ──────────────────────────────────────

    def get_facturas(self) -> list[dict]:
        return InvoiceModel.get_all()

    def get_factura(self, factura_id: int) -> dict | None:
        return InvoiceModel.get_by_id(factura_id)

    # ── Clientes ─────────────────────────────────────────

    def crear_cliente(self, cliente_id: str, nombre: str, telefono: str = "",
                      email: str = "", direccion: str = "") -> tuple[bool, str]:
        """Registra un nuevo cliente."""
        try:
            ok = ClientModel.create(cliente_id, nombre, telefono, email, direccion)
            return (True, "Cliente registrado exitosamente") if ok else (False, "El ID ya existe")
        except Exception as e:
            return False, f"Error al registrar cliente: {str(e)}"

    # ── Inventario ───────────────────────────────────────

    def crear_producto(self, nombre: str, categoria: str = "", stock: int = 0,
                       stock_minimo: int = 5, precio: float = 0.0,
                       costo_promedio: float = 0.0) -> tuple[bool, str]:
        """Crea un nuevo producto en el inventario."""
        try:
            producto_id = InventoryModel.create(
                nombre, categoria, stock, stock_minimo, precio, costo_promedio,
            )
            return True, f"Producto #{producto_id} creado exitosamente"
        except Exception as e:
            return False, f"Error al crear producto: {str(e)}"

    # ── Personal / Mecánicos ─────────────────────────────

    def get_mecanicos(self) -> list[dict]:
        """Obtiene la lista de mecánicos activos."""
        with DatabaseConnection() as db:
            return db.fetchall(
                """
                SELECT s.id, s.nombre, s.cedula
                FROM table_staff s
                INNER JOIN table_usuarios u ON s.id = u.staff_id
                INNER JOIN table_roles r ON u.role_id = r.id
                WHERE s.estado = 'ACTIVO' AND r.nombre_rol IN ('MECANICO', 'ADMINISTRADOR')
                ORDER BY s.nombre
                """
            )

    # ── Facturación ──────────────────────────────────────

    def crear_factura(self, orden_id: int, cliente_id: str,
                      subtotal: float, iva_monto: float, total: float,
                      pago_efectivo: float = 0, pago_transferencia: float = 0,
                      placa: str = None, observaciones: str = None,
                      detalle: list[dict] = None) -> tuple[bool, str]:
        """Crea una nueva factura."""
        try:
            usuario_id = self.auth.current_user["id"]
            factura_id = InvoiceModel.create(
                orden_id, cliente_id, usuario_id, subtotal, iva_monto, total,
                pago_efectivo, pago_transferencia, placa, observaciones, detalle,
            )
            return True, f"Factura #{factura_id} creada exitosamente"
        except Exception as e:
            return False, f"Error al crear factura: {str(e)}"