"""
Widget de tabla genérica con filtros, paginación y selección.
Reutilizable en todos los módulos del sistema.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLineEdit, QPushButton, QLabel,
    QHeaderView, QSizePolicy, QAbstractItemView, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QIcon


class DataTable(QWidget):
    """Tabla genérica con búsqueda y paginación."""

    row_selected = Signal(dict)
    double_clicked = Signal(dict)

    def __init__(self, headers=None, parent=None):
        super().__init__(parent)
        self._headers = headers or []
        self._data = []
        self._page = 0
        self._page_size = 50
        self._total_rows = 0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Barra de búsqueda
        search_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 13px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
        """)
        self.search_input.textChanged.connect(self._on_search)
        search_bar.addWidget(self.search_input)

        self.btn_refresh = QPushButton("↻ Actualizar")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        self.btn_refresh.clicked.connect(self._on_refresh)
        search_bar.addWidget(self.btn_refresh)

        layout.addLayout(search_bar)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(len(self._headers))
        self.table.setHorizontalHeaderLabels(self._headers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        self.table.itemClicked.connect(self._on_row_clicked)
        self.table.itemDoubleClicked.connect(self._on_double_click)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background: white;
                gridline-color: #f3f4f6;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px 12px;
            }
            QTableWidget::item:selected {
                background: #dbeafe;
                color: #1e40af;
            }
            QHeaderView::section {
                background: #f8fafc;
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                font-weight: 700;
                font-size: 12px;
                color: #475569;
                text-transform: uppercase;
            }
        """)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        layout.addWidget(self.table)

        # Barra de paginación
        pag_bar = QHBoxLayout()
        self.lbl_info = QLabel("0 registros")
        self.lbl_info.setStyleSheet("color: #64748b; font-size: 12px;")
        pag_bar.addWidget(self.lbl_info)

        pag_bar.addStretch()

        self.btn_prev = QPushButton("‹ Anterior")
        self.btn_prev.setStyleSheet("""
            QPushButton {
                padding: 6px 14px;
                background: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-size: 12px;
                color: #475569;
            }
            QPushButton:hover { background: #e2e8f0; }
            QPushButton:disabled { color: #cbd5e1; }
        """)
        self.btn_prev.clicked.connect(self._prev_page)
        pag_bar.addWidget(self.btn_prev)

        self.lbl_page = QLabel("Página 1")
        self.lbl_page.setStyleSheet("font-size: 12px; color: #475569; margin: 0 8px;")
        pag_bar.addWidget(self.lbl_page)

        self.btn_next = QPushButton("Siguiente ›")
        self.btn_next.setStyleSheet(self.btn_prev.styleSheet())
        self.btn_next.clicked.connect(self._next_page)
        pag_bar.addWidget(self.btn_next)

        layout.addLayout(pag_bar)

    def set_headers(self, headers):
        """Define los encabezados de la tabla."""
        self._headers = headers
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

    def load_data(self, data):
        """Carga los datos en la tabla."""
        self._data = data
        self._total_rows = len(data)
        self._page = 0
        self._render_page()

    def _render_page(self):
        """Renderiza la página actual."""
        self.table.setRowCount(0)
        start = self._page * self._page_size
        end = min(start + self._page_size, self._total_rows)
        page_data = self._data[start:end]

        if not page_data:
            self.lbl_info.setText("0 registros")
            self.lbl_page.setText("Página 0")
            self.btn_prev.setEnabled(False)
            self.btn_next.setEnabled(False)
            return

        self.table.setRowCount(len(page_data))
        for row_idx, row in enumerate(page_data):
            values = list(row.values()) if isinstance(row, dict) else row
            for col_idx, val in enumerate(values):
                if col_idx >= len(self._headers):
                    break
                item = QTableWidgetItem(str(val or ""))
                item.setData(Qt.UserRole, row if isinstance(row, dict) else {})
                self.table.setItem(row_idx, col_idx, item)

        total_pages = max(1, (self._total_rows + self._page_size - 1) // self._page_size)
        self.lbl_info.setText(f"{self._total_rows} registros")
        self.lbl_page.setText(f"Página {self._page + 1} de {total_pages}")
        self.btn_prev.setEnabled(self._page > 0)
        self.btn_next.setEnabled(end < self._total_rows)

    def _on_search(self, text):
        """Filtra los datos por el texto de búsqueda."""
        if not text.strip():
            self._page = 0
            return
        QTimer.singleShot(300, lambda: self._apply_filter(text))

    def _apply_filter(self, text):
        if self.search_input.text() != text:
            return
        filtered = [
            r for r in self._data
            if any(text.lower() in str(v).lower() for v in (r.values() if isinstance(r, dict) else r))
        ]
        self._data = filtered
        self._total_rows = len(filtered)
        self._page = 0
        self._render_page()

    def _on_refresh(self):
        """Recarga los datos (debe ser sobrescrito externamente)."""
        pass

    def _prev_page(self):
        if self._page > 0:
            self._page -= 1
            self._render_page()

    def _next_page(self):
        if (self._page + 1) * self._page_size < self._total_rows:
            self._page += 1
            self._render_page()

    def _on_row_clicked(self, item):
        row_data = item.data(Qt.UserRole)
        if row_data:
            self.row_selected.emit(row_data)

    def _on_double_click(self, item):
        row_data = item.data(Qt.UserRole)
        if row_data:
            self.double_clicked.emit(row_data)

    def get_selected_row(self):
        """Retorna los datos de la fila seleccionada o None."""
        items = self.table.selectedItems()
        if items:
            return items[0].data(Qt.UserRole)
        return None

    def clear(self):
        """Limpia la tabla."""
        self._data = []
        self._total_rows = 0
        self._page = 0
        self.table.setRowCount(0)
        self.lbl_info.setText("0 registros")
        self.lbl_page.setText("Página 0")