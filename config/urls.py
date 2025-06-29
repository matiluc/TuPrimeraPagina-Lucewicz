"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from portfolio import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls), # admin
    path('', views.index, name='index'), # home
    path('recetas', views.recetas, name='recetas'), # recetas
    path("receta/<int:pk>/", views.detalle_receta, name="detalle_receta"), # recetas individuales
    # path('contacto', views.contacto, name='contacto'), # ya no está
    path('crear_receta', views.crear_receta, name='crear_receta'), # crear receta nueva
    path('ckeditor/', include('ckeditor_uploader.urls')), # editor con estilos para el form de crear receta nueva
    path('pauta', views.pauta, name='pauta'), # pauta
    path('suscriptor', views.suscriptor, name='suscriptor'), # form suscriptor
    path('buscador/', views.buscador, name='buscador'), # buscador
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # pagar agregar fotos al form de recetas pero probe tantas cosas que no se sigue siendo necesario

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)