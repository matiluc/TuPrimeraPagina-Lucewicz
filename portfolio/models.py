from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.utils import timezone # para poner fecha en posteo

# para foto avatar
from django.templatetags.static import static
import os

# Class 1 = esta arriba porque me daba error al estar abajo ya que se llama en la clase Receta
# class Categorias(models.Model):
#     nombre = models.CharField(max_length=50, unique=True)

#     def __str__(self):
#         return self.nombre

CATEGORIA_CHOICES = [
    ('para_diabeticos', 'Para Diabéticos'),
    ('sin_tacc', 'Sin TACC'),
    ('bajo_en_calorias', 'Bajo en Calorías'),
    ('vegano', 'Vegano'),
    ('vegetariano', 'Vegetariano'),
    ('sin_lactosa', 'Sin Lactosa'),
]

# Class 2 = para manejar las recetas
class Receta(models.Model):
    titulo = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='recetas/', null=True, blank=True)
    categorias = models.JSONField(default=list, blank=True, null=True) 
    receta = RichTextField(blank=False)
    fecha = models.DateField(default=timezone.now)  # <-- FECHA
    autor = models.ForeignKey(User, on_delete=models.CASCADE)  # <-- AUTOR

    def __str__(self):
        return self.titulo
    
    def get_categorias_display(self):
        category_map = dict(CATEGORIA_CHOICES)
        if self.categorias is None:
            return []
        return [category_map.get(cat, cat.replace('_', ' ').capitalize()) for cat in self.categorias]


# Class 3 = para crear bbdd con suscriptores al blog y posibles updates con newsletter
class Suscriptor(models.Model):
    nombre = models.CharField(max_length=40)
    email = models.EmailField()

    def __str__(self):
        return f'{self.nombre} {self.email}'

# Class 4 = para crear bbdd con perfiles con usuario, avatar y bio y foto default si no tiene
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, default='portfolio/img/default-avatar.jpg')
    biografia = models.TextField(blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def get_avatar_url(self):
        if self.avatar and os.path.isfile(self.avatar.path):
            return self.avatar.url
        return static('portfolio/img/default-avatar.jpg')