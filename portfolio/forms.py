from django import forms
from .models import Receta
from ckeditor.widgets import CKEditorWidget

class RecetaForm(forms.ModelForm):
    receta = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = Receta
        fields = ['titulo', 'foto', 'receta']

# class RecetaFormWeb(forms.Form):
#     titulo = forms.CharField(max_length=100)
#     foto = forms.ImageField(upload_to='recetas/', blank=True, null=True)
#     receta = forms.CharField()