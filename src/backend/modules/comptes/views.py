import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Max, F
from django.contrib.auth.decorators import login_required

from modules.comptes.models import CompteArgent, CompteOr, MouvementCompte
from modules.core.services.prix_or_service import get_latest_prix_or, set_prix_or
from django.utils import timezone
from decimal import Decimal
from modules.karfa.models import Karfa
from modules.dettes.models import Dette

@login_required
def accueil_comptes(request):
    """Page d'accueil du module Comptes."""
    # Liquidités (Uniquement comptes non archivés)
    total_liquidites = CompteArgent.objects.filter(archive=False).aggregate(total=Sum('solde'))['total'] or 0

    # Or (Uniquement comptes non archivés)
    prix_or = get_latest_prix_or()
    total_or_gnf = 0
    total_poids_or = CompteOr.objects.filter(archive=False).aggregate(total=Sum('poids_grammes'))['total'] or 0
    if prix_or:
        total_or_gnf = total_poids_or * prix_or.prix_gramme

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

    total_comptes = total_liquidites + total_or_gnf
    patrimoine_total = total_comptes + total_karfa + total_creances - total_dettes

    return render(request, 'modules/comptes/accueil.html', {
        'total_liquidites': total_liquidites,
        'total_or_gnf': total_or_gnf,
        'total_poids_or': total_poids_or,
        'patrimoine_total': patrimoine_total,
        'prix_or': prix_or,
        'total_creances': total_creances,
        'total_dettes': total_dettes,
        'total_karfa': total_karfa,
    })

@login_required
def liste_comptes(request):
    """Liste de tous les comptes Argent et Or actifs."""
    comptes_argent = CompteArgent.objects.filter(archive=False).order_by('nom')
    comptes_or = CompteOr.objects.filter(archive=False).order_by('nom')
    
    total_argent = comptes_argent.aggregate(total=Sum('solde'))['total'] or 0
    total_poids_or = comptes_or.aggregate(total=Sum('poids_grammes'))['total'] or 0
    prix_or = get_latest_prix_or()

    if prix_or:
        for c in comptes_or:
            c.valeur_gnf = c.poids_grammes * prix_or.prix_gramme

    # Engagements Karfa par bénéficiaire
    karfas = Karfa.objects.filter(
        archive=False,
        statut__in=['ACTIF', 'PARTIELLEMENT_RENDU']
    ).exclude(statut='RENDU_TOTAL').prefetch_related('mouvements')

    dic_personnes = {}
    for k in karfas:
        nom = k.beneficiaire
        if nom not in dic_personnes:
            dic_personnes[nom] = {
                'beneficiaire': nom,
                'total': 0,
                'dernier_mouvement': None
            }
        
        dic_personnes[nom]['total'] += k.montant_actuel
        
        # Trouver la date du dernier mouvement (s'il y en a)
        last_m = k.mouvements.order_by('-date').first()
        if last_m:
            if not dic_personnes[nom]['dernier_mouvement'] or last_m.date > dic_personnes[nom]['dernier_mouvement']:
                dic_personnes[nom]['dernier_mouvement'] = last_m.date

    # Tri par montant total décroissant
    karfa_par_personne = sorted(dic_personnes.values(), key=lambda x: x['total'], reverse=True)

    return render(request, 'modules/comptes/liste.html', {
        'comptes_argent': comptes_argent,
        'comptes_or': comptes_or,
        'total_argent': total_argent,
        'karfa_par_personne': karfa_par_personne,
        'total_poids_or': total_poids_or,
        'prix_or': prix_or,
    })

@login_required
@login_required
def detail_compte(request, id):
    """Affichage du détail d'un compte (Argent ou Or)."""
    try:
        compte = CompteArgent.objects.get(id=id)
        type_compte = 'argent'
        is_or = False
    except CompteArgent.DoesNotExist:
        compte = get_object_or_404(CompteOr, id=id)
        type_compte = 'or'
        is_or = True
        
    mouvements = compte.mouvements.all().order_by('-date')
        
    return render(request, 'modules/comptes/detail.html', {
        'compte': compte,
        'is_or': is_or,
        'type_compte': type_compte,
        'nature': type_compte,
        'mouvements': mouvements
    })



@login_required
def saisie_prix_or_manuel(request):
    if request.method == 'POST':
        try:
            prix = int(request.POST['prix_manuel'])
            set_prix_or(prix)
            messages.success(request, f"Prix enregistré : {prix} GNF/g")
        except Exception:
            messages.error(request, "Valeur invalide")
    return redirect('comptes:accueil')

from .forms import CompteArgentForm, CompteOrForm

@login_required
def creer_compte(request):
    """Vue pour la création d'un nouveau compte (Argent ou Or)."""
    if request.method == 'POST':
        nature = request.POST.get('nature')
        
        if nature == 'argent':
            form = CompteArgentForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f"Compte Argent '{form.cleaned_data['nom']}' créé avec succès.")
                return redirect('comptes:liste_comptes')
            else:
                for error in form.errors.values():
                    messages.error(request, error)
        elif nature == 'or':
            form = CompteOrForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f"Compte Or '{form.cleaned_data['nom']}' créé avec succès.")
                return redirect('comptes:liste_comptes')
            else:
                # Get the validation error messages
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}" if field != '__all__' else error)
        else:
            messages.error(request, "Nature du compte inconnue.")
            
    return render(request, 'modules/comptes/form.html')

