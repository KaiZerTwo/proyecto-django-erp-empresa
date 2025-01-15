# employees/urls.py

from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('fichar/entrada/<int:empleado_id>/', views.fichar_entrada, name='fichar_entrada'),
    path('fichar/salida/<int:fichaje_id>/', views.fichar_salida, name='fichar_salida'),
    path('fichajes/', views.fichajes_list, name='fichajes_list'),
]

