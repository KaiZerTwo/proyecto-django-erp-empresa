from django.urls import path
from .views import fichar_entrada, fichar_salida, fichajes_list

urlpatterns = [
    path('api/fichar/entrada/', fichar_entrada, name='fichar_entrada'),
    path('api/fichar/salida/', fichar_salida, name='fichar_salida'),
    path('api/fichajes/', fichajes_list, name='fichajes_list'),
]
