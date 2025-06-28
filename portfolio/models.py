from django.db import models

class Receta(models.Model):
    titulo = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='recetas/', blank=True, null=True)
    receta = models.TextField