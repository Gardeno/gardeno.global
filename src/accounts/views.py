from django.shortcuts import render
from django.contrib.auth import logout, login
from django.http import HttpResponseRedirect
from .models import User


def accounts_login(request):
    error = None
    next_url = None
    if request.GET.get('next', None):
        next_url = request.GET['next']
    elif request.GET.get('next', None):
        next_url = request.POST['next']
    if request.POST:
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        if not email:
            error = 'Email address is required'
        elif not password:
            error = 'Password is required'
        else:
            try:
                user = User.objects.get(email__iexact=email.strip())
            except Exception as exception:
                user = None
            if not user:
                error = 'Email / password is incorrect'
            elif not user.check_password(password):
                error = 'Email / password is incorrect'
            else:
                login(request, user)
                return HttpResponseRedirect(next_url if next_url else '/')
    return render(request, 'accounts/login.html', {
        'next_url': next_url,
        'error': error,
    })


def accounts_signup(request):
    return render(request, 'accounts/signup.html')


def accounts_logout(request):
    logout(request)
    return HttpResponseRedirect('/')
