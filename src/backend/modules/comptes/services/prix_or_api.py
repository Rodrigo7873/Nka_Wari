import requests
from datetime import datetime
from modules.core.services.prix_or_service import set_prix_or

def recuperer_prix_or_depuis_api():
    """
    Récupère le prix de l'or via MetalpriceAPI (gratuit, sans clé)
    """
    try:
        # API publique gratuite
        url = "https://api.metalpriceapi.com/v1/latest?base=XAU&currencies=GNF"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Le prix est dans data['rates']['GNF']
            prix_par_once = data.get('rates', {}).get('GNF', 0)
            
            if prix_par_once:
                # 1 once = 31.1035 grammes
                prix_par_gramme = prix_par_once / 31.1035
                
                # Sauvegarde via service central
                set_prix_or(int(prix_par_gramme))
                return True
    except Exception as e:
        # Log minimal: conserver la gestion d'erreur sans affichage console
        return False
    
    return False