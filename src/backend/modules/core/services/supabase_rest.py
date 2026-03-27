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

# =============================================================================
# VUE DJANGO POUR LA SYNCHRONISATION PWA -> SUPABASE
# =============================================================================
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def sync_pwa_to_supabase(request):
    """
    Endpoint qui réceptionne la file d'attente hors ligne (la variable 'queue') 
    envoyée par la PWA (sync.js) et la répercute sur Supabase via l'API REST.
    """
    if request.method == "POST":
        try:
            op = json.loads(request.body)
            action_type = op.get("type", "CREATE")
            table = op.get("table")
            data = op.get("data", {})
            
            if not table:
                return JsonResponse({"status": "error", "message": "Table manquante"}, status=400)
                
            # Traitement selon le type d'opération
            if action_type in ["CREATE", "UPDATE"]:
                res = supabase_post(table, data, upsert=True) # last-write-wins method
                if res is not None:
                    return JsonResponse({"status": "success", "result": res}, status=200)
                else:
                    return JsonResponse({"status": "error", "message": "Erreur Supabase"}, status=500)
            
            elif action_type == "DELETE":
                # La suppression via REST nécessite l'ID 
                obj_id = data.get("id")
                if obj_id:
                    url = os.getenv("SUPABASE_URL")
                    headers = get_headers()
                    response = requests.delete(f"{url}/rest/v1/{table}?id=eq.{obj_id}", headers=headers)
                    if response.status_code in [200, 204]:
                        return JsonResponse({"status": "success"}, status=200)
                    
            return JsonResponse({"status": "unhandled_operation"}, status=400)
            
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "JSON invalide"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"status": "method_not_allowed"}, status=405)