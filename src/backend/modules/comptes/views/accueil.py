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
def accueil_comptes(request):
    """Page d'accueil du module Comptes."""
    # Liquidités (Uniquement comptes non archivés du USER)
    total_liquidites = CompteArgent.objects.filter(cree_par=request.user, archive=False).aggregate(total=Sum('solde'))['total'] or 0

    # Or (Uniquement comptes non archivés du USER)
    prix_or = get_latest_prix_or(request.user)
    total_or_gnf = 0
    total_poids_or = CompteOr.objects.filter(cree_par=request.user, archive=False).aggregate(total=Sum('poids_grammes'))['total'] or 0
    if prix_or:
        total_or_gnf = total_poids_or * prix_or.prix_gramme

    # Créances (On me doit)
    total_creances = Dette.objects.filter(
        cree_par=request.user,
        sens='ON_ME_DOIT',
        archive=False
    ).aggregate(total=Sum('montant_restant'))['total'] or 0

    # Dettes (Je dois)
    total_dettes = Dette.objects.filter(
        cree_par=request.user,
        sens='JE_DOIS',
        archive=False
    ).aggregate(total=Sum('montant_restant'))['total'] or 0

    # Karfa actifs
    total_karfa = Karfa.objects.filter(
        cree_par=request.user,
        archive=False
    ).aggregate(total=Sum('montant_actuel'))['total'] or 0

    total_comptes = total_liquidites + total_or_gnf
    patrimoine_total = total_comptes + total_karfa + total_creances - total_dettes

    return render(request, 'modules/comptes/accueil.html', {
        'total_liquidites': total_liquidites,
        'total_or_gnf': total_or_gnf,
        'total_poids_or': total_poids_or,
        'patrimoine_total': patrimoine_total,
        'prix_or': prix_or,
        'total_creances': total_creances,
        'total_dettes': total_dettes,
        'total_karfa': total_karfa,
    })
