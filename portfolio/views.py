from django.shortcuts import render, redirect, get_object_or_404
from .forms import RecetaForm, SuscriptorForm, PerfilForm, UserEditForm
from .models import Receta, Suscriptor
from django.contrib import messages
from django.utils import timezone # PARA FECHA

# PARA LOGIN:
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm

# PARA QUE SOLO PUEDA EDITAR SUPERUSER:
from django.contrib.auth.decorators import user_passes_test, login_required

# PARA BUSQUEDA DE ETIQUETAS DESDE BUSCADOR
from django.db.models import Q

# PARA MODIFICACIÓN DE PERFIL
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import UserEditForm, PerfilForm
from .models import Perfil
from django.contrib.auth.models import User

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

# def index(request):
#     context = {
#         'total_recetas': Receta.objects.count(),
#         'total_suscriptores': Suscriptor.objects.count(),
#     }
#     return render(request, 'portfolio/index.html', context)

def index(request):
    
    if request.method == 'POST':
        form = SuscriptorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Te suscribiste exitosamente!')
            return redirect('index')
    else:
        form = SuscriptorForm()

    context = {
        'total_recetas': Receta.objects.count(),
        'total_suscriptores': Suscriptor.objects.count(),
        'form': form}
    
    return render(request, 'portfolio/index.html', context)


# VIEW RECETAS + PAGINACIÓN DE PAG RECETAS PARA VER EN TANDAS DE 6

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


# ORDENA RECETAS POR NOMBRE

def listar_recetas(request):
    orden = request.GET.get('orden')
    print(f"Parámetro 'orden' recibido: {orden}")
    print(f"Todos los parámetros GET: {request.GET}")
    
    # OBTIENE RECETAS SIN ORDEN
    recetas_sin_orden = Receta.objects.all()
    print(f"Recetas sin orden: {[r.titulo for r in recetas_sin_orden]}")
    
    # APLICA ORDEN
    if orden == '-titulo':
        recetas = recetas_sin_orden.order_by('-titulo')
        print("Aplicando orden Z-A")
    elif orden == 'titulo':
        recetas = recetas_sin_orden.order_by('titulo')
        print("Aplicando orden A-Z")
    else:
        recetas = recetas_sin_orden.order_by('titulo') # A - Z
        print("Aplicando orden por defecto (A-Z)")
    
    print(f"Recetas ordenadas: {[r.titulo for r in recetas]}")
    
    context = {
        'recetas': recetas,
        'orden': orden,
    }
    
    return render(request, 'tu_template.html', context)


#############################################################

# FUNCIONES FORMULARIOS

# FORM SUSCRIPCIÓN NEWSLETTER

def suscriptor(request):
    if request.method == 'POST':
        form = SuscriptorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Te suscribiste exitosamente!')
            return redirect('suscriptor')
    else:
        form = SuscriptorForm()
    return render(request, 'portfolio/suscriptor.html', {'form': form})


# CREAR RECETA CON AUTOR Y FECHA

def crear_receta(request):
    if request.method == 'POST':
        form = RecetaForm(request.POST, request.FILES)
        if form.is_valid():
            receta = form.save(commit=False)
            receta.autor = request.user  # AUTOR
            if not receta.fecha:  # ASIGNA FECHA ACTUAL SI NO TIENE
                receta.fecha = timezone.now()

            receta.save()
            form.save_m2m()  # GUARDA MANY TO MANY COMO CATEGORÍAS

            messages.success(request, '¡La receta se creó exitosamente!')
            return redirect('tabla_edicion_recetas')  # Redirigimos a la tabla de edición de recetas
    else:
        form = RecetaForm()

    return render(request, 'portfolio/crear_receta.html', {'form': form})

# FORM DE CREAR RECETA FUNCIONANDO, ANULADO PARA PROBAR LINKEO DE RECETA CON AUTOR
# Formulario crear receta
# def crear_receta(request):
#     if request.method == 'POST':
#         form = RecetaForm(request.POST, request.FILES)
#         if form.is_valid():
#             receta = form.save(commit=False)
#             receta.autor = request.user # asigna autor, sino me olvido
#             receta.save()
#             if not receta.fecha:
#                 receta.fecha = timezone.now()
#             receta.save()
#             form.save_m2m()
#             messages.success(request, '¡La receta se creó exitosamente!')
#             return redirect('tabla_edicion_recetas')
#     else:
#         form = RecetaForm()
#     return render(request, 'portfolio/crear_receta.html', {'form': form})


