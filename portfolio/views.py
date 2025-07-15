# ==============================================================================
# IMPORTS NECESARIOS
# ==============================================================================

# Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User

# Modelos
from .models import Receta, Suscriptor, Perfil, CATEGORIA_CHOICES

# Formularios
from .forms import RecetaForm, SuscriptorForm, PerfilForm, UserEditForm, UserRegisterForm

# ==============================================================================
# FUNCIONES AUXILIARES / DECORADORES
# ==============================================================================


def solo_superuser(user):
    return user.is_superuser


# ==============================================================================
# VISTAS GENERALES (Páginas Estáticas / Sin Lógica Compleja)
# ==============================================================================


def padre(request):
    return render(request, "portfolio/padre.html")


def pauta(request):
    return render(request, "portfolio/pauta.html")


def about_me(request):
    return render(request, "portfolio/about_me.html")


# INCLUYE SUSCRIPCIÓN AL NEWSLETTER Y CONTADORES
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
        'total_usuarios': User.objects.count(),
        'form': form
    }
    return render(request, 'portfolio/index.html', context)

# ==============================================================================
# VISTAS DE AUTENTICACIÓN Y REGISTRO
# ==============================================================================


# INICIO DE SESIÓN
def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.cleaned_data.get('username')
            contrasenia = form.cleaned_data.get('password')
            user = authenticate(username=usuario, password=contrasenia)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
                return redirect('index')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()

    form.fields['username'].widget.attrs['placeholder'] = 'Nombre de usuario'
    form.fields['username'].widget.attrs['class'] = 'form-control'
    form.fields['password'].widget.attrs['placeholder'] = 'Contraseña'
    form.fields['password'].widget.attrs['class'] = 'form-control'
    # ------------------------------------------------------------------

    return render(request, 'portfolio/usuario/login.html', {"form": form})


# REGISTRO DE NUEVOS USUARIOS
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Opcional: Crear un perfil vacío para el nuevo usuario
            Perfil.objects.get_or_create(user=user)
            messages.success(request, 'Usuario creado con éxito. ¡Ya puedes iniciar sesión!')
            return redirect('login')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = UserRegisterForm()
    return render(request, 'portfolio/usuario/registro.html', {'form': form})


# ==============================================================================
# VISTAS DE RECETAS
# ==============================================================================


def recetas(request):
    limite = int(request.GET.get('limite', 6))
    recetas = Receta.objects.order_by('-id')[:limite]
    todas_las_recetas = Receta.objects.count()
    
    context = {
        'recetas': recetas,
        'mostrar_mas': limite < todas_las_recetas,
        'siguiente_limite': limite + 6
    }
    return render(request, "portfolio/recetas.html", context)


# MUESTRA RECETA ELEGIDA
def detalle_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    return render(request, 'portfolio/detalle_receta.html', {'receta': receta})


# CREAR RECETA
@login_required
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


# EDITAR USUARIO SI SE ES EL USUARIO O ADMIN
@login_required
def editar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    
    # Solo el autor o un superusuario pueden editar
    if request.user != receta.autor and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para editar esta receta.')
        return redirect('recetas')

    if request.method == 'POST':
        # Lógica para borrar la foto
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
            messages.error(request, 'Hubo un error al guardar la receta. Revisa los campos.')
            print(form.errors) # Para depuración
    else:
        form = RecetaForm(instance=receta)
    
    context = {
        'form': form, 
        'receta': receta,
        'contenido_receta': receta.receta if receta.receta else ''
    }
    return render(request, 'portfolio/editar_receta.html', context)


# ELIMIAR RECETA SIENDO AUTOR O ADMIN
@login_required
def eliminar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)

    # Restricción de permisos: Solo el autor o un superusuario pueden eliminar
    if request.user != receta.autor and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para eliminar esta receta.')
        return redirect('recetas')
    
    if request.method == 'POST':
        titulo_receta = receta.titulo 
        receta.delete()
        messages.success(request, f'La receta "{titulo_receta}" se eliminó exitosamente.') 
        return redirect('tabla_edicion_recetas')
    
    return redirect('tabla_edicion_recetas')


# BUSCA RECETAS POR TITULO O CATEGORIAS
def buscador(request):
    consulta = request.GET.get("q")
    recetas = None
    if consulta:
        q_objects = Q(titulo__icontains=consulta)
        
        # Búsqueda por valor de categoría (ej. 'postres')
        consulta_normalizada = consulta.lower().replace(' ', '_')
        q_objects |= Q(categorias__icontains=consulta_normalizada)
        
        # Búsqueda por etiqueta visible de categoría (ej. 'Postres')
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


