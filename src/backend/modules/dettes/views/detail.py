from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from modules.dettes.models import Dette, Remboursement
import csv
from django.http import HttpResponse
from django.utils import timezone

@login_required
def detail_dette(request, id):
    dette = get_object_or_404(Dette, id=id, cree_par=request.user)
    operations = Remboursement.objects.filter(dette=dette).order_by('-date')
    return render(request, 'modules/dettes/detail.html', {
        'dette': dette,
        'operations': operations
    })
