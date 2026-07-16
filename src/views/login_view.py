"""
src/views/login_view.py
Vista de inicio de sesión - Pantalla de login del taller.
"""

import flet as ft
from config.settings import COLOR_PRIMARY, COLOR_ACCENT, COLOR_BG, COLOR_TEXT, APP_NAME, APP_VERSION
from src.views.components.custom_widgets import (
    CustomTextField, CustomButton, CustomSnackBar, COLOR_ERROR, COLOR_WHITE, COLOR_DISABLED,
)


class LoginView:
    """Pantalla de inicio de sesión."""

    def __init__(self, page: ft.Page, auth_controller):
        self.page = page
        self.auth = auth_controller
        self._username_field = None
        self._password_field = None
        self._login_btn = None
        self._error_text = None
        self._loading = False

    def build(self) -> ft.Control:
        """Construye la vista de login."""
        self._username_field = CustomTextField(
            label="Usuario",
            hint_text="Ingrese su nombre de usuario",
            icon=ft.icons.PERSON,
            autofocus=True,
            on_submit=lambda e: self._password_field.focus(),
        )
        self._password_field = CustomTextField(
            label="Contraseña",
            hint_text="Ingrese su contraseña",
            icon=ft.icons.LOCK,
            password=True,
            on_submit=lambda e: self._do_login(),
        )
        self._login_btn = CustomButton(
            text="Iniciar Sesión",
            icon=ft.icons.LOGIN,
            variant="primary",
            width=300,
            on_click=lambda e: self._do_login(),
        )
        self._error_text = ft.Text("", color=COLOR_ERROR, size=12, visible=False)

        # Logo / branding
        logo = ft.Column([
            ft.Icon(name=ft.icons.CONSTRUCTION, color=COLOR_ACCENT, size=64),
            ft.Text(APP_NAME, size=28, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
            ft.Text("Sistema de Gestión de Taller", size=14, color=COLOR_DISABLED),
            ft.Text(f"v{APP_VERSION}", size=11, color=COLOR_DISABLED),
        ], spacing=4, alignment=ft.MainAxisAlignment.CENTER,
           horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        # Formulario
        form = ft.Column([
            self._username_field,
            self._password_field,
            self._error_text,
            ft.Container(height=8),
            self._login_btn,
        ], spacing=12, alignment=ft.MainAxisAlignment.CENTER,
           horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        # Layout principal
        return ft.Container(
            content=ft.Column([
                ft.Container(height=40),
                logo,
                ft.Container(height=24),
                ft.Card(
                    content=ft.Container(
                        content=form,
                        padding=32,
                        bgcolor=COLOR_WHITE,
                        border_radius=16,
                    ),
                    elevation=4,
                    width=380,
                    color=COLOR_WHITE,
                ),
                ft.Container(height=16),
                ft.Text("© 2026 Taller Multiservicio PRO", size=11, color=COLOR_DISABLED),
            ], spacing=0, alignment=ft.MainAxisAlignment.CENTER,
               horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True,
            bgcolor=COLOR_BG,
        )

    def _do_login(self):
        """Ejecuta el login."""
        if self._loading:
            return
        username = self._username_field.value.strip() if self._username_field.value else ""
        password = self._password_field.value if self._password_field.value else ""

        if not username or not password:
            self._show_error("Usuario y contraseña son requeridos")
            return

        self._set_loading(True)
        self._error_text.visible = False
        self._error_text.update()

        success, message = self.auth.login(username, password)

        self._set_loading(False)

        if success:
            self.page.show_snack_bar(CustomSnackBar(message, "success"))
            self.page.go("/home")
        else:
            self._show_error(message)

    def _set_loading(self, loading: bool):
        self._loading = loading
        self._login_btn.disabled = loading
        self._login_btn.text = "Ingresando..." if loading else "Iniciar Sesión"
        self._username_field.disabled = loading
        self._password_field.disabled = loading
        self._login_btn.update()
        self._username_field.update()
        self._password_field.update()

    def _show_error(self, message: str):
        self._error_text.value = message
        self._error_text.visible = True
        self._error_text.update()