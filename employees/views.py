# employees/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Empleado, Fichaje


def fichar_entrada(request, empleado_id):
    """
    Marca la entrada del empleado (si no tiene un fichaje abierto).
    """
    empleado = get_object_or_404(Empleado, id=empleado_id)

    if request.method == 'POST':
        # Verificamos si ya tiene un fichaje abierto (fecha_salida = None)
        fichaje_abierto = Fichaje.objects.filter(empleado=empleado, fecha_salida__isnull=True).first()
        if fichaje_abierto:
            # Podrías mostrar un error, o redirigir, etc.
            return render(request, 'employees/error.html', {
                'mensaje': 'Ya tienes un fichaje abierto. Cierra antes de abrir otro.'
            })

        # Crear un nuevo fichaje con fecha_entrada = ahora
        Fichaje.objects.create(
            empleado=empleado,
            fecha_entrada=timezone.now()
        )
        return redirect('employees:fichajes_list')

    return render(request, 'employees/fichar_entrada.html', {'empleado': empleado})


def fichar_salida(request, fichaje_id):
    """
    Marca la salida del fichaje abierto.
    """
    fichaje = get_object_or_404(Fichaje, id=fichaje_id)
    if request.method == 'POST':
        fichaje.fecha_salida = timezone.now()
        fichaje.save()
        return redirect('employees:fichajes_list')

    return render(request, 'employees/fichar_salida.html', {'fichaje': fichaje})


def fichajes_list(request):
    """
    Lista todos los fichajes, ordenados por fecha de entrada descendente.
    """
    fichajes = Fichaje.objects.select_related('empleado').order_by('-fecha_entrada')
    return render(request, 'employees/fichajes_list.html', {'fichajes': fichajes})