# MUESTRA RECETAS DE "A" A LA "Z"
def listar_recetas(request):
    orden = request.GET.get('orden', 'titulo')
    
    recetas_queryset = Receta.objects.all()
    
    if orden == '-titulo':
        recetas = recetas_queryset.order_by('-titulo')
    elif orden == 'titulo':
        recetas = recetas_queryset.order_by('titulo')
    else:
        recetas = recetas_queryset.order_by('titulo')
    
    context = {
        'recetas': recetas,
        'orden': orden,
    }
    return render(request, 'portfolio/listar_recetas.html', context)


# ==============================================================================
# VISTAS DE SUSCRIPTORES
# ==============================================================================


# SUSCRIBIRSE
def suscriptor(request):
    if request.method == 'POST':
        form = SuscriptorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Te suscribiste exitosamente!')
            return redirect('index')
    else:
        form = SuscriptorForm()
    return render(request, 'portfolio/suscriptor.html', {'form': form})


# TABLA DE EDICIÓN DE SUSCRIPTOIRES
@user_passes_test(solo_superuser)
def tabla_edicion_suscriptores(request):
    suscriptores = Suscriptor.objects.all().order_by('nombre')
    return render(request, 'portfolio/tabla_edicion_suscriptores.html', {'suscriptores': suscriptores})


# EDITAR INFORMACIÓN DE SUSCRIPTOR
@user_passes_test(solo_superuser)
def editar_suscriptor(request, pk):
    suscriptor = get_object_or_404(Suscriptor, pk=pk)
    
    if request.method == 'POST':
        form = SuscriptorForm(request.POST, instance=suscriptor)
        if form.is_valid():
            form.save()
            messages.success(request, '¡El suscriptor se editó exitosamente!')
            return redirect('tabla_edicion_suscriptores') # VUELVE A TABLA
        else:
            messages.error(request, 'Hubo un error al guardar el suscriptor. Revisa los campos.')
    else:
        form = SuscriptorForm(instance=suscriptor)
    
    context = {
        'form': form, 
        'suscriptor': suscriptor,
    }
    return render(request, 'portfolio/editar_suscriptor.html', context)


# ELIMINA SUSCRIPTOR SI SE ES ADMIN
@user_passes_test(solo_superuser)
def eliminar_suscriptor(request, pk):
    suscriptor = get_object_or_404(Suscriptor, pk=pk)
    
    if request.method == 'POST':
        nombre_suscriptor = suscriptor.nombre
        suscriptor.delete()
        messages.success(request, f'El suscriptor "{nombre_suscriptor}" se eliminó exitosamente.') 
        return redirect('tabla_edicion_suscriptores')
    
    return redirect('tabla_edicion_suscriptores')


# ==============================================================================
# VISTAS DE GESTIÓN DE USUARIOS Y PERFILES
# ==============================================================================


# PERMITE A USUARIOS EDITAR SU PERFIL O A SUPERUSER EDITAR EL DE CUALQUIERA. MANEJO DE CONTRASEÑA
@login_required
def perfil_usuario(request, pk=None):
    is_editing_other_user = False
    user_to_edit = request.user

    if pk:
        if not request.user.is_superuser:
            messages.error(request, "No tienes permisos para editar otros perfiles.")
            return redirect('index') # VOLVER A PAGINA DE ACCESO DENEGADO (HACER)
        
        user_to_edit = get_object_or_404(User, pk=pk)
        is_editing_other_user = True
    
    # INTENTA OBTENER PERFIL ASOCIADO, SI NO EXISTE CREA UNO
    perfil, created = Perfil.objects.get_or_create(user=user_to_edit)

    # INICIALIZA FORMS CON LOS DATOS
    user_form = UserEditForm(request.POST or None, instance=user_to_edit)
    perfil_form = PerfilForm(request.POST or None, request.FILES or None, instance=perfil)
    
    password_form = None
    # FORMULARIO DE CAMBIO DE PASSWORD NO SE MUESTRA SI SE EDITA A OTRO USER
    if not is_editing_other_user:
        password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        if 'submit_perfil' in request.POST:
            if user_form.is_valid() and perfil_form.is_valid():
                user_form.save()
                perfil_form.save()
                if is_editing_other_user:
                    messages.success(request, f'¡El perfil de "{user_to_edit.username}" fue actualizado correctamente por el superusuario!')
                    return redirect('tabla_edicion_usuarios')
                else:
                    messages.success(request, 'Tu perfil fue actualizado correctamente.')
                    return redirect('perfil')
            else:
                messages.error(request, 'Por favor, corrige los errores en el formulario de perfil.')

        elif 'submit_password' in request.POST and not is_editing_other_user:
            # SOLO SE GUARDA Y VALIDA CONTRASEÑA SI ES TU PROPIO PERFIL
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user) # MANTIENE SESIÓN ABIERTA
                messages.success(request, 'Contraseña actualizada correctamente.')
                return redirect('perfil')
            else:
                messages.error(request, 'Por favor, corrige los errores en el formulario de contraseña.')

    context = {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'password_form': password_form,
        'is_editing_other_user': is_editing_other_user,
        'editing_target_username': user_to_edit.username,
        'user_object': user_to_edit,
        'perfil_object': perfil,
    }
    return render(request, 'portfolio/usuario/perfil.html', context)


