from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from modules.dettes.models import Dette
from modules.dettes.forms import DetteForm
from modules.comptes.models import MouvementCompte

@login_required
def creer_dette(request):
    if request.method == 'POST':
        form = DetteForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    dette = form.save(commit=False)
                    dette.cree_par = request.user
                    dette.save()

                    # Si c'est une créance (On me doit), on débite le compte
                    if dette.sens == 'ON_ME_DOIT' and dette.compte_debit:
                        compte = dette.compte_debit
                        montant = dette.montant
                        
                        # Déduire du solde
                        compte.solde -= montant
                        compte.save()

                        # Enregistrer le mouvement
                        MouvementCompte.objects.create(
                            compte_argent=compte,
                            type=MouvementCompte.TYPE_RETRAIT,
                            montant=montant,
                            motif=f"Créance à {dette.personne} - Motif: {dette.motif}",
                            cree_par=request.user
                        )

                    # 1️⃣ AUTOMATISATION : Créer un compte pour chaque dette "Je dois"
                    if dette.sens == 'JE_DOIS':
                        from modules.comptes.models import CompteArgent
                        CompteArgent.objects.create(
                            nom=f"Dette : {dette.personne}",
                            type_compte='DETTE',
                            solde=dette.montant,
                            dette_liee=dette,
                            cree_par=request.user,
                            archive=False
                        )

                    messages.success(request, "Dette enregistrée avec succès.")
                    return redirect('dettes:toutes_dettes')
            except Exception as e:
                messages.error(request, f"Une erreur est survenue : {str(e)}")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = DetteForm(user=request.user)
    
    return render(request, 'modules/dettes/form.html', {'form': form})

