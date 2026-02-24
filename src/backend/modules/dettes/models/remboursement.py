from django.db import models
from .dette import Dette

class Remboursement(models.Model):
    dette = models.ForeignKey(Dette, on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=12, decimal_places=0)
    date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Remboursement de {self.montant} GNF sur {self.dette}"

    class Meta:
        app_label = 'dettes'