# CREA PERFIL, SI EL USUARIO NO TIENE PERFIL SE CREA UNO
@login_required
def crear_perfil(request):
    # SI USUARIO YA TIENE PERFIL, REDIRIGE A EDITAR PERFIL
    try:
        request.user.perfil
        messages.info(request, "Ya tienes un perfil, te hemos redirigido a la página de edición.")
        return redirect('perfil')
    except Perfil.DoesNotExist:
        pass # SI NO EXIST PERFIL, CONTINÚA

    if request.method == 'POST':
        perfil_form = PerfilForm(request.POST, request.FILES)
        if perfil_form.is_valid():
            perfil = perfil_form.save(commit=False)
            perfil.user = request.user
            perfil.save()
            messages.success(request, 'Perfil creado correctamente.')
            return redirect('perfil')
        else:
            messages.error(request, 'Hubo un error al crear el perfil. Revisa los campos.')
    else:
        perfil_form = PerfilForm()

    return render(request, 'portfolio/usuario/crear_perfil.html', {'perfil_form': perfil_form})


# MUESTRA PERFIL PÚBLICO Y SUS RECETAS
def perfil_publico(request, username):
    user = get_object_or_404(User, username=username)
    recetas = Receta.objects.filter(autor=user).order_by('-fecha')

    try:
        perfil = user.perfil
    except Perfil.DoesNotExist:
        perfil = None

    return render(request, 'portfolio/usuario/perfil_publico.html', {
        'user': user,
        'recetas': recetas,
        'perfil': perfil,
    })


# ==============================================================================
# VISTAS DE ADMINISTRACIÓN (SOLO SUPERUSUARIO)
# ==============================================================================


# MUESTRA TABLA DE RECETAS, SUPERUSER LAS VE TODAS NO IMPORTA USUARIO, SINO, SOLO SE VEN LAS CREADAS POR UNO MISMO
@login_required
def tabla_edicion_recetas(request):
    if request.user.is_superuser:
        recetas = Receta.objects.all().order_by('-id')
    else:
        recetas = Receta.objects.filter(autor=request.user).order_by('-id')
    
    return render(request, 'portfolio/tabla_edicion_recetas.html', {'recetas': recetas})


@user_passes_test(solo_superuser)
def tabla_edicion_usuarios(request):
    """
    Muestra una tabla de todos los usuarios, excluyendo al superusuario actual.
    Solo accesible por superusuarios.
    """
    # SE EXCLUYE A SI MISMO DE LA LISTA
    usuarios = User.objects.exclude(pk=request.user.pk).order_by('username')
    return render(request, 'portfolio/tabla_edicion_usuarios.html', {'usuarios': usuarios})


# SUPERUSER PUEDE ELIMINAR OTRO USUARIO, IMPIDE BORRARSE A SI MISMO
@login_required
@user_passes_test(solo_superuser)
def eliminar_usuario_superuser(request, pk):
    """
    Permite a los superusuarios eliminar a otros usuarios.
    Impide que un superusuario se elimine a sí mismo.
    """
    user_to_delete = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        if request.user.pk == user_to_delete.pk:
            messages.error(request, "¡ERROR! No puedes eliminar tu propia cuenta de superusuario.")
        else:
            username_deleted = user_to_delete.username
            user_to_delete.delete()
            messages.success(request, f'¡Usuario "{username_deleted}" eliminado exitosamente!')
        
        return redirect('tabla_edicion_usuarios')
    return redirect('tabla_edicion_usuarios')