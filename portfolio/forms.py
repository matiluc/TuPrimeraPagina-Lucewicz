from django import forms
from .models import Receta, Suscriptor
from ckeditor.widgets import CKEditorWidget

# Formulario subida receta nueva
class RecetaForm(forms.ModelForm):
    receta = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = Receta
        fields = ['titulo', 'foto', 'categorias', 'receta']
        widgets = {
            # estos dos son para que el nombre del campo aparezca dentro del campo
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            # agregue esto para poder hacer dropdown de categorias
            'categorias': forms.SelectMultiple(attrs={'class': 'form-select'})
        }

# Formulario Newsletter
class SuscriptorForm(forms.ModelForm):
    class Meta:
        model = Suscriptor
        fields = ['nombre', 'apellido', 'email']
        # esto para el mensaje de advertencia
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }