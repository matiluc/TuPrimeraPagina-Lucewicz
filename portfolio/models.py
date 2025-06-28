from django.db import models

class Receta(models.Model):
    titulo = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='recetas/', blank=True, null=True)
    receta = models.TextField()

    def __str__(self):
        return self.titulo

class Chef(models.Model):
    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40)
    email = models.EmailField()

class Moderador(models.Model):
    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40)
    email = models.EmailField()