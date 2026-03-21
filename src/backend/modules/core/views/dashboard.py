from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max, F, Q
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import json
import random
import string
from modules.core.models import Profil

from modules.comptes.models import CompteArgent, CompteOr
from modules.core.services.prix_or_service import get_latest_prix_or
from modules.karfa.models import Karfa
from modules.dettes.models import Dette, Remboursement
from modules.karfa.models import MouvementKarfa

@login_required
def accueil(request):
    from modules.comptes.models import CompteArgent, CompteOr, MouvementCompte
    from modules.core.services.prix_or_service import get_latest_prix_or
    from modules.dettes.models import Dette, Remboursement
    from modules.karfa.models import Karfa, MouvementKarfa

    user = request.user

    # 1. Calculs des Soldes (Filtrés par utilisateur)
    total_liquidites = CompteArgent.objects.filter(cree_par=user, archive=False).exclude(type_compte='DETTE').aggregate(total=Sum('solde'))['total'] or 0
    prix_or = get_latest_prix_or(user)
    total_poids_or = CompteOr.objects.filter(cree_par=user, archive=False).aggregate(total=Sum('poids_grammes'))['total'] or 0
    
    total_or_gnf = 0
    prix_or_val = 0
    if prix_or:
        total_or_gnf = total_poids_or * prix_or.prix_gramme
        prix_or_val = prix_or.prix_gramme

    total_comptes = total_liquidites + total_or_gnf

    # Karfa actifs (Filtrés)
    total_karfa = Karfa.objects.filter(cree_par=user, archive=False).aggregate(total=Sum('montant_actuel'))['total'] or 0

    # Créances & Dettes (Filtrées)
    total_creances = Dette.objects.filter(cree_par=user, sens='ON_ME_DOIT', archive=False).aggregate(total=Sum('montant_restant'))['total'] or 0
    total_dettes = Dette.objects.filter(cree_par=user, sens='JE_DOIS', archive=False).aggregate(total=Sum('montant_restant'))['total'] or 0

    # Nouveaux indicateurs
    patrimoine_net = total_comptes + total_creances - total_dettes
    total_cash = total_liquidites + total_karfa

    # 2. Dernières opérations (Filtrées par utilisateur)
    ops = []
    
    # Karfa
    for mk in MouvementKarfa.objects.filter(cree_par=user).order_by('-date')[:3]:
        ops.append({
            'type_name': f"Karfa {mk.get_type_display()}",
            'personne': mk.karfa.beneficiaire,
            'montant': mk.montant,
            'unite': 'GNF',
            'date': mk.date,
            'color': '#f59e0b',
            'icon': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/></svg>'
        })
    
    # Dettes
    for d in Dette.objects.filter(cree_par=user).order_by('-date_creation')[:3]:
        ops.append({
            'type_name': "Créance" if d.sens == 'ON_ME_DOIT' else "Dette",
            'personne': d.personne,
            'montant': d.montant,
            'unite': 'GNF',
            'date': d.date_creation,
            'color': '#3b82f6' if d.sens == 'ON_ME_DOIT' else '#ef4444',
            'icon': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><path d="M10 9H8"/></svg>'
        })
        
    # Remboursements
    for r in Remboursement.objects.filter(dette__cree_par=user).order_by('-date')[:3]:
        ops.append({
            'type_name': r.get_type_display(),
            'personne': r.dette.personne,
            'montant': r.montant,
            'unite': 'GNF',
            'date': r.date,
            'color': '#10b981',
            'icon': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>'
        })
        
    # Mouvements Comptes
    for mc in MouvementCompte.objects.filter(Q(compte_argent__cree_par=user) | Q(compte_or__cree_par=user)).order_by('-date')[:3]:
        compte = mc.compte_argent or mc.compte_or
        is_or_move = mc.compte_or is not None
        ops.append({
            'type_name': f"Compte {mc.get_type_display()}",
            'personne': compte.nom if compte else "Mon Compte",
            'montant': mc.montant,
            'unite': 'g' if is_or_move else 'GNF',
            'date': mc.date,
            'color': '#8b5cf6',
            'icon': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3 4 7l4 4"/><path d="M4 7h16"/><path d="m16 21 4-4-4-4"/><path d="M20 17H4"/></svg>'
        })

    ops.sort(key=lambda x: x['date'], reverse=True)
    recentes_ops = ops[:3]

    return render(request, 'modules/core/accueil.html', {
        'patrimoine_net': patrimoine_net,
        'total_cash': total_cash,
        'prix_or': prix_or_val,
        'recentes_ops': recentes_ops
    })

