# website/urls.py
from django.urls import path
from . import views  # asumiendo que tendrás vistas en website/views.py

app_name = 'website'  # (opcional, ayuda a namespacing)

urlpatterns = [
    # Ejemplo de ruta (pon al menos una)
    # path('', views.index, name='index'),
]
