from django.core.checks import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from .models import Producto, Proveedor, Pedido, EmailConfig


def productos_list(request):
    productos = Producto.objects.all()
    return render(request, 'stock/productos_list.html', {'productos': productos})

def pedidos_list(request):
    pedidos = Pedido.objects.select_related('proveedor').order_by('-fecha_creacion')
    return render(request, 'stock/pedidos_list.html', {'pedidos': pedidos})

def proveedores_list(request):
    proveedores = Proveedor.objects.all().order_by('nombre')
    return render(request, 'stock/proveedores_list.html', {'proveedores': proveedores})


def enviar_pedido(request, pedido_id):
    # Obtener el pedido
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Obtener configuración de correo
    email_config = EmailConfig.objects.first()  # Usamos la primera configuración
    if not email_config:
        messages.error(request, "No se encontró configuración de correo.")
        return redirect('stock:pedidos_list')  # Redirigir a la lista de pedidos

    # Crear el backend de correo dinámico
    email_backend = EmailBackend(
        host=email_config.host,
        port=email_config.port,
        username=email_config.email,
        password=email_config.password,
        use_tls=email_config.use_tls,
        fail_silently=False,
    )

    # Configurar el correo
    email = EmailMessage(
        subject=f"Pedido {pedido.id} - Detalles",
        body=(
            f"Estimado {pedido.proveedor.nombre},\n\n"
            f"El pedido {pedido.id} ha sido procesado.\n\n"
            "Saludos,\nEquipo de Gestión."
        ),
        from_email=email_config.email,
        to=[pedido.proveedor.email],
        connection=email_backend,
    )

    # Intentar enviar el correo
    try:
        email.send()
        # Actualizar estado del pedido
        pedido.estado = 'Enviado'
        pedido.save()

        # Mensaje de éxito
        messages.success(request, f"Correo enviado correctamente a {pedido.proveedor.email}.")
    except Exception as e:
        messages.error(request, f"Error al enviar el correo: {e}")

    return redirect('stock:pedidos_list')

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

