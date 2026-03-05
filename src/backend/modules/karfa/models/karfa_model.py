"""
Module 1 : Gestion de Karfa
Modèle Karfa - Cahier des Charges N'ka Wari §2
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Karfa(models.Model):
    """
    Karfa = Dépôt gratuit, sans échéance, conservé dans le solde personnel.
    """
    
    # Statuts conformes au CdC §2.3
    STATUT_ACTIF = 'ACTIF'
    STATUT_PARTIELLEMENT_RENDU = 'PARTIELLEMENT_RENDU'
    STATUT_RENDU_TOTAL = 'RENDU_TOTAL'
    STATUT_EN_LITIGE = 'EN_LITIGE'
    
    CHOIX_STATUT = [
        (STATUT_ACTIF, 'En main'),
        (STATUT_PARTIELLEMENT_RENDU, 'Partiellement rendu'),
        (STATUT_RENDU_TOTAL, 'Rendu totalement'),
        (STATUT_EN_LITIGE, 'En litige'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID'
    )
    
    # Bénéficiaire (celui qui confie l'argent)
    beneficiaire = models.CharField(
        max_length=100,
        verbose_name='Bénéficiaire'
    )
    
    # Montants
    montant_initial = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name='Montant initial (GNF)'
    )
    
    montant_actuel = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name='Montant actuel (GNF)'
    )
    
    devise = models.CharField(
        max_length=3,
        default='GNF',
        editable=False,
        verbose_name='Devise'
    )
    
    # Dates
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )
    
    date_rendu_total = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date de restitution totale'
    )
    
    # Statut et conditions
    statut = models.CharField(
        max_length=20,
        choices=CHOIX_STATUT,
        default=STATUT_ACTIF,
        verbose_name='Statut'
    )
    
    motif = models.TextField(
        blank=True,
        verbose_name='Motif du dépôt'
    )
    
    # Justificatif optionnel (CdC §2.3 : photo optionnelle)
    justificatif = models.ImageField(
        upload_to='karfa/justificatifs/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='Justificatif (photo/reçu)'
    )
    
    # Archivage auto après 30j (CdC §2.3)
    archive = models.BooleanField(
        default=False,
        verbose_name='Archivé'
    )
    
    date_archivage = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date d\'archivage'
    )
    
    # Métadonnées
    cree_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='karfas_crees',
        verbose_name='Créé par'
    )
    
    class Meta:
        verbose_name = 'Karfa'
        verbose_name_plural = 'Karfas'
        ordering = ['-date_creation']
        constraints = [
            models.UniqueConstraint(
                fields=['beneficiaire', 'motif', 'date_creation'],
                name='unique_karfa_par_beneficiaire_motif_date',
                condition=models.Q(archive=False)
            )
        ]
    
    def __str__(self):
        return f"Karfa {self.beneficiaire} - {self.montant_actuel:,.0f} GNF ({self.get_statut_display()})"
    
    def save(self, *args, **kwargs):
        """Initialise montant_actuel = montant_initial à la création."""
        if not self.pk:
            self.montant_actuel = self.montant_initial
        super().save(*args, **kwargs)
    
    @property
    def est_actif(self):
        """Vérifie si le Karfa est actif."""
        return self.statut == self.STATUT_ACTIF
    
    @property
    def montant_rendu(self):
        """Calcule le montant déjà rendu."""
        return self.montant_initial - self.montant_actuel
    
    def restituer(self, montant, note=""):
        """
        Effectue une restitution (totale ou partielle).
        Crée automatiquement un mouvement.
        """
        from .mouvement import MouvementKarfa
        
        if montant > self.montant_actuel:
            raise ValueError("Le montant à restituer dépasse le montant actuel.")
        
        ancien_montant = self.montant_actuel
        self.montant_actuel -= montant
        
        # Mise à jour du statut
        if self.montant_actuel == 0:
            self.statut = self.STATUT_RENDU_TOTAL
            from django.utils import timezone
            self.date_rendu_total = timezone.now()
        else:
            self.statut = self.STATUT_PARTIELLEMENT_RENDU
        
        self.save()
        
        # Créer le mouvement
        MouvementKarfa.objects.create(
            karfa=self,
            type=MouvementKarfa.TYPE_RETRAIT,
            montant=montant,
            solde_apres=self.montant_actuel,
            note=note or f"Restitution de {montant:,.0f} GNF"
        )
        
        return self
    
    def archiver_si_30j(self):
        """
        Auto-archivage après 30 jours pour les KARFA rendus totalement
        """
        from django.utils import timezone
        from datetime import timedelta
        
        if self.statut == self.STATUT_RENDU_TOTAL and self.date_rendu_total:
            if not self.archive:
                delta = timezone.now() - self.date_rendu_total
                if delta.days >= 30:
                    self.archive = True
                    self.date_archivage = timezone.now()
                    self.save()
                    return True
        return False