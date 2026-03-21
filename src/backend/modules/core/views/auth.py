from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth import authenticate, login, logout
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
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
import re

from modules.core.models import Profil, PinUtilisateur
from modules.core.models.question_securite import QuestionSecuriteManager

from modules.comptes.models import CompteArgent, CompteOr
from modules.core.services.prix_or_service import get_latest_prix_or
from modules.karfa.models import Karfa
from modules.dettes.models import Dette, Remboursement
from modules.karfa.models import MouvementKarfa

def login_view(request):
    if request.method == 'POST':
        login_mode = request.POST.get('login_mode')
        login_value = request.POST.get('login_value', '').strip()
        password = request.POST.get('password')
        
        user = None
        try:
            if login_mode == 'tel':
                tel_clean = login_value.replace(" ", "")
                profil = Profil.objects.filter(telephone=tel_clean).first()
                if profil:
                    user = profil.user
            else:
                profil = Profil.objects.filter(identifiant=login_value).first()
                if profil:
                    user = profil.user
                else:
                    user = User.objects.filter(email=login_value).first()
            
            if user:
                authenticated_user = authenticate(request, username=user.username, password=password)
                if authenticated_user:
                    login(request, authenticated_user)
                    # Forcer la persistance de la session à 30 jours (ou selon settings)
                    from django.conf import settings
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                    request.session.modified = True
                    
                    # Réinitialiser les tentatives et invalider la session PIN actuelle
                    # pour forcer la vérification immédiate après le login
                    pin_config, _ = PinUtilisateur.objects.get_or_create(user=authenticated_user)
                    pin_config.reset_tentatives()
                    request.session['pin_valide'] = False
                    
                    # Forcer la redirection selon l'existence d'un PIN
                    pin_exists = PinUtilisateur.objects.filter(user=authenticated_user).exists()
                    if pin_exists:
                        # PIN existe déjà -> vérifier
                        return redirect('core:verifier_pin')
                    else:
                        # PIN n'existe pas -> définir
                        return redirect('core:definir_pin')
            
            messages.error(request, "Identifiants ou mot de passe incorrect")
        except Exception as e:
            messages.error(request, f"Erreur de connexion : {str(e)}")

    return render(request, 'modules/core/login.html')

def logout_view(request):
    logout(request)
    return redirect('core:login')

def register_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        prenom = request.POST.get('prenom', '')
        nom = request.POST.get('nom', '')
        
        if password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas")
            return render(request, 'modules/core/register.html')
            
        try:
            validate_password(password)
        except ValidationError as e:
            for message in e.messages:
                messages.error(request, message)
            return render(request, 'modules/core/register.html')
            
        identifiant = generer_identifiant(nom, prenom)
        user = User.objects.create_user(
            username=identifiant,
            password=password,
            first_name=prenom,
            last_name=nom
        )
        Profil.objects.create(user=user, identifiant=identifiant)
        login(request, user)
        request.session['new_user_id'] = identifiant
        return redirect('core:registration_success')
        
    return render(request, 'core/register.html')

def register_wizard(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '')
            password = data.get('password')
            prenom = data.get('prenom', '')
            nom = data.get('nom', '')
            telephone = data.get('telephone', '').replace(" ", "")
            question = data.get('question', '')
            reponse = data.get('reponse', '')
            
            try:
                validate_password(password)
            except ValidationError as e:
                return JsonResponse({'success': False, 'error': " ".join(e.messages)})
            
            identifiant = generer_identifiant(nom, prenom)
            user = User.objects.create_user(
                username=identifiant, email=email, password=password,
                first_name=prenom, last_name=nom
            )
            Profil.objects.create(
                user=user, identifiant=identifiant, telephone=telephone,
                question_secrete=question, reponse_secrete=reponse
            )
            login(request, user)
            return JsonResponse({'success': True, 'user_id': identifiant})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    return render(request, 'modules/core/register_wizard.html')

def registration_success(request):
    user_id = request.session.get('new_user_id', 'Inconnu')
    return render(request, 'modules/core/registration_success.html', {'user_id': user_id})

def generer_identifiant(nom, prenom):
    nom = nom.strip().replace(" ", "")
    prenom = prenom.strip().replace(" ", "")
    partie_nom = nom[-2:].upper() if len(nom) >= 2 else nom.upper()
    partie_prenom = prenom[:2].upper() if len(prenom) >= 2 else prenom.upper()
    base = partie_nom + partie_prenom
    while True:
        chiffres = ''.join(random.choices(string.digits, k=6))
        identifiant = base + chiffres
        if not Profil.objects.filter(identifiant=identifiant).exists():
            return identifiant

