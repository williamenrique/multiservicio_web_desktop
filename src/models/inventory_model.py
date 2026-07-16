"""
src/models/inventory_model.py
Modelo de inventario: CRUD sobre table_inventario y table_kardex.
"""

from database.connection import DatabaseConnection


class InventoryModel:
    """Gestión de productos e inventario."""

    @staticmethod
    def get_all() -> list[dict]:
        """Obtiene todos los productos activos."""
        with DatabaseConnection() as db:
            return db.fetchall(
                """
                SELECT * FROM table_inventario
                WHERE estado = 'ACTIVO'
                ORDER BY nombre
                """
            )

    @staticmethod
    def get_by_id(producto_id: int) -> dict | None:
        """Busca producto por ID."""
        with DatabaseConnection() as db:
            return db.fetchone(
                "SELECT * FROM table_inventario WHERE id = %s",
                (producto_id,),
            )

    @staticmethod
    def search(term: str) -> list[dict]:
        """Busca productos por nombre o categoría."""
        with DatabaseConnection() as db:
            like = f"%{term}%"
            return db.fetchall(
                """
                SELECT * FROM table_inventario
                WHERE (nombre LIKE %s OR categoria LIKE %s) AND estado = 'ACTIVO'
                ORDER BY nombre
                LIMIT 20
                """,
                (like, like),
            )

    @staticmethod
    def get_low_stock() -> list[dict]:
        """Productos con stock bajo el mínimo."""
        with DatabaseConnection() as db:
            return db.fetchall(
                """
                SELECT * FROM table_inventario
                WHERE stock <= stock_minimo AND estado = 'ACTIVO'
                ORDER BY stock ASC
                """
            )

    @staticmethod
    def update_stock(producto_id: int, cantidad: int, tipo: str,
                     referencia_id: str, usuario_id: int, observacion: str = None) -> bool:
        """
        Actualiza stock y registra en kardex.
        tipo: 'ENTRADA_COMPRA', 'SALIDA_VENTA', 'AJUSTE_MANUAL', 'DEVOLUCION'
        """
        with DatabaseConnection() as db:
            producto = db.fetchone(
                "SELECT stock FROM table_inventario WHERE id = %s",
                (producto_id,),
            )
            if not producto:
                return False

            stock_anterior = producto["stock"]
            if tipo in ("SALIDA_VENTA",):
                stock_actual = stock_anterior - cantidad
            else:
                stock_actual = stock_anterior + cantidad

            db.update(
                "UPDATE table_inventario SET stock = %s WHERE id = %s",
                (stock_actual, producto_id),
            )
            db.update(
                """
                INSERT INTO table_kardex
                (producto_id, tipo_movimiento, cantidad, stock_anterior, stock_actual,
                 referencia_id, usuario_id, observacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (producto_id, tipo, cantidad, stock_anterior, stock_actual,
                 referencia_id, usuario_id, observacion),
            )
            return True

    @staticmethod
    def create(nombre: str, categoria: str = "", stock: int = 0,
               stock_minimo: int = 5, precio: float = 0.0,
               costo_promedio: float = 0.0, unidad: str = "UNIDAD",
               tipo: str = "PRODUCTO") -> int:
        """Crea un nuevo producto en el inventario."""
        with DatabaseConnection() as db:
            producto_id = db.insert(
                """
                INSERT INTO table_inventario
                (nombre, categoria, stock, stock_minimo, precio, costo_promedio, estado)
                VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVO')
                """,
                (nombre, categoria, stock, stock_minimo, precio, costo_promedio),
            )
            return producto_id