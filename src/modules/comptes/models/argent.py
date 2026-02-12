from django.db import models
from modules.core.models.base_model import TimeStampedModel

class CompteArgent(TimeStampedModel):
    """
    Compte d'argent : Banque, Mobile Money, Cash, Autre
    """
    
    SOUS_TYPE_CHOIX = [
        ('BANQUE', 'Banque'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('CASH', 'Espèces'),
        ('AUTRE', 'Autre'),
    ]
    
    nom = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nom du compte"
    )
    
    sous_type = models.CharField(
        max_length=20,
        choices=SOUS_TYPE_CHOIX,
        verbose_name="Type de compte"
    )
    
    solde = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name="Solde (GNF)"
    )
    
    est_actif = models.BooleanField(
        default=True,
        verbose_name="Compte actif"
    )

    class Meta:
        verbose_name = "Compte Argent"
        verbose_name_plural = "Comptes Argent"
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.get_sous_type_display()}) - {self.solde:,.0f} GNF"