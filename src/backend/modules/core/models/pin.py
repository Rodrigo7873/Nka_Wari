from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta

class PinUtilisateur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pin_config')
    pin_hash = models.CharField(max_length=128)  # Stocké de manière sécurisée (hashé)
    tentatives = models.IntegerField(default=0)
    bloque_jusqua = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def set_pin(self, raw_pin):
        """Hash le PIN avant de le stocker avec l'algorithme par défaut de Django (PBKDF2/Bcrypt)."""
        self.pin_hash = make_password(raw_pin)
        self.tentatives = 0
        self.bloque_jusqua = None
        self.save()

    def verifier_pin(self, pin):
        """Vérifie le PIN brut par rapport au hash stocké."""
        if self.est_bloque():
            return False
        return check_password(pin, self.pin_hash)

    def est_bloque(self):
        """Vérifie si le compte est actuellement bloqué (15 min)."""
        return self.bloque_jusqua and self.bloque_jusqua > timezone.now()

    def incrementer_tentatives(self):
        """Incrémente les tentatives et bloque après 3 échecs (3 échecs = 15 min)."""
        self.tentatives += 1
        if self.tentatives >= 3:
            self.bloque_jusqua = timezone.now() + timedelta(minutes=15)
        self.save()

    def reset_tentatives(self):
        """Réinitialise le compteur après un succès."""
        self.tentatives = 0
        self.bloque_jusqua = None
        self.save()

    class Meta:
        verbose_name = "PIN Utilisateur"
        verbose_name_plural = "PIN Utilisateurs"
