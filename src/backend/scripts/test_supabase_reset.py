import os
from dotenv import load_dotenv
import requests

# Charger les variables d'environnement
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ Variables SUPABASE_URL ou SUPABASE_KEY non définies dans .env")
    exit(1)

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
}

try:
    # Tenter une requête simple (récupérer la liste des tables)
    response = requests.get(f"{url}/rest/v1/", headers=headers)
    
    if response.status_code == 200:
        print("✅ Connexion réussie !")
        print("📊 Réponse :", response.json())
    else:
        print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"❌ Exception : {e}")