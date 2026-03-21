from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
from ..models.pin import PinUtilisateur
from ..models.profil import Profil

@login_required
def definir_pin(request):
    """Permet à l'utilisateur de définir son code PIN initial (4 ou 6 chiffres)."""
    pin_config, created = PinUtilisateur.objects.get_or_create(user=request.user)
    
    if pin_config.pin_hash and not request.session.get('resetting_pin'):
        return redirect('core:dashboard')

    if request.method == 'POST':
        pin = request.POST.get('pin')
        confirmpin = request.POST.get('confirmpin')
        
        if not pin or len(pin) not in [4, 6] or not pin.isdigit():
            messages.error(request, "Le code PIN doit être composé de 4 ou 6 chiffres.")
        elif pin != confirmpin:
            messages.error(request, "Les deux codes saisis ne sont pas identiques.")
        else:
            pin_config.set_pin(pin)
            request.session['pin_valide'] = True
            
            # Nettoyer le flag de reset
            if 'resetting_pin' in request.session:
                del request.session['resetting_pin']
                
            messages.success(request, "Votre code PIN a été configuré avec succès.")
            response = redirect('core:dashboard')
            # Marquer le navigateur comme ayant validé le PIN
            response.set_cookie('pin_browser_session', '1', expires=None) # Expire à la fermeture
            return response
            
    return render(request, 'modules/pin/definir.html', {
        'deja_defini': bool(pin_config.pin_hash)
    })

@login_required
def verifier_pin(request):
    """Écran de déverrouillage de l'application via le code PIN."""
    try:
        pin_config = PinUtilisateur.objects.get(user=request.user)
    except PinUtilisateur.DoesNotExist:
        return redirect('core:definir_pin')

    if not pin_config.pin_hash:
        return redirect('core:definir_pin')

    # Si déjà valide pour ce navigateur, pas besoin de rester ici
    if request.session.get('pin_valide') and request.COOKIES.get('pin_browser_session'):
        return redirect('core:dashboard')

    if request.method == 'POST':
        pin = request.POST.get('pin', '')
        
        if pin_config.est_bloque():
            messages.error(request, "Compte bloqué temporairement suite à 3 échecs.")
            logout(request) # Déconnexion forcée selon spécifications
            return redirect('core:login')

        if pin_config.verifier_pin(pin):
            # Succès
            pin_config.reset_tentatives()
            request.session['pin_valide'] = True
            
            response = redirect('core:dashboard')
            # Marquer le navigateur (session éphémère)
            response.set_cookie('pin_browser_session', '1', expires=None) 
            return response
        else:
            # Échec
            pin_config.incrementer_tentatives()
            tentatives = pin_config.tentatives
            
            if tentatives >= 3:
                messages.error(request, "Sécurité : 3 échecs de PIN. Vous avez été déconnecté.")
                logout(request)
                return redirect('core:login')
            else:
                messages.error(request, f"Code PIN incorrect ({tentatives}/3).")
                
    return render(request, 'modules/pin/verifier.html', {
        'bloque': pin_config.est_bloque(),
        'tentatives': pin_config.tentatives
    })

@login_required
def reinitialiser_pin(request):
    """Réinitialise le PIN via le mot de passe du compte."""
    if request.method == 'POST':
        password = request.POST.get('password')
        if request.user.check_password(password):
            pin_config, _ = PinUtilisateur.objects.get_or_create(user=request.user)
            pin_config.pin_hash = ""
            pin_config.save()
            
            if 'pin_valide' in request.session:
                del request.session['pin_valide']
            
            request.session['resetting_pin'] = True
            messages.info(request, "Veuillez choisir votre nouveau code PIN.")
            return redirect('core:definir_pin')
        else:
            messages.error(request, "Mot de passe incorrect.")
            
    return render(request, 'modules/pin/reinitialiser.html')

def pin_oublie(request):
    """Réinitialisation du PIN quand l'utilisateur l'a oublié."""
    # S'assurer que l'utilisateur est connecté pour éviter toute faille
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': "Vous devez être connecté pour réinitialiser votre PIN."})

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'verifier_identite':
            identifier = request.POST.get('identifier', '').strip()
            password = request.POST.get('password')
            
            if not identifier or not password:
                return JsonResponse({'success': False, 'message': "Tous les champs sont requis."})
                
            # Nettoyer l'identifiant numérique pour la comparaison
            identifier_clean = identifier.replace(' ', '')
            
            # Utiliser directement le profil de l'utilisateur connecté
            user = request.user
            try:
                profil = user.profil
                
                # Vérifier que l'identifiant correspond bien à cet utilisateur
                if identifier not in [profil.identifiant, profil.telephone] and identifier_clean != profil.telephone:
                    return JsonResponse({'success': False, 'message': "L'identifiant ou le numéro de téléphone ne correspond pas à votre compte."})
                
                # Vérifier le mot de passe de l'utilisateur connecté
                if user.check_password(password):
                    # Stocker l'UID en session pour sécuriser la suite
                    request.session['reset_pin_user_id'] = user.id
                    return JsonResponse({
                        'success': True, 
                        'message': f"Identité confirmée : {user.first_name} {user.last_name}"
                    })
                else:
                    return JsonResponse({'success': False, 'message': "Mot de passe incorrect."})
            except Exception:
                return JsonResponse({'success': False, 'message': "Erreur lors de la récupération de votre profil."})
        elif action == 'reinitialiser':
            user_id = request.session.get('reset_pin_user_id')
            if not user_id:
                return JsonResponse({'success': False, 'message': "Session expirée. Veuillez recommencer."})
            
            new_pin = request.POST.get('new_pin')
            confirm_pin = request.POST.get('confirm_pin')
            
            if not new_pin or new_pin != confirm_pin:
                return JsonResponse({'success': False, 'message': "Les codes PIN ne correspondent pas."})
                
            if len(new_pin) not in [4, 6] or not new_pin.isdigit():
                return JsonResponse({'success': False, 'message': "Le code PIN doit comporter 4 ou 6 chiffres."})
            
            try:
                user = User.objects.get(id=user_id)
                pin_config, _ = PinUtilisateur.objects.get_or_create(user=user)
                pin_config.set_pin(new_pin)
                
                # Nettoyage
                if 'reset_pin_user_id' in request.session:
                    del request.session['reset_pin_user_id']
                if 'pin_valide' in request.session:
                    del request.session['pin_valide']
                
                messages.success(request, "Votre code PIN a été réinitialisé avec succès.")
                return JsonResponse({'success': True, 'redirect_url': reverse('core:verifier_pin')})
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': "Erreur technique : utilisateur introuvable."})

    return render(request, 'modules/pin/pin_oublie.html')
