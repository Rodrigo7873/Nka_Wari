import os
import requests
import uuid
from dotenv import load_dotenv

load_dotenv()

def get_headers():
    key = os.getenv("SUPABASE_KEY")
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

def supabase_get(table, params=None):
    """
    Récupère des données d'une table Supabase.
    """
    url = os.getenv("SUPABASE_URL")
    response = requests.get(f"{url}/rest/v1/{table}", headers=get_headers(), params=params)
    response.raise_for_status()
    return response.json()

def supabase_post(table, data, upsert=True):
    """
    Insère ou met à jour (upsert) des données dans une table Supabase.
    """
    url = os.getenv("SUPABASE_URL")
    headers = get_headers()
    
    # Configuration pour l'UPSERT (évite les erreurs 409 sur les clés primaires existantes)
    # Configuration pour l'UPSERT (évite les erreurs 409 sur les clés primaires existantes)
    if upsert:
        headers["Prefer"] = "return=representation,resolution=merge-duplicates"
    else:
        headers["Prefer"] = "return=representation"

    # Conversion des UUID en string pour la sérialisation JSON
    if isinstance(data, list):
        for item in data:
            for k, v in item.items():
                if isinstance(v, uuid.UUID):
                    item[k] = str(v)
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, uuid.UUID):
                data[k] = str(v)

    response = requests.post(f"{url}/rest/v1/{table}", headers=headers, json=data)
    response.raise_for_status()
    
    try:
        return response.json()
    except Exception:
        return None