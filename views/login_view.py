"""
Ventana de Login.
Interfaz de autenticación de usuarios.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QSpacerItem, QSizePolicy, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QIcon


class LoginView(QWidget):
    """Ventana de inicio de sesión."""

    login_successful = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("loginView")
        self.setStyleSheet("""
            #loginView {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #1e3a5f, stop: 1 #0f172a
                );
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Contenedor central
        card = QFrame()
        card.setFixedWidth(420)
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
                padding: 40px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)
        card_layout.setContentsMargins(40, 40, 40, 40)

        # Logo / Título
        title = QLabel("MULTISERVICIO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: 800;
            color: #1e3a5f;
            letter-spacing: 2px;
        """)
        card_layout.addWidget(title)

        subtitle = QLabel("Sistema de Gestión de Taller")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 13px;
            color: #64748b;
            margin-bottom: 20px;
        """)
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(10)

        # Campo usuario
        lbl_user = QLabel("Usuario")
        lbl_user.setStyleSheet("font-size: 13px; font-weight: 600; color: #334155;")
        card_layout.addWidget(lbl_user)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingrese su usuario")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 14px;
                background: #f8fafc;
            }
            QLineEdit:focus {
                border-color: #2563eb;
                background: white;
            }
        """)
        card_layout.addWidget(self.username_input)

        # Campo contraseña
        lbl_pass = QLabel("Contraseña")
        lbl_pass.setStyleSheet("font-size: 13px; font-weight: 600; color: #334155;")
        card_layout.addWidget(lbl_pass)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingrese su contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self.username_input.styleSheet())
        self.password_input.returnPressed.connect(self._on_login_clicked)
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(8)

        # Botón de login
        self.btn_login = QPushButton("INICIAR SESIÓN")
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                padding: 14px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #2563eb, stop: 1 #1d4ed8);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 700;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #1d4ed8, stop: 1 #1e40af);
            }
            QPushButton:pressed {
                background: #1e40af;
            }
        """)
        self.btn_login.clicked.connect(self._on_login_clicked)
        card_layout.addWidget(self.btn_login)

        # Label de error
        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setStyleSheet("color: #dc2626; font-size: 12px; font-weight: 500;")
        self.lbl_error.setVisible(False)
        card_layout.addWidget(self.lbl_error)

        card_layout.addStretch()

        layout.addWidget(card)

    def _on_login_clicked(self):
        """Emite señal con credenciales para que el controller las procese."""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.show_error("Usuario y contraseña son requeridos")
            return

        from controllers.login_controller import LoginController
        user = LoginController.login(username, password)

        if user:
            self.lbl_error.setVisible(False)
            self.login_successful.emit(user)
        else:
            self.show_error("Usuario o contraseña incorrectos")

    def show_error(self, message):
        """Muestra un mensaje de error."""
        self.lbl_error.setText(message)
        self.lbl_error.setVisible(True)
        self.password_input.clear()
        self.password_input.setFocus()

    def reset(self):
        """Limpia los campos del formulario."""
        self.username_input.clear()
        self.password_input.clear()
        self.lbl_error.setVisible(False)
        self.username_input.setFocus()