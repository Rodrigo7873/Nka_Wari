from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Dette(models.Model):
    SENS_CHOICES = [
        ('JE_DOIS', 'Je dois'),
        ('ON_ME_DOIT', 'On me doit'),
    ]

    STATUT_CHOICES = [
        ('NON_PAYEE', 'Non payée'),
        ('PARTIELLEMENT_PAYEE', 'Partiellement payée'),
        ('PAYEE', 'Payée'),
        ('EN_LITIGE', 'En litige'),
    ]

    sens = models.CharField(max_length=20, choices=SENS_CHOICES)
    montant = models.DecimalField(max_digits=12, decimal_places=0)
    montant_restant = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    personne = models.CharField(max_length=100)
    motif = models.TextField(blank=True)
    echeance = models.DateField(null=True, blank=True)
    garantie = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='NON_PAYEE')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_dernier_paiement = models.DateTimeField(null=True, blank=True)
    archive = models.BooleanField(default=False)
    date_archivage = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_sens_display()} – {self.personne} – {self.montant} GNF"

    class Meta:
        app_label = 'dettes'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.montant_restant = self.montant
        super().save(*args, **kwargs)

    # ✅ méthode ajoutée à l'intérieur de la classe
    def archiver_si_payee_depuis_30j(self):
        if self.statut == 'PAYEE' and self.date_dernier_paiement:
            delta = timezone.now() - self.date_dernier_paiement
            if delta.days >= 30 and not self.archive:
                self.archive = True
                self.date_archivage = timezone.now()
                self.save()
                return True
        return False