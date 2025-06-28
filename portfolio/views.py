from django.shortcuts import render, redirect, get_object_or_404
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

def crear_receta(request):
    if request.method == 'POST':
        form = RecetaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')  # o a donde quieras volver
    else:
        form = RecetaForm()
    return render(request, "portfolio/crear_receta.html", {'form': form})

def detalle_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    return render(request, 'portfolio/detalle_receta.html', {'receta': receta})