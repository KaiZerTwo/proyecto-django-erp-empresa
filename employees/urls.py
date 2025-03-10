# employees/urls.py

from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.employees_home, name='home'),  # Página principal de empleados
    path('fichar/', views.fichar, name='fichar'),
    path('fichajes/', views.fichajes_list, name='fichajes_list'),
    path('add/', views.add_employee, name='add_employee'),
]

