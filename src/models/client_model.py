"""
src/models/client_model.py
Modelo de clientes: CRUD sobre table_clientes.
"""

from database.connection import DatabaseConnection


class ClientModel:
    """Gestión de clientes del taller."""

    @staticmethod
    def get_all() -> list[dict]:
        """Obtiene todos los clientes."""
        with DatabaseConnection() as db:
            return db.fetchall(
                "SELECT * FROM table_clientes ORDER BY nombre"
            )

    @staticmethod
    def get_by_id(cliente_id: str) -> dict | None:
        """Busca cliente por ID (cédula/NIT)."""
        with DatabaseConnection() as db:
            return db.fetchone(
                "SELECT * FROM table_clientes WHERE id = %s",
                (cliente_id,),
            )

    @staticmethod
    def search(term: str) -> list[dict]:
        """Busca clientes por nombre, teléfono o ID."""
        with DatabaseConnection() as db:
            like = f"%{term}%"
            return db.fetchall(
                """
                SELECT * FROM table_clientes
                WHERE nombre LIKE %s OR telefono LIKE %s OR id LIKE %s
                ORDER BY nombre
                LIMIT 20
                """,
                (like, like, like),
            )

    @staticmethod
    def create(cliente_id: str, nombre: str, telefono: str = "",
               email: str = "", direccion: str = "") -> bool:
        """Registra un nuevo cliente."""
        with DatabaseConnection() as db:
            rows = db.update(
                """
                INSERT INTO table_clientes (id, nombre, telefono, email, direccion)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (cliente_id, nombre, telefono, email, direccion),
            )
            return rows > 0

    @staticmethod
    def update(cliente_id: str, nombre: str = None, telefono: str = None,
               email: str = None, direccion: str = None) -> bool:
        """Actualiza datos de un cliente."""
        fields = []
        params = []
        for col, val in [("nombre", nombre), ("telefono", telefono),
                         ("email", email), ("direccion", direccion)]:
            if val is not None:
                fields.append(f"{col} = %s")
                params.append(val)
        if not fields:
            return False
        params.append(cliente_id)
        with DatabaseConnection() as db:
            rows = db.update(
                f"UPDATE table_clientes SET {', '.join(fields)} WHERE id = %s",
                tuple(params),
            )
            return rows > 0