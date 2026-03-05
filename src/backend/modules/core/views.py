from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('karfa_list')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
            return render(request, 'auth/login.html', {'error': "Identifiants invalides"})
    return render(request, 'auth/login.html')

from django.contrib.auth.decorators import login_required
from django.db.models import Sum

@login_required
def accueil(request):
    # Imports locaux pour éviter potentiellement des circularités avec d'autres modules
    from modules.comptes.models import CompteArgent, CompteOr, MouvementCompte
    from modules.core.services.prix_or_service import get_latest_prix_or
    from modules.dettes.models import Dette, Remboursement
    from modules.karfa.models import Karfa, MouvementKarfa

    # 1. Patrimoine Net Total et Total des Comptes
    total_liquidites = CompteArgent.objects.filter(archive=False).aggregate(total=Sum('solde'))['total'] or 0
    prix_or = get_latest_prix_or()
    total_or_gnf = 0
    total_poids_or = CompteOr.objects.filter(archive=False).aggregate(total=Sum('poids_grammes'))['total'] or 0
    
    if prix_or:
        total_or_gnf = total_poids_or * prix_or.prix_gramme
        prix_or_val = prix_or.prix_gramme
    else:
        prix_or_val = 0

    total_comptes = total_liquidites + total_or_gnf

    # Karfa actifs
    total_karfa = Karfa.objects.filter(
        archive=False,
        statut__in=['ACTIF', 'PARTIELLEMENT_RENDU']
    ).aggregate(total=Sum('montant_actuel'))['total'] or 0

    # Créances (On me doit)
    total_creances = Dette.objects.filter(
        sens='ON_ME_DOIT',
        archive=False
    ).aggregate(total=Sum('montant_restant'))['total'] or 0

    # Dettes (Je dois)
    total_dettes = Dette.objects.filter(
        sens='JE_DOIS',
        archive=False
    ).aggregate(total=Sum('montant_restant'))['total'] or 0

    patrimoine_total = total_comptes + total_karfa + total_creances - total_dettes

    # 3 dernières opérations
    ops = []
    
    for mk in MouvementKarfa.objects.all().order_by('-date')[:3]:
        ops.append({
            'type_name': f"Karfa {mk.get_type_display()}",
            'personne': mk.karfa.beneficiaire,
            'montant': mk.montant,
            'date': mk.date,
            'color': '#f59e0b',
            'icon': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/></svg>'
        })
        
    for d in Dette.objects.all().order_by('-date_creation')[:3]:
        ops.append({
            'type_name': "Créance" if d.sens == 'ON_ME_DOIT' else "Nouvelle dette",
            'personne': d.personne,
            'montant': d.montant,
            'date': d.date_creation,
            'color': '#3b82f6' if d.sens == 'ON_ME_DOIT' else '#ef4444',
            'icon': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><path d="M10 9H8"/></svg>'
        })
        
    for r in Remboursement.objects.all().order_by('-date')[:3]:
        ops.append({
            'type_name': r.get_type_display(),
            'personne': r.dette.personne,
            'montant': r.montant,
            'date': r.date,
            'color': '#10b981',
            'icon': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>'
        })
        
    for mc in MouvementCompte.objects.select_related('compte_argent', 'compte_or').order_by('-date')[:3]:
        compte = mc.compte_argent or mc.compte_or
        ops.append({
            'type_name': f"Compte {mc.get_type_display()}",
            'personne': compte.nom if compte else "Mon Compte",
            'montant': int(mc.montant),
            'date': mc.date,
            'color': '#8b5cf6',
            'icon': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3 4 7l4 4"/><path d="M4 7h16"/><path d="m16 21 4-4-4-4"/><path d="M20 17H4"/></svg>'
        })

    ops.sort(key=lambda x: x['date'], reverse=True)
    recentes_ops = ops[:3]

    return render(request, 'core/accueil.html', {
        'patrimoine_total': patrimoine_total,
        'total_comptes': total_comptes,
        'prix_or': prix_or_val,
        'recentes_ops': recentes_ops
    })

@login_required
def toutes_operations(request):
    from modules.comptes.models import MouvementCompte
    from modules.dettes.models import Dette, Remboursement
    from modules.karfa.models import MouvementKarfa

    # Fetching up to 100 recent operations from each module to construct a comprehensive list
    ops = []
    
    for mk in MouvementKarfa.objects.all().order_by('-date')[:100]:
        ops.append({
            'type_name': f"Karfa {mk.get_type_display()}",
            'personne': mk.karfa.beneficiaire,
            'montant': mk.montant,
            'date': mk.date,
            'color': '#f59e0b',
            'icon': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/></svg>'
        })
        
    for d in Dette.objects.all().order_by('-date_creation')[:100]:
        ops.append({
            'type_name': "Créance" if d.sens == 'ON_ME_DOIT' else "Nouvelle dette",
            'personne': d.personne,
            'montant': d.montant,
            'date': d.date_creation,
            'color': '#3b82f6' if d.sens == 'ON_ME_DOIT' else '#ef4444',
            'icon': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>'
        })
        
    for r in Remboursement.objects.all().order_by('-date')[:100]:
        ops.append({
            'type_name': r.get_type_display(),
            'personne': r.dette.personne,
            'montant': r.montant,
            'date': r.date,
            'color': '#10b981',
            'icon': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>'
        })
        
    for mc in MouvementCompte.objects.select_related('compte_argent', 'compte_or').order_by('-date')[:100]:
        compte = mc.compte_argent or mc.compte_or
        ops.append({
            'type_name': f"Compte {mc.get_type_display()}",
            'personne': compte.nom if compte else "Mon Compte",
            'montant': int(mc.montant),
            'date': mc.date,
            'color': '#8b5cf6',
            'icon': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3 4 7l4 4"/><path d="M4 7h16"/><path d="m16 21 4-4-4-4"/><path d="M20 17H4"/></svg>'
        })

    ops.sort(key=lambda x: x['date'], reverse=True)
    toutes_ops = ops[:200]

    return render(request, 'core/toutes_operations.html', {
        'operations': toutes_ops
    })