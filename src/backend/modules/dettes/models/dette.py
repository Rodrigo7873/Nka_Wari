from django.db import models
from django.core.exceptions import ValidationError
from modules.core.models.base_model import TimeStampedModel
from modules.dettes.enums import StatutDette

class Dette(TimeStampedModel):
    """
    Modèle représentant une dette ou une créance
    """
    sens = models.CharField(
        max_length=20,
        choices=[('JE_DOIS', 'Je dois'), ('ON_ME_DOIT', 'On me doit')],
        verbose_name="Sens"
    )
    
    montant = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Montant (GNF)"
    )
    
    montant_restant = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Montant restant (GNF)"
    )
    
    personne = models.CharField(
        max_length=100,
        verbose_name="Créancier/Débiteur"
    )
    
    motif = models.TextField(
        blank=True,
        verbose_name="Motif"
    )
    
    echeance = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date d'échéance"
    )
    
    garantie = models.TextField(
        blank=True,
        verbose_name="Garantie"
    )
    
    statut = models.CharField(
        max_length=25,
        choices=StatutDette.choices,
        default=StatutDette.NON_PAYEE,
        verbose_name="Statut"
    )
    
    date_dernier_paiement = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernier paiement"
    )

    class Meta:
        verbose_name = "Dette"
        verbose_name_plural = "Dettes"
        ordering = ['-date_creation']
        app_label = 'dettes'

    def __str__(self):
        if self.sens == 'JE_DOIS':
            return f"Je dois {self.montant_restant} GNF à {self.personne}"
        return f"{self.personne} me doit {self.montant_restant} GNF"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.montant_restant = self.montant
        super().save(*args, **kwargs)
    
    def effectuer_paiement(self, montant, note=""):
        """
        Méthode simple pour enregistrer un paiement
        """
        from .remboursement import Remboursement
        
        if montant <= 0:
            raise ValueError("Le montant doit être positif")
        
        if montant > self.montant_restant:
            raise ValueError("Montant supérieur au restant dû")
        
        Remboursement.objects.create(
            dette=self,
            montant=montant,
            note=note
        )
        
        self.montant_restant -= montant
        from django.utils import timezone
        self.date_dernier_paiement = timezone.now()
        
        if self.montant_restant == 0:
            self.statut = StatutDette.PAYEE
        
        self.save()
        return True