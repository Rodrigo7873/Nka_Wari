from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .models import Dette, Remboursement


@login_required
def liste_dettes(request):
    dettes = Dette.objects.filter(archive=False)
    total_je_dois = dettes.filter(sens='JE_DOIS').aggregate(total=Sum('montant_restant'))['total'] or 0
    total_on_me_doit = dettes.filter(sens='ON_ME_DOIT').aggregate(total=Sum('montant_restant'))['total'] or 0

    return render(request, 'modules/dettes/list.html', {
        'dettes': dettes,
        'total_je_dois': total_je_dois,
        'total_on_me_doit': total_on_me_doit,
    })

@login_required
def creer_dette(request):
    if request.method == 'POST':
        Dette.objects.create(
            sens=request.POST['sens'],
            personne=request.POST['personne'],
            montant=request.POST['montant'],
            motif=request.POST.get('motif', ''),
            echeance=request.POST.get('echeance') or None,
            garantie=request.POST.get('garantie', ''),
        )
        messages.success(request, "Dette créée avec succès.")
        return redirect('liste_dettes')
    return render(request, 'modules/dettes/form.html')

@login_required
def rembourser_dette(request, id):
    dette = get_object_or_404(Dette, id=id)

    if request.method == 'POST':
        montant = int(request.POST['montant'])
        if montant <= 0 or montant > dette.montant_restant:
            messages.error(request, "Montant invalide.")
        else:
            Remboursement.objects.create(
                dette=dette,
                montant=montant,
                note=request.POST.get('note', '')
            )
            dette.montant_restant -= montant
            if dette.montant_restant == 0:
                dette.statut = 'PAYEE'
            else:
                dette.statut = 'PARTIELLEMENT_PAYEE'
            dette.save()
            messages.success(request, "Remboursement enregistré.")
            return redirect('liste_dettes')

    return render(request, 'modules/dettes/rembourser.html', {'dette': dette})

import csv
from django.http import HttpResponse

@login_required
def export_dettes_csv(request):
    dettes = Dette.objects.filter(archive=False)
    
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