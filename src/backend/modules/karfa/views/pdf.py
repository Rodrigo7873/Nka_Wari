from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from xhtml2pdf import pisa
import io

from modules.karfa.models import Karfa, MouvementKarfa

@login_required
def export_karfa_pdf(request):
    """
    Génère un PDF listant tous les Karfa actifs de l'utilisateur avec xhtml2pdf.
    """
    # Filtrer tous les Karfa actifs de l'utilisateur
    karfas = Karfa.objects.filter(cree_par=request.user, archive=False).order_by('beneficiaire')
    
    # Calcul du montant total engagé
    total_engage = karfas.aggregate(total=Sum('montant_actuel'))['total'] or 0
    
    # Récupérer les 10 dernières opérations pour un rapport complet
    dernieres_ops = MouvementKarfa.objects.filter(karfa__cree_par=request.user).order_by('-date')[:10]

    # Préparation du nom d'utilisateur pour éviter les tags bruts si objet complexe
    user_display = request.user.get_full_name() or request.user.username

    # Contexte pour le template
    context = {
        'karfas': karfas,
        'total_engage': total_engage,
        'dernieres_ops': dernieres_ops,
        'user_name': user_display,
        'date': timezone.now(),
    }
    
    # Rendu du template HTML en chaîne
    html_string = render_to_string('modules/karfa/pdf.html', context)
    
    # Création de la réponse HTTP
    response = HttpResponse(content_type='application/pdf')
    filename = f"karfa_nkawari_{timezone.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Génération du PDF avec xhtml2pdf (Pisa)
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    
    # Si erreur, on renvoie un HttpResponse d'erreur
    if pisa_status.err:
        return HttpResponse('Une erreur est survenue lors de la génération du PDF.', status=500)
    
    return response
