from django.contrib import admin
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.html import format_html
from django.core.mail import EmailMessage
from .models import Proveedor, Producto, Pedido, DetallePedido, Categoria, EmailConfig


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'email', 'direccion')
    search_fields = ('nombre', 'email', 'telefono')


# Nuevo: registramos la categoría
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'tipo_comida', 'proveedor', 'stock', 'unidad_medida', 'precio')
    # 1. Filtramos por la nueva categoría, por el tipo de comida y por el proveedor
    list_filter = ('categoria', 'tipo_comida', 'proveedor')
    # 2. Permite búsqueda rápida
    search_fields = ('nombre', 'proveedor__nombre')
    # 3. Editar stock y precio rápidamente
    list_editable = ('stock', 'precio')


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    fields = ('producto', 'cantidad', 'comentario')
    autocomplete_fields = ['producto']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'estado', 'fecha_creacion', 'fecha_envio', 'boton_enviar_pedido')
    list_filter = ('estado', 'proveedor')
    search_fields = ('proveedor__nombre',)
    inlines = [DetallePedidoInline]
    actions = ['marcar_como_enviado']

    @admin.action(description='Marcar como Enviado')
    def marcar_como_enviado(self, request, queryset):
        queryset.update(estado='Enviado')

    def boton_enviar_pedido(self, obj):
        """
        Genera un botón para enviar el pedido directamente desde el admin.
        """
        if obj.estado != 'Enviado':  # Solo mostrar si el pedido no está enviado
            return format_html(
                '<a class="button" href="{}">Enviar Pedido</a>',
                f"/admin/stock/pedido/{obj.id}/enviar/"
            )
        return "Enviado"
    boton_enviar_pedido.short_description = "Acción"

    # Custom URL para manejar el envío de pedidos desde el botón
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pedido_id>/enviar/',
                self.admin_site.admin_view(self.enviar_pedido),
                name='enviar_pedido',
            ),
        ]
        return custom_urls + urls

    def enviar_pedido(self, request, pedido_id):
        """
        Lógica para enviar el pedido por correo y actualizar el estado.
        """
        from django.core.mail import EmailMessage
        from stock.models import EmailConfig

        # Recuperar el pedido
        pedido = self.get_object(request, pedido_id)
        if not pedido:
            self.message_user(request, "Pedido no encontrado.", level='error')
            return redirect('/admin/stock/pedido/')

        # Cambiar estado del pedido
        pedido.estado = 'Enviado'
        pedido.fecha_envio = timezone.now()
        pedido.save()

        # Obtener configuración de correo
        email_config = EmailConfig.objects.first()
        if not email_config:
            self.message_user(request, "No hay configuración de correo disponible.", level='error')
            return redirect('/admin/stock/pedido/')

        # Obtener los detalles del pedido
        detalles = pedido.detalles.all()  # Usamos el related_name "detalles" del modelo DetallePedido

        # Construir el cuerpo del correo
        productos = "\n".join([
            f"- {detalle.producto.nombre}: {detalle.cantidad} {detalle.producto.unidad_medida}"
            for detalle in detalles
        ])
        cuerpo = (
            f"Estimado {pedido.proveedor.nombre},\n\n"
            f"Su pedido con ID {pedido.id} ha sido procesado con éxito. A continuación, los detalles del pedido:\n\n"
            f"{productos}\n\n"
            f"Observaciones: {pedido.observaciones or 'Ninguna'}\n\n"
            f"Saludos cordiales,\n"
            f"Equipo de Gestión."
        )

        # Enviar correo
        try:
            email_backend = email_config.get_connection()
            email = EmailMessage(
                subject=f"Detalles del Pedido {pedido.id}",
                body=cuerpo,
                from_email=email_config.email,
                to=[pedido.proveedor.email],
                connection=email_backend
            )
            email.send()
            self.message_user(request,
                              f"Pedido {pedido.id} enviado correctamente al proveedor {pedido.proveedor.email}.",
                              level='success')
        except Exception as e:
            self.message_user(request, f"Pedido {pedido.id} enviado, pero falló el envío del correo: {e}",
                              level='error')

        return redirect('/admin/stock/pedido/')


@admin.register(EmailConfig)
class EmailConfigAdmin(admin.ModelAdmin):
    list_display = ('email', 'host', 'port', 'use_tls')
    list_editable = ('host', 'port', 'use_tls')
