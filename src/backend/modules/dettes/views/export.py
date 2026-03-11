from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from modules.dettes.models import Dette, Remboursement
import csv
from django.http import HttpResponse
from django.utils import timezone

@login_required
def export_dettes_csv(request):
    dettes = Dette.objects.filter(cree_par=request.user, archive=False)
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="dettes.csv"'
    response.write('\ufeff')
    
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Sens', 'Personne', 'Montant total', 'Restant dû', 'Statut', 'Échéance'])
    
    for d in dettes:
        writer.writerow([
            d.get_sens_display(),
            d.personne,
            str(d.montant),
            str(d.montant_restant),
            d.get_statut_display(),
            d.echeance.strftime('%d/%m/%Y') if d.echeance else ''
        ])
    
    return response
