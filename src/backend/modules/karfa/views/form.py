from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from modules.karfa.models import Karfa
from modules.karfa.models import MouvementKarfa
import csv
from django.http import HttpResponse
from django.utils import timezone

from django.contrib.auth.models import User

@login_required
def karfa_create(request):
    """Créer un Karfa avec gestion du bénéficiaire."""
    if request.method == 'POST':
        try:
            montant = request.POST.get('montant', '0').replace(' ', '')
            beneficiaire_nom = request.POST.get('beneficiaire', '').strip()

            if not beneficiaire_nom:
                raise Exception("Le nom du bénéficiaire est requis.")

            # Récupérer ou créer l'utilisateur bénéficiaire
            # NOTE: On utilise le nom comme username pour simplification dans ce projet.
            beneficiaire, _ = User.objects.get_or_create(username=beneficiaire_nom)

            Karfa.objects.create(
                beneficiaire=beneficiaire,
                cree_par=request.user,
                montant_initial=montant,
                montant_actuel=montant,
                motif=request.POST.get('motif', '')
            )
            messages.success(request, "Karfa créé avec succès !")
            return redirect('karfa:karfa_list')
        except Exception as e:
            messages.error(request, f"Erreur de création : {str(e)}")

    mouvements = MouvementKarfa.objects.filter(karfa__cree_par=request.user).order_by('-date')[:5]
    return render(request, 'modules/karfa/form.html')
