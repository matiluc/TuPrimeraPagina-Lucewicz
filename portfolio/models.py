from django.db import models
from ckeditor.fields import RichTextField

class Receta(models.Model):
    titulo = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='recetas/', blank=True, null=True)
    receta = RichTextField()

    def __str__(self):
        return self.titulo
    
class Suscriptor(models.Model):
    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40)
    email = models.EmailField()

    def __str__(self):
        return f'{self.nombre} {self.apellido}'