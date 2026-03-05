from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .models import Dette, Remboursement
import csv
from django.http import HttpResponse
from django.utils import timezone


@login_required
def liste_dettes(request):
    dettes = Dette.objects.filter(archive=False)
    total_je_dois = dettes.filter(sens='JE_DOIS').aggregate(total=Sum('montant_restant'))['total'] or 0
    total_on_me_doit = dettes.filter(sens='ON_ME_DOIT').aggregate(total=Sum('montant_restant'))['total'] or 0

    dernieres_ops = Remboursement.objects.all().order_by('-date')[:5]

    return render(request, 'modules/dettes/list.html', {
        'total_je_dois': total_je_dois,
        'total_on_me_doit': total_on_me_doit,
        'dernieres_ops': dernieres_ops,
    })


@login_required
def toutes_dettes(request):
    dettes_je_dois = Dette.objects.filter(sens='JE_DOIS', archive=False).order_by('-date_creation')
    dettes_on_me_doit = Dette.objects.filter(sens='ON_ME_DOIT', archive=False).order_by('-date_creation')
    return render(request, 'modules/dettes/toutes.html', {
        'dettes_je_dois': dettes_je_dois,
        'dettes_on_me_doit': dettes_on_me_doit,
    })


@login_required
def liste_archives_dettes(request):
    archives = Dette.objects.filter(archive=True).order_by('-date_archivage')
    return render(request, 'modules/dettes/archives.html', {
        'archives': archives,
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
        return redirect('dettes:liste_dettes')
    return render(request, 'modules/dettes/form.html')


@login_required
def rembourser_dette(request, id):
    dette = get_object_or_404(Dette, id=id)

    if request.method == 'POST':
        try:
            montant = int(request.POST['montant'])
            if montant <= 0 or montant > dette.montant_restant:
                messages.error(request, "Montant invalide.")
            else:
                Remboursement.objects.create(
                    dette=dette,
                    type='REMBOURSEMENT',
                    montant=montant,
                    note=request.POST.get('note', '')
                )
                dette.montant_restant -= montant
                if dette.montant_restant == 0:
                    dette.statut = 'PAYEE'
                    dette.date_dernier_paiement = timezone.now()
                else:
                    dette.statut = 'PARTIELLEMENT_PAYEE'
                dette.save()
                messages.success(request, "Remboursement enregistré.")
                return redirect('dettes:liste_dettes')
        except ValueError:
            messages.error(request, "Montant invalide.")

    return render(request, 'modules/dettes/rembourser.html', {'dette': dette})


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


@login_required
def toutes_operations_dettes(request):
    operations = Remboursement.objects.all().order_by('-date')
    return render(request, 'modules/dettes/operations.html', {'operations': operations})


@login_required
def detail_dette(request, id):
    dette = get_object_or_404(Dette, id=id)
    operations = Remboursement.objects.filter(dette=dette).order_by('-date')
    return render(request, 'modules/dettes/detail.html', {
        'dette': dette,
        'operations': operations
    })


@login_required
def archiver_dette(request, id):
    dette = get_object_or_404(Dette, id=id)
    if dette.archive:
        dette.archive = False
        dette.date_archivage = None
        messages.success(request, f"La dette de {dette.personne} a été désarchivée.")
    else:
        dette.archive = True
        dette.date_archivage = timezone.now()
        messages.success(request, f"La dette de {dette.personne} a été archivée.")
    dette.save()
    return redirect('dettes:detail_dette', id=id)


@login_required
def ajouter_paiement(request, id):
    dette = get_object_or_404(Dette, id=id)
    if request.method == 'POST':
        try:
            montant = int(request.POST.get('montant', 0))
            motif = request.POST.get('motif', '').strip()
            type_form = request.POST.get('type_paiement')
            
            if montant <= 0:
                messages.error(request, "Le montant doit être supérieur à 0.")
                return redirect('dettes:detail_dette', id=id)

            mapping = {
                'ajout': 'AJOUT',
                'ajouter_creance': 'AJOUT',
                'remboursement': 'REMBOURSEMENT',
                'encaisser': 'ENCAISSEMENT'
            }
            
            op_type = mapping.get(type_form)
            if not op_type:
                messages.error(request, "Type d'opération inconnu.")
                return redirect('dettes:detail_dette', id=id)

            if op_type == 'AJOUT':
                dette.montant += montant
                dette.montant_restant += montant
            else: # REMBOURSEMENT or ENCAISSEMENT
                if montant > dette.montant_restant:
                    messages.error(request, "Le montant ne peut pas dépasser le reste à payer.")
                    return redirect('dettes:detail_dette', id=id)
                dette.montant_restant -= montant

            # Mise à jour du statut
            if dette.montant_restant == 0:
                dette.statut = 'PAYEE'
                dette.date_dernier_paiement = timezone.now()
            elif dette.montant_restant < dette.montant:
                dette.statut = 'PARTIELLEMENT_PAYEE'
                dette.date_dernier_paiement = timezone.now()
            else:
                dette.statut = 'NON_PAYEE'
            
            dette.save()

            # Création de l'opération
            Remboursement.objects.create(
                dette=dette,
                type=op_type,
                montant=montant,
                note=motif
            )
            
            messages.success(request, f"Opération {op_type} effectuée.")
        except ValueError:
            messages.error(request, "Montant invalide.")
            
    return redirect('dettes:detail_dette', id=id)