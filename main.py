"""
main.py
Punto de entrada de la aplicación Taller Multiservicio PRO.
Framework: Flet (Desktop)
Arquitectura: MVC
"""

import flet as ft
from config.settings import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from src.controllers.auth_controller import AuthController
from src.controllers.workshop_controller import WorkshopController
from src.views.login_view import LoginView
from src.views.home_view import HomeView
from src.views.profile_view import ProfileView


def main(page: ft.Page):
    """Entry point de Flet."""

    # ── Configuración de la ventana ─────────────────────
    page.title = APP_NAME
    page.window.width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.window.min_width = WINDOW_MIN_WIDTH
    page.window.min_height = WINDOW_MIN_HEIGHT
    page.window.center()
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.fonts = {"Roboto": "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap"}

    # ── Controladores (singletons en la sesión) ─────────
    auth = AuthController()
    workshop = WorkshopController(auth)

    # ── Vistas ──────────────────────────────────────────
    login_view = LoginView(page, auth)
    home_view = HomeView(page, auth, workshop)
    profile_view = ProfileView(page, auth)

    # ── Contenedor principal ────────────────────────────
    main_container = ft.Container(expand=True)

    def route_change(route_event: ft.RouteChangeEvent):
        """Maneja el cambio de ruta."""
        route = route_event.route
        main_container.content = None

        if route == "/login" or route == "/":
            # Si ya está autenticado, redirigir a home
            if auth.is_authenticated:
                page.go("/home")
                return
            main_container.content = login_view.build()

        elif route == "/home":
            if not auth.is_authenticated:
                page.go("/login")
                return
            main_container.content = home_view.build()

        elif route == "/profile":
            if not auth.is_authenticated:
                page.go("/login")
                return
            main_container.content = profile_view.build()

        else:
            # Ruta desconocida → redirigir según auth
            page.go("/home" if auth.is_authenticated else "/login")
            return

        page.update()

    # ── Inicializar enrutamiento ────────────────────────
    page.on_route_change = route_change
    page.add(main_container)
    page.go("/login")


if __name__ == "__main__":
    ft.app(target=main)
# ft.app(target=main, view=ft.AppView.WEB_BROWSER)
# ft.run(main)