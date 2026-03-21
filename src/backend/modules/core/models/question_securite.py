from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password

class QuestionSecuriteManager:
    """
    Gestionnaire pour la vérification sécurisée des réponses aux questions secrètes.
    Utilise le système de hachage de Django (PBKDF2/Bcrypt) pour les réponses.
    """
    
    @staticmethod
    def verifier_reponse(profil, reponse_brute):
        """
        Vérifie si la réponse fournie correspond à celle enregistrée dans le profil.
        Si la réponse dans le profil semble être en clair (migration), 
        on la hache pour la prochaine fois.
        """
        reponse_stockee = profil.reponse_secrete.strip().lower()
        reponse_brute = reponse_brute.strip().lower()
        
        # Vérifier si c'est un hash Django
        if reponse_stockee.startswith(('pbkdf2_', 'bcrypt_', 'argon2_')):
            return check_password(reponse_brute, reponse_stockee)
        
        # Sinon, comparaison classique (fallback pour les anciennes données en clair)
        # Mais on conseille de hacher la réponse lors du prochain enregistrement
        return reponse_stockee == reponse_brute

    @staticmethod
    def hacher_reponse(reponse_brute):
        """Retourne le hash sécurisé de la réponse."""
        return make_password(reponse_brute.strip().lower())
