"""
src/models/vehicle_model.py
Modelo de vehículos: CRUD sobre table_vehiculos.
"""

from database.connection import DatabaseConnection


class VehicleModel:
    """Gestión de vehículos del taller."""

    @staticmethod
    def get_all() -> list[dict]:
        """Obtiene todos los vehículos con datos del cliente."""
        with DatabaseConnection() as db:
            return db.fetchall(
                """
                SELECT v.placa, v.marca, v.modelo, v.anio, v.color,
                       c.id AS cliente_id, c.nombre AS cliente_nombre,
                       c.telefono AS cliente_telefono
                FROM table_vehiculos v
                LEFT JOIN table_clientes c ON v.cliente_id = c.id
                ORDER BY v.placa
                """
            )

    @staticmethod
    def get_by_placa(placa: str) -> dict | None:
        """Busca vehículo por placa."""
        with DatabaseConnection() as db:
            return db.fetchone(
                """
                SELECT v.*, c.nombre AS cliente_nombre, c.telefono AS cliente_telefono
                FROM table_vehiculos v
                LEFT JOIN table_clientes c ON v.cliente_id = c.id
                WHERE v.placa = %s
                """,
                (placa,),
            )

    @staticmethod
    def get_by_cliente(cliente_id: str) -> list[dict]:
        """Obtiene vehículos de un cliente específico."""
        with DatabaseConnection() as db:
            return db.fetchall(
                "SELECT * FROM table_vehiculos WHERE cliente_id = %s",
                (cliente_id,),
            )

    @staticmethod
    def create(placa: str, cliente_id: str, marca: str = "",
               modelo: str = "", anio: int = None, color: str = "") -> bool:
        """Registra un nuevo vehículo."""
        with DatabaseConnection() as db:
            rows = db.update(
                """
                INSERT INTO table_vehiculos (placa, cliente_id, marca, modelo, anio, color)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (placa, cliente_id, marca, modelo, anio, color),
            )
            return rows > 0

    @staticmethod
    def update(placa: str, marca: str = None, modelo: str = None,
               anio: int = None, color: str = None) -> bool:
        """Actualiza datos de un vehículo."""
        fields = []
        params = []
        if marca is not None:
            fields.append("marca = %s")
            params.append(marca)
        if modelo is not None:
            fields.append("modelo = %s")
            params.append(modelo)
        if anio is not None:
            fields.append("anio = %s")
            params.append(anio)
        if color is not None:
            fields.append("color = %s")
            params.append(color)
        if not fields:
            return False
        params.append(placa)
        with DatabaseConnection() as db:
            rows = db.update(
                f"UPDATE table_vehiculos SET {', '.join(fields)} WHERE placa = %s",
                tuple(params),
            )
            return rows > 0