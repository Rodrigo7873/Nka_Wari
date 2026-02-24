from django.test import TestCase
from django.contrib.auth import get_user_model

from modules.karfa.models.karfa_model import Karfa
from modules.karfa.models.mouvement import MouvementKarfa


User = get_user_model()


class KarfaModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='karfa_user', password='testpass')

    def test_restituer_partial_and_total(self):
        k = Karfa.objects.create(
            beneficiaire=self.user,
            cree_par=self.user,
            montant_initial=1000,
            montant_actuel=1000,
            motif='test'
        )

        # Restitution partielle
        k.restituer(400, note='partiel')
        k.refresh_from_db()
        self.assertEqual(int(k.montant_actuel), 600)
        self.assertEqual(k.statut, Karfa.STATUT_PARTIELLEMENT_RENDU)

        m = MouvementKarfa.objects.filter(karfa=k, type=MouvementKarfa.TYPE_RETRAIT).order_by('-date').first()
        self.assertIsNotNone(m)
        self.assertEqual(int(m.montant), 400)
        self.assertEqual(int(m.solde_apres), 600)

        # Restitution totale
        k.restituer(600, note='total')
        k.refresh_from_db()
        self.assertEqual(int(k.montant_actuel), 0)
        self.assertEqual(k.statut, Karfa.STATUT_RENDU_TOTAL)
        self.assertIsNotNone(k.date_rendu_total)
