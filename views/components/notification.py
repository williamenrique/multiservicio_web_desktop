"""
Widget de notificaciones emergentes (Toast).
Muestra mensajes temporales en la esquina superior derecha.
"""

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QColor, QFont


class Toast(QFrame):
    """Notificación emergente tipo toast con auto-cierre."""

    _instances = []

    def __init__(self, message, type="info", duration=3000, parent=None):
        super().__init__(parent)
        self._duration = duration
        self._setup_ui(message, type)
        self._setup_animation()
        Toast._instances.append(self)
        self._reposition_all()

    def _setup_ui(self, message, type):
        self.setFixedWidth(380)
        self.setMinimumHeight(50)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        colors = {
            "success": ("#059669", "#d1fae5", "#065f46"),
            "error": ("#dc2626", "#fee2e2", "#991b1b"),
            "warning": ("#d97706", "#fef3c7", "#92400e"),
            "info": ("#2563eb", "#dbeafe", "#1e40af"),
        }
        bg_color, light_bg, text_color = colors.get(type, colors["info"])

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background: {light_bg};
                border-left: 5px solid {bg_color};
                border-radius: 10px;
                padding: 12px 16px;
            }}
        """)
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(12, 10, 12, 10)

        icon_map = {
            "success": "✓",
            "error": "✕",
            "warning": "⚠",
            "info": "ℹ",
        }
        icon_label = QLabel(icon_map.get(type, "ℹ"))
        icon_label.setStyleSheet(f"font-size: 20px; color: {bg_color};")
        icon_label.setFixedWidth(30)
        container_layout.addWidget(icon_label)

        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(f"color: {text_color}; font-size: 13px; font-weight: 500;")
        container_layout.addWidget(msg_label, 1)

        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                font-size: 18px;
                color: {text_color};
                font-weight: bold;
            }}
            QPushButton:hover {{ background: rgba(0,0,0,0.1); border-radius: 12px; }}
        """)
        close_btn.clicked.connect(self.close_toast)
        container_layout.addWidget(close_btn)

        layout.addWidget(container)

        # Auto-cierre
        QTimer.singleShot(duration, self.close_toast)

    def _setup_animation(self):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def _reposition_all(self):
        """Reubica todos los toasts visibles."""
        y_offset = 20
        for toast in Toast._instances:
            if toast.isVisible():
                toast.move(toast.parent().width() - 410, y_offset if toast.parent() else 20)
                y_offset += toast.height() + 10

    def close_toast(self):
        """Cierra el toast con animación."""
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(300)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.finished.connect(self._do_close)
        self.fade_out.start()

    def _do_close(self):
        if self in Toast._instances:
            Toast._instances.remove(self)
        self.close()
        self.deleteLater()
        self._reposition_all()

    @staticmethod
    def show_success(message, parent=None, duration=3000):
        Toast(message, "success", duration, parent)

    @staticmethod
    def show_error(message, parent=None, duration=4000):
        Toast(message, "error", duration, parent)

    @staticmethod
    def show_warning(message, parent=None, duration=3500):
        Toast(message, "warning", duration, parent)

    @staticmethod
    def show_info(message, parent=None, duration=3000):
        Toast(message, "info", duration, parent)