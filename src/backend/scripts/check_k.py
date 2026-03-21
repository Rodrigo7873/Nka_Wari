import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from modules.karfa.models import Karfa
from django.db.models import Sum, Max, F

print("--- Query with Join ---")
qs1 = Karfa.objects.filter(
    archive=False,
    statut__in=['ACTIF', 'PARTIELLEMENT_RENDU']
).values(
    'beneficiaire__username'
).annotate(
    total=Sum('montant_actuel'),
    der_mouv=Max('mouvements__date')
)
for q in qs1:
    print(q)

print("--- Query without Join ---")
qs2 = Karfa.objects.filter(
    archive=False,
    statut__in=['ACTIF', 'PARTIELLEMENT_RENDU']
).values(
    'beneficiaire__username'
).annotate(
    total=Sum('montant_actuel')
)
for q in qs2:
    print(q)
