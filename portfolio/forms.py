from django import forms
from .models import Receta, Suscriptor
from ckeditor.widgets import CKEditorWidget

class RecetaForm(forms.ModelForm):
    receta = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = Receta
        fields = ['titulo', 'foto', 'receta']

class SuscriptorForm(forms.ModelForm):
    class Meta:
        model = Suscriptor
        fields = ['nombre', 'apellido', 'email']