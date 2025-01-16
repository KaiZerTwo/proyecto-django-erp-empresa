# employees/admin.py

from django.contrib import admin
from django.utils.html import format_html
from datetime import timedelta
from .models import Empleado, Fichaje

class IncidenciaFilter(admin.SimpleListFilter):
    title = 'Incidencia'
    parameter_name = 'incidencia'

    def lookups(self, request, model_admin):
        return [
            ('con_incidencia', 'Con incidencia'),
            ('sin_incidencia', 'Sin incidencia'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'con_incidencia':
            return queryset.exclude(incidencia__isnull=True).exclude(incidencia__exact='')
        elif self.value() == 'sin_incidencia':
            return queryset.filter(incidencia__isnull=True) | queryset.filter(incidencia__exact='')
        return queryset


class HorasFilter6(admin.SimpleListFilter):
    """
    Filtra por duracion mayor o menor a 6h.
    """
    title = 'Horas trabajadas'
    parameter_name = 'duracion_horas'

    def lookups(self, request, model_admin):
        return [
            ('menos_6', 'Menos de 6h'),
            ('seis_mas', '6h o más'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'menos_6':
            return queryset.filter(duracion__lt=timedelta(hours=6))
        elif self.value() == 'seis_mas':
            return queryset.filter(duracion__gte=timedelta(hours=6))
        return queryset


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('dni', 'nombre', 'apellido', 'telefono', 'correo')
    search_fields = ('dni', 'nombre', 'apellido')


@admin.register(Fichaje)
class FichajeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'empleado',
        'fecha_entrada',
        'fecha_salida',
        'duracion_horas',
        'colored_incidencia',
        'automatica',
    )
    list_filter = (
        'empleado',
        'automatica',
        IncidenciaFilter,
        HorasFilter6,  # si quieres filtrar por <6h o >=6h
    )
    search_fields = (
        'empleado__dni',
        'empleado__nombre',
        'empleado__apellido',
        'incidencia',
    )
    date_hierarchy = 'fecha_entrada'
    ordering = ('-fecha_entrada',)
    readonly_fields = ('duracion',)

    def duracion_horas(self, obj):
        return f"{obj.horas_trabajadas():.2f} h"
    duracion_horas.short_description = 'Horas'

    def colored_incidencia(self, obj):
        """
        Si hay incidencia, la mostramos en rojo.
        Si no hay, dejamos la celda en blanco.
        """
        if obj.incidencia:
            return format_html('<span style="color: red;">{}</span>', obj.incidencia)
        return ''
    colored_incidencia.short_description = "Incidencia"
