from django.db import models
from django.contrib.auth.models import User

class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    identifiant = models.CharField(max_length=20, unique=True)
    telephone = models.CharField(max_length=20, blank=True)
    question_secrete = models.CharField(max_length=200)
    reponse_secrete = models.CharField(max_length=200)

    def __str__(self):
        return f"Profil de {self.user.username} ({self.identifiant})"
