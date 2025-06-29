from django.shortcuts import render, redirect, get_object_or_404
from .forms import RecetaForm, SuscriptorForm
from .models import Receta, Suscriptor
from django.contrib import messages


#############################################################

# FUNCIONES SIMPLES:

def padre(request):
    return render(request, "portfolio/padre.html")

def pauta(request):
    return render(request, "portfolio/pauta.html")

# def contacto(request):
#     return render(request, "portfolio/contacto.html")

#############################################################

# FUNCIONES COMPLEJAS

# View de index + funcion para contar totales en bbdd
def index(request):
    context = {
        'total_recetas': Receta.objects.count(),
        'total_suscriptores': Suscriptor.objects.count(),
    }
    return render(request, 'portfolio/index.html', context)

# View de recetas + paginación de la pagina de recetas (para ver de a tandas)
def recetas(request):
    limite = int(request.GET.get('limite', 6))
    recetas = Receta.objects.order_by('-id')[:limite]
    # recetas = Receta.objects.all()[:limite]
    todas_las_recetas = Receta.objects.count()
    
    context = {
        'recetas': recetas,
        'mostrar_mas': limite < todas_las_recetas,
        'siguiente_limite': limite + 6
    }
    return render(request, "portfolio/recetas.html", context)

# Para ver cada receta individualmmente, pk = primary key
def detalle_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    return render(request, 'portfolio/detalle_receta.html', {'receta': receta})

#############################################################

# FUNCIONES FORMULARIOS

# Formulario suscripcion al newsletter
def suscriptor(request):
    if request.method == 'POST':
        form = SuscriptorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # para dar una confirmacion que se sucribió ok
            messages.success(request, '¡Te suscribiste exitosamente!')
            return redirect('suscriptor')
    else:
        form = SuscriptorForm()
    return render(request, 'portfolio/suscriptor.html', {'form': form})

# Formulario crear receta
def crear_receta(request):
    if request.method == 'POST':
        form = RecetaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('recetas')
    else:
        form = RecetaForm()
    return render(request, 'portfolio/crear_receta.html', {'form': form})

# Buscador de recetas + formulario de búsqueda
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