@login_required
def modifier_compte(request, id):
    """Modifier les infos de base d'un compte."""
    # On cherche d'abord dans Argent, puis dans Or
    try:
        compte = CompteArgent.objects.get(id=id)
        type_compte = 'argent'
        form_class = CompteArgentForm
    except CompteArgent.DoesNotExist:
        compte = get_object_or_404(CompteOr, id=id)
        type_compte = 'or'
        form_class = CompteOrForm
        
    if request.method == 'POST':
        form = form_class(request.POST, instance=compte)
        if form.is_valid():
            form.save()
            messages.success(request, f"Compte '{compte.nom}' mis à jour.")
            return redirect('comptes:detail_compte', id=id)
    else:
        form = form_class(instance=compte)
        
    return render(request, 'modules/comptes/form.html', {
        'form': form,
        'compte': compte,
        'modifier': True,
        'nature': type_compte
    })

@login_required
def liste_archives_comptes(request):
    """Liste des comptes archivés (Argent et Or)."""
    archives_argent = CompteArgent.objects.filter(archive=True)
    archives_or = CompteOr.objects.filter(archive=True)
    
    # Marquage pour distinguer les types dans le template
    for a in archives_argent:
        a.nature = 'argent'
    for o in archives_or:
        o.nature = 'or'
        
    from itertools import chain
    from django.utils.timezone import now
    
    archives = sorted(
        chain(archives_argent, archives_or),
        key=lambda x: x.date_archivage if x.date_archivage else now(),
        reverse=True
    )
    
    return render(request, 'modules/comptes/archives.html', {
        'comptes_archives': archives,
    })

@login_required
def archiver_compte(request, id):
    """Archive un compte."""
    try:
        compte = CompteArgent.objects.get(id=id)
    except CompteArgent.DoesNotExist:
        compte = get_object_or_404(CompteOr, id=id)
    
    compte.archive = True
    compte.date_archivage = timezone.now()
    compte.save()
    messages.success(request, f"Le compte '{compte.nom}' a été archivé.")
    return redirect('comptes:liste_comptes')

@login_required
def desarchiver_compte(request, id):
    """Désarchive un compte."""
    try:
        compte = CompteArgent.objects.get(id=id)
    except CompteArgent.DoesNotExist:
        compte = get_object_or_404(CompteOr, id=id)
    
    compte.archive = False
    compte.date_archivage = None
    compte.save()
    messages.success(request, f"Le compte '{compte.nom}' a été désarchivé.")
    return redirect('comptes:detail_compte', id=id)

@login_required
def supprimer_compte(request, id):
    """Supprime un compte définitivement si archivé et solde à zéro."""
    try:
        compte = CompteArgent.objects.get(id=id)
        solde_zero = (compte.solde == 0)
    except CompteArgent.DoesNotExist:
        compte = get_object_or_404(CompteOr, id=id)
        solde_zero = (compte.poids_grammes == 0)
    
    if not compte.archive:
        messages.error(request, "Impossible de supprimer un compte actif. Archivez-le d'abord.")
        return redirect('comptes:detail_compte', id=id)
    
    if not solde_zero:
        messages.error(request, "Le solde ou poids doit être à zéro pour supprimer le compte.")
        return redirect('comptes:detail_compte', id=id)
    
    nom = compte.nom
    compte.delete()
    messages.success(request, f"Le compte '{nom}' a été définitivement supprimé.")
    return redirect('comptes:liste_archives')

@login_required
def export_comptes_csv(request):
    """Exportation des comptes actifs en CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export_comptes.csv"'
    
    # BOM pour UTF-8 (Excel)
    response.write(u'\ufeff'.encode('utf8'))
    
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Type', 'Nom', 'Solde/Poids', 'Unité', 'Carat', 'Date création'])
    
    # Comptes Argent
    comptes_argent = CompteArgent.objects.filter(archive=False)
    for c in comptes_argent:
        writer.writerow([
            f"Argent ({c.get_type_compte_display()})",
            c.nom,
            c.solde,
            'GNF',
            '',
            c.date_creation.strftime('%d/%m/%Y %H:%M')
        ])
        
    # Comptes Or
    comptes_or = CompteOr.objects.filter(archive=False)
    for c in comptes_or:
        writer.writerow([
            'Or',
            c.nom,
            str(c.poids_grammes).replace('.', ','),
            'g',
            c.carat if c.carat else '24',
            c.date_creation.strftime('%d/%m/%Y %H:%M')
        ])
        
    return response

@login_required
def update_prix_or_manual(request):
    """Point d'entrée pour mise à jour prix or (redirige vers saisie manuelle)."""
    return redirect('comptes:saisie_prix_or_manuel')

@login_required
def ajouter_retirer_mouvement(request, type_compte, id):
    """Gère l'ajout ou le retrait de fonds/poids via POST."""
    if type_compte == 'argent':
        compte = get_object_or_404(CompteArgent, id=id)
    else:
        compte = get_object_or_404(CompteOr, id=id)
        
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
                effectue_par=request.user
            )
            
        except Exception as e:
            messages.error(request, f"Erreur lors du mouvement : {e}")
            
    return redirect('comptes:detail_compte', type_compte=type_compte, id=id)

@login_required
def operation_compte(request, id):
    """Gère l'ajout ou le retrait de fonds/poids via le formulaire de détail."""
    # On cherche le compte (Argent ou Or)
    try:
        compte = CompteArgent.objects.get(id=id)
        est_argent = True
    except CompteArgent.DoesNotExist:
        compte = get_object_or_404(CompteOr, id=id)
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
                effectue_par=request.user
            )
            
            messages.success(request, "Opération effectuée avec succès.")
        except (ValueError, Decimal.InvalidOperation):
            messages.error(request, "Montant saisi invalide.")
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {e}")
            
    return redirect('comptes:detail_compte', id=id)
