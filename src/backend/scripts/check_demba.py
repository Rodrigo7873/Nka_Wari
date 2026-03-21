import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from modules.karfa.models import Karfa
from django.db.models import Sum

queryset_all = Karfa.objects.filter(beneficiaire__username='Demba', archive=False)
total_all = queryset_all.aggregate(total=Sum('montant_actuel'))['total'] or 0
print(f'TOTAL_ALL_FOR_DEMBA: {total_all}')
for k in queryset_all:
    print(f'ID: {k.id}, MONTANT: {k.montant_actuel}, STATUT: {k.statut}, ARCHIVE: {k.archive}')
