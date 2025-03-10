from rest_framework import serializers
from .models import Fichaje

class FichajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fichaje
        fields = '__all__'
