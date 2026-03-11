from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from xhtml2pdf import pisa
import io

from modules.dettes.models import Dette, Remboursement

@login_required
def export_dettes_pdf(request):
    """
    Génère un PDF listant toutes les dettes actives de l'utilisateur avec xhtml2pdf.
    """
    # Récupérer les dettes (Je dois et On me doit)
    dettes_je_dois = Dette.objects.filter(cree_par=request.user, archive=False, sens='JE_DOIS').order_by('-date_creation')
    dettes_on_me_doit = Dette.objects.filter(cree_par=request.user, archive=False, sens='ON_ME_DOIT').order_by('-date_creation')
    
    # Calcul des totaux
    total_je_dois = dettes_je_dois.aggregate(total=Sum('montant_restant'))['total'] or 0
    total_on_me_doit = dettes_on_me_doit.aggregate(total=Sum('montant_restant'))['total'] or 0
    
    # Récupérer les 10 derniers remboursements/paiements
    derniers_paiements = Remboursement.objects.filter(dette__cree_par=request.user).order_by('-date')[:10]

    # Contexte pour le template
    context = {
        'dettes_je_dois': dettes_je_dois,
        'dettes_on_me_doit': dettes_on_me_doit,
        'total_je_dois': total_je_dois,
        'total_on_me_doit': total_on_me_doit,
        'derniers_paiements': derniers_paiements,
        'user_name': request.user.get_full_name() or request.user.username,
        'date': timezone.now(),
    }
    
    # Rendu du template HTML en chaîne
    html_string = render_to_string('modules/dettes/pdf.html', context)
    
    # Création de la réponse HTTP
    response = HttpResponse(content_type='application/pdf')
    filename = f"dettes_nkawari_{timezone.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Génération du PDF avec xhtml2pdf (Pisa)
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    
    # Si erreur, on renvoie un HttpResponse d'erreur
    if pisa_status.err:
        return HttpResponse('Une erreur est survenue lors de la génération du PDF.', status=500)
    
    return response
