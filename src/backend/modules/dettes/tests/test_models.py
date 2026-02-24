from django.test import TestCase

from modules.dettes.models.dette import Dette
from modules.dettes.models.remboursement import Remboursement


class DetteModelTest(TestCase):
    def test_rembourser_partial_and_total(self):
        d = Dette.objects.create(sens='JE_DOIS', montant=1000, personne='Alice')
        d.refresh_from_db()
        self.assertEqual(int(d.montant_restant), 1000)

        # Paiement partiel
        Remboursement.objects.create(dette=d, montant=400)
        d.montant_restant -= 400
        d.statut = 'PARTIELLEMENT_PAYEE' if d.montant_restant > 0 else 'PAYEE'
        d.save()
        d.refresh_from_db()
        self.assertEqual(int(d.montant_restant), 600)
        self.assertEqual(d.statut, 'PARTIELLEMENT_PAYEE')

        # Paiement total
        Remboursement.objects.create(dette=d, montant=600)
        d.montant_restant -= 600
        d.statut = 'PAYEE' if d.montant_restant == 0 else 'PARTIELLEMENT_PAYEE'
        d.save()
        d.refresh_from_db()
        self.assertEqual(int(d.montant_restant), 0)
        self.assertEqual(d.statut, 'PAYEE')
