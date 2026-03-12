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
def creer_compte(request):
    """Vue pour la création d'un nouveau compte (Argent ou Or)."""
    if request.method == 'POST':
        nature = request.POST.get('nature')
        
        if nature == 'argent':
            form = CompteArgentForm(request.POST, user=request.user)
            if form.is_valid():
                compte = form.save(commit=False)
                compte.cree_par = request.user
                compte.save()
                messages.success(request, f"Compte Argent '{compte.nom}' créé avec succès.")
                return redirect('comptes:liste_comptes')
            else:
                for error in form.errors.values():
                    messages.error(request, error)
        elif nature == 'or':
            form = CompteOrForm(request.POST)
            if form.is_valid():
                compte = form.save(commit=False)
                compte.cree_par = request.user
                compte.save()
                messages.success(request, f"Compte Or '{compte.nom}' créé avec succès.")
                return redirect('comptes:liste_comptes')
            else:
                # Get the validation error messages
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}" if field != '__all__' else error)
        else:
            messages.error(request, "Nature du compte inconnue.")
            
    return render(request, 'modules/comptes/form.html')

@login_required
def modifier_compte(request, id):
    """Modifier les infos de base d'un compte."""
    type_param = request.GET.get('type')
    
    if type_param == 'or':
        compte = get_object_or_404(CompteOr, id=id, cree_par=request.user)
        type_compte = 'or'
        form_class = CompteOrForm
    elif type_param == 'argent':
        compte = get_object_or_404(CompteArgent, id=id, cree_par=request.user)
        type_compte = 'argent'
        form_class = CompteArgentForm
    else:
        # Fallback
        try:
            compte = CompteArgent.objects.get(id=id, cree_par=request.user)
            type_compte = 'argent'
            form_class = CompteArgentForm
        except CompteArgent.DoesNotExist:
            compte = get_object_or_404(CompteOr, id=id, cree_par=request.user)
            type_compte = 'or'
            form_class = CompteOrForm
        
    if request.method == 'POST':
        if type_compte == 'argent':
            form = form_class(request.POST, instance=compte, user=request.user)
        else:
            form = form_class(request.POST, instance=compte)
            
        if form.is_valid():
            form.save()
            messages.success(request, f"Compte '{compte.nom}' mis à jour.")
            return redirect(f"{redirect('comptes:detail_compte', id=id).url}?type={type_compte}")
    else:
        if type_compte == 'argent':
            form = form_class(instance=compte, user=request.user)
        else:
            form = form_class(instance=compte)
        
    return render(request, 'modules/comptes/form.html', {
        'form': form,
        'compte': compte,
        'modifier': True,
        'nature': type_compte
    })
