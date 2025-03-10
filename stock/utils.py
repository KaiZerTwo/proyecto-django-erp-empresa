from .models import Pedido, DetallePedido

def duplicar_pedido(pedido):
    """
    Duplica un pedido enviado, creando uno nuevo con los mismos productos y cantidades.
    """
    nuevo_pedido = Pedido.objects.create(
        proveedor=pedido.proveedor,
        estado="Pendiente"
    )

    # Guardar el nuevo pedido antes de copiar los detalles
    nuevo_pedido.save()

    # Copiar los productos del pedido anterior al nuevo
    for detalle in pedido.detalles.all():
        DetallePedido.objects.create(
            pedido=nuevo_pedido,
            producto=detalle.producto,
            cantidad=detalle.cantidad,
            comentario=detalle.comentario
        )

    print(f"📌 Pedido {pedido.id} duplicado correctamente → Nuevo Pedido ID: {nuevo_pedido.id}")  # Debug en consola

    return nuevo_pedido

