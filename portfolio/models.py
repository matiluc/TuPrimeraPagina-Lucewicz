from django.db import models
from ckeditor.fields import RichTextField

class Receta(models.Model):
    titulo = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='recetas/', blank=True, null=True)
    receta = RichTextField()

    def __str__(self):
        return self.titulo