from django.db import models

class AboutInfo(models.Model):
    """
    Module 4.1 - À Propos
    Informations fixes sur l'application et le développeur
    """
    
    nom_application = models.CharField(
        max_length=50,
        default="N'Ka Wari",
        editable=False
    )
    
    version = models.CharField(
        max_length=20,
        default="1.0.0",
        verbose_name="Version"
    )
    
    developpeur = models.CharField(
        max_length=100,
        default="Demba DOUMBOUYA",
        editable=False
    )
    
    email = models.EmailField(
        default="Rodrigodoumbouya@gmail.com",
        editable=False
    )
    
    telephone = models.CharField(
        max_length=20,
        default="+224 628 74 19 60",
        editable=False
    )
    
    localisation = models.CharField(
        max_length=100,
        default="U-de Labé, Guinée",
        editable=False
    )
    
    remerciements = models.TextField(
        default="Cheick Mohamed DIALLO",
        editable=False
    )
    
    class Meta:
        verbose_name = "À Propos"
        verbose_name_plural = "À Propos"
        app_label = 'parametres'
    
    def __str__(self):
        return f"{self.nom_application} v{self.version}"
    
    @classmethod
    def get_info(cls):
        """
        Retourne les informations À Propos (instance unique)
        """
        info, created = cls.objects.get_or_create(pk=1)
        return info