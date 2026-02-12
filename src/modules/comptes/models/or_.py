from django.db import models
from modules.core.models.base_model import TimeStampedModel

class CompteOr(TimeStampedModel):
    """
    Compte d'or physique : poids en grammes (3 décimales), carat informatif
    """
    
    nom = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nom du compte or"
    )
    
    poids_grammes = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name="Poids (grammes)"
    )
    
    carat = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Carat (optionnel)"
    )
    
    est_actif = models.BooleanField(
        default=True,
        verbose_name="Compte actif"
    )

    class Meta:
        verbose_name = "Compte Or"
        verbose_name_plural = "Comptes Or"
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} - {self.poids_grammes:.3f} g" + (f" ({self.carat} carats)" if self.carat else "")


class PrixOr(models.Model):
    """
    Prix du jour de l'or en GNF/gramme - Saisie manuelle obligatoire (CDC §5.3)
    """
    
    prix_gramme = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Prix du gramme d'or (GNF)"
    )
    
    date_saisie = models.DateField(
        auto_now_add=True,
        verbose_name="Date de saisie"
    )
    
    class Meta:
        verbose_name = "Prix de l'or"
        verbose_name_plural = "Prix de l'or"
        ordering = ['-date_saisie']
        get_latest_by = 'date_saisie'

    def __str__(self):
        return f"Or: {self.prix_gramme:,.0f} GNF/g - {self.date_saisie}"