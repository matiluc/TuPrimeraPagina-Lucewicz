from django import forms
from .models import Receta
from ckeditor.widgets import CKEditorWidget

class RecetaForm(forms.ModelForm):
    receta = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = Receta
        fields = ['titulo', 'foto', 'receta']