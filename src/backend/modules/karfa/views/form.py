from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from modules.karfa.models import Karfa
from modules.karfa.models import MouvementKarfa
import csv
from django.http import HttpResponse
from django.utils import timezone

@login_required
def karfa_create(request):
    """Créer un Karfa — n'utilise plus de user de test en clair.

    Utilise `request.user` comme `beneficiaire` et `cree_par` (utilisateur connecté).
    """
    user = request.user

    if request.method == 'POST':
        try:
            montant = request.POST['montant']
            beneficiaire_nom = request.POST['beneficiaire'].strip()

            Karfa.objects.create(
                beneficiaire=beneficiaire_nom,
                cree_par=user,
                montant_initial=montant,
                montant_actuel=montant,
                motif=request.POST.get('motif', '')
            )
            messages.success(request, "Karfa créé avec succès !")
            return redirect('karfa:karfa_list')
        except Exception as e:
            messages.error(request, f"Erreur : {str(e)}")

    mouvements = MouvementKarfa.objects.filter(karfa__cree_par=request.user).order_by('-date')[:5]
    return render(request, 'modules/karfa/form.html')
