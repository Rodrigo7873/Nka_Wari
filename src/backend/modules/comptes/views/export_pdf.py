from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from xhtml2pdf import pisa
import io

from modules.comptes.models import CompteArgent, CompteOr
from modules.core.services.prix_or_service import get_latest_prix_or

@login_required
def export_comptes_pdf(request):
    """
    Génère un PDF listant tous les comptes de l'utilisateur avec xhtml2pdf.
    """
    # Filtrer tous les comptes actifs de l'utilisateur
    comptes_argent_base = CompteArgent.objects.filter(cree_par=request.user, archive=False).order_by('nom')
    
    # Séparer les comptes réels des comptes dette (passifs)
    comptes_argent = comptes_argent_base.exclude(type_compte='DETTE')
    # Les comptes de dettes pour l'affichage séparé
    comptes_dette = CompteArgent.objects.filter(
        cree_par=request.user, 
        archive=False, 
        type_compte='DETTE'
    )
    
    comptes_or = CompteOr.objects.filter(cree_par=request.user, archive=False).order_by('nom')
    
    # Calcul des totaux
    total_argent = comptes_argent.aggregate(total=Sum('solde'))['total'] or 0
    total_dette = comptes_dette.aggregate(total=Sum('solde'))['total'] or 0
    total_poids_or = comptes_or.aggregate(total=Sum('poids_grammes'))['total'] or 0
    
    prix_or = get_latest_prix_or(request.user)
    if prix_or:
        for c in comptes_or:
            c.valeur_gnf = c.poids_grammes * prix_or.prix_gramme

    # Contexte pour le template
    context = {
        'comptes_argent': comptes_argent,
        'comptes_dette': comptes_dette,
        'comptes_or': comptes_or,
        'total_argent': total_argent,
        'total_dette': total_dette,
        'total_poids_or': total_poids_or,
        'prix_or': prix_or,
        'user': request.user,
        'date': timezone.now(),
    }
    
    # Rendu du template HTML en chaîne
    html_string = render_to_string('modules/comptes/pdf.html', context)
    
    # Création de la réponse HTTP
    response = HttpResponse(content_type='application/pdf')
    filename = f"comptes_nkawari_{timezone.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Génération du PDF avec xhtml2pdf (Pisa)
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    
    # Si erreur, on renvoie un HttpResponse d'erreur
    if pisa_status.err:
        return HttpResponse('Une erreur est survenue lors de la génération du PDF.', status=500)
    
    return response
