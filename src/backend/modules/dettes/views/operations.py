from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from modules.dettes.models import Dette, Remboursement
import csv
from django.http import HttpResponse
from django.utils import timezone

@login_required
def rembourser_dette(request, id):
    dette = get_object_or_404(Dette, id=id, cree_par=request.user)

    if request.method == 'POST':
        try:
            montant = int(request.POST['montant'])
            if montant <= 0 or montant > dette.montant_restant:
                messages.error(request, "Montant invalide.")
            else:
                Remboursement.objects.create(
                    dette=dette,
                    type='REMBOURSEMENT',
                    montant=montant,
                    note=request.POST.get('note', '')
                )
                dette.montant_restant -= montant
                if dette.montant_restant == 0:
                    dette.statut = 'PAYEE'
                    dette.date_dernier_paiement = timezone.now()
                else:
                    dette.statut = 'PARTIELLEMENT_PAYEE'
                dette.save()

                # 2️⃣ MISE À JOUR DU COMPTE LIE (Si c'est une dette "Je dois")
                if dette.sens == 'JE_DOIS':
                    compte_lie = dette.compte_dette
                    if compte_lie:
                        compte_lie.solde = dette.montant_restant
                        if dette.montant_restant == 0:
                            compte_lie.archive = True
                            compte_lie.date_archivage = timezone.now()
                        compte_lie.save()

                messages.success(request, "Remboursement enregistré.")
                return redirect('dettes:liste_dettes')
        except ValueError:
            messages.error(request, "Montant invalide.")

    return render(request, 'modules/dettes/rembourser.html', {'dette': dette})

@login_required
def ajouter_paiement(request, id):
    dette = get_object_or_404(Dette, id=id, cree_par=request.user)
    if request.method == 'POST':
        try:
            montant = int(request.POST.get('montant', 0))
            motif = request.POST.get('motif', '').strip()
            type_form = request.POST.get('type_paiement')
            
            if montant <= 0:
                messages.error(request, "Le montant doit être supérieur à 0.")
                return redirect('dettes:detail_dette', id=id)

            mapping = {
                'ajout': 'AJOUT',
                'ajouter_creance': 'AJOUT',
                'remboursement': 'REMBOURSEMENT',
                'encaisser': 'ENCAISSEMENT'
            }
            
            op_type = mapping.get(type_form)
            if not op_type:
                messages.error(request, "Type d'opération inconnu.")
                return redirect('dettes:detail_dette', id=id)

            if op_type == 'AJOUT':
                dette.montant += montant
                dette.montant_restant += montant
            else: # REMBOURSEMENT or ENCAISSEMENT
                if montant > dette.montant_restant:
                    messages.error(request, "Le montant ne peut pas dépasser le reste à payer.")
                    return redirect('dettes:detail_dette', id=id)
                dette.montant_restant -= montant

            # Mise à jour du statut
            if dette.montant_restant == 0:
                dette.statut = 'PAYEE'
                dette.date_dernier_paiement = timezone.now()
            elif dette.montant_restant < dette.montant:
                dette.statut = 'PARTIELLEMENT_PAYEE'
                dette.date_dernier_paiement = timezone.now()
            else:
                dette.statut = 'NON_PAYEE'
            
            dette.save()

            # Mise à jour du compte lié (Si c'est une dette "Je dois")
            if dette.sens == 'JE_DOIS':
                compte_lie = dette.compte_dette
                if compte_lie:
                    compte_lie.solde = dette.montant_restant
                    if dette.montant_restant == 0:
                        compte_lie.archive = True
                        compte_lie.date_archivage = timezone.now()
                    compte_lie.save()

            # Création de l'opération
            Remboursement.objects.create(
                dette=dette,
                type=op_type,
                montant=montant,
                note=motif
            )
            
            messages.success(request, f"Opération {op_type} effectuée.")
        except ValueError:
            messages.error(request, "Montant invalide.")
            
    return redirect('dettes:detail_dette', id=id)

@login_required
def toutes_operations_dettes(request):
    operations = Remboursement.objects.filter(dette__cree_par=request.user).order_by('-date')
    return render(request, 'modules/dettes/operations.html', {'operations': operations})


