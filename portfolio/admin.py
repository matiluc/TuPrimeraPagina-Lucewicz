from django.contrib import admin
from .models import Receta, Chef, Moderador

admin.site.register(Receta)
admin.site.register(Chef)
admin.site.register(Moderador)