from typing import Optional, Tuple
import requests
from django.utils import timezone

from modules.parametres.models.prix_or import PrixOrParam


def get_latest_prix_or() -> Optional[PrixOrParam]:
    """Retourne la dernière instance `PrixOrParam` ou None."""
    try:
        return PrixOrParam.objects.latest()
    except PrixOrParam.DoesNotExist:
        return None


def set_prix_or(prix_gramme: int) -> PrixOrParam:
    """Crée une nouvelle valeur de prix du jour."""
    return PrixOrParam.objects.create(prix_gramme=prix_gramme)


def recuperer_prix_or() -> Tuple[bool, int]:
    """Tente de récupérer le prix depuis une API publique.

    Retourne (succes, prix_gramme)
    En cas d'échec, retourne le dernier prix connu ou une valeur par défaut.
    """
    try:
        url = "https://api.metalpriceapi.com/v1/latest?base=XAU&currencies=GNF"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            prix_par_once = data.get('rates', {}).get('GNF', 0)
            if prix_par_once:
                prix_par_gramme = int(prix_par_once / 31.1035)
                # Enregistrer
                set_prix_or(prix_par_gramme)
                return True, prix_par_gramme
    except Exception:
        pass

    dernier = get_latest_prix_or()
    if dernier:
        return True, int(dernier.prix_gramme)

    return False, 75000