@login_required
def ajouter_dette(request, id):
    """Augmenter le montant d'une créance existante."""
    from modules.comptes.models import CompteArgent, MouvementCompte
    from django.db import transaction

    dette = get_object_or_404(Dette, id=id, cree_par=request.user)
    
    # Sécurité : Uniquement pour les créances "On me doit"
    if dette.sens != 'ON_ME_DOIT':
        messages.error(request, "Seules les créances (On me doit) peuvent être augmentées.")
        return redirect('dettes:detail_dette', id=id)

    # Récupérer les comptes argent du user avec solde > 0 (Exclure les comptes DETTE)
    comptes = CompteArgent.objects.filter(cree_par=request.user, archive=False, solde__gt=0).exclude(type_compte='DETTE')

    if request.method == 'POST':
        compte_id = request.POST.get('compte_id')
        try:
            montant_ajout = int(request.POST.get('montant', 0))
            motif = request.POST.get('motif', '').strip()
            
            if montant_ajout <= 0:
                messages.error(request, "Le montant doit être supérieur à 0.")
            else:
                compte = get_object_or_404(CompteArgent, id=compte_id, cree_par=request.user)
                
                if compte.solde < montant_ajout:
                    messages.error(request, f"Solde insuffisant sur le compte {compte.nom} ({compte.solde:,.0f} GNF).")
                else:
                    with transaction.atomic():
                        # 1. Débiter le compte
                        compte.solde -= montant_ajout
                        compte.save()
                        
                        # 2. Augmenter la dette
                        dette.montant += montant_ajout
                        dette.montant_restant += montant_ajout
                        
                        # Mettre à jour le statut
                        if dette.montant_restant > 0:
                            if dette.montant_restant == dette.montant:
                                dette.statut = 'NON_PAYEE'
                            else:
                                dette.statut = 'PARTIELLEMENT_PAYEE'
                        dette.save()
                        
                        # 3. Créer le mouvement de compte
                        MouvementCompte.objects.create(
                            compte_argent=compte,
                            type=MouvementCompte.TYPE_RETRAIT,
                            montant=montant_ajout,
                            motif=f"Augmentation créance {dette.personne} - {motif}",
                            cree_par=request.user
                        )
                        
                        # 4. Créer l'opération de dette (AJOUT)
                        Remboursement.objects.create(
                            dette=dette,
                            type='AJOUT',
                            montant=montant_ajout,
                            note=motif or "Augmentation de la créance"
                        )
                        
                        messages.success(request, f"La créance a été augmentée de {montant_ajout:,.0f} GNF.")
                        return redirect('dettes:detail_dette', id=id)
        except (ValueError, TypeError):
            messages.error(request, "Données invalides.")

    return render(request, 'modules/dettes/ajouter.html', {
        'dette': dette,
        'comptes': comptes
    })


@login_required
def encaisser_dette(request, id):
    """Encaisser (rembourser) une créance ("On me doit") vers un compte."""
    from modules.comptes.models import CompteArgent, MouvementCompte
    from django.db import transaction

    dette = get_object_or_404(Dette, id=id, cree_par=request.user)
    
    if dette.sens != 'ON_ME_DOIT':
        messages.error(request, "Seules les créances (On me doit) peuvent être encaissées.")
        return redirect('dettes:detail_dette', id=id)

    if dette.statut == 'PAYEE':
        messages.error(request, "Cette créance est déjà totalement encaissée.")
        return redirect('dettes:detail_dette', id=id)

    comptes = CompteArgent.objects.filter(cree_par=request.user, archive=False).exclude(type_compte='DETTE')

    if request.method == 'POST':
        compte_id = request.POST.get('compte_id')
        try:
            montant_encaisse = int(request.POST.get('montant', 0))
            note = request.POST.get('note', '').strip()
            
            if montant_encaisse <= 0:
                messages.error(request, "Le montant doit être supérieur à 0.")
            elif montant_encaisse > dette.montant_restant:
                messages.error(request, "Le montant ne peut pas dépasser le reste à récupérer.")
            else:
                compte = get_object_or_404(CompteArgent, id=compte_id, cree_par=request.user)
                
                with transaction.atomic():
                    # 1. Créditer le compte
                    compte.solde += montant_encaisse
                    compte.save()
                    
                    # 2. Diminuer le reste de la dette
                    dette.montant_restant -= montant_encaisse
                    
                    # Mise à jour du statut
                    if dette.montant_restant == 0:
                        dette.statut = 'PAYEE'
                        dette.date_dernier_paiement = timezone.now()
                    else:
                        dette.statut = 'PARTIELLEMENT_PAYEE'
                        dette.date_dernier_paiement = timezone.now()
                    dette.save()
                    
                    # 3. Créer le mouvement de compte
                    MouvementCompte.objects.create(
                        compte_argent=compte,
                        type=MouvementCompte.TYPE_AJOUT,
                        montant=montant_encaisse,
                        motif=f"Encaissement créance {dette.personne} - {note}",
                        cree_par=request.user
                    )
                    
                    # 4. Créer l'opération de dette (ENCAISSEMENT)
                    Remboursement.objects.create(
                        dette=dette,
                        type='ENCAISSEMENT',
                        montant=montant_encaisse,
                        note=note or "Encaissement partiel/total"
                    )
                    
                    messages.success(request, f"{montant_encaisse:,.0f} GNF encaissés sur le compte {compte.nom}.")
                    return redirect('dettes:detail_dette', id=id)
        except (ValueError, TypeError):
            messages.error(request, "Données invalides.")

    return render(request, 'modules/dettes/encaisser.html', {
        'dette': dette,
        'comptes': comptes
    })
