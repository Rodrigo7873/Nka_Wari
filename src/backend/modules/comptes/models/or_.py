from django.db import models

class CompteOr(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    poids_grammes = models.DecimalField(max_digits=10, decimal_places=3)
    carat = models.IntegerField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    archive = models.BooleanField(default=False)
    date_archivage = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.nom} – {self.poids_grammes} g"