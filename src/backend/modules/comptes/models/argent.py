from django.db import models

class CompteArgent(models.Model):
    TYPE_CHOIX = [
        ('BANQUE', 'Banque'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('CASH', 'Espèces'),
        ('DETTE', 'Dettes'),
        ('AUTRE', 'Autre'),
    ]

    nom = models.CharField(max_length=50) # Retrait de unique=True car plusieurs utilisateurs peuvent avoir un compte "Cash"
    cree_par = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='comptes_argent', null=True)
    type_compte = models.CharField(max_length=20, choices=TYPE_CHOIX)
    solde = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    # Nouveau champ pour lier à une dette si type_compte == 'DETTE'
    dette_liee = models.ForeignKey('dettes.Dette', on_delete=models.SET_NULL, null=True, blank=True, related_name='comptes_argent_lies')
    date_creation = models.DateTimeField(auto_now_add=True)
    archive = models.BooleanField(default=False)
    date_archivage = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.nom} ({self.cree_par.username}) – {self.solde} GNF"