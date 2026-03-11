from django.shortcuts import render, redirect, get_object_or_404
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
from modules.core.models import Profil

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
                    return redirect('core:accueil')
            
            messages.error(request, "Identifiants ou mot de passe incorrect")
        except Exception as e:
            messages.error(request, f"Erreur de connexion : {str(e)}")

    return render(request, 'core/login.html')

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
            return render(request, 'core/register.html')
            
        try:
            validate_password(password)
        except ValidationError as e:
            for message in e.messages:
                messages.error(request, message)
            return render(request, 'core/register.html')
            
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
            
    return render(request, 'core/register_wizard.html')

def registration_success(request):
    user_id = request.session.get('new_user_id', 'Inconnu')
    return render(request, 'core/registration_success.html', {'user_id': user_id})

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

# --- DASHBOARD & VUES MÉTIERS ---
