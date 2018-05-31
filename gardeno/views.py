from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def grows(request):
    return render(request, 'grows.html')
