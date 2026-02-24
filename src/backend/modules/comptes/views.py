from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

from modules.comptes.models.argent import CompteArgent
from modules.comptes.models.or_ import CompteOr
from modules.core.services.prix_or_service import get_latest_prix_or, recuperer_prix_or, set_prix_or
from modules.karfa.models import Karfa
from modules.dettes.models import Dette


@login_required
def liste_comptes(request):
    comptes_argent = CompteArgent.objects.all()
    comptes_or = CompteOr.objects.all()
    prix_or = get_latest_prix_or()

    return render(request, 'modules/comptes/liste.html', {
        'comptes_argent': comptes_argent,
        'comptes_or': comptes_or,
        'prix_or': prix_or,
    })


@login_required
def tableau_bord(request):
    # Liquidités
    total_liquidites = CompteArgent.objects.aggregate(total=Sum('solde'))['total'] or 0

    # Or
    prix_or = get_latest_prix_or()
    total_or = 0
    if prix_or:
        total_or = CompteOr.objects.aggregate(
            total=Sum('poids_grammes')
        )['total'] or 0
        total_or = total_or * prix_or.prix_gramme

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

    # Karfa actifs
    total_karfa = Karfa.objects.filter(
        archive=False
    ).aggregate(total=Sum('montant_actuel'))['total'] or 0

    patrimoine_total = total_liquidites + total_or + total_creances - total_dettes

    return render(request, 'modules/comptes/tableau_bord.html', {
        'total_liquidites': total_liquidites,
        'total_or': total_or,
        'total_creances': total_creances,
        'total_dettes': total_dettes,
        'total_karfa': total_karfa,
        'patrimoine_total': patrimoine_total,
        'prix_or': prix_or,
    })


@login_required
def update_prix_or_manual(request):
    """
    Récupère le prix via le service puis l'enregistre.
    """
    succes, prix = recuperer_prix_or()

    if succes:
        # prix déjà sauvegardé par le service
        messages.success(request, f"Prix mis à jour : {prix} GNF/g")
    else:
        messages.warning(request, "API indisponible, valeur par défaut utilisée")

    return redirect('liste_comptes')


@login_required
def saisie_prix_or_manuel(request):
    if request.method == 'POST':
        try:
            prix = int(request.POST['prix_manuel'])
            set_prix_or(prix)
            messages.success(request, f"Prix enregistré : {prix} GNF/g")
        except Exception:
            messages.error(request, "Valeur invalide")
    return redirect('liste_comptes')