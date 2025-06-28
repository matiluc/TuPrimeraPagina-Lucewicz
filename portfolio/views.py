from django.shortcuts import render, redirect
from .forms import RecetaForm
from .models import Receta

def padre(request):
    return render(request, "portfolio/padre.html")

def index(request):
    return render(request, "portfolio/index.html")

def recetas(request):
    recetas = Receta.objects.all()
    return render(request, "portfolio/recetas.html", {'recetas': recetas})

def contacto(request):
    return render(request, "portfolio/contacto.html")

def lista_recetas(request):
    recetas = Receta.objects.all()
    return render(request, "portfolio/lista_recetas.html", {'recetas': recetas})

def crear_receta(request):
    if request.method == 'POST':
        form = RecetaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')  # o a donde quieras volver
    else:
        form = RecetaForm()
    return render(request, "portfolio/crear_receta.html", {'form': form})