@login_required
def toutes_operations(request):
    from modules.comptes.models import MouvementCompte
    from modules.dettes.models import Dette, Remboursement
    from modules.karfa.models import MouvementKarfa
    user = request.user
    ops = []
    
    # Karfa
    for mk in MouvementKarfa.objects.filter(cree_par=user).order_by('-date')[:100]:
        ops.append({
            'type_name': f"Karfa {mk.get_type_display()}",
            'personne': mk.karfa.beneficiaire,
            'montant': mk.montant,
            'unite': 'GNF',
            'date': mk.date,
            'color': '#f59e0b',
            'icon': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/></svg>'
        })
    
    # Dettes/Créances
    for d in Dette.objects.filter(cree_par=user).order_by('-date_creation')[:100]:
        ops.append({
            'type_name': "Créance" if d.sens == 'ON_ME_DOIT' else "Dette",
            'personne': d.personne,
            'montant': d.montant,
            'unite': 'GNF',
            'date': d.date_creation,
            'color': '#3b82f6' if d.sens == 'ON_ME_DOIT' else '#ef4444',
            'icon': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><path d="M10 9H8"/></svg>'
        })
    
    # Remboursements/Encaissements
    for r in Remboursement.objects.filter(dette__cree_par=user).order_by('-date')[:100]:
        ops.append({
            'type_name': r.get_type_display(),
            'personne': r.dette.personne,
            'montant': r.montant,
            'unite': 'GNF',
            'date': r.date,
            'color': '#10b981',
            'icon': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>'
        })
    
    # Mouvements Comptes
    for mc in MouvementCompte.objects.filter(Q(compte_argent__cree_par=user) | Q(compte_or__cree_par=user)).order_by('-date')[:100]:
        compte = mc.compte_argent or mc.compte_or
        is_or_move = mc.compte_or is not None
        ops.append({
            'type_name': f"Compte {mc.get_type_display()}",
            'personne': compte.nom if compte else "Mon Compte",
            'montant': mc.montant,
            'unite': 'g' if is_or_move else 'GNF',
            'date': mc.date,
            'color': '#8b5cf6',
            'icon': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3 4 7l4 4"/><path d="M4 7h16"/><path d="m16 21 4-4-4-4"/><path d="M20 17H4"/></svg>'
        })
        
    ops.sort(key=lambda x: x['date'], reverse=True)
    return render(request, 'modules/core/toutes_operations.html', {'operations': ops})


# --- PWA ---
def offline_view(request):
    return render(request, 'offline.html')

@login_required
def notifications_view(request):
    """Vue pour afficher toutes les notifications d'un utilisateur."""
    from modules.core.models import Notification
    notifications = Notification.objects.filter(user=request.user)
    
    # Marquer tout comme lu quand on visite la page
    notifications.filter(is_read=False).update(is_read=True)
    
    return render(request, 'modules/core/notifications_list.html', {
        'notifications': notifications
    })

def service_worker(request):
    from django.http import HttpResponse
    import os
    from django.conf import settings
    sw_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'static', 'sw.js')
    with open(sw_path, 'r') as f:
        return HttpResponse(f.read(), content_type='application/javascript')

def manifest_view(request):
    from django.http import HttpResponse
    import os
    from django.conf import settings
    manifest_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'static', 'manifest.json')
    with open(manifest_path, 'r') as f:
        return HttpResponse(f.read(), content_type='application/json')
