from django.db import models

class Parametres(models.Model):
    langue = models.CharField(max_length=10, default='fr')
    format_date = models.CharField(max_length=20, default='DD/MM/YYYY')
    format_heure = models.CharField(max_length=10, default='24h')
    notifications = models.BooleanField(default=True)
    version = models.CharField(max_length=10, default='1.0.0')

    class Meta:
        verbose_name = "Paramètre"
        verbose_name_plural = "Paramètres"