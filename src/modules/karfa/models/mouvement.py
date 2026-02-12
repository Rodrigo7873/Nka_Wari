"""
Module 1 : Gestion de Karfa
Modèle MouvementKarfa - Historique des mouvements (CdC §2.3)
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class MouvementKarfa(models.Model):
    """
    Historique complet des mouvements sur un Karfa.
    Chaque entrée/sortie est tracée (CdC §2.3 : Suivie du mouvement de karfa).
    """
    
    # Types de mouvements
    TYPE_CREATION = 'CREATION'
    TYPE_AJOUT = 'AJOUT'
    TYPE_RETRAIT = 'RETRAIT'
    TYPE_ANNULATION = 'ANNULATION'
    
    CHOIX_TYPE = [
        (TYPE_CREATION, 'Création'),
        (TYPE_AJOUT, 'Ajout de fonds'),
        (TYPE_RETRAIT, 'Retrait/Restitution'),
        (TYPE_ANNULATION, 'Annulation'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID'
    )
    
    # Lien vers le Karfa concerné
    karfa = models.ForeignKey(
        'karfa.Karfa',  # Import différé pour éviter circularité
        on_delete=models.CASCADE,
        related_name='mouvements',
        verbose_name='Karfa'
    )
    
    # Type de mouvement
    type = models.CharField(
        max_length=20,
        choices=CHOIX_TYPE,
        verbose_name='Type de mouvement'
    )
    
    # Montant du mouvement (toujours positif)
    montant = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name='Montant (GNF)'
    )
    
    # Solde après l'opération
    solde_apres = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name='Solde après opération (GNF)'
    )
    
    # Date et heure automatiques
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date du mouvement'
    )
    
    # Note explicative
    note = models.TextField(
        blank=True,
        verbose_name='Note/Commentaire'
    )
    
    # Utilisateur ayant effectué l'opération (traçabilité)
    effectue_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mouvements_karfa',
        verbose_name='Effectué par'
    )
    
    # Justificatif optionnel pour ce mouvement spécifique
    justificatif = models.ImageField(
        upload_to='karfa/mouvements/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='Justificatif'
    )
    
    class Meta:
        verbose_name = 'Mouvement de Karfa'
        verbose_name_plural = 'Mouvements de Karfa'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['karfa', '-date']),
            models.Index(fields=['type', 'date']),
        ]
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.montant:,.0f} GNF ({self.date.strftime('%d/%m/%Y %H:%M')})"
    
    @property
    def est_entree(self):
        """Retourne True si c'est une entrée d'argent."""
        return self.type in [self.TYPE_CREATION, self.TYPE_AJOUT]
    
    @property
    def est_sortie(self):
        """Retourne True si c'est une sortie d'argent."""
        return self.type in [self.TYPE_RETRAIT, self.TYPE_ANNULATION]