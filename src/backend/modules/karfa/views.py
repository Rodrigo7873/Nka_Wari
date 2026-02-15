from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Karfa
from modules.comptes.models.argent import CompteArgent

# @login_required
def karfa_list(request):
    """Liste des Karfa actifs"""
    # Simulation de compte pour le test
    compte_test, _ = CompteArgent.objects.get_or_create(
        nom="Compte Principal",
        sous_type="CASH",
        defaults={'solde': 1000000}
    )
    
    karfas = Karfa.objects.filter(archive=False)
    
    # Calcul des soldes
    total_engage = karfas.aggregate(total=Sum('montant_actuel'))['total'] or 0
    solde_total = compte_test.solde
    solde_disponible = solde_total - total_engage
    
    return render(request, 'modules/karfa/list.html', {
        'karfas': karfas,
        'solde_total': solde_total,
        'solde_disponible': solde_disponible,
        'total_engage': total_engage
    })

# @login_required
def karfa_create(request):
    from django.contrib.auth.models import User
    
    # Créer utilisateur test UNE SEULE FOIS
    user_test, created = User.objects.get_or_create(
        username='test',
        defaults={'password': 'test1234'}
    )
    
    if request.method == 'POST':
        try:
            montant = request.POST['montant']
            
            # UTILISE .create() AVEC montant_actuel
            Karfa.objects.create(
                beneficiaire=user_test,
                cree_par=user_test,
                montant_initial=montant,
                montant_actuel=montant,  # ✅ OBLIGATOIRE
                motif=request.POST.get('motif', '')
            )
            messages.success(request, "Karfa créé avec succès !")
            return redirect('karfa:karfa_list')
        except Exception as e:
            messages.error(request, f"Erreur : {str(e)}")
    
    return render(request, 'modules/karfa/form.html')

# @login_required
def karfa_detail(request, pk):
    """Détail d'un Karfa"""
    karfa = get_object_or_404(Karfa, pk=pk)
    return render(request, 'modules/karfa/detail.html', {'karfa': karfa})

# @login_required
def karfa_restituer(request, pk):
    """Restitution partielle ou totale"""
    karfa = get_object_or_404(Karfa, pk=pk)
    
    if request.method == 'POST':
        try:
            montant = int(request.POST['montant'])
            karfa.restituer(montant, request.POST.get('note', ''))
            messages.success(request, f"Restitution de {montant} GNF effectuée")
        except Exception as e:
            messages.error(request, f"Erreur : {str(e)}")
    
    return redirect('karfa:karfa_detail', pk=pk)