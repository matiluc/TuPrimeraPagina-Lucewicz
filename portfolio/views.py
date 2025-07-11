from django.shortcuts import render, redirect, get_object_or_404
from .forms import RecetaForm, SuscriptorForm
from .models import Receta, Suscriptor
from django.contrib import messages
from django.utils import timezone # PARA FECHA

# para login:
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm

# para que solo pueda editar superuser:
from django.contrib.auth.decorators import user_passes_test, login_required

# especial para búsqueda de etiquetas
from django.db.models import Q

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
            receta.autor = request.user # asigna autor, sino me olvido
            receta.save()
            if not receta.fecha:
                receta.fecha = timezone.now()
            receta.save()
            form.save_m2m()
            messages.success(request, '¡La receta se creó exitosamente!')
            return redirect('tabla_edicion_recetas')
    else:
        form = RecetaForm()
    return render(request, 'portfolio/crear_receta.html', {'form': form})

# Buscador de recetas + formulario de búsqueda #### SIN BUSCAR EN ETIQUETAS
# def buscador(request):
#     consulta = request.GET.get("q")
#     if consulta:
#         recetas = Receta.objects.filter(titulo__icontains=consulta)
#         return render(request, "portfolio/resultados_busqueda.html", {
#             "recetas": recetas,
#             "consulta": consulta,
#         })
#     else:
#         return render(request, "portfolio/buscador.html")

def buscador(request):
    consulta = request.GET.get("q")
    if consulta:
        recetas = Receta.objects.filter(
            Q(titulo__icontains=consulta) |
            Q(categorias__nombre__icontains=consulta)
        ).distinct()
        return render(request, "portfolio/resultados_busqueda.html", {
            "recetas": recetas,
            "consulta": consulta,
        })
    else:
        return render(request, "portfolio/buscador.html")

#############################################################

# EDITAR

@login_required
def tabla_edicion_recetas(request):
    if request.user.is_superuser:
        recetas = Receta.objects.all().order_by('-id')
    else:
        recetas = Receta.objects.filter(autor=request.user).order_by('-id')
    
    return render(request, 'portfolio/tabla_edicion_recetas.html', {'recetas': recetas})

def tabla_edicion_suscriptores(request):
    suscriptores = Suscriptor.objects.all().order_by('apellido')
    return render(request, 'portfolio/tabla_edicion_suscriptores.html', {'suscriptores': suscriptores})

# EDITAR RECETA USA EL FORM PARA CREAR PERO MANTIENE LA INFO

@login_required
def editar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    
    # SOLO PUEDE EDITAR ADMIN O AUTOR
    if request.user != receta.autor and not request.user.is_superuser:
        return redirect('recetas')  # o a tu página principal

    if request.method == 'POST':
        # Manejar el borrado de imagen
        if 'foto-clear' in request.POST and receta.foto:
            receta.foto.delete()
            receta.foto = None
            receta.save()
        
        # Crear el formulario con los datos recibidos
        form = RecetaForm(request.POST, request.FILES, instance=receta)
        
        # Verifica si el formulario es válido
        if form.is_valid():
            form.save()  # Guardar la receta sin necesidad de reasignar a receta
            messages.success(request, '¡La receta se editó exitosamente!')
            return redirect('tabla_edicion_recetas')  # Redirige al listado de todas las recetas del usuario
        else:
            # Si el formulario no es válido, muestra los errores
            messages.error(request, 'Hubo un error al guardar la receta.')
            print(form.errors)  # Para depurar en consola si algo está mal
    else:
        form = RecetaForm(instance=receta)
    
    # Pasar el contenido de la receta al template
    context = {
        'form': form, 
        'receta': receta,
        'contenido_receta': receta.receta if receta.receta else ''
    }
    
    return render(request, 'portfolio/editar_receta.html', context)


# PERMISOS DE SUPERUSER PARA EDITAR

def solo_superuser(user):
    return user.is_superuser

# EDITAR SUSCRIPTOR (SOLO SUPERUSER / ADMIN)

@user_passes_test(solo_superuser)
def editar_suscriptor(request, pk):
    suscriptor = get_object_or_404(Suscriptor, pk=pk)
    
    if request.method == 'POST':
        form = SuscriptorForm(request.POST, instance=suscriptor)
        
        if form.is_valid():
            suscriptor = form.save()
            messages.success(request, '¡El suscriptor se editó exitosamente!')
            return redirect('editar_suscriptor', pk=pk)
    else:
        form = SuscriptorForm(instance=suscriptor)
    
    # Pasar el contenido de la receta al template
    context = {
        'form': form, 
        'suscriptor': suscriptor,
    }
    
    return render(request, 'portfolio/editar_suscriptor.html', context)


#############################################################

# ELIMINAR

def eliminar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    
    if request.method == 'POST':
        titulo_receta = receta.titulo 
        receta.delete()
        messages.success(request, f'La receta "{titulo_receta}" se eliminó exitosamente.', extra_tags='receta') 
        return redirect('tabla_edicion_recetas')
    
    # Si no es POST, mostrar página de confirmación
    return render(request, 'portfolio/tabla_edicion_recetas.html', {'receta': receta})


def eliminar_suscriptor(request, pk):
    suscriptor = get_object_or_404(Suscriptor, pk=pk)
    
    if request.method == 'POST':
        suscriptor.delete()
        messages.success(request, f'El suscriptor "{suscriptor}" se eliminó exitosamente.', extra_tags='suscriptor') 
        return redirect('tabla_edicion_suscriptores')
    
    # Si no es POST, mostrar página de confirmación
    return render(request, 'portfolio/tabla_edicion_suscriptores.html', {'suscriptor': suscriptor})

#############################################################

# LOGIN

def login_request(request):
    if request.method == 'POST':

        form = AuthenticationForm(request, data = request.POST)
        if form.is_valid():

            usuario = form.cleaned_data.get('username')
            contrasenia = form.cleaned_data.get('password')

            user = authenticate(username= usuario, password=contrasenia)

            if user is not None:
                login(request, user)

        return redirect('index')
    form= AuthenticationForm()
    return render(request, 'portfolio/usuario/login.html', {"form": form})


def register(request):
    if request.method == 'POST':

        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado con éxito. Ya podés iniciar sesión.')
            return redirect('login')
        else:
            messages.error(request, 'Por favor corregí los errores en el formulario.')
    else:
        form = UserRegisterForm()

    return render(request, 'portfolio/usuario/registro.html', {'form': form})