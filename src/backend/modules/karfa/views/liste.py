from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from modules.karfa.models import Karfa
from modules.karfa.models import MouvementKarfa
import csv
from django.http import HttpResponse
from django.utils import timezone

@login_required
def karfa_list(request):
    karfas = Karfa.objects.filter(cree_par=request.user, archive=False)

    # Calcul du montant total engagé
    total_engage = karfas.aggregate(total=Sum('montant_actuel'))['total'] or 0

    # Récupérer les 5 dernières opérations du Karfa pour cet utilisateur
    dernieres_ops = MouvementKarfa.objects.filter(karfa__cree_par=request.user).order_by('-date')[:5]

    context = {
        'karfas': karfas,
        'total_engage': total_engage,
        'dernieres_ops': dernieres_ops,
    }

    return render(request, 'modules/karfa/list.html', context)

@login_required
def liste_tous_karfa(request):
    karfas = Karfa.objects.filter(cree_par=request.user, archive=False).order_by('-date_creation')
    return render(request, 'modules/karfa/tous.html', {'karfas': karfas})
