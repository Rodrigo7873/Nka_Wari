import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Max, F
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal

from modules.comptes.models import CompteArgent, CompteOr, MouvementCompte
from modules.core.services.prix_or_service import get_latest_prix_or, set_prix_or
from modules.karfa.models import Karfa
from modules.dettes.models import Dette
from modules.comptes.forms import CompteArgentForm, CompteOrForm

@login_required
def saisie_prix_or_manuel(request):
    if request.method == 'POST':
        try:
            prix = int(request.POST['prix_manuel'])
            set_prix_or(prix, request.user)
            messages.success(request, f"Prix enregistré : {prix} GNF/g")
        except Exception:
            messages.error(request, "Valeur invalide")
    return redirect('comptes:accueil')



@login_required
def update_prix_or_manual(request):
    """Point d'entrée pour mise à jour prix or (redirige vers saisie manuelle)."""
    return redirect('comptes:saisie_prix_or_manuel')

@login_required
def ajouter_retirer_mouvement(request, type_compte, id):
    """Gère l'ajout ou le retrait de fonds/poids via POST."""
    if type_compte == 'argent':
        compte = get_object_or_404(CompteArgent, id=id, cree_par=request.user)
    else:
        compte = get_object_or_404(CompteOr, id=id, cree_par=request.user)
        
    if request.method == 'POST':
        type_mouv = request.POST.get('type_mouvement') # 'AJOUT' ou 'RETRAIT'
        try:
            m_str = request.POST.get('montant', '0').replace(',', '.')
            montant = Decimal(m_str)
            motif = request.POST.get('motif', '')
            
            if montant <= 0:
                messages.error(request, "Le montant doit être supérieur à zéro.")
                return redirect('comptes:detail_compte', type_compte=type_compte, id=id)
            
            if type_mouv == 'AJOUT':
                if type_compte == 'argent':
                    compte.solde += montant
                else:
                    compte.poids_grammes += montant
                messages.success(request, f"Ajout réussi sur {compte.nom}")
            elif type_mouv == 'RETRAIT':
                if type_compte == 'argent':
                    if compte.solde < montant:
                        messages.error(request, "Solde insuffisant.")
                        return redirect('comptes:detail_compte', type_compte=type_compte, id=id)
                    compte.solde -= montant
                else:
                    if compte.poids_grammes < montant:
                        messages.error(request, "Poids insuffisant.")
                        return redirect('comptes:detail_compte', type_compte=type_compte, id=id)
                    compte.poids_grammes -= montant
                messages.success(request, f"Retrait effectué sur {compte.nom}")
            else:
                messages.error(request, "Type de mouvement invalide.")
                return redirect('comptes:detail_compte', type_compte=type_compte, id=id)
            
            compte.save()
            
            # Créer le mouvement
            MouvementCompte.objects.create(
                compte_argent=compte if type_compte == 'argent' else None,
                compte_or=compte if type_compte == 'or' else None,
                type=type_mouv,
                montant=montant,
                motif=motif,
                cree_par=request.user
            )
            
        except Exception as e:
            messages.error(request, f"Erreur lors du mouvement : {e}")
            
    return redirect('comptes:detail_compte', type_compte=type_compte, id=id)

@login_required
def operation_compte(request, id):
    """Gère l'ajout ou le retrait de fonds/poids via le formulaire de détail."""
    # On cherche le compte du USER
    try:
        compte = CompteArgent.objects.get(id=id, cree_par=request.user)
        est_argent = True
    except CompteArgent.DoesNotExist:
        compte = get_object_or_404(CompteOr, id=id, cree_par=request.user)
        est_argent = False
    
    if request.method == 'POST':
        type_op = request.POST.get('type_operation')
        try:
            m_str = request.POST.get('montant', '0').replace(',', '.')
            montant = Decimal(m_str)
            motif = request.POST.get('motif', '')
            
            if montant <= 0:
                messages.error(request, "Le montant doit être supérieur à zéro.")
                return redirect('comptes:detail_compte', id=id)

            if est_argent:
                if type_op == 'ajout':
                    compte.solde += montant
                    type_mvt = 'AJOUT'
                else:
                    if montant > compte.solde:
                        messages.error(request, "Solde insuffisant.")
                        return redirect('comptes:detail_compte', id=id)
                    compte.solde -= montant
                    type_mvt = 'RETRAIT'
            else:
                # Pour l'or, on manipule le poids
                if type_op == 'ajout':
                    compte.poids_grammes += montant
                    type_mvt = 'AJOUT'
                else:
                    if montant > compte.poids_grammes:
                        messages.error(request, "Poids insuffisant.")
                        return redirect('comptes:detail_compte', id=id)
                    compte.poids_grammes -= montant
                    type_mvt = 'RETRAIT'
            
            compte.save()
            
            # Enregistrement du mouvement
            MouvementCompte.objects.create(
                compte_argent=compte if est_argent else None,
                compte_or=compte if not est_argent else None,
                type=type_mvt,
                montant=montant,
                motif=motif,
                cree_par=request.user
            )
            
            messages.success(request, "Opération effectuée avec succès.")
        except (ValueError, Decimal.InvalidOperation):
            messages.error(request, "Montant saisi invalide.")
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {e}")
            
    return redirect('comptes:detail_compte', id=id)
