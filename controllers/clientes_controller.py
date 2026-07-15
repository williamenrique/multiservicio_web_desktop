"""
Controlador de Clientes.
Orquesta las operaciones de clientes y vehículos.
"""

from models.cliente_model import ClienteModel
from utils.validators import cedula_valida, email_valido, telefono_valido, requerido


class ClientesController:
    """Maneja la lógica de negocio de clientes."""

    @staticmethod
    def listar(order_by="nombre", limit=None, offset=None):
        """Lista clientes activos."""
        return ClienteModel.get_all(order_by=order_by, limit=limit, offset=offset)

    @staticmethod
    def obtener(cliente_id):
        """Obtiene un cliente por ID."""
        return ClienteModel.get_by_id(cliente_id, id_field="id")

    @staticmethod
    def buscar(termino):
        """Busca clientes por nombre, cédula o teléfono."""
        if not requerido(termino):
            return []
        return ClienteModel.buscar(termino)

    @staticmethod
    def crear(data):
        """Crea un nuevo cliente con validaciones."""
        errores = []

        if not requerido(data.get("id")):
            errores.append("La cédula/NIT es obligatorio")
        elif not cedula_valida(data.get("id", "")):
            errores.append("La cédula/NIT no tiene un formato válido")

        if not requerido(data.get("nombre")):
            errores.append("El nombre del cliente es obligatorio")

        if data.get("email") and not email_valido(data["email"]):
            errores.append("El email no tiene un formato válido")

        if data.get("telefono") and not telefono_valido(data["telefono"]):
            errores.append("El teléfono no tiene un formato válido")

        if errores:
            return {"success": False, "errors": errores}

        return {"success": True, "id": ClienteModel.create(data)}

    @staticmethod
    def actualizar(cliente_id, data):
        """Actualiza un cliente existente."""
        ClienteModel.update(cliente_id, data, id_field="id")
        return {"success": True}

    @staticmethod
    def eliminar(cliente_id):
        """Elimina (soft delete) un cliente."""
        ClienteModel.delete(cliente_id, id_field="id")
        return {"success": True}

    @staticmethod
    def get_vehiculos(cliente_id):
        """Obtiene los vehículos de un cliente."""
        return ClienteModel.get_vehiculos(cliente_id)

    @staticmethod
    def crear_vehiculo(data):
        """Registra un vehículo para un cliente."""
        errores = []

        if not requerido(data.get("placa")):
            errores.append("La placa es obligatoria")

        if not requerido(data.get("cliente_id")):
            errores.append("El cliente es obligatorio")

        if errores:
            return {"success": False, "errors": errores}

        try:
            ClienteModel.crear_vehiculo(data)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}