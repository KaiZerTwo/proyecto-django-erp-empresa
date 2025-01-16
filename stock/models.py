from django.db import models


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()

    def __str__(self):
        return self.nombre


# 1. Nuevo modelo de Categoría
class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    UNIDADES_CHOICES = [
        ('UN', 'Unidades'),
        ('KG', 'Kilogramos'),
        ('LT', 'Litros'),
        ('BT', 'Botellas'),
        ('PK', 'Paquetes'),
    ]

    TIPOS_COMIDA_CHOICES = [
        ('Carne', 'Carne'),
        ('Pescado', 'Pescado'),
        ('Verdura', 'Verdura'),
        ('Fruta', 'Fruta'),
        ('Panadería', 'Panadería'),
    ]

    # 2. Reemplazamos el antiguo campo 'categoria' (CharField) por una ForeignKey a Categoria
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="productos")

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_comida = models.CharField(max_length=50, choices=TIPOS_COMIDA_CHOICES, blank=True, null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unidad_medida = models.CharField(max_length=2, choices=UNIDADES_CHOICES, default='UN')

    def __str__(self):
        return f"{self.nombre} - {self.categoria} ({self.proveedor.nombre})"


class Pedido(models.Model):
    ESTADOS_CHOICES = [
        ('Pendiente', 'Pendiente de Validar'),
        ('Validado', 'Validado'),
        ('Enviado', 'Enviado'),
    ]

    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)  # Relación con Proveedor
    estado = models.CharField(max_length=10, choices=ESTADOS_CHOICES, default='Pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(blank=True, null=True)  # Opcional: Fecha de envío
    observaciones = models.TextField(blank=True, null=True)  # Campo para comentarios adicionales

    def __str__(self):
        return f"Pedido {self.id} - {self.proveedor.nombre} ({self.estado})"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    comentario = models.TextField(blank=True, null=True)  # Ej: Notas adicionales del producto

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} {self.producto.unidad_medida}"
