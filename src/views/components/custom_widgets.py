"""
src/views/components/custom_widgets.py
Componentes Flet reutilizables con estilo corporativo del taller.
"""

import flet as ft
from config.settings import COLOR_PRIMARY, COLOR_ACCENT, COLOR_BG, COLOR_SURFACE, COLOR_TEXT


# ── Colores ─────────────────────────────────────────────

COLOR_ERROR = "#D32F2F"
COLOR_SUCCESS = "#388E3C"
COLOR_WARNING = "#F57C00"
COLOR_INFO = "#1976D2"
COLOR_BORDER = "#BDBDBD"
COLOR_DISABLED = "#9E9E9E"
COLOR_WHITE = "#FFFFFF"
COLOR_CARD_BG = "#F5F5F5"


# ── Botones ─────────────────────────────────────────────

class CustomButton(ft.ElevatedButton):
    """Botón elevado con estilo del taller."""

    def __init__(self, text: str, on_click=None, icon: str = None,
                 variant: str = "primary", width: int = None, height: int = 48,
                 disabled: bool = False, tooltip: str = None):
        colors = {
            "primary": (COLOR_PRIMARY, COLOR_WHITE),
            "accent": (COLOR_ACCENT, COLOR_WHITE),
            "danger": (COLOR_ERROR, COLOR_WHITE),
            "success": (COLOR_SUCCESS, COLOR_WHITE),
            "outline": (COLOR_WHITE, COLOR_PRIMARY),
        }
        bg, fg = colors.get(variant, colors["primary"])
        style = ft.ButtonStyle(
            bgcolor=bg, color=fg, shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding(16, 8, 16, 8),
        )
        super().__init__(
            text=text, on_click=on_click, icon=icon, style=style,
            width=width, height=height, disabled=disabled, tooltip=tooltip,
        )


class CustomIconButton(ft.IconButton):
    """Botón de ícono estilizado."""

    def __init__(self, icon: str, on_click=None, tooltip: str = None,
                 variant: str = "default", size: int = 24):
        colors = {
            "default": COLOR_TEXT,
            "primary": COLOR_PRIMARY,
            "danger": COLOR_ERROR,
            "accent": COLOR_ACCENT,
        }
        super().__init__(
            icon=icon, on_click=on_click, tooltip=tooltip,
            icon_color=colors.get(variant, COLOR_TEXT), icon_size=size,
        )


# ── Campos de texto ─────────────────────────────────────

class CustomTextField(ft.TextField):
    """Campo de texto con estilo consistente."""

    def __init__(self, label: str = None, hint_text: str = None,
                 icon: str = None, password: bool = False, width: int = None,
                 multiline: bool = False, min_lines: int = 1, max_lines: int = 5,
                 read_only: bool = False, value: str = None,
                 on_change=None, on_submit=None, autofocus: bool = False,
                 keyboard_type: str = None, prefix_text: str = None,
                 suffix_text: str = None, max_length: int = None):
        super().__init__(
            label=label, hint_text=hint_text, prefix_icon=icon if icon else None,
            password=password, can_reveal_password=password,
            width=width, multiline=multiline, min_lines=min_lines,
            max_lines=max_lines, read_only=read_only, value=value,
            on_change=on_change, on_submit=on_submit, autofocus=autofocus,
            keyboard_type=keyboard_type, prefix_text=prefix_text,
            suffix_text=suffix_text, max_length=max_length,
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_PRIMARY,
            cursor_color=COLOR_PRIMARY,
            text_style=ft.TextStyle(color=COLOR_TEXT, size=14),
            label_style=ft.TextStyle(color=COLOR_TEXT),
            border_radius=8,
            filled=True,
            bgcolor=COLOR_WHITE,
        )


