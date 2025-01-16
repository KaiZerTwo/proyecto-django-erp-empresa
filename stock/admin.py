from django.contrib import admin
from .models import Proveedor, Producto, Pedido, DetallePedido, Categoria


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
    list_display = ('id', 'proveedor', 'estado', 'fecha_creacion', 'fecha_envio')
    list_filter = ('estado', 'proveedor')
    search_fields = ('proveedor__nombre',)
    inlines = [DetallePedidoInline]
    actions = ['marcar_como_enviado']

    @admin.action(description='Marcar como Enviado')
    def marcar_como_enviado(self, request, queryset):
        queryset.update(estado='Enviado')
