from django.db import models
from modules.core.models.base_model import TimeStampedModel

class Remboursement(TimeStampedModel):
    """
    Modèle représentant un paiement/remboursement partiel ou total
    """
    dette = models.ForeignKey(
        'Dette',
        on_delete=models.CASCADE,
        related_name='paiements'
    )
    
    montant = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Montant remboursé (GNF)"
    )
    
    date_paiement = models.DateTimeField(
        auto_now_add=True
    )
    
    note = models.TextField(
        blank=True
    )

    class Meta:
        verbose_name = "Remboursement"
        verbose_name_plural = "Remboursements"
        ordering = ['-date_paiement']
        app_label = 'dettes'