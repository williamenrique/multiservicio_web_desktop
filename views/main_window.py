"""
Ventana principal (Dashboard).
Contiene la navegación entre módulos y el panel de inicio.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QStackedWidget, QSizePolicy, QScrollArea,
    QGridLayout
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap

from views.login_view import LoginView
from views.modules.inventario_view import InventarioView
from views.modules.clientes_view import ClientesView
from views.modules.facturacion_view import FacturacionView


class MainWindow(QMainWindow):
    """Ventana principal con navegación lateral y dashboard."""

    def __init__(self):
        super().__init__()
        self._current_user = None
        self._setup_ui()
        self._show_login()

    def _setup_ui(self):
        self.setWindowTitle("Multiservicio - Sistema de Gestión")
        self.setMinimumSize(1200, 750)
        self.setStyleSheet("""
            QMainWindow {
                background: #f1f5f9;
            }
        """)

        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Stack para login / app
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        # Login
        self.login_view = LoginView()
        self.login_view.login_successful.connect(self._on_login_success)
        self.stack.addWidget(self.login_view)

        # Pantalla principal de la app
        self.app_widget = self._create_app_layout()
        self.stack.addWidget(self.app_widget)

    def _create_app_layout(self):
        """Crea el layout de la aplicación con sidebar y contenido."""
        app = QWidget()
        app_layout = QHBoxLayout(app)
        app_layout.setContentsMargins(0, 0, 0, 0)
        app_layout.setSpacing(0)

        # Sidebar
        self.sidebar = self._create_sidebar()
        app_layout.addWidget(self.sidebar)

        # Contenido principal
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Header
        self.header = self._create_header()
        content_layout.addWidget(self.header)

        # Stack de vistas
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background: #f1f5f9;")

        # Dashboard
        self.dashboard = self._create_dashboard()
        self.content_stack.addWidget(self.dashboard)

        # Módulos
        self.inventario_view = InventarioView()
        self.content_stack.addWidget(self.inventario_view)

        self.clientes_view = ClientesView()
        self.content_stack.addWidget(self.clientes_view)

        self.facturacion_view = FacturacionView()
        self.content_stack.addWidget(self.facturacion_view)

        content_layout.addWidget(self.content_stack)
        app_layout.addWidget(content, 1)

        return app

    def _create_sidebar(self):
        """Crea la barra lateral de navegación."""
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QFrame {
                background: #0f172a;
                border-right: 1px solid #1e293b;
            }
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo
        logo_container = QFrame()
        logo_container.setStyleSheet("background: #0f172a; padding: 20px;")
        logo_layout = QVBoxLayout(logo_container)

        logo = QLabel("MULTISERVICIO")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            font-size: 18px;
            font-weight: 800;
            color: white;
            letter-spacing: 2px;
        """)
        logo_layout.addWidget(logo)

        logo_sub = QLabel("Taller Pro")
        logo_sub.setAlignment(Qt.AlignCenter)
        logo_sub.setStyleSheet("font-size: 11px; color: #94a3b8; margin-top: -5px;")
        logo_layout.addWidget(logo_sub)

        layout.addWidget(logo_container)

        # Separador
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #1e293b;")
        layout.addWidget(sep)

        layout.addSpacing(10)

        # Menú de navegación
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊", "Dashboard", 0),
            ("inventario", "📦", "Inventario", 1),
            ("clientes", "👥", "Clientes", 2),
            ("facturacion", "🧾", "Facturación", 3),
        ]

        for key, icon, label, index in nav_items:
            btn = QPushButton(f"  {icon}  {label}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(48)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 0 20px;
                    background: transparent;
                    border: none;
                    border-radius: 0;
                    color: #94a3b8;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: #1e293b;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, idx=index: self._navigate_to(idx))
            layout.addWidget(btn)
            self.nav_buttons[key] = btn

        layout.addStretch()

        # Info del usuario
        user_frame = QFrame()
        user_frame.setStyleSheet("background: #1e293b; padding: 16px;")
        user_layout = QVBoxLayout(user_frame)
        user_layout.setSpacing(4)

        self.lbl_user_name = QLabel("")
        self.lbl_user_name.setStyleSheet("color: white; font-size: 13px; font-weight: 600;")
        user_layout.addWidget(self.lbl_user_name)

        self.lbl_user_role = QLabel("")
        self.lbl_user_role.setStyleSheet("color: #94a3b8; font-size: 11px;")
        user_layout.addWidget(self.lbl_user_role)

        btn_logout = QPushButton("  🚪  Cerrar Sesión")
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 16px;
                background: transparent;
                border: 1px solid #334155;
                border-radius: 6px;
                color: #94a3b8;
                font-size: 12px;
                margin-top: 8px;
            }
            QPushButton:hover {
                background: #334155;
                color: white;
            }
        """)
        btn_logout.clicked.connect(self._logout)
        user_layout.addWidget(btn_logout)

        layout.addWidget(user_frame)

        return sidebar

    def _create_header(self):
        """Crea la barra superior."""
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame {
                background: white;
                border-bottom: 1px solid #e2e8f0;
            }
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)

        self.lbl_page_title = QLabel("Dashboard")
        self.lbl_page_title.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: #0f172a;
        """)
        layout.addWidget(self.lbl_page_title)

        layout.addStretch()

        self.lbl_date = QLabel("")
        self.lbl_date.setStyleSheet("color: #64748b; font-size: 13px;")
        layout.addWidget(self.lbl_date)

        return header

    def _create_dashboard(self):
        """Crea el dashboard con tarjetas de resumen."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #f1f5f9; }")

        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Tarjetas de resumen
        cards_grid = QGridLayout()
        cards_grid.setSpacing(16)

        cards = [
            ("💰", "Ventas Hoy", "0,00 Bs", "#059669", "#d1fae5"),
            ("📦", "Productos Bajos", "0", "#dc2626", "#fee2e2"),
            ("👥", "Clientes Registrados", "0", "#2563eb", "#dbeafe"),
            ("🧾", "Facturas Pendientes", "0", "#d97706", "#fef3c7"),
        ]

        self.card_labels = {}
        for i, (icon, title, value, color, bg) in enumerate(cards):
            card = self._create_card(icon, title, value, color, bg)
            cards_grid.addWidget(card, i // 2, i % 2)
            self.card_labels[title] = card.findChild(QLabel, f"card_value_{title}")

        layout.addLayout(cards_grid)

        # Acceso rápido
        quick_title = QLabel("Acceso Rápido")
        quick_title.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #0f172a;
            margin-top: 10px;
        """)
        layout.addWidget(quick_title)

        quick_grid = QGridLayout()
        quick_grid.setSpacing(12)

        quick_actions = [
            ("➕", "Nueva Venta", 3),
            ("📦", "Nuevo Producto", 1),
            ("👤", "Nuevo Cliente", 2),
            ("📊", "Reporte Diario", 0),
        ]

        for i, (icon, text, idx) in enumerate(quick_actions):
            btn = QPushButton(f"{icon}  {text}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(80)
            btn.setStyleSheet("""
                QPushButton {
                    background: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: 600;
                    color: #334155;
                    text-align: center;
                }
                QPushButton:hover {
                    border-color: #2563eb;
                    background: #f8fafc;
                }
            """)
            btn.clicked.connect(lambda checked, m=idx: self._navigate_to(m))
            quick_grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(quick_grid)
        layout.addStretch()

        scroll.setWidget(dashboard)
        return scroll

    def _create_card(self, icon, title, value, color, bg):
        """Crea una tarjeta de resumen."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 20px;
            }}
        """)
        card.setFixedHeight(140)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 28px;")
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; color: #64748b; font-weight: 500;")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setObjectName(f"card_value_{title}")
        value_label.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {color};")
        layout.addWidget(value_label)

        return card

    def _show_login(self):
        """Muestra la pantalla de login."""
        self.stack.setCurrentIndex(0)
        self.login_view.reset()

    def _on_login_success(self, user):
        """Maneja el login exitoso."""
        self._current_user = user
        self.lbl_user_name.setText(user.get("staff_nombre", user.get("username", "")))
        self.lbl_user_role.setText(user.get("nombre_rol", ""))
        self.stack.setCurrentIndex(1)
        self._navigate_to(0)

    def _navigate_to(self, index):
        """Navega a una vista específica."""
        titles = ["Dashboard", "Inventario", "Clientes", "Facturación"]
        if index < len(titles):
            self.lbl_page_title.setText(titles[index])
        self.content_stack.setCurrentIndex(index)

        # Actualizar estilos del menú
        for key, btn in self.nav_buttons.items():
            is_active = {
                "dashboard": index == 0,
                "inventario": index == 1,
                "clientes": index == 2,
                "facturacion": index == 3,
            }.get(key, False)
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 0 20px;
                    background: {'#1e293b' if is_active else 'transparent'};
                    border: none;
                    border-radius: 0;
                    color: {'white' if is_active else '#94a3b8'};
                    font-size: 14px;
                    font-weight: { '700' if is_active else '500'};
                    border-left: { '3px solid #2563eb' if is_active else '3px solid transparent'};
                }}
                QPushButton:hover {{
                    background: #1e293b;
                    color: white;
                }}
            """)

        # Refrescar datos al navegar
        if index == 1:
            self.inventario_view.refresh()
        elif index == 2:
            self.clientes_view.refresh()
        elif index == 3:
            self.facturacion_view.refresh()

    def _logout(self):
        """Cierra la sesión."""
        from controllers.login_controller import LoginController
        LoginController.logout()
        self._current_user = None
        self._show_login()