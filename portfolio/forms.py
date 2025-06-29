from django import forms
from .models import Receta, Suscriptor
from ckeditor.widgets import CKEditorWidget

# Formulario subida receta nueva
class RecetaForm(forms.ModelForm):
    receta = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = Receta
        fields = ['titulo', 'foto', 'receta']

# Formulario Newsletter
class SuscriptorForm(forms.ModelForm):
    class Meta:
        model = Suscriptor
        fields = ['nombre', 'apellido', 'email']
        # esto para el mensaje de advertencia
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }