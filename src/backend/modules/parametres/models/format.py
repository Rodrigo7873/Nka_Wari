from django.db import models

class FormatParam(models.Model):
    """
    Paramètres de format : Heure 24h, Date JJ/MM/AAAA
    Paramètres globaux de l'application
    """
    
    format_24h = models.BooleanField(
        default=True,
        verbose_name="Format 24h (sinon 12h AM/PM)"
    )
    
    format_date = models.CharField(
        max_length=20,
        default='DD/MM/YYYY',
        editable=False,  # Fixé par CDC
        verbose_name="Format de date"
    )
    
    langue = models.CharField(
        max_length=10,
        default='fr',
        editable=False,  # Fixé par CDC
        verbose_name="Langue"
    )
    
    class Meta:
        verbose_name = "Paramètre - Format"
        verbose_name_plural = "Paramètres - Format"
        app_label = 'parametres'
    
    def __str__(self):
        return f"Format: {'24h' if self.format_24h else '12h'}, {self.format_date}"
    
    @classmethod
    def get_config(cls):
        """
        Retourne la configuration unique (ou crée par défaut)
        """
        config, created = cls.objects.get_or_create(pk=1)
        return config