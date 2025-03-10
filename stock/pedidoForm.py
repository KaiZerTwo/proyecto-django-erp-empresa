from django import forms
from .models import Pedido, DetallePedido, Producto

class PedidoForm(forms.ModelForm):
    productos = forms.ModelMultipleChoiceField(
        queryset=Producto.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Pedido
        fields = ['proveedor', 'estado', 'observaciones']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['productos'].queryset = Producto.objects.filter(proveedor=self.instance.proveedor)

    def save(self, commit=True):
        pedido = super().save(commit=False)
        if commit:
            pedido.save()
            for producto in self.cleaned_data['productos']:
                DetallePedido.objects.get_or_create(
                    pedido=pedido,
                    producto=producto,
                    defaults={'cantidad': 1}  # Inicializamos en 1 unidad
                )
        return pedido

