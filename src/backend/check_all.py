import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from modules.karfa.models import Karfa
from django.db.models import Sum

queryset = Karfa.objects.filter(archive=False)
print("ALL NON-ARCHIVED KARFAS:")
for k in queryset:
    print(f"BENE: {k.beneficiaire.username}, ID: {k.id}, MONTANT: {k.montant_actuel}, STAT: {k.statut}")
