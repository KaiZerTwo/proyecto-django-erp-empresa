# stock/urls.py
from django.urls import path
from . import views
from .views import hacer_pedido

app_name = 'stock'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),  # ✅ Ruta correcta
    path('productos/', views.productos_list, name='productos_list'),
    path('proveedores/', views.proveedores_list, name='proveedores_list'),
    path('pedidos/', views.pedidos_list, name='pedidos_list'),
    path('pedidos/<int:pedido_id>/editar/', views.editar_pedido, name='editar_pedido'),
    path('pedidos/<int:pedido_id>/enviar/', views.enviar_pedido, name='enviar_pedido'),
    path('admin/hacer_pedido/<int:proveedor_id>/', hacer_pedido, name='hacer_pedido'),

]
