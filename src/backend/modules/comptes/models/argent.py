from django.db import models

class CompteArgent(models.Model):
    TYPE_CHOIX = [
        ('BANQUE', 'Banque'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('CASH', 'Espèces'),
        ('AUTRE', 'Autre'),
    ]

    nom = models.CharField(max_length=50, unique=True)
    type_compte = models.CharField(max_length=20, choices=TYPE_CHOIX)
    solde = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} – {self.solde} GNF"