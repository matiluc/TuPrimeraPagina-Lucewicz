from django.shortcuts import render, redirect, get_object_or_404
from .forms import RecetaForm, SuscriptorForm
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

def pauta(request):
    return render(request, "portfolio/pauta.html")

def crear_receta(request):
    if request.method == 'POST':
        form = RecetaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('recetas')
    else:
        form = RecetaForm()

    return render(request, 'portfolio/crear_receta.html', {'form': form})

# def recetaFormWeb(request):
#     if request.method == "POST":
#         miFormulario = RecetaFormWeb(request.POST)
#         if miFormulario.is_valid():
#             informacion = miFormulario.cleaned_data
#             nueva_receta = Receta(titulo=informacion["titulo"], receta=informacion["receta"])
#             nueva_receta.save()
#             return render(request, "portfolio/recetas.html")
    
#     else

def detalle_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    return render(request, 'portfolio/detalle_receta.html', {'receta': receta})

# Suscripcion
def suscriptor(request):
    if request.method == 'POST':
        form = SuscriptorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = SuscriptorForm()

    return render(request, 'portfolio/suscriptor.html', {'form': form})


# Buscador de recetas
def buscador(request):
    consulta = request.GET.get("q")

    if consulta:
        recetas = Receta.objects.filter(titulo__icontains=consulta)
        return render(request, "portfolio/resultados_busqueda.html", {
            "recetas": recetas,
            "consulta": consulta,
        })
    else:
        return render(request, "portfolio/buscador.html")