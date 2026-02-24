from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

from modules.comptes import views as comptes_views
from modules.comptes.models.argent import CompteArgent
from modules.comptes.models.or_ import CompteOr
from modules.parametres.models.prix_or import PrixOrParam
from modules.dettes.models.dette import Dette
from modules.karfa.models.karfa_model import Karfa


User = get_user_model()


class ComptesViewsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_tableau_bord_patrimoine_total(self):
        # Comptes argent
        CompteArgent.objects.create(nom='Compte Principal', type_compte='CASH', solde=100000)

        # Comptes or
        CompteOr.objects.create(nom='Or1', poids_grammes=10.000)

        # Prix or central
        PrixOrParam.objects.create(prix_gramme=500000)

        # Dettes / Créances
        Dette.objects.create(sens='ON_ME_DOIT', montant=20000, personne='Bob')
        Dette.objects.create(sens='JE_DOIS', montant=15000, personne='Carol')

        # Karfa
        Karfa.objects.create(beneficiaire=self.user, montant_initial=5000, montant_actuel=5000)

        # Préparer la requête
        request = self.factory.get('/tableau_bord')
        request.user = self.user

        response = comptes_views.tableau_bord(request)
        content = response.content.decode()

        # Calcul attendu
        total_liquidites = 100000
        total_or = 10.000 * 500000
        total_creances = 20000
        total_dettes = 15000
        patrimoine_expected = int(total_liquidites + total_or + total_creances - total_dettes)

        self.assertEqual(response.status_code, 200)
        self.assertIn(f"{patrimoine_expected} GNF", content)
