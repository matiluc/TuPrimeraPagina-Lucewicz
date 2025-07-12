from django import forms
from .models import Receta, Suscriptor, Perfil
from ckeditor.widgets import CKEditorWidget

# para login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# FORM RECETA NUEVA

class RecetaForm(forms.ModelForm):
    receta = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = Receta
        exclude = ['fecha'] # PARA EXCLUIR LA EDICION DE FECHA AL MOMOENTO DE POSTEAR
        fields = ['titulo', 'foto', 'categorias', 'receta']
        widgets = {
            # estos dos son para que el nombre del campo aparezca dentro del campo
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            # agregue esto para poder hacer dropdown de categorias
            'categorias': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'receta': CKEditorWidget(),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


# FORM NEWSLETTER

class SuscriptorForm(forms.ModelForm):
    
    class Meta:
        model = Suscriptor
        fields = ['nombre', 'email']
        # esto para el mensaje de advertencia
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }


# FORM CREACIÓN USUARIO

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña', 'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Repetir contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Repetir contraseña', 'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        help_texts = {k: "" for k in fields}


# CREACIÓN DE PERFIL

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['avatar', 'biografia']
        widgets = {
            'biografia': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Contanos algo sobre vos...',
                'rows': 4
            }),
        }

# EDICIÓN DE PERFIL

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }
