from django.db import models
from django.core.mail.backends.smtp import EmailBackend


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

    MONEDAS_CHOICES = [
        ('EUR', '€ - Euro'),
        ('USD', '$ - Dólar'),
        ('GBP', '£ - Libra Esterlina'),
    ]

    # Eliminamos TIPOS_COMIDA_CHOICES porque ya tenemos categoria

    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="productos")
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=3, choices=MONEDAS_CHOICES, default='EUR')  # Nueva opción de moneda
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unidad_medida = models.CharField(max_length=5, choices=UNIDADES_CHOICES, default='UN')  # Aumentamos a 5 caracteres

    def precio_con_moneda(self):
        """
        Muestra el precio con el símbolo de la moneda.
        """
        simbolos = {'EUR': '€', 'USD': '$', 'GBP': '£'}
        return f"{self.precio} {simbolos.get(self.moneda, '€')}"

    def __str__(self):
        return f"{self.nombre} - {self.categoria} ({self.proveedor.nombre})"



class Pedido(models.Model):
    ESTADOS_CHOICES = [
        ('Pendiente', 'Pendiente de Enviar'),
        ('Enviado', 'Enviado'),
    ]

    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    estado = models.CharField(max_length=10, choices=ESTADOS_CHOICES, default='Pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Se guarda automáticamente
    fecha_envio = models.DateTimeField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)  # Observaciones del pedido
    comentario = models.TextField(blank=True, null=True)  # Comentario general

    def __str__(self):
        return f"Pedido {self.id} - {self.proveedor.nombre} ({self.estado})"



class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)  # Ahora solo acepta números enteros
    comentario = models.TextField(blank=True, null=True)

    def subtotal(self):
        """Calcula el subtotal por producto"""
        return self.cantidad * self.producto.precio

    def save(self, *args, **kwargs):
        if self.producto.proveedor != self.pedido.proveedor:
            raise ValueError("El producto no pertenece al proveedor de este pedido.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} {self.producto.unidad_medida}"




class EmailConfig(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=128)
    host = models.CharField(max_length=128, default="smtp.gmail.com")
    port = models.PositiveIntegerField(default=587)
    use_tls = models.BooleanField(default=True)

    def get_connection(self):
        return EmailBackend(
            host=self.host,
            port=self.port,
            username=self.email,
            password=self.password,
            use_tls=self.use_tls,
        )

    def __str__(self):
        return f"Configuración: {self.email}"
