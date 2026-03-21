from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Parametres, About

@login_required
def parametres(request):
    params, created = Parametres.objects.get_or_create(user=request.user)
    return render(request, 'modules/parametres/parametres.html', {'params': params})

@login_required
def update_parametres(request):
    if request.method == 'POST':
        params, created = Parametres.objects.get_or_create(user=request.user)
        if 'notifications' in request.POST:
            params.notifications_activees = request.POST.get('notifications') == 'true'

        params.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
def about(request):
    infos = About.objects.first()
    if not infos:
        infos = About.objects.create()
    params, created = Parametres.objects.get_or_create(user=request.user)
    return render(request, 'modules/parametres/about.html', {
        'infos': infos,
        'params': params
    })