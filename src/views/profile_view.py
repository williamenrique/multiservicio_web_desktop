"""
src/views/profile_view.py
Vista de perfil de usuario.
"""

import flet as ft
from config.settings import COLOR_PRIMARY, COLOR_ACCENT, COLOR_BG, COLOR_TEXT, APP_NAME
from src.views.components.custom_widgets import (
    CustomAppBar, CustomCard, CustomButton, CustomTextField,
    CustomSnackBar, LoadingIndicator,
    COLOR_WHITE, COLOR_DISABLED, COLOR_SUCCESS,
)


class ProfileView:
    """Pantalla de perfil del usuario autenticado."""

    def __init__(self, page: ft.Page, auth_controller):
        self.page = page
        self.auth = auth_controller

    def build(self) -> ft.Control:
        """Construye la vista de perfil."""
        user = self.auth.current_user
        if not user:
            self.page.go("/login")
            return ft.Container()

        appbar = CustomAppBar(
            title="Mi Perfil",
            user_name=self.auth.get_user_display_name(),
            role_name=self.auth.get_user_role_name(),
            on_logout=lambda e: self._logout(),
            on_profile=None,
        )

        # Información del usuario
        info_items = [
            ("Usuario", user.get("username", "-")),
            ("Nombre", user.get("nombre", "-")),
            ("Rol", self.auth.get_user_role_name()),
            ("Email", user.get("email", "-")),
            ("Teléfono", user.get("telefono", "-")),
        ]

        info_rows = []
        for label, value in info_items:
            info_rows.append(
                ft.Row([
                    ft.Text(label, size=13, weight=ft.FontWeight.BOLD, color=COLOR_DISABLED, width=100),
                    ft.Text(value, size=14, color=COLOR_TEXT),
                ], spacing=8)
            )

        info_card = CustomCard(
            content=ft.Column(info_rows, spacing=12),
            width=500,
        )

        # Cambio de contraseña
        self._current_pw = CustomTextField(
            label="Contraseña actual",
            icon=ft.icons.LOCK,
            password=True,
            width=300,
        )
        self._new_pw = CustomTextField(
            label="Nueva contraseña",
            icon=ft.icons.LOCK_RESET,
            password=True,
            width=300,
        )
        self._confirm_pw = CustomTextField(
            label="Confirmar nueva contraseña",
            icon=ft.icons.LOCK_RESET,
            password=True,
            width=300,
        )
        self._pw_error = ft.Text("", color="#D32F2F", size=12, visible=False)
        self._pw_success = ft.Text("", color=COLOR_SUCCESS, size=12, visible=False)

        change_pw_btn = CustomButton(
            text="Cambiar Contraseña",
            icon=ft.icons.SAVE,
            variant="primary",
            width=300,
            on_click=lambda e: self._change_password(),
        )

        pw_card = CustomCard(
            content=ft.Column([
                ft.Text("Cambiar Contraseña", size=16, weight=ft.FontWeight.BOLD,
                        color=COLOR_PRIMARY),
                ft.Container(height=8),
                self._current_pw,
                self._new_pw,
                self._confirm_pw,
                self._pw_error,
                self._pw_success,
                ft.Container(height=8),
                change_pw_btn,
            ], spacing=8),
            width=500,
        )

        # Botón volver
        back_btn = CustomButton(
            text="Volver al Inicio",
            icon=ft.icons.ARROW_BACK,
            variant="outline",
            on_click=lambda e: self.page.go("/home"),
        )

        return ft.Column([
            appbar,
            ft.Container(
                content=ft.Column([
                    ft.Text("Perfil de Usuario", size=22, weight=ft.FontWeight.BOLD,
                            color=COLOR_PRIMARY),
                    ft.Container(height=16),
                    info_card,
                    ft.Container(height=24),
                    pw_card,
                    ft.Container(height=16),
                    back_btn,
                ], spacing=0, scroll=ft.ScrollMode.AUTO),
                padding=24,
                expand=True,
                bgcolor=COLOR_BG,
            ),
        ], spacing=0, expand=True)

    def _change_password(self):
        """Lógica de cambio de contraseña."""
        self._pw_error.visible = False
        self._pw_success.visible = False
        self._pw_error.update()
        self._pw_success.update()

        current = self._current_pw.value or ""
        new_pw = self._new_pw.value or ""
        confirm = self._confirm_pw.value or ""

        if not current or not new_pw or not confirm:
            self._pw_error.value = "Todos los campos son requeridos"
            self._pw_error.visible = True
            self._pw_error.update()
            return

        if new_pw != confirm:
            self._pw_error.value = "Las contraseñas nuevas no coinciden"
            self._pw_error.visible = True
            self._pw_error.update()
            return

        if len(new_pw) < 6:
            self._pw_error.value = "La contraseña debe tener al menos 6 caracteres"
            self._pw_error.visible = True
            self._pw_error.update()
            return

        # Verificar contraseña actual
        from src.models.user_model import UserModel
        user = UserModel.authenticate(self.auth.current_user["username"], current)
        if user is None:
            self._pw_error.value = "Contraseña actual incorrecta"
            self._pw_error.visible = True
            self._pw_error.update()
            return

        # Cambiar contraseña
        ok = UserModel.change_password(self.auth.current_user["id"], new_pw)
        if ok:
            self._pw_success.value = "Contraseña actualizada exitosamente"
            self._pw_success.visible = True
            self._pw_success.update()
            self._current_pw.value = ""
            self._new_pw.value = ""
            self._confirm_pw.value = ""
            self._current_pw.update()
            self._new_pw.update()
            self._confirm_pw.update()
        else:
            self._pw_error.value = "Error al cambiar la contraseña"
            self._pw_error.visible = True
            self._pw_error.update()

    def _logout(self):
        self.auth.logout()
        self.page.go("/login")