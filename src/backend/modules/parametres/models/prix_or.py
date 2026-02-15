from django.db import models

class PrixOrParam(models.Model):
    """
    Paramètre : Prix du jour de l'or en GNF/gramme
    Saisie manuelle obligatoire - Une seule entrée (la plus récente fait foi)
    """
    
    prix_gramme = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Prix du gramme d'or (GNF)"
    )
    
    date_saisie = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de saisie"
    )
    
    class Meta:
        verbose_name = "Paramètre - Prix de l'or"
        verbose_name_plural = "Paramètres - Prix de l'or"
        get_latest_by = 'date_saisie'
        app_label = 'parametres'
    
    def __str__(self):
        return f"Prix Or: {self.prix_gramme:,.0f} GNF/g - {self.date_saisie.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def get_prix_jour(cls):
        """
        Retourne le dernier prix saisi
        """
        try:
            return cls.objects.latest()
        except cls.DoesNotExist:
            return None