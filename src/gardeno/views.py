from django.shortcuts import render
from django.http import HttpResponseRedirect
from accounts.models import LaunchSignup


def index(request):
    return render(request, 'index.html', {
        "success": request.GET.get('success', None) == '',
        "error": request.GET.get('error', None) == '',
    })


def notify(request):
    email = request.POST.get('email', '')
    if not email:
        return HttpResponseRedirect('/?error')
    else:
        LaunchSignup.objects.create(email=email)
    return HttpResponseRedirect('/?success')


def grows(request):
    return render(request, 'grows.html')
