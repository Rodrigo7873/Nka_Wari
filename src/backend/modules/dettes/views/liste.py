from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from modules.dettes.models import Dette, Remboursement
import csv
from django.http import HttpResponse
from django.utils import timezone

@login_required
def liste_dettes(request):
    dettes = Dette.objects.filter(cree_par=request.user, archive=False)
    total_je_dois = dettes.filter(sens='JE_DOIS').aggregate(total=Sum('montant_restant'))['total'] or 0
    total_on_me_doit = dettes.filter(sens='ON_ME_DOIT').aggregate(total=Sum('montant_restant'))['total'] or 0

    dernieres_ops = Remboursement.objects.filter(dette__cree_par=request.user).order_by('-date')[:5]

    return render(request, 'modules/dettes/list.html', {
        'total_je_dois': total_je_dois,
        'total_on_me_doit': total_on_me_doit,
        'dernieres_ops': dernieres_ops,
    })

@login_required
def toutes_dettes(request):
    dettes_je_dois = Dette.objects.filter(cree_par=request.user, sens='JE_DOIS', archive=False).order_by('-date_creation')
    dettes_on_me_doit = Dette.objects.filter(cree_par=request.user, sens='ON_ME_DOIT', archive=False).order_by('-date_creation')
    return render(request, 'modules/dettes/toutes.html', {
        'dettes_je_dois': dettes_je_dois,
        'dettes_on_me_doit': dettes_on_me_doit,
    })
