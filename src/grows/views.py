from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def grows_list(request):
    return render(request, 'grows/list.html')


@login_required
def grows_create(request):
    return render(request, 'grows/create.html')
