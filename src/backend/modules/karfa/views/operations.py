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
def karfa_restituer(request, pk):
    """Restitution partielle ou totale"""
    karfa = get_object_or_404(Karfa, pk=pk, cree_par=request.user)
    
    if request.method == 'POST':
        try:
            montant = int(request.POST['montant'])
            karfa.restituer(montant, request.POST.get('note', ''))
            messages.success(request, f"Restitution de {montant} GNF effectuée")
        except Exception as e:
            messages.error(request, f"Erreur : {str(e)}")
    
    return redirect('karfa:detail_karfa', pk=pk)

import csv
from django.http import HttpResponse

@login_required
def ajouter_retirer_karfa(request, pk):
    karfa = get_object_or_404(Karfa, pk=pk, cree_par=request.user)
    if request.method == 'POST':
        type_mvt = request.POST['type_mouvement']
        montant = int(request.POST['montant'])
        motif = request.POST.get('motif', '').strip()

        if type_mvt == 'AJOUT':
            karfa.montant_actuel += montant
            type_mouvement = 'AJOUT'
            note = motif if motif else f"Ajout de {montant} GNF"
            
            if karfa.montant_actuel > 0:
                karfa.statut = 'ACTIF'
        else:
            if montant > karfa.montant_actuel:
                messages.error(request, "Montant trop élevé")
                return redirect('karfa:detail_karfa', pk=pk)
            karfa.montant_actuel -= montant
            type_mouvement = 'RETRAIT'
            note = motif if motif else f"Retrait de {montant} GNF"

            if karfa.montant_actuel == 0:
                karfa.statut = 'RENDU_TOTAL'
                from django.utils import timezone
                karfa.date_rendu_total = timezone.now()
            else:
                karfa.statut = 'PARTIELLEMENT_RENDU'

        karfa.save()

        MouvementKarfa.objects.create(
            karfa=karfa,
            type=type_mouvement,
            montant=montant,
            note=note,
            solde_apres=karfa.montant_actuel,
            cree_par=request.user
        )

        messages.success(request, f"Opération effectuée : {note}")
        return redirect('karfa:detail_karfa', pk=pk)

@login_required
def toutes_operations(request):
    operations = MouvementKarfa.objects.filter(karfa__cree_par=request.user).order_by('-date')
    return render(request, 'modules/karfa/operations.html', {'operations': operations})
