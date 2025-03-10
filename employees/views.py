# employees/views.py
from django.db.models import Sum, F, ExpressionWrapper, DurationField
from django.utils.dateparse import parse_date
import json
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages

from .forms import EmpleadoForm
from .models import Empleado, Fichaje

def fichar(request):
    """
    Vista única para fichar entrada o salida según el estado del empleado.
    """
    if request.method == 'POST':
        dni = request.POST.get('dni', '').strip()

        if not dni:
            messages.error(request, 'Por favor, introduce tu DNI.')
            return redirect('employees:fichar')

        empleado = Empleado.objects.filter(dni=dni).first()

        if not empleado:
            messages.error(request, 'Empleado no encontrado.')
            return redirect('employees:fichar')

        # Buscar un fichaje abierto (sin fecha_salida registrada)
        fichaje_abierto = Fichaje.objects.filter(empleado=empleado, fecha_salida__isnull=True).first()

        if fichaje_abierto:
            # Registrar salida porque hay una entrada abierta
            fichaje_abierto.fecha_salida = timezone.now()
            fichaje_abierto.save()
            messages.success(request, f'{empleado.nombre} {empleado.apellido} ha fichado su SALIDA correctamente.')
        else:
            # Registrar nueva entrada
            Fichaje.objects.create(
                empleado=empleado,
                fecha_entrada=timezone.now()
            )
            messages.success(request, f'{empleado.nombre} {empleado.apellido} ha fichado su ENTRADA correctamente.')

        return redirect('employees:fichar')

    return render(request, 'employees/fichar.html')


def fichajes_list(request):
    query = request.GET.get('q', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    fichajes = Fichaje.objects.select_related('empleado').order_by('-fecha_entrada')

    # Filtrar por nombre o apellido si se ingresa en el formulario
    if query:
        fichajes = fichajes.filter(
            empleado__nombre__icontains=query
        ) | fichajes.filter(
            empleado__apellido__icontains=query
        )

    # Filtrar por rango de fechas
    if start_date and end_date:
        fichajes = fichajes.filter(
            fecha_entrada__date__gte=parse_date(start_date),
            fecha_salida__date__lte=parse_date(end_date)
        )

    # Agrupar y sumar la duración total por empleado y fecha de entrada
    horas_por_empleado = fichajes.values(
        'empleado__nombre', 'empleado__apellido', 'fecha_entrada__date'
    ).annotate(
        total_horas=Sum(
            ExpressionWrapper(F('duracion'), output_field=DurationField())
        )
    )

    # Preparar datos para el gráfico
    empleados_totales = {}
    for ficha in horas_por_empleado:
        empleado_nombre = f"{ficha['empleado__nombre']} {ficha['empleado__apellido']}"
        total_horas = ficha['total_horas']

        # 🔥 **Corrección: Manejar NoneType**
        if total_horas is None:
            horas_trabajadas = 0  # Si no hay salida, asumimos 0 horas trabajadas
        else:
            horas_trabajadas = total_horas.total_seconds() / 3600

        # Sumar las horas trabajadas por día
        if empleado_nombre in empleados_totales:
            empleados_totales[empleado_nombre] += horas_trabajadas
        else:
            empleados_totales[empleado_nombre] = horas_trabajadas

    empleados_nombres = list(empleados_totales.keys())
    horas_totales = [round(horas, 2) for horas in empleados_totales.values()]

    context = {
        'fichajes': fichajes,
        'empleados': json.dumps(empleados_nombres),
        'horas': json.dumps(horas_totales),
    }

    return render(request, 'employees/fichajes_list.html', context)
def employees_home(request):
    """Vista principal de empleados"""
    return render(request, 'employees/employees.html')

def add_employee(request):
    """Vista para agregar un nuevo empleado"""
    if request.method == "POST":
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Empleado agregado correctamente.")
            return redirect('employees:home')
    else:
        form = EmpleadoForm()

    return render(request, 'employees/add_employee.html', {'form': form})