import os
from dotenv import load_dotenv
import requests

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ Variables manquantes dans .env")
    exit(1)

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
}

try:
    response = requests.get(f"{url}/rest/v1/", headers=headers)
    if response.status_code == 200:
        print("[SUCCESS] Connexion réussie !")
        print(response.json())
    else:
        print(f"[ERROR] Erreur {response.status_code}: {response.text}")
except Exception as e:
    print(f"[EXCEPTION] : {e}")
