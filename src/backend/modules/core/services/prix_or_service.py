from typing import Optional, Tuple
import requests
from django.utils import timezone

from modules.parametres.models.prix_or import PrixOrParam


def get_latest_prix_or(user=None) -> Optional[PrixOrParam]:
    """Retourne la dernière instance `PrixOrParam` de l'utilisateur ou None."""
    if not user or user.is_anonymous:
        return None
    try:
        return PrixOrParam.objects.filter(cree_par=user).latest()
    except PrixOrParam.DoesNotExist:
        return None


def set_prix_or(prix_gramme: int, user=None) -> Optional[PrixOrParam]:
    """Crée une nouvelle valeur de prix du jour pour l'utilisateur."""
    if not user or user.is_anonymous:
        return None
    return PrixOrParam.objects.create(prix_gramme=prix_gramme, cree_par=user)


def recuperer_prix_or(user=None) -> Tuple[bool, int]:
    """Tente de récupérer le prix depuis une API publique pour l'utilisateur.

    Retourne (succes, prix_gramme)
    - succes=True si l'API a répondu avec un nouveau prix.
    - succes=False si l'API a échoué.
    """
    try:
        # Note: L'URL ci-dessous nécessite normalement une API_KEY (ex: &api_key=...)
        # Sans clé, l'API MetalPrice renverra une erreur 401 ou 403.
        url = "https://api.metalpriceapi.com/v1/latest?base=XAU&currencies=GNF"
        resp = requests.get(url, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                prix_par_once = data.get('rates', {}).get('GNF', 0)
                if prix_par_once:
                    prix_par_gramme = int(prix_par_once / 31.1035)
                    # Enregistrer la nouvelle valeur pour l'utilisateur
                    if user:
                        set_prix_or(prix_par_gramme, user)
                    return True, prix_par_gramme
    except Exception as e:
        print(f"Erreur API Or: {e}")

    # En cas d'échec de l'API, on ne retourne pas True avec l'ancien prix
    # On laisse la vue gérer le message d'erreur
    dernier = get_latest_prix_or(user)
    if dernier:
        return False, int(dernier.prix_gramme)

    return False, 0