class CustomDropdown(ft.Dropdown):
    """Dropdown estilizado."""

    def __init__(self, label: str = None, options: list = None,
                 value: str = None, width: int = None, on_change=None,
                 hint_text: str = None):
        opts = []
        if options:
            for opt in options:
                if isinstance(opt, str):
                    opts.append(ft.dropdown.Option(opt))
                elif isinstance(opt, dict):
                    opts.append(ft.dropdown.Option(key=opt.get("value", opt.get("key")),
                                                    text=opt.get("text", opt.get("label"))))
                else:
                    opts.append(opt)
        super().__init__(
            label=label, options=opts, value=value, width=width,
            on_change=on_change, hint_text=hint_text,
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_PRIMARY,
            bgcolor=COLOR_WHITE,
            border_radius=8,
        )


# ── Tarjetas ────────────────────────────────────────────

class CustomCard(ft.Card):
    """Tarjeta elevada con padding."""

    def __init__(self, content: ft.Control, padding: int = 16,
                 elevation: int = 2, width: int = None, height: int = None,
                 on_click=None):
        super().__init__(
            content=ft.Container(
                content=content, padding=padding, bgcolor=COLOR_WHITE,
                border_radius=12,
            ),
            elevation=elevation, width=width, height=height,
            color=COLOR_WHITE, on_click=on_click,
        )


class StatCard(ft.Card):
    """Tarjeta de estadística para dashboard."""

    def __init__(self, title: str, value: str, icon: str = None,
                 color: str = COLOR_PRIMARY, subtitle: str = None):
        icon_widget = ft.Icon(name=icon, color=color, size=32) if icon else None
        content = ft.Column([
            ft.Row([
                icon_widget,
                ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=color),
            ], spacing=12, alignment=ft.MainAxisAlignment.CENTER) if icon_widget else
            ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=color, text_align=ft.TextAlign.CENTER),
            ft.Text(title, size=12, color=COLOR_DISABLED, text_align=ft.TextAlign.CENTER),
            ft.Text(subtitle, size=11, color=COLOR_TEXT, text_align=ft.TextAlign.CENTER) if subtitle else ft.Container(),
        ], spacing=4, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        super().__init__(
            content=ft.Container(content=content, padding=20, bgcolor=COLOR_WHITE, border_radius=12),
            elevation=2, width=180, height=140, color=COLOR_WHITE,
        )


# ── Tabla de datos ──────────────────────────────────────

class CustomDataTable(ft.DataTable):
    """Tabla de datos estilizada."""

    def __init__(self, columns: list[str], rows: list[list] = None,
                 on_row_click=None, sortable: bool = True, width: int = None):
        cols = [
            ft.DataColumn(
                ft.Text(col, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY, size=13),
                on_sort=lambda e, i=i: print(f"Sort col {i}") if sortable else None,
            )
            for i, col in enumerate(columns)
        ]
        data_rows = []
        if rows:
            for row in rows:
                cells = [
                    ft.DataCell(ft.Text(str(cell), size=12, color=COLOR_TEXT))
                    for cell in row
                ]
                data_rows.append(ft.DataRow(
                    cells=cells,
                    on_select_changed=lambda e, r=row: on_row_click(r) if on_row_click else None,
                ))
        super().__init__(
            columns=cols, rows=data_rows, width=width,
            border=ft.border.all(1, COLOR_BORDER),
            border_radius=8,
            heading_row_color=ft.Colors.with_opacity(0.05, COLOR_PRIMARY, ft.Colors.WHITE),
            data_row_color={"hovered": ft.Colors.with_opacity(0.03, COLOR_ACCENT, ft.Colors.WHITE)},
            divider_thickness=0.5,
        )

    def update_rows(self, rows: list[list], on_row_click=None):
        """Actualiza las filas de la tabla."""
        self.rows.clear()
        for row in rows:
            cells = [ft.DataCell(ft.Text(str(cell), size=12, color=COLOR_TEXT)) for cell in row]
            self.rows.append(ft.DataRow(
                cells=cells,
                on_select_changed=lambda e, r=row: on_row_click(r) if on_row_click else None,
            ))
        self.update()


