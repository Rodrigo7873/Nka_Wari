from django.core.management.base import BaseCommand
from modules.dettes.models import Dette

class Command(BaseCommand):
    help = 'Archive les dettes payées depuis plus de 30 jours'

    def handle(self, *args, **options):
        dettes = Dette.objects.filter(archive=False, statut='PAYEE')
        compteur = 0
        for dette in dettes:
            if dette.archiver_si_payee_depuis_30j():
                compteur += 1
        self.stdout.write(f"{compteur} dette(s) archivée(s).")