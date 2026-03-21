from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max, F
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import json
import random
import string
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
import time
from modules.core.models import Profil, PinUtilisateur

from modules.comptes.models import CompteArgent, CompteOr
from modules.core.services.prix_or_service import get_latest_prix_or
from modules.karfa.models import Karfa
from modules.dettes.models import Dette, Remboursement
from modules.karfa.models import MouvementKarfa

@login_required
def profil_view(request):
    """Affiche le profil de l'utilisateur connecté."""
    try:
        profil = Profil.objects.get(user=request.user)
    except Profil.DoesNotExist:
        from django.utils.crypto import get_random_string
        profil = Profil.objects.create(
            user=request.user,
            identifiant=get_random_string(8).upper(),
            telephone='',
            question_secrete='Non définie',
            reponse_secrete='Non définie'
        )
    
    return render(request, 'modules/core/profil.html', {
        'profil': profil,
        'user': request.user,
        'mode': 'view',
    })

@login_required
def modifier_profil(request):
    """Modifie le nom et prénom de l'utilisateur connecté."""
    if request.method == 'POST':
        prenom = request.POST.get('prenom', '').strip()
        nom = request.POST.get('nom', '').strip()
        if prenom and nom:
            request.user.first_name = prenom
            request.user.last_name = nom
            request.user.save()
            messages.success(request, "Profil mis à jour avec succès.")
        else:
            messages.error(request, "Le nom et le prénom ne peuvent pas être vides.")
        return redirect('core:profil')
    return redirect('core:profil')

@login_required
def changer_mot_de_passe(request):
    """Gère le changement de mot de passe via AJAX avec sécurité."""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if 'pwd_error_count' not in request.session:
            request.session['pwd_error_count'] = 0

        if not request.user.check_password(old_password):
            request.session['pwd_error_count'] += 1
            attempts_left = 3 - request.session['pwd_error_count']
            
            if request.session['pwd_error_count'] >= 3:
                del request.session['pwd_error_count']
                logout(request)
                return JsonResponse({
                    'success': False, 
                    'error': 'Compte verrouillé suite à plusieurs tentatives.',
                    'redirect_url': '/login/'
                })
            
            return JsonResponse({
                'success': False, 
                'field': 'old_password',
                'error': f"Ancien mot de passe incorrect ({attempts_left} essais restants)."
            })

        if new_password != confirm_password:
            return JsonResponse({
                'success': False, 
                'field': 'confirm_password',
                'error': "Les nouveaux mots de passe ne correspondent pas."
            })

        if len(new_password) < 8:
            return JsonResponse({
                'success': False, 
                'field': 'new_password',
                'error': "Le mot de passe doit contenir au moins 8 caractères."
            })

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        request.session['pwd_error_count'] = 0

        messages.success(request, "Mot de passe mis à jour avec succès.")
        return JsonResponse({'success': True, 'message': "Profil sécurisé !"})

@login_required
@require_POST
@csrf_protect
def changer_pin(request):
    """Gère le changement de code PIN avec optimisation de vitesse et sécurité."""
    start_time = time.time()
    try:
        data = json.loads(request.body)
        ancien = data.get('ancien')
        nouveau = data.get('nouveau')
        confirmation = data.get('confirmation')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Données invalides'}, status=400)

    # Sécurité lockout (Session)
    if 'pin_error_count' not in request.session:
        request.session['pin_error_count'] = 0

    # Optimisation : select_related pour récupérer l'user en une seule requête
    try:
        pin_obj = PinUtilisateur.objects.select_related('user').get(user=request.user)
    except PinUtilisateur.DoesNotExist:
        return JsonResponse({'error': "Erreur PIN."}, status=404)

    # 1. Validation de l'ancien PIN
    if not pin_obj.verifier_pin(ancien):
        request.session['pin_error_count'] += 1
        attempts_left = 3 - request.session['pin_error_count']
        
        duration = (time.time() - start_time) * 1000
        if request.session['pin_error_count'] >= 3:
            del request.session['pin_error_count']
            logout(request)
            return JsonResponse({
                'error': 'Compte déconnecté pour sécurité.',
                'redirect_url': '/login/',
                'duration': f"{duration:.2f}ms"
            }, status=403)
        
        return JsonResponse({
            'error': f"Ancien PIN incorrect ({attempts_left} restants).",
            'duration': f"{duration:.2f}ms"
        }, status=400)

    # 2. Vérification de correspondance
    if nouveau != confirmation:
        return JsonResponse({'error': "Les PIN ne correspondent pas."}, status=400)

    # 3. Validation de format
    if not nouveau or len(nouveau) not in [4, 6] or not nouveau.isdigit():
        return JsonResponse({'error': "Le PIN doit comporter 4 ou 6 chiffres."}, status=400)

    # 4. Succès optimisé
    pin_obj.set_pin(nouveau)
    request.session['pin_error_count'] = 0 # reset
    
    duration = (time.time() - start_time) * 1000
    messages.success(request, "Code PIN mis à jour avec succès.")
    return JsonResponse({
        'success': True, 
        'message': "PIN modifié avec succès",
        'duration': f"{duration:.2f}ms"
    })
