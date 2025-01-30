# apps/website/views.py
from django.shortcuts import render

def home(request):
    return render(request, 'templates/website/home.html')

