# employees/urls.py

from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('fichar/', views.fichar, name='fichar'),
    path('fichajes/', views.fichajes_list, name='fichajes_list'),
]

