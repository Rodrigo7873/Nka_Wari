from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def export_comptes_pdf(request):
    return HttpResponse("Export PDF Comptes bientôt disponible.")
