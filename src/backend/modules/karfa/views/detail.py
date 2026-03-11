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
def karfa_detail(request, pk):
    """Détail d'un Karfa"""
    karfa = get_object_or_404(Karfa, pk=pk, cree_par=request.user)
    return render(request, 'modules/karfa/detail.html', {'karfa': karfa})

@login_required
def detail_karfa(request, pk):
    karfa = get_object_or_404(Karfa, pk=pk, cree_par=request.user)
    mouvements = karfa.mouvements.all().order_by('-date')
    return render(request, 'modules/karfa/detail.html', {
        'karfa': karfa,
        'mouvements': mouvements
    })

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
