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
def export_karfa_csv(request):
    karfas = Karfa.objects.filter(cree_par=request.user, archive=False).order_by('-date_creation')
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
