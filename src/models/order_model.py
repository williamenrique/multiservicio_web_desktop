"""
src/models/order_model.py
Modelo de órdenes de servicio: CRUD sobre table_ordenes_servicio,
table_orden_checklist, table_orden_estados_log.
"""

from database.connection import DatabaseConnection


class OrderModel:
    """Gestión de órdenes de servicio del taller."""

    @staticmethod
    def get_all(estado: str = None) -> list[dict]:
        """Obtiene todas las órdenes, opcionalmente filtradas por estado."""
        with DatabaseConnection() as db:
            if estado:
                return db.fetchall(
                    """
                    SELECT o.*, c.nombre AS cliente_nombre, s.nombre AS mecanico_nombre
                    FROM table_ordenes_servicio o
                    LEFT JOIN table_clientes c ON o.cliente_id = c.id
                    LEFT JOIN table_staff s ON o.mecanico_id = s.id
                    WHERE o.estado = %s
                    ORDER BY o.fecha_ingreso DESC
                    """,
                    (estado,),
                )
            return db.fetchall(
                """
                SELECT o.*, c.nombre AS cliente_nombre, s.nombre AS mecanico_nombre
                FROM table_ordenes_servicio o
                LEFT JOIN table_clientes c ON o.cliente_id = c.id
                LEFT JOIN table_staff s ON o.mecanico_id = s.id
                ORDER BY o.fecha_ingreso DESC
                """
            )

    @staticmethod
    def search(cliente_id: str = None, placa: str = None) -> list[dict]:
        """Busca órdenes por cliente_id o placa."""
        with DatabaseConnection() as db:
            if cliente_id:
                return db.fetchall(
                    """
                    SELECT o.*, c.nombre AS cliente_nombre, s.nombre AS mecanico_nombre
                    FROM table_ordenes_servicio o
                    LEFT JOIN table_clientes c ON o.cliente_id = c.id
                    LEFT JOIN table_staff s ON o.mecanico_id = s.id
                    WHERE o.cliente_id = %s
                    ORDER BY o.fecha_ingreso DESC
                    """,
                    (cliente_id,),
                )
            if placa:
                return db.fetchall(
                    """
                    SELECT o.*, c.nombre AS cliente_nombre, s.nombre AS mecanico_nombre
                    FROM table_ordenes_servicio o
                    LEFT JOIN table_clientes c ON o.cliente_id = c.id
                    LEFT JOIN table_staff s ON o.mecanico_id = s.id
                    WHERE o.placa = %s
                    ORDER BY o.fecha_ingreso DESC
                    """,
                    (placa,),
                )
            return []

    @staticmethod
    def get_by_id(orden_id: int) -> dict | None:
        """Obtiene una orden con todos sus datos relacionados."""
        with DatabaseConnection() as db:
            orden = db.fetchone(
                """
                SELECT o.*, c.nombre AS cliente_nombre, c.telefono AS cliente_telefono,
                       s.nombre AS mecanico_nombre, v.marca, v.modelo, v.anio, v.color
                FROM table_ordenes_servicio o
                LEFT JOIN table_clientes c ON o.cliente_id = c.id
                LEFT JOIN table_staff s ON o.mecanico_id = s.id
                LEFT JOIN table_vehiculos v ON o.placa = v.placa
                WHERE o.id = %s
                """,
                (orden_id,),
            )
            if orden:
                orden["checklist"] = db.fetchall(
                    "SELECT * FROM table_orden_checklist WHERE orden_id = %s",
                    (orden_id,),
                )
                orden["historial_estados"] = db.fetchall(
                    """
                    SELECT h.*, u.username
                    FROM table_orden_estados_log h
                    LEFT JOIN table_usuarios u ON h.usuario_id = u.id
                    WHERE h.orden_id = %s
                    ORDER BY h.fecha ASC
                    """,
                    (orden_id,),
                )
            return orden

    @staticmethod
    def create(cliente_id: str, placa: str, mecanico_id: str = None,
               kilometraje: str = "", nivel_combustible: str = "",
               diagnostico_entrada: str = "", observaciones: str = "",
               checklist_items: list[dict] = None) -> int:
        """Crea una nueva orden de servicio."""
        with DatabaseConnection() as db:
            orden_id = db.insert(
                """
                INSERT INTO table_ordenes_servicio
                (cliente_id, placa, mecanico_id, kilometraje, nivel_combustible,
                 diagnostico_entrada, observaciones, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'RECIBIDO')
                """,
                (cliente_id, placa, mecanico_id, kilometraje, nivel_combustible,
                 diagnostico_entrada, observaciones),
            )
            # Insertar checklist items
            if checklist_items:
                for item in checklist_items:
                    db.update(
                        """
                        INSERT INTO table_orden_checklist (orden_id, item, estado, observacion)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (orden_id, item.get("item"), item.get("estado", 0),
                         item.get("observacion")),
                    )
            return orden_id

    @staticmethod
    def update_estado(orden_id: int, nuevo_estado: str, usuario_id: int,
                      comentario: str = None) -> bool:
        """Cambia el estado de una orden y registra en el log."""
        with DatabaseConnection() as db:
            orden = db.fetchone(
                "SELECT estado FROM table_ordenes_servicio WHERE id = %s",
                (orden_id,),
            )
            if not orden:
                return False
            estado_anterior = orden["estado"]

            db.update(
                "UPDATE table_ordenes_servicio SET estado = %s WHERE id = %s",
                (nuevo_estado, orden_id),
            )
            db.update(
                """
                INSERT INTO table_orden_estados_log
                (orden_id, estado_anterior, estado_nuevo, usuario_id, comentario)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (orden_id, estado_anterior, nuevo_estado, usuario_id, comentario),
            )
            return True

    @staticmethod
    def get_active_orders_count() -> dict:
        """Conteo de órdenes por estado para el dashboard."""
        with DatabaseConnection() as db:
            rows = db.fetchall(
                """
                SELECT estado, COUNT(*) AS total
                FROM table_ordenes_servicio
                WHERE estado NOT IN ('ENTREGADO', 'CANCELADO')
                GROUP BY estado
                """
            )
            return {r["estado"]: r["total"] for r in rows}