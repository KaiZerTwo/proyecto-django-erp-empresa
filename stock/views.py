from django.shortcuts import render
from .models import Producto, Proveedor, Pedido

def productos_list(request):
    productos = Producto.objects.all()
    return render(request, 'stock/productos_list.html', {'productos': productos})

def proveedores_list(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'stock/proveedores_list.html', {'proveedores': proveedores})

def pedidos_list(request):
    pedidos = Pedido.objects.all()
    return render(request, 'stock/pedidos_list.html', {'pedidos': pedidos})

