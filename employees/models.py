# employees/models.py

from django.db import models
from django.utils import timezone
from datetime import timedelta

class Empleado(models.Model):
    """
    Representa a un empleado, con DNI, nombre, apellido, teléfono y correo opcional.
    """
    dni = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(blank=True, null=True)  # Opcional

    def __str__(self):
        return f"{self.nombre} {self.apellido} (DNI: {self.dni})"

    def horas_trabajadas_diarias(self):
        # Ejemplo para calcular horas del día actual
        ahora = timezone.now()
        inicio_dia = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = inicio_dia + timedelta(days=1)
        fichajes_hoy = self.fichajes.filter(
            fecha_entrada__lt=fin_dia,
            fecha_salida__gte=inicio_dia
        )
        total_horas = 0.0
        for fichaje in fichajes_hoy:
            total_horas += fichaje.horas_trabajadas_dentro_de_rango(inicio_dia, fin_dia)
        return total_horas

    def horas_trabajadas_semanales(self):
        # Ejemplo para calcular horas de la semana en curso (lunes-domingo)
        ahora = timezone.now()
        lunes_semana = ahora - timedelta(days=ahora.weekday())
        inicio_semana = lunes_semana.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_semana = inicio_semana + timedelta(days=7)
        fichajes_semana = self.fichajes.filter(
            fecha_entrada__lt=fin_semana,
            fecha_salida__gte=inicio_semana
        )
        total_horas = 0.0
        for fichaje in fichajes_semana:
            total_horas += fichaje.horas_trabajadas_dentro_de_rango(inicio_semana, fin_semana)
        return total_horas


class Fichaje(models.Model):
    """
    Un registro de fichaje por empleado (entrada y salida en un mismo objeto).
    """
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='fichajes')
    fecha_entrada = models.DateTimeField()
    fecha_salida = models.DateTimeField(blank=True, null=True)
    duracion = models.DurationField(blank=True, null=True)

    # Para cierres automáticos / incidencias
    automatica = models.BooleanField(default=False)
    incidencia = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.fecha_entrada and self.fecha_salida:
            self.duracion = self.fecha_salida - self.fecha_entrada
        super().save(*args, **kwargs)

    def horas_trabajadas(self) -> float:
        """
        Retorna la duración en horas de ESTE fichaje.
        Si no hay salida, calcula 'on the fly' hasta ahora.
        """
        if self.duracion is not None:
            return self.duracion.total_seconds() / 3600
        elif self.fecha_entrada and not self.fecha_salida:
            diff = timezone.now() - self.fecha_entrada
            return diff.total_seconds() / 3600
        else:
            return 0.0

    def horas_trabajadas_dentro_de_rango(self, inicio, fin) -> float:
        """
        Para casos donde el fichaje cruza medianoche u otro rango.
        Retorna cuántas horas de este fichaje caen en [inicio, fin].
        """
        fecha_salida_efectiva = self.fecha_salida or timezone.now()
        rango_inicio = max(self.fecha_entrada, inicio)
        rango_fin = min(fecha_salida_efectiva, fin)
        if rango_fin > rango_inicio:
            delta = rango_fin - rango_inicio
            return delta.total_seconds() / 3600
        return 0.0

    def __str__(self):
        salida = self.fecha_salida if self.fecha_salida else '---'
        return f"Fichaje {self.pk} - {self.empleado} ({self.fecha_entrada} -> {salida})"
