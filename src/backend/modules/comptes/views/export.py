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
def export_comptes_csv(request):
    """Exportation des comptes actifs en CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export_comptes.csv"'
    
    # BOM pour UTF-8 (Excel)
    response.write(u'\ufeff'.encode('utf8'))
    
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Type', 'Nom', 'Solde/Poids', 'Unité', 'Carat', 'Date création'])
    
    # Comptes Argent du USER
    comptes_argent = CompteArgent.objects.filter(cree_par=request.user, archive=False)
    for c in comptes_argent:
        writer.writerow([
            f"Argent ({c.get_type_compte_display()})",
            c.nom,
            c.solde,
            'GNF',
            '',
            c.date_creation.strftime('%d/%m/%Y %H:%M')
        ])
        
    # Comptes Or du USER
    comptes_or = CompteOr.objects.filter(cree_par=request.user, archive=False)
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
