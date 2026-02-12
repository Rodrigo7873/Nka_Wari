from django.db import models

class TypeDette(models.TextChoices):
    EMPRUNT_LIQUIDE = 'EMPRUNT_LIQUIDE', 'Emprunt liquide'
    CREDIT_ACHAT = 'CREDIT_ACHAT', 'Crédit achat'
    PRET = 'PRET', 'Prêt'

class SensDette(models.TextChoices):
    JE_DOIS = 'JE_DOIS', 'Je dois'
    ON_ME_DOIT = 'ON_ME_DOIT', 'On me doit'

class StatutDette(models.TextChoices):
    NON_PAYEE = 'NON_PAYEE', 'Non payée'
    PARTIELLEMENT_PAYEE = 'PARTIELLEMENT_PAYEE', 'Partiellement payée'
    PAYEE = 'PAYEE', 'Payée'
    EN_LITIGE = 'EN_LITIGE', 'En litige'