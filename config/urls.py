from django.contrib import admin
from django.urls import path, include
from portfolio import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [

    # VER
    path('admin/', admin.site.urls), # ADMIN
    path('', views.index, name='index'), # HOME
    path('recetas', views.recetas, name='recetas'), # LISTA RECETAS
    path("receta/<int:pk>/", views.detalle_receta, name="detalle_receta"), # RECETAS INDIVIDUALES
    path('pauta', views.pauta, name='pauta'), # PAUTA
    path('buscador/', views.buscador, name='buscador'), # BUSCADOR

    # CREAR
    path('crear_receta', views.crear_receta, name='crear_receta'), # RECETA NUEVA
    path('suscriptor', views.suscriptor, name='suscriptor'), # SUSCRIBIRSE NEWSLETTER

    # EDITAR
    path('receta/editar/<int:pk>/', views.editar_receta, name='editar_receta'), # EDITAR RECETA INDIVIDUAL
    path('suscriptor/editar/<int:pk>/', views.editar_suscriptor, name='editar_suscriptor'), # EDITAR SUSCRIPTOR INDIVIDUAL
    path('ckeditor/', include('ckeditor_uploader.urls')), # EDITOR DE ESTILOS PARA EL FORM DE RECETA NUEVA
    path('tabla_edicion_recetas/', views.tabla_edicion_recetas, name='tabla_edicion_recetas'),
    path('tabla_edicion_suscriptores/', views.tabla_edicion_suscriptores, name='tabla_edicion_suscriptores'),
    path('tabla_edicion_usuarios/', views.tabla_edicion_usuarios, name='tabla_edicion_usuarios'),

    # ELIMINAR
    path('receta/eliminar/<int:pk>/', views.eliminar_receta, name='eliminar_receta'),
    path('suscriptor/eliminar/<int:pk>/', views.eliminar_suscriptor, name='eliminar_suscriptor'),

    # USUARIOS
    path('usuario/login', views.login_request, name='login'),
    path('usuario/registro', views.register, name='registro'),
    path('usuario/salir', LogoutView.as_view(next_page='index'), name='salir'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('perfil/crear/', views.crear_perfil, name='crear_perfil'),
    path('perfil/<str:username>/', views.perfil_publico, name='perfil_publico'), # PARA VER PERFIL PÚBLICO
    path('tabla_edicion_usuarios/', views.tabla_edicion_usuarios, name='tabla_edicion_usuarios'), # TABLA EDICION USUARIOS
    path('usuarios/editar/<int:pk>/', views.perfil_usuario, name='editar_usuario_superuser'), 
    path('usuarios/eliminar/<int:pk>/', views.eliminar_usuario_superuser, name='eliminar_usuario_superuser'),

    # CAMBIO PASSWORDS
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # pagar agregar fotos al form de recetas pero probe tantas cosas que no se sigue siendo necesario

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)