"""
Controlador de Inventario.
Orquesta las operaciones de productos, stock y kardex.
"""

from models.inventario_model import InventarioModel
from utils.validators import monto_valido, requerido


class InventarioController:
    """Maneja la lógica de negocio del inventario."""

    @staticmethod
    def listar(order_by="nombre", limit=None, offset=None):
        """Lista productos activos."""
        return InventarioModel.get_all(order_by=order_by, limit=limit, offset=offset)

    @staticmethod
    def obtener(producto_id):
        """Obtiene un producto por ID."""
        return InventarioModel.get_by_id(producto_id)

    @staticmethod
    def buscar(termino):
        """Busca productos por nombre o categoría."""
        if not requerido(termino):
            return []
        return InventarioModel.buscar(termino)

    @staticmethod
    def crear(data):
        """Crea un nuevo producto con validaciones."""
        errores = []

        if not requerido(data.get("nombre")):
            errores.append("El nombre del producto es obligatorio")

        if not monto_valido(data.get("precio", 0)):
            errores.append("El precio debe ser un número válido")

        if not monto_valido(data.get("ultimo_costo", 0)):
            errores.append("El costo debe ser un número válido")

        if errores:
            return {"success": False, "errors": errores}

        return {"success": True, "id": InventarioModel.create(data)}

    @staticmethod
    def actualizar(producto_id, data):
        """Actualiza un producto existente."""
        InventarioModel.update(producto_id, data)
        return {"success": True}

    @staticmethod
    def eliminar(producto_id):
        """Elimina (soft delete) un producto."""
        InventarioModel.delete(producto_id)
        return {"success": True}

    @staticmethod
    def get_stock_bajo():
        """Obtiene productos con stock por debajo del mínimo."""
        return InventarioModel.get_stock_bajo()

    @staticmethod
    def registrar_movimiento(producto_id, tipo, cantidad, referencia_id, usuario_id, observacion=None):
        """
        Registra un movimiento de kardex.
        tipos: ENTRADA_COMPRA, SALIDA_VENTA, AJUSTE_MANUAL, DEVOLUCION
        """
        try:
            InventarioModel.registrar_movimiento(
                producto_id, tipo, cantidad, referencia_id, usuario_id, observacion
            )
            return {"success": True}
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Error al registrar movimiento: {e}"}