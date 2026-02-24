from django.core.management.base import BaseCommand
from ...services.prix_or_service import recuperer_prix_or

class Command(BaseCommand):
    help = 'Met à jour le prix de l’or'

    def handle(self, *args, **options):
        succes, prix = recuperer_prix_or()

        if succes:
            self.stdout.write(self.style.SUCCESS(f'Prix mis à jour : {prix} GNF/g'))
        else:
            self.stdout.write(self.style.WARNING('Utilisation du prix par défaut'))