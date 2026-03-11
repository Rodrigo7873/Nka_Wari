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

@login_required
def profil_view(request):
    """Affiche le profil de l'utilisateur connecté."""
    # Add try-except to handle users (like superusers) without a profile
    try:
        profil = Profil.objects.get(user=request.user)
    except Profil.DoesNotExist:
        # Create a default profile if it doesn't exist
        from django.utils.crypto import get_random_string
        profil = Profil.objects.create(
            user=request.user,
            identifiant=get_random_string(8).upper(),
            telephone='',
            question_secrete='Non définie',
            reponse_secrete='Non définie'
        )
    
    return render(request, 'core/profil.html', {
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
