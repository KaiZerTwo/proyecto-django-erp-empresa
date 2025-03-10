from django.urls import path
from .views import home

app_name = 'website'  # Si usas 'website:home' en las plantillas

urlpatterns = [
    path('', home, name='home'),
]

