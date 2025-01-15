# stock/urls.py
from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    path('productos/', views.productos_list, name='productos_list'),
    path('proveedores/', views.proveedores_list, name='proveedores_list'),
    path('pedidos/', views.pedidos_list, name='pedidos_list'),
]
