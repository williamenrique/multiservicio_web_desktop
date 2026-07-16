"""
src/views/home_view.py
Vista principal / Dashboard del taller con navegación lateral.
"""

import flet as ft
from config.settings import (
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_BG, COLOR_SURFACE, COLOR_TEXT,
    APP_NAME, ESTADOS_ORDEN,
)
from src.views.components.custom_widgets import (
    CustomAppBar, CustomNavigationRail, StatCard, CustomDataTable,
    CustomSnackBar, StatusBadge, EmptyState, LoadingIndicator,
    CustomButton, CustomTextField, CustomDropdown, CustomDialog,
    COLOR_WHITE, COLOR_DISABLED, COLOR_ERROR, COLOR_SUCCESS,
)


class HomeView:
    """Dashboard principal con navegación por secciones."""

    NAV_ITEMS = [
        {"icon": ft.icons.DASHBOARD, "label": "Inicio"},
        {"icon": ft.icons.BUILD, "label": "Órdenes"},
        {"icon": ft.icons.PEOPLE, "label": "Clientes"},
        {"icon": ft.icons.INVENTORY_2, "label": "Inventario"},
        {"icon": ft.icons.RECEIPT, "label": "Facturas"},
    ]

    def __init__(self, page: ft.Page, auth_controller, workshop_controller):
        self.page = page
        self.auth = auth_controller
        self.workshop = workshop_controller
        self._nav_rail = None
        self._content_area = None
        self._appbar = None
        self._current_section = 0

    def build(self) -> ft.Control:
        """Construye la vista principal."""
        self._appbar = CustomAppBar(
            title=APP_NAME,
            user_name=self.auth.get_user_display_name(),
            role_name=self.auth.get_user_role_name(),
            on_logout=lambda e: self._logout(),
            on_profile=lambda e: self.page.go("/profile"),
        )

        self._nav_rail = CustomNavigationRail(
            destinations=self.NAV_ITEMS,
            selected_index=0,
            on_change=self._on_nav_change,
        )

        self._content_area = ft.Container(
            content=self._build_dashboard(),
            expand=True,
            padding=24,
            bgcolor=COLOR_BG,
        )

        return ft.Column([
            self._appbar,
            ft.Row([
                self._nav_rail,
                ft.VerticalDivider(width=1, color=COLOR_DISABLED),
                self._content_area,
            ], expand=True, spacing=0),
        ], spacing=0, expand=True)

    # ── Navegación ───────────────────────────────────────

    def _on_nav_change(self, e):
        self._current_section = e.control.selected_index
        sections = [
            self._build_dashboard,
            self._build_ordenes,
            self._build_clientes,
            self._build_inventario,
            self._build_facturas,
        ]
        self._content_area.content = sections[self._current_section]()
        self._content_area.update()

    def _logout(self):
        self.auth.logout()
        self.page.go("/login")

    # ── Dashboard ────────────────────────────────────────

    def _build_dashboard(self) -> ft.Control:
        """Panel de inicio con estadísticas."""
        data = self.workshop.get_dashboard_data()
        activas = data.get("ordenes_activas", 0)
        ventas = data.get("ventas_hoy", {})
        stock_bajo = data.get("stock_bajo", [])

        total_ventas = ventas.get("total", 0) if ventas else 0
        cantidad_ventas = ventas.get("cantidad", 0) if ventas else 0

        stats_row = ft.Row([
            StatCard("Órdenes Activas", str(activas), ft.icons.BUILD, COLOR_ACCENT),
            StatCard("Ventas Hoy", f"${total_ventas:,.0f}", ft.icons.ATTACH_MONEY, COLOR_SUCCESS,
                     f"{cantidad_ventas} facturas"),
            StatCard("Stock Bajo", str(len(stock_bajo)), ft.icons.WARNING, "#F57C00",
                     "Productos bajo mínimo"),
        ], spacing=16, alignment=ft.MainAxisAlignment.CENTER,
           wrap=True, run_spacing=16)

        # Acciones rápidas
        acciones = ft.Row([
            CustomButton("Nueva Orden", icon=ft.icons.ADD, variant="accent",
                         on_click=lambda e: self._go_section(1)),
            CustomButton("Buscar Cliente", icon=ft.icons.SEARCH, variant="outline",
                         on_click=lambda e: self._go_section(2)),
            CustomButton("Nueva Factura", icon=ft.icons.RECEIPT, variant="outline",
                         on_click=lambda e: self._go_section(4)),
        ], spacing=12, alignment=ft.MainAxisAlignment.CENTER, wrap=True)

        # Stock bajo
        stock_section = ft.Container()
        if stock_bajo:
            stock_rows = [[p.get("nombre", ""), str(p.get("stock_actual", 0)),
                           str(p.get("stock_minimo", 0)), p.get("unidad", "")]
                          for p in stock_bajo[:5]]
            stock_section.content = ft.Column([
                ft.Text("Productos con stock bajo", weight=ft.FontWeight.BOLD,
                        color=COLOR_PRIMARY, size=14),
                CustomDataTable(
                    columns=["Producto", "Actual", "Mínimo", "Unidad"],
                    rows=stock_rows,
                ),
            ], spacing=8)
        else:
            stock_section.content = ft.Text("No hay productos con stock bajo",
                                            color=COLOR_SUCCESS, size=13)

        return ft.Column([
            ft.Text("Panel de Control", size=22, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
            ft.Container(height=16),
            stats_row,
            ft.Container(height=24),
            ft.Text("Acciones Rápidas", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
            ft.Container(height=8),
            acciones,
            ft.Container(height=24),
            stock_section,
        ], spacing=0, scroll=ft.ScrollMode.AUTO)

    def _go_section(self, index: int):
        self._nav_rail.selected_index = index
        self._current_section = index
        self._content_area.content = [
            self._build_dashboard,
            self._build_ordenes,
            self._build_clientes,
            self._build_inventario,
            self._build_facturas,
        ][index]()
        self._nav_rail.update()
        self._content_area.update()

    # ── Órdenes ──────────────────────────────────────────

    def _build_ordenes(self) -> ft.Control:
        """Sección de órdenes de servicio."""
        ordenes = self.workshop.get_ordenes()

        if not ordenes:
            return EmptyState(icon=ft.icons.BUILD, message="No hay órdenes registradas",
                              submessage="Cree una nueva orden desde el panel de inicio")

        rows = []
        for o in ordenes:
            rows.append([
                str(o.get("id", "")),
                o.get("placa", ""),
                o.get("cliente_nombre", o.get("cliente", "")),
                o.get("estado", ""),
                str(o.get("fecha_ingreso", "")),
            ])

        # Filtro por estado
        filtro = CustomDropdown(
            label="Filtrar por estado",
            options=["TODOS"] + ESTADOS_ORDEN,
            value="TODOS",
            width=200,
            on_change=lambda e: self._filtrar_ordenes(e.control.value),
        )

        tabla = CustomDataTable(
            columns=["#", "Placa", "Cliente", "Estado", "Fecha Ingreso"],
            rows=rows,
            on_row_click=lambda r: self._ver_orden(r[0]),
        )

        return ft.Column([
            ft.Row([
                ft.Text("Órdenes de Servicio", size=22, weight=ft.FontWeight.BOLD,
                        color=COLOR_PRIMARY),
                CustomButton("Nueva Orden", icon=ft.icons.ADD, variant="accent",
                             on_click=lambda e: self._nueva_orden()),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            filtro,
            ft.Container(height=12),
            tabla,
        ], spacing=0, scroll=ft.ScrollMode.AUTO)

    def _filtrar_ordenes(self, estado: str):
        ordenes = self.workshop.get_ordenes(None if estado == "TODOS" else estado)
        # Actualizar tabla... (requiere referencia a la tabla)
        self.page.show_snack_bar(CustomSnackBar(f"Filtro: {estado}", "info"))

    def _ver_orden(self, orden_id):
        """Diálogo con detalle completo de la orden."""
        orden = self.workshop.get_orden(int(orden_id))
        if not orden:
            self.page.show_snack_bar(CustomSnackBar("Orden no encontrada", "error"))
            return

        # ── Información general ──────────────────────────
        info_col = ft.Column(spacing=4)
        campos = [
            ("# Orden", str(orden.get("id", ""))),
            ("Cliente", orden.get("cliente_nombre", orden.get("cliente", ""))),
            ("Placa", orden.get("placa", "")),
            ("Mecánico", orden.get("mecanico_nombre", orden.get("mecanico", ""))),
            ("Kilometraje", str(orden.get("kilometraje", ""))),
            ("Combustible", str(orden.get("nivel_combustible", ""))),
            ("Estado", orden.get("estado", "")),
            ("Fecha ingreso", str(orden.get("fecha_ingreso", ""))),
        ]
        for label, val in campos:
            info_col.controls.append(
                ft.Row([
                    ft.Text(f"{label}:", size=12, weight=ft.FontWeight.BOLD,
                            color=COLOR_TEXT_SECONDARY, width=120),
                    ft.Text(val, size=13, color=COLOR_TEXT),
                ], spacing=4, tight=True)
            )

        # ── Diagnóstico ──────────────────────────────────
        diag = orden.get("diagnostico_entrada", "")
        diag_section = ft.Column(spacing=4) if diag else ft.Column()
        if diag:
            diag_section.controls = [
                ft.Text("Diagnóstico de entrada", weight=ft.FontWeight.BOLD, size=13,
                        color=COLOR_PRIMARY),
                ft.Container(
                    content=ft.Text(diag, size=12),
                    bgcolor=COLOR_BG, padding=10, border_radius=8,
                ),
            ]

        # ── Checklist ────────────────────────────────────
        checklist = orden.get("checklist", [])
        checklist_col = ft.Column(spacing=4)
        if checklist:
            checklist_col.controls.append(
                ft.Text("Checklist de ingreso", weight=ft.FontWeight.BOLD, size=13,
                        color=COLOR_PRIMARY))
            for item in checklist:
                estado = item.get("estado", 0)
                icon = ft.icons.CHECK_CIRCLE if estado else ft.icons.CANCEL
                color = COLOR_SUCCESS if estado else COLOR_ERROR
                obs = item.get("observacion", "")
                label = item.get("item", "")
                if obs:
                    label += f" ({obs})"
                checklist_col.controls.append(
                    ft.Row([
                        ft.Icon(icon, size=18, color=color),
                        ft.Text(label, size=12),
                    ], spacing=6, tight=True)
                )

        # ── Historial de estados ─────────────────────────
        historial = orden.get("historial_estados", [])
        hist_col = ft.Column(spacing=4)
        if historial:
            hist_col.controls.append(
                ft.Text("Historial de estados", weight=ft.FontWeight.BOLD, size=13,
                        color=COLOR_PRIMARY))
            for h in historial:
                hist_col.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                StatusBadge(h.get("estado_nuevo", "")),
                                ft.Text(str(h.get("fecha", "")), size=11,
                                        color=COLOR_TEXT_SECONDARY),
                            ], spacing=8, tight=True),
                            ft.Text(h.get("comentario", ""), size=11,
                                    color=COLOR_TEXT_SECONDARY) if h.get("comentario") else ft.Text(),
                        ], spacing=2, tight=True),
                        padding=8, bgcolor=COLOR_SURFACE, border_radius=6,
                    )
                )

        # ── Cambiar estado ───────────────────────────────
        estado_actual = orden.get("estado", "RECIBIDO")
        estados_posibles = ESTADOS_ORDEN
        idx_actual = estados_posibles.index(estado_actual) if estado_actual in estados_posibles else 0
        estados_futuros = estados_posibles[idx_actual + 1:] if idx_actual < len(estados_posibles) - 1 else []

        estado_dd = CustomDropdown(
            label="Nuevo estado",
            options=estados_futuros if estados_futuros else ["(Sin cambios disponibles)"],
            width=250,
        )
        comentario = ft.TextField(
            label="Comentario",
            hint_text="Motivo del cambio de estado...",
            multiline=True, min_lines=2, max_lines=3,
            width=400, border_color=COLOR_DISABLED,
        )

        def cambiar_estado(e):
            if not estados_futuros:
                return
            nuevo = estado_dd.value
            if not nuevo or nuevo == "(Sin cambios disponibles)":
                self.page.show_snack_bar(CustomSnackBar("Seleccione un estado válido", "warning"))
                return
            ok, msg = self.workshop.cambiar_estado_orden(
                int(orden_id), nuevo, comentario.value or "")
            self.page.close(dlg)
            if ok:
                self.page.show_snack_bar(CustomSnackBar(msg, "success"))
                self._content_area.content = self._build_ordenes()
                self._content_area.update()
            else:
                self.page.show_snack_bar(CustomSnackBar(msg, "error"))

        # ── Armar diálogo ────────────────────────────────
        content = ft.Column([
            ft.Text(f"Orden #{orden_id}", size=18, weight=ft.FontWeight.BOLD,
                    color=COLOR_PRIMARY),
            StatusBadge(estado_actual),
            ft.Divider(height=8),
            info_col,
            diag_section,
            ft.Container(height=8),
            checklist_col,
            ft.Container(height=8),
            hist_col,
            ft.Container(height=12),
            ft.Text("Cambiar estado", weight=ft.FontWeight.BOLD, size=13,
                    color=COLOR_PRIMARY),
            ft.Row([estado_dd], spacing=8),
            comentario,
            ft.Row([
                CustomButton("Cerrar", variant="outline",
                             on_click=lambda e: self.page.close(dlg)),
                CustomButton("Cambiar Estado", icon=ft.icons.UPDATE, variant="accent",
                             on_click=cambiar_estado),
            ], alignment=ft.MainAxisAlignment.END, spacing=8),
        ], spacing=0, scroll=ft.ScrollMode.AUTO, width=520)

        dlg = ft.AlertDialog(
            modal=True,
            content=content,
            content_padding=20,
        )
        self.page.open(dlg)

    def _nueva_orden(self):
        """Diálogo para crear una nueva orden de servicio."""
        # ── Campos del formulario ────────────────────────
        cliente_search = CustomTextField(
            label="Buscar cliente",
            hint_text="Nombre, teléfono o ID",
            icon=ft.icons.SEARCH,
            width=400,
        )
        cliente_info = ft.Text("", size=12, color=COLOR_TEXT)
        cliente_id = ft.Text("", visible=False)

        placa_dd = CustomDropdown(
            label="Vehículo (placa)",
            options=[],
            width=200,
        )

        mecanicos = self.workshop.get_mecanicos()
        mecanico_opts = [m["nombre"] for m in mecanicos]
        mecanico_dd = CustomDropdown(
            label="Mecánico asignado",
            options=mecanico_opts,
            width=200,
        )

        kilometraje = CustomTextField(label="Kilometraje", hint_text="Ej: 45000", width=200)
        nivel_comb = CustomTextField(label="Nivel combustible", hint_text="Ej: 1/4", width=200)

        diagnostico = ft.TextField(
            label="Diagnóstico de entrada",
            hint_text="Describa el problema reportado...",
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=500,
            border_color=COLOR_DISABLED,
        )
        observaciones = ft.TextField(
            label="Observaciones",
            hint_text="Notas adicionales...",
            multiline=True,
            min_lines=2,
            max_lines=4,
            width=500,
            border_color=COLOR_DISABLED,
        )

        # ── Checklist ────────────────────────────────────
        checklist_items = [
            "Llave de ruedas", "Gato", "Herramientas", "Tapa gasolina",
            "Radio", "Espejos", "Documentos", "Tapetes",
            "Llanta repuesto", "Extintor", "Botiquín", "Triángulos",
        ]
        checklist_checks = {}
        checklist_col = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, height=200)
        for item in checklist_items:
            cb = ft.Checkbox(label=item, value=False)
            checklist_checks[item] = cb
            checklist_col.controls.append(cb)

        # ── Resultados de búsqueda de cliente ────────────
        client_results = ft.Column(spacing=4, visible=False)

        def on_client_search(e):
            term = cliente_search.value
            if not term or len(term.strip()) < 2:
                return
            resultados = self.workshop.buscar_cliente(term.strip())
            client_results.controls.clear()
            if resultados:
                for c in resultados[:10]:
                    btn = ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.PERSON, size=18, color=COLOR_PRIMARY),
                            ft.Column([
                                ft.Text(c.get("nombre", ""), size=14, weight=ft.FontWeight.BOLD),
                                ft.Text(f"ID: {c.get('id', '')} | Tel: {c.get('telefono', '')}",
                                        size=11, color=COLOR_TEXT_SECONDARY),
                            ], spacing=0, tight=True),
                        ], spacing=8, tight=True),
                        style=ft.ButtonStyle(bgcolor={"": ft.colors.TRANSPARENT}),
                        on_click=lambda _, cid=c["id"], nom=c.get("nombre", ""),
                                      tel=c.get("telefono", ""): select_client(cid, nom, tel),
                    )
                    client_results.controls.append(btn)
                client_results.visible = True
            else:
                client_results.controls.append(
                    ft.Text("No se encontraron clientes", size=12, color=COLOR_ERROR))
                client_results.visible = True
            client_results.update()

        def select_client(cid, nombre, telefono):
            cliente_id.value = cid
            cliente_info.value = f"✓ {nombre} - {telefono}"
            cliente_info.color = COLOR_SUCCESS
            # Cargar vehículos del cliente
            vehiculos = self.workshop.get_vehiculos_cliente(cid)
            placa_dd.options = [v["placa"] for v in vehiculos] if vehiculos else ["(Sin vehículos)"]
            placa_dd.value = placa_dd.options[0] if placa_dd.options else ""
            placa_dd.update()
            client_results.visible = False
            cliente_info.update()
            client_results.update()

        cliente_search.on_submit = on_client_search

        # ── Botón de guardar ─────────────────────────────
        def guardar_orden(e):
            if not cliente_id.value:
                self.page.show_snack_bar(CustomSnackBar("Seleccione un cliente", "warning"))
                return
            if not placa_dd.value or placa_dd.value == "(Sin vehículos)":
                self.page.show_snack_bar(CustomSnackBar("Seleccione un vehículo", "warning"))
                return
            if not mecanico_dd.value:
                self.page.show_snack_bar(CustomSnackBar("Seleccione un mecánico", "warning"))
                return

            # Obtener ID del mecánico
            mecanico_id = ""
            for m in mecanicos:
                if m["nombre"] == mecanico_dd.value:
                    mecanico_id = m["id"]
                    break

            # Checklist
            checklist = []
            for item, cb in checklist_checks.items():
                checklist.append({"item": item, "estado": 1 if cb.value else 0})

            ok, msg = self.workshop.crear_orden(
                cliente_id=cliente_id.value,
                placa=placa_dd.value,
                mecanico_id=mecanico_id,
                kilometraje=kilometraje.value or "",
                nivel_combustible=nivel_comb.value or "",
                diagnostico=diagnostico.value or "",
                observaciones=observaciones.value or "",
                checklist=checklist,
            )
            self.page.close(dlg)
            if ok:
                self.page.show_snack_bar(CustomSnackBar(msg, "success"))
                # Recargar la sección
                self._content_area.content = self._build_ordenes()
                self._content_area.update()
            else:
                self.page.show_snack_bar(CustomSnackBar(msg, "error"))

        # ── Armar el diálogo ─────────────────────────────
        form = ft.Column([
            ft.Text("Nueva Orden de Servicio", size=18, weight=ft.FontWeight.BOLD,
                    color=COLOR_PRIMARY),
            ft.Divider(height=8),
            ft.Text("Cliente", weight=ft.FontWeight.BOLD, size=13),
            ft.Row([cliente_search, CustomButton("Buscar", icon=ft.icons.SEARCH,
                    on_click=on_client_search)], spacing=8),
            client_results,
            cliente_info,
            ft.Container(height=8),
            ft.Row([placa_dd, mecanico_dd], spacing=12),
            ft.Container(height=8),
            ft.Row([kilometraje, nivel_comb], spacing=12),
            ft.Container(height=8),
            diagnostico,
            ft.Container(height=8),
            observaciones,
            ft.Container(height=8),
            ft.Text("Checklist de ingreso", weight=ft.FontWeight.BOLD, size=13),
            ft.Container(
                content=checklist_col,
                border=ft.border.all(1, COLOR_DISABLED),
                border_radius=8,
                padding=12,
            ),
            ft.Container(height=12),
            ft.Row([
                CustomButton("Cancelar", variant="outline",
                             on_click=lambda e: self.page.close(dlg)),
                CustomButton("Guardar Orden", icon=ft.icons.SAVE, variant="accent",
                             on_click=guardar_orden),
            ], alignment=ft.MainAxisAlignment.END, spacing=8),
        ], spacing=0, scroll=ft.ScrollMode.AUTO, width=560)

        dlg = ft.AlertDialog(
            modal=True,
            content=form,
            content_padding=20,
        )
        self.page.open(dlg)

    # ── Clientes ─────────────────────────────────────────

    def _build_clientes(self) -> ft.Control:
        """Sección de clientes."""
        self._client_search_field = CustomTextField(
            label="Buscar cliente",
            hint_text="Nombre, teléfono o ID",
            icon=ft.icons.SEARCH,
            width=400,
            on_submit=lambda e: self._buscar_cliente(e.control.value),
        )
        self._client_results_container = ft.Container(
            content=EmptyState(icon=ft.icons.PEOPLE,
                               message="Use la búsqueda para encontrar clientes",
                               submessage="Ingrese nombre, teléfono o ID del cliente"),
            expand=True,
        )

        return ft.Column([
            ft.Row([
                ft.Text("Clientes", size=22, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                CustomButton("Nuevo Cliente", icon=ft.icons.PERSON_ADD, variant="accent",
                             on_click=lambda e: self._nuevo_cliente()),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=12),
            ft.Row([self._client_search_field,
                    CustomButton("Buscar", icon=ft.icons.SEARCH,
                    on_click=lambda e: self._buscar_cliente(self._client_search_field.value))],
                   spacing=8),
            ft.Container(height=16),
            self._client_results_container,
        ], spacing=0, scroll=ft.ScrollMode.AUTO)

    def _buscar_cliente(self, term: str):
        if not term or len(term.strip()) < 2:
            self.page.show_snack_bar(CustomSnackBar("Ingrese al menos 2 caracteres", "warning"))
            return
        resultados = self.workshop.buscar_cliente(term.strip())
        if resultados:
            rows = [[c.get("id", ""), c.get("nombre", ""), c.get("telefono", ""),
                     c.get("email", ""), c.get("direccion", "")]
                    for c in resultados]
            self._client_results_container.content = ft.Column([
                ft.Text(f"{len(resultados)} cliente(s) encontrado(s)", size=13,
                        color=COLOR_SUCCESS, weight=ft.FontWeight.BOLD),
                ft.Container(height=8),
                CustomDataTable(
                    columns=["ID", "Nombre", "Teléfono", "Email", "Dirección"],
                    rows=rows,
                ),
            ], spacing=0, scroll=ft.ScrollMode.AUTO)
        else:
            self._client_results_container.content = EmptyState(
                icon=ft.icons.SEARCH_OFF,
                message="No se encontraron clientes",
                submessage="Intente con otro término de búsqueda o registre un nuevo cliente")
        self._client_results_container.update()

    def _nuevo_cliente(self):
        """Diálogo para registrar un nuevo cliente."""
        id_field = CustomTextField(label="ID / Cédula / NIT", hint_text="Ej: 1234567890", width=300)
        nombre = CustomTextField(label="Nombre completo", hint_text="Ej: Juan Pérez", width=300)
        telefono = CustomTextField(label="Teléfono", hint_text="Ej: 3001234567", width=300)
        email = CustomTextField(label="Email", hint_text="Ej: cliente@email.com", width=300)
        direccion = ft.TextField(
            label="Dirección",
            hint_text="Dirección de residencia...",
            multiline=True, min_lines=2, max_lines=3,
            width=300, border_color=COLOR_DISABLED,
        )

        def guardar(e):
            if not id_field.value or not nombre.value:
                self.page.show_snack_bar(CustomSnackBar("ID y Nombre son obligatorios", "warning"))
                return
            ok, msg = self.workshop.crear_cliente(
                cliente_id=id_field.value.strip(),
                nombre=nombre.value.strip(),
                telefono=telefono.value.strip(),
                email=email.value.strip(),
                direccion=direccion.value.strip(),
            )
            self.page.close(dlg)
            if ok:
                self.page.show_snack_bar(CustomSnackBar(msg, "success"))
                # Refrescar búsqueda si hay término
                if self._client_search_field.value:
                    self._buscar_cliente(self._client_search_field.value)
            else:
                self.page.show_snack_bar(CustomSnackBar(msg, "error"))

        form = ft.Column([
            ft.Text("Nuevo Cliente", size=18, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
            ft.Divider(height=8),
            id_field, ft.Container(height=8),
            nombre, ft.Container(height=8),
            telefono, ft.Container(height=8),
            email, ft.Container(height=8),
            direccion, ft.Container(height=12),
            ft.Row([
                CustomButton("Cancelar", variant="outline",
                             on_click=lambda e: self.page.close(dlg)),
                CustomButton("Guardar Cliente", icon=ft.icons.SAVE, variant="accent",
                             on_click=guardar),
            ], alignment=ft.MainAxisAlignment.END, spacing=8),
        ], spacing=0, scroll=ft.ScrollMode.AUTO, width=360)

        dlg = ft.AlertDialog(modal=True, content=form, content_padding=20)
        self.page.open(dlg)

    # ── Inventario ───────────────────────────────────────

    def _build_inventario(self) -> ft.Control:
        """Sección de inventario."""
        self._product_search_field = CustomTextField(
            label="Buscar producto / servicio",
            hint_text="Nombre o código",
            icon=ft.icons.SEARCH,
            width=400,
            on_submit=lambda e: self._buscar_producto(e.control.value),
        )
        self._product_results_container = ft.Container(
            content=EmptyState(icon=ft.icons.INVENTORY_2,
                               message="Busque productos o servicios",
                               submessage="Use el campo de búsqueda para encontrar items del inventario"),
            expand=True,
        )

        return ft.Column([
            ft.Row([
                ft.Text("Inventario", size=22, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                CustomButton("Nuevo Producto", icon=ft.icons.ADD, variant="accent",
                             on_click=lambda e: self._nuevo_producto()),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=12),
            ft.Row([self._product_search_field,
                    CustomButton("Buscar", icon=ft.icons.SEARCH,
                    on_click=lambda e: self._buscar_producto(self._product_search_field.value))],
                   spacing=8),
            ft.Container(height=16),
            self._product_results_container,
        ], spacing=0, scroll=ft.ScrollMode.AUTO)

    def _buscar_producto(self, term: str):
        if not term or len(term.strip()) < 2:
            self.page.show_snack_bar(CustomSnackBar("Ingrese al menos 2 caracteres", "warning"))
            return
        resultados = self.workshop.buscar_producto(term.strip())
        if resultados:
            rows = [[str(p.get("id", "")), p.get("nombre", ""), p.get("categoria", ""),
                     str(p.get("stock", 0)), f"${p.get('precio', 0):,.0f}",
                     p.get("estado", "")]
                    for p in resultados]
            self._product_results_container.content = ft.Column([
                ft.Text(f"{len(resultados)} producto(s) encontrado(s)", size=13,
                        color=COLOR_SUCCESS, weight=ft.FontWeight.BOLD),
                ft.Container(height=8),
                CustomDataTable(
                    columns=["ID", "Nombre", "Categoría", "Stock", "Precio", "Estado"],
                    rows=rows,
                ),
            ], spacing=0, scroll=ft.ScrollMode.AUTO)
        else:
            self._product_results_container.content = EmptyState(
                icon=ft.icons.SEARCH_OFF,
                message="No se encontraron productos",
                submessage="Intente con otro término de búsqueda o registre un nuevo producto")
        self._product_results_container.update()

    def _nuevo_producto(self):
        """Diálogo para crear un nuevo producto/servicio."""
        nombre = CustomTextField(label="Nombre del producto", hint_text="Ej: Aceite 20W50", width=300)
        categoria = CustomTextField(label="Categoría", hint_text="Ej: Lubricantes", width=300)
        stock = CustomTextField(label="Stock inicial", hint_text="Ej: 10", width=150)
        stock_min = CustomTextField(label="Stock mínimo", hint_text="Ej: 5", width=150)
        precio = CustomTextField(label="Precio de venta", hint_text="Ej: 45000", width=200)
        costo = CustomTextField(label="Costo promedio", hint_text="Ej: 35000", width=200)

        def guardar(e):
            if not nombre.value:
                self.page.show_snack_bar(CustomSnackBar("El nombre es obligatorio", "warning"))
                return
            try:
                stock_val = int(stock.value) if stock.value else 0
                stock_min_val = int(stock_min.value) if stock_min.value else 5
                precio_val = float(precio.value) if precio.value else 0.0
                costo_val = float(costo.value) if costo.value else 0.0
            except ValueError:
                self.page.show_snack_bar(CustomSnackBar("Valores numéricos inválidos", "error"))
                return

            ok, msg = self.workshop.crear_producto(
                nombre=nombre.value.strip(),
                categoria=categoria.value.strip(),
                stock=stock_val,
                stock_minimo=stock_min_val,
                precio=precio_val,
                costo_promedio=costo_val,
            )
            self.page.close(dlg)
            if ok:
                self.page.show_snack_bar(CustomSnackBar(msg, "success"))
                if self._product_search_field.value:
                    self._buscar_producto(self._product_search_field.value)
            else:
                self.page.show_snack_bar(CustomSnackBar(msg, "error"))

        form = ft.Column([
            ft.Text("Nuevo Producto / Servicio", size=18, weight=ft.FontWeight.BOLD,
                    color=COLOR_PRIMARY),
            ft.Divider(height=8),
            nombre, ft.Container(height=8),
            categoria, ft.Container(height=8),
            ft.Row([stock, stock_min], spacing=12),
            ft.Container(height=8),
            ft.Row([precio, costo], spacing=12),
            ft.Container(height=12),
            ft.Row([
                CustomButton("Cancelar", variant="outline",
                             on_click=lambda e: self.page.close(dlg)),
                CustomButton("Guardar Producto", icon=ft.icons.SAVE, variant="accent",
                             on_click=guardar),
            ], alignment=ft.MainAxisAlignment.END, spacing=8),
        ], spacing=0, scroll=ft.ScrollMode.AUTO, width=360)

        dlg = ft.AlertDialog(modal=True, content=form, content_padding=20)
        self.page.open(dlg)

    # ── Facturas ─────────────────────────────────────────

    def _build_facturas(self) -> ft.Control:
        """Sección de facturación."""
        facturas = self.workshop.get_facturas()

        if not facturas:
            return ft.Column([
                ft.Row([
                    ft.Text("Facturas", size=22, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                    CustomButton("Nueva Factura", icon=ft.icons.ADD, variant="accent",
                                 on_click=lambda e: self._nueva_factura()),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=16),
                EmptyState(icon=ft.icons.RECEIPT, message="No hay facturas registradas",
                           submessage="Las facturas se generan al completar órdenes de servicio"),
            ], spacing=0, scroll=ft.ScrollMode.AUTO)

        rows = []
        for f in facturas:
            rows.append([
                str(f.get("id", "")),
                f.get("cliente_nombre", ""),
                f"${f.get('total', 0):,.0f}",
                f.get("estado_pago", ""),
                str(f.get("fecha_emision", "")),
            ])

        return ft.Column([
            ft.Row([
                ft.Text("Facturas", size=22, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                CustomButton("Nueva Factura", icon=ft.icons.ADD, variant="accent",
                             on_click=lambda e: self._nueva_factura()),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=16),
            CustomDataTable(
                columns=["#", "Cliente", "Total", "Estado Pago", "Fecha"],
                rows=rows,
                on_row_click=lambda r: self.page.show_snack_bar(
                    CustomSnackBar(f"Ver factura #{r[0]}", "info")),
            ),
        ], spacing=0, scroll=ft.ScrollMode.AUTO)

    def _nueva_factura(self):
        """Diálogo para crear una nueva factura a partir de una orden completada."""
        # ── Búsqueda de cliente ─────────────────────────
        cliente_search = CustomTextField(
            label="Buscar cliente", hint_text="Nombre o ID",
            icon=ft.icons.SEARCH, width=350,
        )
        cliente_info = ft.Text("", size=12, color=COLOR_TEXT_SECONDARY)
        cliente_id = ft.Text("", visible=False)

        # ── Selección de orden ──────────────────────────
        orden_dd = CustomDropdown(label="Seleccionar orden", options=["(Busque un cliente primero)"], width=350)
        ordenes_data = []

        # ── Detalle de la orden seleccionada ────────────
        detalle_container = ft.Container(
            content=ft.Text("Seleccione un cliente y una orden", size=12, color=COLOR_TEXT_SECONDARY),
            padding=10, bgcolor=COLOR_BG, border_radius=8,
        )

        # ── Campos de pago ──────────────────────────────
        pago_efectivo = CustomTextField(label="Pago en efectivo $", hint_text="0", width=160)
        pago_transferencia = CustomTextField(label="Pago transferencia $", hint_text="0", width=160)
        total_label = ft.Text("$0", size=20, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY)

        def actualizar_total(e):
            try:
                ef = float(pago_efectivo.value) if pago_efectivo.value else 0
                tr = float(pago_transferencia.value) if pago_transferencia.value else 0
                total_label.value = f"${ef + tr:,.0f}"
                total_label.update()
            except ValueError:
                pass

        pago_efectivo.on_change = actualizar_total
        pago_transferencia.on_change = actualizar_total

        def buscar_cliente_factura(e):
            term = cliente_search.value
            if not term or len(term.strip()) < 2:
                return
            resultados = self.workshop.buscar_cliente(term.strip())
            if not resultados:
                cliente_info.value = "Cliente no encontrado"
                cliente_info.color = COLOR_ERROR
                cliente_info.update()
                return
            c = resultados[0]
            cliente_id.value = str(c.get("id", ""))
            cliente_info.value = f"{c.get('nombre', '')} - {c.get('telefono', '')}"
            cliente_info.color = COLOR_SUCCESS
            cliente_info.update()

            # Buscar órdenes LISTO/ENTREGADO de este cliente
            todas = self.workshop.buscar_ordenes(cliente_id=cliente_id.value)
            ordenes_data.clear()
            opts = []
            for o in todas:
                if o.get("estado") in ("LISTO", "ENTREGADO"):
                    ordenes_data.append(o)
                    opts.append(f"#{o['id']} - {o.get('placa', '')} ({o.get('estado', '')})")
            if opts:
                orden_dd.options = opts
                orden_dd.value = opts[0]
            else:
                orden_dd.options = ["(Sin órdenes facturables)"]
                orden_dd.value = "(Sin órdenes facturables)"
            orden_dd.update()

        cliente_search.on_submit = buscar_cliente_factura

        def seleccionar_orden(e):
            if not orden_dd.value or "(Sin" in orden_dd.value or "(Busque" in orden_dd.value:
                return
            idx = orden_dd.options.index(orden_dd.value)
            o = ordenes_data[idx]
            detalle_container.content = ft.Column([
                ft.Text(f"Orden #{o['id']} - {o.get('placa', '')}", weight=ft.FontWeight.BOLD, size=13),
                ft.Text(f"Estado: {o.get('estado', '')}", size=12),
                ft.Text(f"Diagnóstico: {o.get('diagnostico_entrada', 'Sin diagnóstico')}", size=12),
                ft.Divider(height=4),
                ft.Text("Items del checklist:", size=12, weight=ft.FontWeight.BOLD),
                *[ft.Text(f"  • {ch.get('item', '')}", size=11)
                  for ch in (o.get("checklist", []) or [])],
            ], spacing=2, tight=True, scroll=ft.ScrollMode.AUTO)
            detalle_container.update()

        orden_dd.on_change = seleccionar_orden

        def guardar_factura(e):
            if not cliente_id.value:
                self.page.show_snack_bar(CustomSnackBar("Seleccione un cliente", "warning"))
                return
            if not orden_dd.value or "(Sin" in orden_dd.value or "(Busque" in orden_dd.value:
                self.page.show_snack_bar(CustomSnackBar("Seleccione una orden", "warning"))
                return
            try:
                ef = float(pago_efectivo.value) if pago_efectivo.value else 0
                tr = float(pago_transferencia.value) if pago_transferencia.value else 0
            except ValueError:
                self.page.show_snack_bar(CustomSnackBar("Valores de pago inválidos", "error"))
                return
            total = ef + tr
            if total <= 0:
                self.page.show_snack_bar(CustomSnackBar("El total debe ser mayor a 0", "warning"))
                return

            idx = orden_dd.options.index(orden_dd.value)
            o = ordenes_data[idx]
            iva_monto = round(total * 0.19, 2)
            subtotal = round(total - iva_monto, 2)

            detalle = []
            for ch in (o.get("checklist", []) or []):
                detalle.append({"item": ch.get("item", ""), "valor": 0})

            ok, msg = self.workshop.crear_factura(
                orden_id=int(o["id"]),
                cliente_id=cliente_id.value,
                subtotal=subtotal,
                iva_monto=iva_monto,
                total=total,
                pago_efectivo=ef,
                pago_transferencia=tr,
                placa=o.get("placa", ""),
                observaciones="",
                detalle=detalle,
            )
            self.page.close(dlg)
            if ok:
                self.page.show_snack_bar(CustomSnackBar(msg, "success"))
                self._content_area.content = self._build_facturas()
                self._content_area.update()
            else:
                self.page.show_snack_bar(CustomSnackBar(msg, "error"))

        form = ft.Column([
            ft.Text("Nueva Factura", size=18, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
            ft.Divider(height=8),
            ft.Text("Cliente", weight=ft.FontWeight.BOLD, size=13, color=COLOR_PRIMARY),
            ft.Row([cliente_search, CustomButton("Buscar", on_click=buscar_cliente_factura)], spacing=8),
            cliente_info,
            ft.Container(height=12),
            ft.Text("Orden de servicio", weight=ft.FontWeight.BOLD, size=13, color=COLOR_PRIMARY),
            orden_dd,
            ft.Container(height=8),
            detalle_container,
            ft.Container(height=12),
            ft.Text("Método de pago", weight=ft.FontWeight.BOLD, size=13, color=COLOR_PRIMARY),
            ft.Row([pago_efectivo, pago_transferencia], spacing=12),
            ft.Row([
                ft.Text("Total:", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                total_label,
            ], spacing=8),
            ft.Container(height=12),
            ft.Row([
                CustomButton("Cancelar", variant="outline",
                             on_click=lambda e: self.page.close(dlg)),
                CustomButton("Generar Factura", icon=ft.icons.RECEIPT, variant="accent",
                             on_click=guardar_factura),
            ], alignment=ft.MainAxisAlignment.END, spacing=8),
        ], spacing=0, scroll=ft.ScrollMode.AUTO, width=420)

        dlg = ft.AlertDialog(modal=True, content=form, content_padding=20)
        self.page.open(dlg)