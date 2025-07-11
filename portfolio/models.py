from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.utils import timezone # para poner fecha en posteo

# Class 1 = esta arriba porque me daba error al estar abajo ya que se llama en la clase Receta
class Categorias(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

# Class 2 = para manejar las recetas
class Receta(models.Model):
    titulo = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='recetas/', null=True, blank=True)
    categorias = models.ManyToManyField('Categorias', blank=True)
    receta = RichTextField(blank=False)
    fecha = models.DateField(default=timezone.now)  # <-- FECHA
    autor = models.ForeignKey(User, on_delete=models.CASCADE)  # <-- AUTOR

    def __str__(self):
        return self.titulo

# Class 3 = para crear bbdd con suscriptores al blog y posibles updates con newsletter
class Suscriptor(models.Model):
    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40)
    email = models.EmailField()

    def __str__(self):
        return f'{self.nombre} {self.apellido} {self.email}'