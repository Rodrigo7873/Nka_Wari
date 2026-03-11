from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class MouvementCompte(models.Model):
    TYPE_AJOUT = 'AJOUT'
    TYPE_RETRAIT = 'RETRAIT'
    
    CHOIX_TYPE = [
        (TYPE_AJOUT, 'Ajout'),
        (TYPE_RETRAIT, 'Retrait'),
    ]

    # Un mouvement peut concerner soit un compte argent, soit un compte or
    compte_argent = models.ForeignKey('comptes.CompteArgent', on_delete=models.CASCADE, null=True, blank=True, related_name='mouvements')
    compte_or = models.ForeignKey('comptes.CompteOr', on_delete=models.CASCADE, null=True, blank=True, related_name='mouvements')
    
    type = models.CharField(max_length=10, choices=CHOIX_TYPE)
    montant = models.DecimalField(max_digits=12, decimal_places=3) # Utilise 3 pour l'or aussi
    
    date = models.DateTimeField(auto_now_add=True)
    motif = models.CharField(max_length=255, blank=True)
    cree_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        compte = self.compte_argent or self.compte_or
        return f"{self.type} - {self.montant} ({compte})"
