from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Karfa

from .models import MouvementKarfa

def karfa_list(request):
    karfas = Karfa.objects.filter(archive=False)

    # Calcul du montant total engagé
    total_engage = karfas.aggregate(total=Sum('montant_actuel'))['total'] or 0

    # 5 dernières opérations
    dernieres_ops = MouvementKarfa.objects.all().order_by('-date')[:5]

    return render(request, 'modules/karfa/list.html', {
        'karfas': karfas,
        'total_engage': total_engage,
        'dernieres_ops': dernieres_ops,
    })

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

    mouvements = MouvementKarfa.objects.all().order_by('-date')[:5]
    return render(request, 'modules/karfa/form.html')

def karfa_detail(request, pk):
    """Détail d'un Karfa"""
    karfa = get_object_or_404(Karfa, pk=pk)
    return render(request, 'modules/karfa/detail.html', {'karfa': karfa})

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

import csv
from django.http import HttpResponse

@login_required
def export_karfa_csv(request):
    karfas = Karfa.objects.filter(archive=False).order_by('-date_creation')
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="karfa_export.csv"'
    
    # Ajout explicite du BOM UTF-8 pour forcer Excel à afficher correctement les accents
    response.write(b'\xef\xbb\xbf')
    
    # Utilisation du point-virgule comme délimiteur pour qu'Excel sépare bien les colonnes
    writer = csv.writer(response, delimiter=';')
    
    writer.writerow(['Bénéficiaire', 'Montant (GNF)', 'Motif', 'Statut', 'Date création'])
    
    for k in karfas:
        writer.writerow([
            k.beneficiaire,
            k.montant_actuel,
            k.motif or '',
            k.get_statut_display(),
            k.date_creation.strftime('%d/%m/%Y')
        ])
    return response

@login_required
def liste_tous_karfa(request):
    karfas = Karfa.objects.filter(archive=False).order_by('-date_creation')
    return render(request, 'modules/karfa/tous.html', {'karfas': karfas})

@login_required
def detail_karfa(request, pk):
    karfa = get_object_or_404(Karfa, pk=pk)
    mouvements = karfa.mouvements.all().order_by('-date')
    return render(request, 'modules/karfa/detail.html', {
        'karfa': karfa,
        'mouvements': mouvements
    })

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

@login_required
def ajouter_retirer_karfa(request, pk):
    karfa = get_object_or_404(Karfa, pk=pk)
    if request.method == 'POST':
        type_mvt = request.POST['type_mouvement']
        montant = int(request.POST['montant'])
        motif = request.POST.get('motif', '').strip()

        if type_mvt == 'AJOUT':
            karfa.montant_actuel += montant
            type_mouvement = 'AJOUT'
            note = motif if motif else f"Ajout de {montant} GNF"
            
            if karfa.montant_actuel > 0:
                karfa.statut = 'ACTIF'
        else:
            if montant > karfa.montant_actuel:
                messages.error(request, "Montant trop élevé")
                return redirect('karfa:detail_karfa', pk=pk)
            karfa.montant_actuel -= montant
            type_mouvement = 'RETRAIT'
            note = motif if motif else f"Retrait de {montant} GNF"

            if karfa.montant_actuel == 0:
                karfa.statut = 'RENDU_TOTAL'
                from django.utils import timezone
                karfa.date_rendu_total = timezone.now()
            else:
                karfa.statut = 'PARTIELLEMENT_RENDU'

        karfa.save()

        MouvementKarfa.objects.create(
            karfa=karfa,
            type=type_mouvement,
            montant=montant,
            note=note,
            solde_apres=karfa.montant_actuel
        )

        messages.success(request, f"Opération effectuée : {note}")
        return redirect('karfa:detail_karfa', pk=pk)

@login_required
def liste_archives(request):
    karfas = Karfa.objects.filter(archive=True).order_by('-date_archivage')
    return render(request, 'modules/karfa/archives.html', {'karfas': karfas})

from django.utils import timezone

@login_required
def archiver_karfa(request, pk):
    karfa = get_object_or_404(Karfa, pk=pk)
    if not karfa.archive:
        karfa.archive = True
        karfa.date_archivage = timezone.now()
        karfa.save()
        messages.success(request, f"Karfa de {karfa.beneficiaire} archivé.")
    return redirect('karfa:detail_karfa', pk=pk)

@login_required
def desarchiver_karfa(request, pk):
    karfa = get_object_or_404(Karfa, pk=pk)
    if karfa.archive:
        karfa.archive = False
        karfa.date_archivage = None
        karfa.save()
        messages.success(request, f"Karfa de {karfa.beneficiaire} désarchivé.")
    return redirect('karfa:detail_karfa', pk=pk)

@login_required
def toutes_operations(request):
    operations = MouvementKarfa.objects.all().order_by('-date')
    return render(request, 'modules/karfa/operations.html', {'operations': operations})