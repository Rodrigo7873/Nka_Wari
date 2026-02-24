from django.db import models

class About(models.Model):
    nom_app = models.CharField(max_length=50, default="N'Ka Wari")
    developpeur = models.CharField(max_length=100, default="Demba DOUMBOUYA")
    email = models.EmailField(default="Rodrigodoumbouya@gmail.com")
    telephone = models.CharField(max_length=20, default="+224 628 74 19 60")
    localisation = models.CharField(max_length=100, default="U-de Labé, Guinée")
    remerciements = models.TextField(default="Cheick Mohamed DIALLO")