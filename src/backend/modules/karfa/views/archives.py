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
def liste_archives(request):
    karfas = Karfa.objects.filter(cree_par=request.user, archive=True).order_by('-date_archivage')
    return render(request, 'modules/karfa/archives.html', {'karfas': karfas})

from django.utils import timezone

@login_required
def archiver_karfa(request, pk):
    karfa = get_object_or_404(Karfa, pk=pk, cree_par=request.user)
    if not karfa.archive:
        karfa.archive = True
        karfa.date_archivage = timezone.now()
        karfa.save()
        messages.success(request, f"Karfa de {karfa.beneficiaire} archivé.")
    return redirect('karfa:detail_karfa', pk=pk)

@login_required
def desarchiver_karfa(request, pk):
    karfa = get_object_or_404(Karfa, pk=pk, cree_par=request.user)
    if karfa.archive:
        karfa.archive = False
        karfa.date_archivage = None
        karfa.save()
        messages.success(request, f"Karfa de {karfa.beneficiaire} désarchivé.")
    return redirect('karfa:detail_karfa', pk=pk)
