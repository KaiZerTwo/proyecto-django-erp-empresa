from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.urls import reverse
from django.utils import timezone

from .pedidoForm import PedidoForm
from .models import Producto, Proveedor, Pedido, EmailConfig, DetallePedido
from .utils import duplicar_pedido


def productos_list(request):
    productos = Producto.objects.all()
    return render(request, 'stock/productos_list.html', {'productos': productos})

def pedidos_list(request):
    pedidos = Pedido.objects.select_related('proveedor').order_by('-fecha_creacion')
    return render(request, 'stock/pedidos_list.html', {'pedidos': pedidos})

def proveedores_list(request):
    proveedores = Proveedor.objects.all().order_by('nombre')
    return render(request, 'stock/proveedores_list.html', {'proveedores': proveedores})

def hacer_pedido(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    productos = Producto.objects.filter(proveedor=proveedor)

    if request.method == "POST":
        pedido = Pedido.objects.create(proveedor=proveedor)

        for producto in productos:
            cantidad = request.POST.get(f'cantidad_{producto.id}')
            if cantidad and float(cantidad) > 0:
                DetallePedido.objects.create(pedido=pedido, producto=producto, cantidad=float(cantidad))

        messages.success(request, f"Pedido creado para {proveedor.nombre}.")
        return redirect('/admin/stock/pedido/')

    return render(request, 'stock/hacer_pedido.html', {'proveedor': proveedor, 'productos': productos})


def enviar_pedido(request, pedido_id):
    # Obtener el pedido
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Obtener configuración de correo
    email_config = EmailConfig.objects.first()  # Usamos la primera configuración
    if not email_config:
        messages.error(request, "No se encontró configuración de correo.")
        return redirect(request.META.get('HTTP_REFERER', reverse('admin:stock_pedido_changelist')))

    # Crear el backend de correo dinámico
    email_backend = EmailBackend(
        host=email_config.host,
        port=email_config.port,
        username=email_config.email,
        password=email_config.password,
        use_tls=email_config.use_tls,
        fail_silently=False,
    )

    # Construir detalles del pedido (solo nombre y cantidad, sin precios ni totales)
    detalles_pedido = "\n".join([
        f"- {detalle.producto.nombre}: {int(detalle.cantidad)} {detalle.producto.get_unidad_medida_display()}"
        for detalle in pedido.detalles.all().order_by('producto__nombre')
    ])

    # Crear el contenido del correo
    mensaje = f"""
Estimado {pedido.proveedor.nombre},

Le enviamos la confirmación del pedido #{pedido.id} con los siguientes productos:

{detalles_pedido}

    Si tiene alguna duda, no dude en contactarnos.

    Saludos cordiales,
    Equipo de Gestión
        """.strip()  # Elimina espacios innecesarios al inicio y final

    # Configurar el correo
    email = EmailMessage(
        subject=f"Confirmación de Pedido #{pedido.id}",
        body=mensaje,
        from_email=email_config.email,
        to=[pedido.proveedor.email],
        connection=email_backend,
    )

    # Intentar enviar el correo
    try:
        email.send()
        # Actualizar estado del pedido
        pedido.estado = 'Enviado'
        pedido.fecha_envio = timezone.now()  # Agregar la fecha de envío
        pedido.save()

        # Mensaje de éxito
        messages.success(request, f"Correo enviado correctamente a {pedido.proveedor.email}.")
    except Exception as e:
        messages.error(request, f"Error al enviar el correo: {e}")

    return redirect(request.META.get('HTTP_REFERER', reverse('admin:stock_pedido_changelist')))

def dashboard(request):
    total_productos = Producto.objects.count()
    total_proveedores = Proveedor.objects.count()
    total_pedidos = Pedido.objects.count()

    context = {
        'total_productos': total_productos,
        'total_proveedores': total_proveedores,
        'total_pedidos': total_pedidos
    }
    return render(request, 'stock/dashboard.html', context)

def editar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Si el pedido ya fue enviado, duplicarlo antes de editar
    if pedido.estado.strip().lower() == "enviado":
        nuevo_pedido = duplicar_pedido(pedido)
        messages.info(request, f"📌 El pedido {pedido.id} ya fue enviado. Se creó un nuevo pedido {nuevo_pedido.id} para modificar.")
        return redirect('stock:editar_pedido', pedido_id=nuevo_pedido.id)

    form = PedidoForm(request.POST or None, instance=pedido)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✅ Pedido actualizado correctamente.")
        return redirect('stock:pedidos_list')

    return render(request, 'stock/editar_pedido.html', {'form': form, 'pedido': pedido})



