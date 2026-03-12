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
def liste_archives_comptes(request):
    """Liste des comptes archivés du USER."""
    archives_argent = CompteArgent.objects.filter(cree_par=request.user, archive=True)
    archives_or = CompteOr.objects.filter(cree_par=request.user, archive=True)
    
    # Marquage pour distinguer les types dans le template
    for a in archives_argent:
        a.nature = 'argent'
    for o in archives_or:
        o.nature = 'or'
        
    from itertools import chain
    from django.utils.timezone import now
    
    archives = sorted(
        chain(archives_argent, archives_or),
        key=lambda x: x.date_archivage if x.date_archivage else now(),
        reverse=True
    )
    
    return render(request, 'modules/comptes/archives.html', {
        'comptes_archives': archives,
    })

@login_required
def archiver_compte(request, id):
    """Archive un compte."""
    type_param = request.GET.get('type')
    if type_param == 'or':
        compte = get_object_or_404(CompteOr, id=id, cree_par=request.user)
    elif type_param == 'argent':
        compte = get_object_or_404(CompteArgent, id=id, cree_par=request.user)
    else:
        try:
            compte = CompteArgent.objects.get(id=id, cree_par=request.user)
        except CompteArgent.DoesNotExist:
            compte = get_object_or_404(CompteOr, id=id, cree_par=request.user)
    
    compte.archive = True
    compte.date_archivage = timezone.now()
    compte.save()
    messages.success(request, f"Le compte '{compte.nom}' a été archivé.")
    return redirect('comptes:liste_comptes')

@login_required
def desarchiver_compte(request, id):
    """Désarchive un compte."""
    type_param = request.GET.get('type')
    est_argent = False
    
    if type_param == 'or':
        compte = get_object_or_404(CompteOr, id=id, cree_par=request.user)
    elif type_param == 'argent':
        compte = get_object_or_404(CompteArgent, id=id, cree_par=request.user)
        est_argent = True
    else:
        try:
            compte = CompteArgent.objects.get(id=id, cree_par=request.user)
            est_argent = True
        except CompteArgent.DoesNotExist:
            compte = get_object_or_404(CompteOr, id=id, cree_par=request.user)
    
    compte.archive = False
    compte.date_archivage = None
    compte.save()
    messages.success(request, f"Le compte '{compte.nom}' a été désarchivé.")
    return redirect(f"{redirect('comptes:detail_compte', id=id).url}?type={'argent' if est_argent else 'or'}")

@login_required
def supprimer_compte(request, id):
    """Supprime un compte définitivement."""
    type_param = request.GET.get('type')
    est_argent = False
    
    if type_param == 'or':
        compte = get_object_or_404(CompteOr, id=id, cree_par=request.user)
        solde_zero = (compte.poids_grammes == 0)
    elif type_param == 'argent':
        compte = get_object_or_404(CompteArgent, id=id, cree_par=request.user)
        est_argent = True
        solde_zero = (compte.solde == 0)
    else:
        try:
            compte = CompteArgent.objects.get(id=id, cree_par=request.user)
            est_argent = True
            solde_zero = (compte.solde == 0)
        except CompteArgent.DoesNotExist:
            compte = get_object_or_404(CompteOr, id=id, cree_par=request.user)
            solde_zero = (compte.poids_grammes == 0)
    
    if not compte.archive:
        messages.error(request, "Impossible de supprimer un compte actif. Archivez-le d'abord.")
        return redirect(f"{redirect('comptes:detail_compte', id=id).url}?type={'argent' if est_argent else 'or'}")
    
    if not solde_zero:
        messages.error(request, "Le solde ou poids doit être à zéro pour supprimer le compte.")
        return redirect(f"{redirect('comptes:detail_compte', id=id).url}?type={'argent' if est_argent else 'or'}")
    
    nom = compte.nom
    compte.delete()
    messages.success(request, f"Le compte '{nom}' a été définitivement supprimé.")
    return redirect('comptes:liste_archives')
