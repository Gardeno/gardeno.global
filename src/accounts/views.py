from django.shortcuts import render


def accounts_login(request):
    return render(request, 'accounts/login.html')