# ── SnackBar / Notificaciones ───────────────────────────

class CustomSnackBar(ft.SnackBar):
    """Barra de notificación estilizada."""

    def __init__(self, message: str, variant: str = "info"):
        colors = {
            "info": COLOR_INFO,
            "success": COLOR_SUCCESS,
            "error": COLOR_ERROR,
            "warning": COLOR_WARNING,
        }
        super().__init__(
            content=ft.Text(message, color=COLOR_WHITE, size=14),
            bgcolor=colors.get(variant, COLOR_INFO),
            behavior=ft.SnackBarBehavior.FLOATING,
            duration=4000,
            show_close_icon=True,
        )


# ── Diálogos ────────────────────────────────────────────

class CustomDialog(ft.AlertDialog):
    """Diálogo de confirmación estilizado."""

    def __init__(self, title: str, content: str = "",
                 on_confirm=None, on_cancel=None,
                 confirm_text: str = "Aceptar", cancel_text: str = "Cancelar",
                 variant: str = "primary"):
        colors = {
            "primary": COLOR_PRIMARY,
            "danger": COLOR_ERROR,
            "warning": COLOR_WARNING,
        }
        bg = colors.get(variant, COLOR_PRIMARY)
        super().__init__(
            title=ft.Text(title, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
            content=ft.Text(content, color=COLOR_TEXT) if content else None,
            actions=[
                ft.TextButton(cancel_text, on_click=on_cancel) if on_cancel else ft.Container(),
                ft.ElevatedButton(
                    confirm_text, on_click=on_confirm,
                    style=ft.ButtonStyle(bgcolor=bg, color=COLOR_WHITE, shape=ft.RoundedRectangleBorder(radius=8)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=12),
        )


# ── Barra de navegación ─────────────────────────────────

class CustomNavigationRail(ft.NavigationRail):
    """Barra de navegación lateral estilizada."""

    def __init__(self, destinations: list[dict], on_change=None,
                 selected_index: int = 0):
        """
        destinations: [{"icon": ft.icons.DASHBOARD, "label": "Dashboard"}, ...]
        """
        dests = [
            ft.NavigationRailDestination(
                icon=d["icon"],
                selected_icon=d.get("selected_icon", d["icon"]),
                label=d["label"],
            )
            for d in destinations
        ]
        super().__init__(
            destinations=dests,
            selected_index=selected_index,
            on_change=on_change,
            bgcolor=COLOR_SURFACE,
            indicator_color=COLOR_PRIMARY,
            selected_label_text_style=ft.TextStyle(color=COLOR_PRIMARY, weight=ft.FontWeight.BOLD),
            unselected_label_text_style=ft.TextStyle(color=COLOR_TEXT),
            leading=ft.Container(height=20),
            trailing=ft.Container(height=20),
            width=80,
            extended=False,
        )


# ── Barra superior ──────────────────────────────────────

class CustomAppBar(ft.AppBar):
    """Barra superior de la aplicación."""

    def __init__(self, title: str, user_name: str = "", role_name: str = "",
                 on_logout=None, on_profile=None):
        super().__init__(
            leading=ft.Icon(name=ft.icons.CONSTRUCTION, color=COLOR_ACCENT, size=28),
            leading_width=60,
            title=ft.Text(title, weight=ft.FontWeight.BOLD, color=COLOR_WHITE, size=18),
            center_title=False,
            bgcolor=COLOR_PRIMARY,
            actions=[
                ft.Container(
                    content=ft.Column([
                        ft.Text(user_name, size=12, weight=ft.FontWeight.BOLD, color=COLOR_WHITE),
                        ft.Text(role_name, size=10, color=ft.Colors.with_opacity(0.7, COLOR_WHITE)),
                    ], spacing=0, alignment=ft.MainAxisAlignment.CENTER),
                    margin=ft.margin.only(right=8),
                ),
                ft.PopupMenuButton(
                    icon=ft.icons.ACCOUNT_CIRCLE,
                    icon_color=COLOR_WHITE,
                    items=[
                        ft.PopupMenuItem(text="Perfil", icon=ft.icons.PERSON, on_click=on_profile),
                        ft.PopupMenuItem(),
                        ft.PopupMenuItem(text="Cerrar sesión", icon=ft.icons.LOGOUT, on_click=on_logout),
                    ],
                ),
            ],
        )


# ── Indicador de carga ──────────────────────────────────

class LoadingIndicator(ft.Container):
    """Indicador de carga centrado."""

    def __init__(self, message: str = "Cargando..."):
        super().__init__(
            content=ft.Column([
                ft.ProgressRing(color=COLOR_PRIMARY, width=40, height=40),
                ft.Text(message, size=14, color=COLOR_DISABLED),
            ], spacing=12, alignment=ft.MainAxisAlignment.CENTER,
               horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True,
        )


# ── Estado vacío ────────────────────────────────────────

class EmptyState(ft.Container):
    """Mensaje de estado vacío."""

    def __init__(self, icon: str = ft.icons.INBOX, message: str = "No hay datos disponibles",
                 submessage: str = None):
        content = ft.Column([
            ft.Icon(name=icon, color=COLOR_DISABLED, size=48),
            ft.Text(message, size=16, weight=ft.FontWeight.BOLD, color=COLOR_DISABLED),
            ft.Text(submessage, size=12, color=COLOR_DISABLED) if submessage else ft.Container(),
        ], spacing=8, alignment=ft.MainAxisAlignment.CENTER,
           horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        super().__init__(
            content=content, alignment=ft.alignment.center, expand=True,
        )


# ── Chip / Badge ────────────────────────────────────────

class StatusBadge(ft.Container):
    """Badge de estado coloreado."""

    COLORS = {
        "PENDIENTE": COLOR_WARNING,
        "EN_PROCESO": COLOR_INFO,
        "COMPLETADO": COLOR_SUCCESS,
        "ENTREGADO": COLOR_PRIMARY,
        "CANCELADO": COLOR_ERROR,
        "PAGADO": COLOR_SUCCESS,
        "CREDITO": COLOR_WARNING,
        "VENCIDO": COLOR_ERROR,
    }

    def __init__(self, status: str):
        color = self.COLORS.get(status.upper(), COLOR_DISABLED)
        super().__init__(
            content=ft.Text(status, size=11, weight=ft.FontWeight.BOLD, color=COLOR_WHITE),
            padding=ft.Padding(8, 2, 8, 2),
            border_radius=12,
            bgcolor=color,
            alignment=ft.alignment.center,
        )


# ── Sección colapsable ──────────────────────────────────

class CollapsibleSection(ft.Container):
    """Sección expandible/colapsable."""

    def __init__(self, title: str, content: ft.Control, expanded: bool = True):
        self._expanded = expanded
        self._toggle = ft.IconButton(
            icon=ft.icons.EXPAND_LESS if expanded else ft.icons.EXPAND_MORE,
            icon_color=COLOR_PRIMARY, icon_size=20,
        )
        self._content_container = ft.Container(
            content=content, visible=expanded, animate_opacity=200,
        )
        header = ft.Row([
            ft.Text(title, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY, size=14),
            self._toggle,
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self._toggle.on_click = self._toggle_section
        super().__init__(
            content=ft.Column([header, self._content_container], spacing=8),
            padding=12, border_radius=8, bgcolor=COLOR_CARD_BG,
        )

    def _toggle_section(self, e):
        self._expanded = not self._expanded
        self._toggle.icon = ft.icons.EXPAND_LESS if self._expanded else ft.icons.EXPAND_MORE
        self._content_container.visible = self._expanded
        self._toggle.update()
        self._content_container.update()