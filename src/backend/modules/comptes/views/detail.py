import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Max, F
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal

from modules.comptes.models import CompteArgent, CompteOr, MouvementCompte
from modules.core.services.prix_or_service import get_latest_prix_or, set_prix_or
from modules.karfa.models import Karfa
from modules.dettes.models import Dette
from modules.comptes.forms import CompteArgentForm, CompteOrForm

@login_required
@login_required
def detail_compte(request, id):
    type_param = request.GET.get('type')
    
    if type_param == 'or':
        compte = get_object_or_404(CompteOr, id=id, cree_par=request.user)
        type_compte = 'or'
        is_or = True
    elif type_param == 'argent':
        compte = get_object_or_404(CompteArgent, id=id, cree_par=request.user)
        type_compte = 'argent'
        is_or = False
    else:
        # Fallback si le paramètre type n'est pas fourni
        try:
            compte = CompteArgent.objects.get(id=id, cree_par=request.user)
            type_compte = 'argent'
            is_or = False
        except CompteArgent.DoesNotExist:
            compte = get_object_or_404(CompteOr, id=id, cree_par=request.user)
            type_compte = 'or'
            is_or = True
    mouvements = compte.mouvements.all().order_by('-date')
        
    return render(request, 'modules/comptes/detail.html', {
        'compte': compte,
        'is_or': is_or,
        'type_compte': type_compte,
        'nature': type_compte,
        'mouvements': mouvements
    })
