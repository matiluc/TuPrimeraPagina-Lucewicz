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


# ordenar recetas por nombre

def listar_recetas(request):
    # Debug: imprimir en consola del servidor
    orden = request.GET.get('orden')
    print(f"Parámetro 'orden' recibido: {orden}")
    print(f"Todos los parámetros GET: {request.GET}")
    
    # Obtener todas las recetas SIN orden primero
    recetas_sin_orden = Receta.objects.all()
    print(f"Recetas sin orden: {[r.titulo for r in recetas_sin_orden]}")
    
    # Aplicar orden
    if orden == '-titulo':
        recetas = recetas_sin_orden.order_by('-titulo')
        print("Aplicando orden Z-A")
    elif orden == 'titulo':
        recetas = recetas_sin_orden.order_by('titulo')
        print("Aplicando orden A-Z")
    else:
        recetas = recetas_sin_orden.order_by('titulo')  # Por defecto A-Z
        print("Aplicando orden por defecto (A-Z)")
    
    # Mostrar resultado final
    print(f"Recetas ordenadas: {[r.titulo for r in recetas]}")
    
    context = {
        'recetas': recetas,
        'orden': orden,
    }
    
    return render(request, 'tu_template.html', context)


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
            receta = form.save(commit=False)
            receta.save()
            messages.success(request, '¡La receta se subió exitosamente!')
            form.save_m2m()
            return redirect('crear_receta')
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

#############################################################

# EDITAR

def tabla_edicion_recetas(request):
    recetas = Receta.objects.all()
    return render(request, 'portfolio/tabla_edicion_recetas.html', {'recetas': recetas})

# EDITAR RECETA USA EL FORM PARA CREAR PERO MANTIENE LA INFO

def editar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    
    if request.method == 'POST':
        form = RecetaForm(request.POST, request.FILES, instance=receta)
        if form.is_valid():
            receta = form.save(commit=False)
            receta.save()
            messages.success(request, '¡La receta se editó exitosamente!')
            form.save_m2m()
            return redirect('editar_receta', pk=receta.pk)
    else:
        form = RecetaForm(instance=receta)
    
    return render(request, 'portfolio/editar_receta.html', {'form': form, 'receta': receta})

#############################################################

# ELIMINAR

def eliminar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    
    if request.method == 'POST':
        titulo_receta = receta.titulo 
        receta.delete()
        messages.success(request, f'La receta "{titulo_receta}" se eliminó exitosamente.') 
        return redirect('tabla_edicion_recetas')
    
    # Si no es POST, mostrar página de confirmación
    return render(request, 'portfolio/tabla_edicion_recetas.html', {'receta': receta})