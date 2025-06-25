from django.shortcuts import render
from django.http import HttpResponse

def saludar(request):
    return HttpResponse("Hola desde Django")

def index(request):
    return render(request, "portfolio/padre.html")