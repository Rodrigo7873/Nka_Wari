from django.db import models

class TimeStampedModel(models.Model):
    """
    Modèle abstrait qui ajoute les champs date_creation et date_modification
    """
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True