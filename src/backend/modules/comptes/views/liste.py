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
def liste_comptes(request):
    """Liste de tous les comptes Argent et Or actifs du USER."""
    # Filtrer tous les comptes actifs de l'utilisateur
    comptes_argent_base = CompteArgent.objects.filter(cree_par=request.user, archive=False).order_by('nom')
    
    # 1. Séparer les comptes réels des comptes dette (passifs)
    comptes_argent = comptes_argent_base.exclude(type_compte='DETTE')
    # Correction : Récupération explicite des comptes de dettes pour l'affichage séparé
    comptes_dette = CompteArgent.objects.filter(
        cree_par=request.user, 
        archive=False, 
        type_compte='DETTE'
    ).select_related('dette_liee')
    
    comptes_or = CompteOr.objects.filter(cree_par=request.user, archive=False).order_by('nom')
    
    # Calcul des totaux
    total_argent = comptes_argent.aggregate(total=Sum('solde'))['total'] or 0
    total_dette = comptes_dette.aggregate(total=Sum('solde'))['total'] or 0
    total_poids_or = comptes_or.aggregate(total=Sum('poids_grammes'))['total'] or 0
    
    prix_or = get_latest_prix_or(request.user)

    if prix_or:
        for c in comptes_or:
            c.valeur_gnf = c.poids_grammes * prix_or.prix_gramme

    # Engagements Karfa par bénéficiaire (Analyse rapide)
    karfas = Karfa.objects.filter(
        cree_par=request.user,
        archive=False,
        statut__in=['ACTIF', 'PARTIELLEMENT_RENDU']
    ).exclude(statut='RENDU_TOTAL').prefetch_related('mouvements')

    dic_personnes = {}
    for k in karfas:
        nom = k.beneficiaire
        if nom not in dic_personnes:
            dic_personnes[nom] = {'beneficiaire': nom, 'total': 0, 'dernier_mouvement': None}
        dic_personnes[nom]['total'] += k.montant_actuel
        last_m = k.mouvements.order_by('-date').first()
        if last_m:
            if not dic_personnes[nom]['dernier_mouvement'] or last_m.date > dic_personnes[nom]['dernier_mouvement']:
                dic_personnes[nom]['dernier_mouvement'] = last_m.date

    # Tri par montant total décroissant
    karfa_par_personne = sorted(dic_personnes.values(), key=lambda x: x['total'], reverse=True)

    return render(request, 'modules/comptes/liste.html', {
        'comptes_argent': comptes_argent,
        'comptes_dette': comptes_dette,
        'comptes_or': comptes_or,
        'total_argent': total_argent,
        'total_dette': total_dette,
        'karfa_par_personne': karfa_par_personne,
        'total_poids_or': total_poids_or,
        'prix_or': prix_or,
    })
