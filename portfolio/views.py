from django.shortcuts import render, redirect, get_object_or_404
from .forms import RecetaForm, SuscriptorForm, PerfilForm, UserEditForm
from .models import Receta, Suscriptor, CATEGORIA_CHOICES
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
            receta.autor = request.user
            if not receta.fecha:
                receta.fecha = timezone.now()

            receta.save()

            messages.success(request, '¡La receta se creó exitosamente!')
            return redirect('tabla_edicion_recetas')
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
        q_objects = Q(titulo__icontains=consulta)
        
        consulta_normalizada = consulta.lower().replace(' ', '_')
        q_objects |= Q(categorias__icontains=consulta_normalizada)
    
        matched_category_values = []
        for val, label in CATEGORIA_CHOICES:
            if consulta.lower() in label.lower():
                matched_category_values.append(val)
        
        if matched_category_values:
            for val in matched_category_values:
                q_objects |= Q(categorias__icontains=val)

        recetas = Receta.objects.filter(q_objects).distinct()
    
    return render(request, "portfolio/buscador.html", {
        "consulta": consulta,
        "recetas": recetas,
    })

#############################################################


# EDITAR

# PARA QUE SOLO EL ADMIN PUEDA EDITAR
def solo_superuser(user):
    return user.is_superuser

@login_required
def tabla_edicion_recetas(request):
    if request.user.is_superuser:
        recetas = Receta.objects.all().order_by('-id')
    else:
        recetas = Receta.objects.filter(autor=request.user).order_by('-id')
    
    return render(request, 'portfolio/tabla_edicion_recetas.html', {'recetas': recetas})


# TABLA EDICION DE USUARIOS

@user_passes_test(solo_superuser)
def tabla_edicion_usuarios(request):
    usuarios = User.objects.all().order_by('username')
    return render(request, 'portfolio/tabla_edicion_usuarios.html', {'usuarios': usuarios})

# ELIMINAR USUARIOS COMO ADMIN

@login_required
@user_passes_test(solo_superuser)
def eliminar_usuario_superuser(request, pk):
    user_to_delete = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        if request.user.pk == user_to_delete.pk:
            messages.error(request, "No puedes eliminar tu propia cuenta de superusuario.")
        else:
            user_to_delete.delete()
            messages.success(request, f'¡Usuario "{user_to_delete.username}" eliminado exitosamente!')
        
        return redirect('tabla_edicion_usuarios')
    return redirect('tabla_edicion_usuarios')


# EDITAR RECETA USA EL FORM PARA CREAR PERO MANTIENE LA INFO

@login_required
def editar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    
    # SOLO PUEDE EDITAR ADMIN O AUTOR
    if request.user != receta.autor and not request.user.is_superuser:
        return redirect('recetas')

    if request.method == 'POST':
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
            print(form.errors)
    else:
        form = RecetaForm(instance=receta)
    
    context = {
        'form': form, 
        'receta': receta,
        'contenido_receta': receta.receta if receta.receta else ''
    }
    
    return render(request, 'portfolio/editar_receta.html', context)


# PERMISOS DE SUPERUSER PARA EDITAR


@user_passes_test(solo_superuser)
def tabla_edicion_suscriptores(request):
    suscriptores = Suscriptor.objects.all().order_by('nombre')
    return render(request, 'portfolio/tabla_edicion_suscriptores.html', {'suscriptores': suscriptores})

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
def perfil_usuario(request, pk=None): # ¡Añadimos 'pk=None' para hacerlo opcional!
    # Determina qué usuario estamos editando
    is_editing_other_user = False
    if pk: # Si se proporcionó un PK, un superusuario está editando a otro
        if not request.user.is_superuser: # Si no es superusuario, no puede editar a otros
            messages.error(request, "No tienes permisos para editar otros perfiles.")
            return redirect('index') # O a donde creas conveniente
        
        user_to_edit = get_object_or_404(User, pk=pk)
        is_editing_other_user = True
    else: # Si no hay PK, el usuario logueado está editando su propio perfil
        user_to_edit = request.user
    
    # Intenta obtener el perfil asociado. Si no existe, lo redirige a crear_perfil solo si es su propio perfil.
    try:
        perfil = user_to_edit.perfil
    except Perfil.DoesNotExist:
        if not is_editing_other_user: # Solo redirige si es el propio usuario sin perfil
            return redirect('crear_perfil')
        else: # Si es superusuario editando a alguien sin perfil, crea uno directamente
            perfil = Perfil.objects.create(user=user_to_edit)


    # INICIALIZA FORMS (usando user_to_edit en lugar de request.user)
    user_form = UserEditForm(request.POST or None, instance=user_to_edit)
    perfil_form = PerfilForm(request.POST or None, request.FILES or None, instance=perfil)
    
    # El formulario de cambio de contraseña SOLO se inicializa si NO estamos editando a otro usuario
    password_form = None
    if not is_editing_other_user:
        password_form = PasswordChangeForm(user_to_edit)

    if request.method == 'POST':
        if 'submit_perfil' in request.POST:
            if user_form.is_valid() and perfil_form.is_valid():
                user_form.save()
                perfil_form.save()
                if is_editing_other_user:
                    messages.success(request, f'¡El perfil de "{user_to_edit.username}" fue actualizado correctamente por el superusuario!')
                    return redirect('tabla_edicion_usuarios') # Redirige a la tabla si el superusuario editó
                else:
                    messages.success(request, 'Tu perfil fue actualizado correctamente.')
                    return redirect('perfil') # Redirige a su propio perfil
            else:
                messages.error(request, 'Por favor, corrige los errores en el formulario.')

        # La lógica de cambio de contraseña SOLO se ejecuta si NO estamos editando a otro usuario
        elif 'submit_password' in request.POST and not is_editing_other_user:
            password_form = PasswordChangeForm(user_to_edit, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Contraseña actualizada correctamente.')
                return redirect('perfil') # Redirige a su propio perfil (debe ser el suyo)
            else:
                messages.error(request, 'Por favor, corrige los errores en el formulario de contraseña.')

    context = {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'password_form': password_form, # Será None si is_editing_other_user es True
        'is_editing_other_user': is_editing_other_user, # Para que el template sepa el contexto
        'editing_target_username': user_to_edit.username, # Para mostrar el nombre del usuario que se edita
        'user': user_to_edit, # El usuario que se está editando (para mostrar su información)
        'perfil': perfil, # El perfil del usuario que se está editando
    }
    return render(request, 'portfolio/usuario/perfil.html', context)


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