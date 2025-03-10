from django.contrib import admin
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.html import format_html
from django.core.mail import EmailMessage
from django.urls import reverse
from .models import Proveedor, Producto, Pedido, DetallePedido, Categoria, EmailConfig
from .pedidoForm import PedidoForm


class ProductoInline(admin.TabularInline):
    model = Producto
    extra = 0
    fields = ('nombre', 'categoria', 'precio_con_moneda', 'stock')
    readonly_fields = ('nombre', 'categoria', 'precio_con_moneda', 'stock')
    can_delete = False
    show_change_link = True

class PedidoInline(admin.TabularInline):
    model = Pedido
    extra = 0
    fields = ('estado', 'fecha_creacion', 'fecha_envio')
    readonly_fields = ('estado', 'fecha_creacion', 'fecha_envio')
    can_delete = False
    show_change_link = True

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'email', 'direccion', 'ver_productos', 'hacer_pedido_link')  # Asegúrate de incluirla correctamente
    search_fields = ('nombre', 'email', 'telefono')
    inlines = []  # Si usas inlines, agrégalos aquí.

    def ver_productos(self, obj):
        """
        Muestra un enlace en el admin para ver los productos de este proveedor.
        """
        url = f"/admin/stock/producto/?proveedor__id__exact={obj.id}"
        return format_html('<a href="{}">Ver Productos</a>', url)

    ver_productos.short_description = "Productos"

    def hacer_pedido_link(self, obj):
        """
        Agrega un botón en el admin para hacer un pedido directamente desde el proveedor.
        """
        url = reverse('stock:hacer_pedido', args=[obj.id])  # Usar 'stock:hacer_pedido' con el namespace
        return format_html(
            '<a class="button" href="{}" style="background-color: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 5px;">Hacer Pedido</a>',
            url
        )

    hacer_pedido_link.short_description = "Hacer Pedido"

admin.site.register(Proveedor, ProveedorAdmin)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'ver_productos')

    def ver_productos(self, obj):
        """
        Muestra un enlace en el admin para ver los productos de esta categoría.
        """
        url = f"/admin/stock/producto/?categoria__id__exact={obj.id}"
        return format_html('<a href="{}">Ver Productos</a>', url)

    ver_productos.short_description = "Productos"


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'proveedor', 'stock', 'unidad_medida', 'precio', 'precio_con_moneda')
    list_filter = ('categoria', 'proveedor')
    search_fields = ('nombre', 'proveedor__nombre')
    list_editable = ('stock', 'precio')

    def precio_con_moneda(self, obj):
        """
        Muestra el precio con el símbolo de la moneda en la lista del admin.
        """
        simbolos = {'EUR': '€', 'USD': '$', 'GBP': '£'}
        return f"{obj.precio} {simbolos.get(obj.moneda, '€')}"

    precio_con_moneda.short_description = "Precio"


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    fields = ('producto', 'cantidad')
    autocomplete_fields = []

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "producto":
            pedido_id = request.resolver_match.kwargs.get('object_id')
            if pedido_id:
                try:
                    pedido = Pedido.objects.get(pk=pedido_id)
                    kwargs["queryset"] = Producto.objects.filter(proveedor=pedido.proveedor)
                except Pedido.DoesNotExist:
                    kwargs["queryset"] = Producto.objects.none()
            else:
                kwargs["queryset"] = Producto.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

def duplicar_pedido_admin(modeladmin, request, queryset):
    """
    Permite duplicar pedidos seleccionados en el admin.
    """
    for pedido in queryset:
        nuevo_pedido = Pedido.objects.create(
            proveedor=pedido.proveedor,
            estado="Pendiente",  # El nuevo pedido siempre comienza como Pendiente
        )

        # Copiar los productos del pedido original al nuevo
        for detalle in pedido.detalles.all():
            DetallePedido.objects.create(
                pedido=nuevo_pedido,
                producto=detalle.producto,
                cantidad=detalle.cantidad,
                comentario=detalle.comentario
            )

        modeladmin.message_user(request, f"Se ha duplicado el pedido {pedido.id}. Nuevo pedido: {nuevo_pedido.id}")


        duplicar_pedido_admin.short_description = "Duplicar Pedido"

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    form = PedidoForm
    inlines = [DetallePedidoInline]

    list_display = ('id', 'proveedor', 'estado_coloreado', 'fecha_creacion', 'fecha_envio', 'total_pedido', 'boton_enviar_pedido')
    list_filter = ('estado', 'proveedor')
    search_fields = ('proveedor__nombre',)
    readonly_fields = ('fecha_creacion', 'fecha_envio', 'mostrar_detalles')

    def total_pedido(self, obj):
        """Calcula el total del pedido sumando todos los subtotales."""
        return sum(detalle.subtotal() for detalle in obj.detalles.all())

    total_pedido.short_description = "Total Pedido"

    def estado_coloreado(self, obj):
        """Muestra el estado del pedido con colores."""
        colores = {
            "Pendiente": "background-color: yellow; color: black; padding: 5px; border-radius: 5px;",
            "Enviado": "background-color: green; color: white; padding: 5px; border-radius: 5px;",
        }
        return format_html('<span style="{}">{}</span>', colores.get(obj.estado, ""), obj.estado)

    estado_coloreado.short_description = "Estado"  # ✅ Esto lo hace visible en el admin

    def mostrar_detalles(self, obj):
        productos_html = "<table style='width:100%; border-collapse: collapse;'>"
        productos_html += "<tr><th>Producto</th><th>Cantidad</th><th>Precio</th><th>Total</th></tr>"

        total_pedido = 0
        for detalle in obj.detalles.all():
            subtotal = detalle.subtotal()
            total_pedido += subtotal
            productos_html += f"""
                <tr>
                    <td>{detalle.producto.nombre}</td>
                    <td>{detalle.cantidad}</td>
                    <td>{detalle.producto.precio} {detalle.producto.get_moneda_display()}</td>
                    <td>{subtotal} {detalle.producto.get_moneda_display()}</td>
                </tr>
            """

        productos_html += f"<tr><td colspan='3'><strong>Total:</strong></td><td><strong>{total_pedido} EUR</strong></td></tr>"
        productos_html += "</table>"

        return format_html(productos_html)

    mostrar_detalles.short_description = "Detalles del Pedido"

    def boton_enviar_pedido(self, obj):
        """Muestra un botón para enviar el pedido directamente desde el admin."""
        return format_html(
            '<a class="button" href="{}" style="background-color: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 5px;">Enviar Pedido</a>',
            reverse('stock:enviar_pedido', args=[obj.id])
        )

    boton_enviar_pedido.short_description = "Acciones"


@admin.register(EmailConfig)
class EmailConfigAdmin(admin.ModelAdmin):
    list_display = ('email', 'host', 'port', 'use_tls')
    list_editable = ('host', 'port', 'use_tls')