# --- RÉINITIALISATION DE MOT DE PASSE ---

def password_reset_choice(request):
    """Étape 1 : Choix entre ID/Email ou Téléphone."""
    return render(request, 'modules/core/auth/password_reset_choice.html')

def password_reset_identifier(request):
    """Étape 2 : Saisie de l'identifiant selon la méthode choisie.
    
    Méthodes possibles (champ POST 'method') :
      - 'email'  → cherche un user par email et envoie un lien de réinitialisation
      - 'id'     → cherche par identifiant interne, redirige vers question secrète
      - 'tel'    → cherche par téléphone, redirige vers question secrète
    """
    mode = request.GET.get('mode', 'tel')

    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        mode = request.POST.get('mode', 'tel')
        method = request.POST.get('method', 'tel')  # 'email', 'id' ou 'tel'

        user = None

        if method == 'email':
            # Recherche strictement par email
            user = User.objects.filter(email=identifier).first()
        elif method == 'tel':
            tel_clean = identifier.replace(" ", "")
            profil = Profil.objects.filter(telephone=tel_clean).first()
            if profil:
                user = profil.user
        else:
            # method == 'id' : recherche par identifiant interne uniquement
            profil = Profil.objects.filter(identifiant=identifier).first()
            if profil:
                user = profil.user

        if user:
            if method == 'email':
                # La récupération par email est temporairement indisponible
                return render(request, 'modules/core/auth/password_reset_choice.html', {
                    'mode': mode,
                    'show_email_unavailable': True,
                })

            else:
                # method == 'id' ou 'tel' → Question secrète
                request.session['reset_user_id'] = user.id
                return redirect('core:password_reset_question')

        # Aucun compte trouvé
        messages.error(request, "Aucun compte trouvé avec ces informations.")
        return render(request, 'modules/core/auth/password_reset_choice.html', {
            'mode': mode,
            'identifier': identifier,
        })

    return render(request, 'modules/core/auth/password_reset_choice.html', {'mode': mode})

def password_reset_question(request):
    """Étape 3 : Vérification de la question secrète."""
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('core:password_reset_choice')
    
    user = get_object_or_404(User, id=user_id)
    profil = user.profil
    
    # Mapping des questions pour affichage complet
    QUESTIONS_MAPPING = {
        'equipe': "Votre équipe préférée ?",
        'ecole': "Le nom de votre première école ?",
        'animal': "Le nom de votre premier animal ?",
        'ville': "Votre ville de naissance ?",
        'mere': "Le nom de jeune fille de votre mère ?",
    }
    
    # Récupérer la phrase complète ou la valeur brute si non trouvée
    question_a_afficher = QUESTIONS_MAPPING.get(profil.question_secrete, profil.question_secrete)
    
    if request.method == 'POST':
        reponse = request.POST.get('reponse', '').strip()
        
        if QuestionSecuriteManager.verifier_reponse(profil, reponse):
            request.session['question_valide'] = True
            return redirect('core:password_reset_confirm')
        else:
            messages.error(request, "Réponse incorrecte.")
            
    return render(request, 'modules/core/auth/password_reset_question.html', {
        'question': question_a_afficher
    })

def password_reset_confirm(request, uidb64=None, token=None):
    """Étape 4 : Saisie du nouveau mot de passe."""
    user = None
    
    # Via lien email
    if uidb64 and token:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if not default_token_generator.check_token(user, token):
                messages.error(request, "Le lien de réinitialisation est invalide ou a expiré.")
                return redirect('core:password_reset_choice')
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, "Lien de réinitialisation invalide.")
            return redirect('core:password_reset_choice')
    else:
        # Via question secrète
        user_id = request.session.get('reset_user_id')
        if not user_id or not request.session.get('question_valide'):
            return redirect('core:password_reset_choice')
        user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas.")
        else:
            # Validation de la complexité
            # 8 car, Maj, Min, Chiffre
            if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', password):
                messages.error(request, "Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule et un chiffre.")
            else:
                user.set_password(password)
                user.save()
                
                # Nettoyage session
                if 'reset_user_id' in request.session: del request.session['reset_user_id']
                if 'question_valide' in request.session: del request.session['question_valide']
                
                messages.success(request, "Votre mot de passe a été réinitialisé avec succès.")
                return redirect('core:login')

    return render(request, 'modules/core/auth/password_reset_confirm.html')

# --- DASHBOARD & VUES MÉTIERS ---
