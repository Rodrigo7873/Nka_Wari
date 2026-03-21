from django.db import models
from django.contrib.auth.models import User

class Parametres(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parametres', null=True, blank=True)
    langue = models.CharField(max_length=10, default='fr')
    format_date = models.CharField(max_length=20, default='DD/MM/YYYY')
    format_heure = models.CharField(max_length=10, default='24h')
    notifications_activees = models.BooleanField(default=True)
    theme = models.CharField(
        max_length=10,
        choices=[('clair', 'Clair'), ('sombre', 'Sombre')],
        default='clair'
    )
    version = models.CharField(max_length=10, default='1.0.0')

    class Meta:
        verbose_name = "Paramètre"
        verbose_name_plural = "Paramètres"

    def __str__(self):
        return f"Paramètres de {self.user.username if self.user else 'Inconnu'}"