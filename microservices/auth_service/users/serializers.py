from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'dni', 'telefono', 'password']
        extra_kwargs = {'password': {'write_only': True}}  # 🔥 La contraseña no se devuelve en la respuesta

    def create(self, validated_data):
        # 🔥 Usamos create_user para que Django encripte la contraseña automáticamente
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],  # La contraseña se encripta aquí
            dni=validated_data.get('dni', ''),
            telefono=validated_data.get('telefono', '')
        )
        user.is_active = True  # 🔥 Aseguramos que el usuario esté activo
        user.save()
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personaliza el token JWT para incluir más información del usuario.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        data['email'] = self.user.email
        return data
