from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from modules.dettes.models import Dette, Remboursement
import csv
from django.http import HttpResponse
from django.utils import timezone

@login_required
def liste_archives_dettes(request):
    archives = Dette.objects.filter(cree_par=request.user, archive=True).order_by('-date_archivage')
    return render(request, 'modules/dettes/archives.html', {
        'archives': archives,
    })

@login_required
def archiver_dette(request, id):
    dette = get_object_or_404(Dette, id=id, cree_par=request.user)
    if dette.archive:
        dette.archive = False
        dette.date_archivage = None
        messages.success(request, f"La dette de {dette.personne} a été désarchivée.")
    else:
        dette.archive = True
        dette.date_archivage = timezone.now()
        messages.success(request, f"La dette de {dette.personne} a été archivée.")
    dette.save()

    # 3️⃣ ARCHIVAGE SYNCHRONISÉ DU COMPTE
    if dette.sens == 'JE_DOIS':
        compte_lie = dette.compte_dette
        if compte_lie:
            compte_lie.archive = dette.archive
            compte_lie.date_archivage = dette.date_archivage
            compte_lie.save()
    return redirect('dettes:detail_dette', id=id)