# BUSCADOR CON BUSQUEDA DE CATEGORÍAS

def buscador(request):
    consulta = request.GET.get("q")
    recetas = None
    if consulta:
        recetas = Receta.objects.filter(
            Q(titulo__icontains=consulta) |
            Q(categorias__nombre__icontains=consulta)
        ).distinct()
    return render(request, "portfolio/buscador.html", {
        "consulta": consulta,
        "recetas": recetas,
    })

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
    suscriptores = Suscriptor.objects.all().order_by('nombre')
    return render(request, 'portfolio/tabla_edicion_suscriptores.html', {'suscriptores': suscriptores})


# EDITAR RECETA USA EL FORM PARA CREAR PERO MANTIENE LA INFO

@login_required
def editar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    
    # SOLO PUEDE EDITAR ADMIN O AUTOR
    if request.user != receta.autor and not request.user.is_superuser:
        return redirect('recetas')

    if request.method == 'POST':
        # MANEJO DE BORRADO DE FOTO
        if 'foto-clear' in request.POST and receta.foto:
            receta.foto.delete()
            receta.foto = None
            receta.save()
        
        form = RecetaForm(request.POST, request.FILES, instance=receta)
        
        if form.is_valid():
            form.save()
            messages.success(request, '¡La receta se editó exitosamente!')
            return redirect('tabla_edicion_recetas')
        else:
            messages.error(request, 'Hubo un error al guardar la receta.')
            print(form.errors)  # PARA DEPURAR EN CONSOLA ERRORES
    else:
        form = RecetaForm(instance=receta)
    
    # CONTENIDO DE RECETA AL TEMPLATE
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
    
    return render(request, 'portfolio/tabla_edicion_recetas.html', {'receta': receta})


def eliminar_suscriptor(request, pk):
    suscriptor = get_object_or_404(Suscriptor, pk=pk)
    
    if request.method == 'POST':
        suscriptor.delete()
        messages.success(request, f'El suscriptor "{suscriptor}" se eliminó exitosamente.', extra_tags='suscriptor') 
        return redirect('tabla_edicion_suscriptores')
    
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


# REGISTRO

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



# EDICION Y VISUALIZACION PERFIL

@login_required
def perfil_usuario(request):
    user = request.user
    
    try:
        perfil = user.perfil
    except Perfil.DoesNotExist:
        return redirect('crear_perfil')

    # INICIALIZA FORMS
    user_form = UserEditForm(request.POST or None, instance=user)
    perfil_form = PerfilForm(request.POST or None, request.FILES or None, instance=perfil)
    password_form = PasswordChangeForm(user)

    if request.method == 'POST':
        if 'submit_perfil' in request.POST:
            if user_form.is_valid() and perfil_form.is_valid():
                user_form.save()  # GUARDA CAMBIOSA EN USUARIO (NOMBRE Y EMAIL)
                perfil_form.save()  # GUARDA CAMBIOS EN PERFIL (AVATAR Y BIO)
                messages.success(request, 'Tu perfil fue actualizado correctamente.')
                return redirect('perfil')  # 
            else:
                messages.error(request, 'Por favor, corrige los errores en el formulario.')

        elif 'submit_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user) # ESTO MANTIENE SESION ACTIVA
                messages.success(request, 'Contraseña actualizada correctamente.')
                return redirect('perfil')

    return render(request, 'portfolio/usuario/perfil.html', {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'password_form': password_form,
    })


# CREAR PERFIL CON LOGIN REQUERIDO

@login_required
def crear_perfil(request):
    if request.method == 'POST':
        perfil_form = PerfilForm(request.POST, request.FILES)
        if perfil_form.is_valid():
            perfil = perfil_form.save(commit=False)
            perfil.user = request.user
            perfil.save()
            messages.success(request, 'Perfil creado correctamente.')
            return redirect('perfil')
    else:
        perfil_form = PerfilForm()

    return render(request, 'portfolio/usuario/crear_perfil.html', {'perfil_form': perfil_form})


# PARA VER PERFIL

def perfil_publico(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('404')
    
    # OBTIENE RECETAS
    recetas = Receta.objects.filter(autor=user)
    
    return render(request, 'portfolio/usuario/perfil_publico.html', {
        'user': user,
        'recetas': recetas
    })