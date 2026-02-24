from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Parametres, About


@login_required
def parametres(request):
    params = Parametres.objects.first()
    if not params:
        params = Parametres.objects.create()
    return render(request, 'modules/parametres/parametres.html', {'params': params})


@login_required
def about(request):
    infos = About.objects.first()
    if not infos:
        infos = About.objects.create()
    return render(request, 'modules/parametres/about.html', {'infos': infos})