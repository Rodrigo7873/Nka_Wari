import os
import sys
import django
import requests
import uuid
from decimal import Decimal

# Ajouter le chemin du projet au sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from modules.comptes.models.argent import CompteArgent
from modules.dettes.models.dette import Dette
from modules.karfa.models.karfa_model import Karfa
from modules.karfa.models.mouvement import MouvementKarfa
from modules.dettes.models.remboursement import Remboursement
from modules.comptes.models.or_ import CompteOr
from modules.parametres.models.parametres import Parametres
from modules.parametres.models.about import About

from modules.core.services.supabase_rest import supabase_post

def migrate_model_to_supabase(model_class, supabase_table_name):
    """
    Lit les données de SQLite via l'ORM Django et les insère dans Supabase.
    """
    print(f"\n[INFO] Migration de {model_class.__name__} vers '{supabase_table_name}'...")
    
    records = model_class.objects.all()
    total = records.count()
    print(f"[DATA] {total} enregistrements trouvés dans SQLite.")
    
    if total == 0:
        return
    
    data_to_insert = []
    for obj in records:
        row = {}
        for field in obj._meta.fields:
            field_name = field.name
            value = getattr(obj, field_name)
            
            # Conversion des types spéciaux pour JSON/Supabase
            if isinstance(value, Decimal):
                value = float(value)
            elif isinstance(field, (django.db.models.ForeignKey, django.db.models.OneToOneField)):
                value = value.id if value else None
            elif isinstance(value, uuid.UUID):
                value = str(value)
            elif hasattr(value, 'name') and hasattr(value, 'url'): # Fichiers/Images Django
                try:
                    # On utilise .name qui est plus sûr que .url
                    value = str(value.name) if value and value.name else None
                except (ValueError, Exception):
                    value = None
            elif hasattr(value, 'isoformat'): # Dates et Datetimes
                value = value.isoformat()
            
            row[field_name] = value
        data_to_insert.append(row)
    
    try:
        # Utilisation du client REST (POST)
        result = supabase_post(supabase_table_name, data_to_insert)
        print(f"[SUCCESS] Migration réussie : {len(data_to_insert)} lignes synchronisées.")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Erreur lors de l'insertion dans Supabase : {e}")
        if e.response is not None:
            print(f"   Statut: {e.response.status_code}")
            print(f"   Corps de l'erreur: {e.response.text}")
        else:
            print("   Pas de réponse du serveur")
    except Exception as e:
        print(f"[ERROR] Erreur inattendue : {e}")

if __name__ == "__main__":
    # Liste des migrations à effectuer
    # Assurez-vous que les noms de tables côté Supabase correspondent (en minuscules généralement)
    try:
        # 1. Migration des comptes
        migrate_model_to_supabase(CompteArgent, "compte_argent")
        
        # 2. Migration des dettes
        # Note: Dans le modèle Django c'est 'compte_debit', dans Supabase c'est 'compte_source'
        # On peut adapter les données avant l'envoi si nécessaire
        print(f"\n[INFO] Migration de Dette vers 'dette'...")
        records = Dette.objects.all()
        total = records.count()
        print(f"[DATA] {total} enregistrements trouvés dans SQLite.")
        
        if total > 0:
            data_to_insert = []
            for obj in records:
                row = {
                    "id": obj.id,
                    "sens": obj.sens,
                    "montant": float(obj.montant),
                    "montant_restant": float(obj.montant_restant),
                    "personne": obj.personne,
                    "motif": obj.motif,
                    "echeance": obj.echeance.isoformat() if obj.echeance else None,
                    "garantie": obj.garantie,
                    "statut": obj.statut,
                    "date_creation": obj.date_creation.isoformat() if obj.date_creation else None,
                    "date_dernier_paiement": obj.date_dernier_paiement.isoformat() if obj.date_dernier_paiement else None,
                    "archive": obj.archive,
                    "cree_par": obj.cree_par.id if obj.cree_par else None,
                    "compte_source": obj.compte_debit.id if obj.compte_debit else None,
                }
                data_to_insert.append(row)
            
            try:
                supabase_post("dette", data_to_insert)
                print(f"[SUCCESS] Migration réussie : {len(data_to_insert)} dettes synchronisées.")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Erreur lors de l'insertion dans Supabase : {e}")
                if e.response is not None:
                    print(f"   Corps de l'erreur: {e.response.text}")
        
        # 3. Migration des remboursements
        print(f"\n[INFO] Migration de Remboursement vers 'remboursement'...")
        records = Remboursement.objects.all()
        total = records.count()
        print(f"[DATA] {total} enregistrements trouvés dans SQLite.")
        
        if total > 0:
            data_to_insert = []
            for obj in records:
                row = {
                    "id": obj.id,
                    "dette_id": obj.dette.id if obj.dette else None, # Correction mapping
                    "montant": float(obj.montant),
                    "date": obj.date.isoformat() if obj.date else None,
                    "note": obj.note,
                    "type": obj.type,
                }
                data_to_insert.append(row)
            
            try:
                supabase_post("remboursement", data_to_insert)
                print(f"[SUCCESS] Migration réussie : {len(data_to_insert)} remboursements synchronisés.")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Erreur lors de l'insertion dans Supabase : {e}")
                if e.response is not None:
                    print(f"   Corps de l'erreur: {e.response.text}")

        # 4. Migration de Karfa
        print(f"\n[INFO] Migration de Karfa vers 'karfa'...")
        records = Karfa.objects.all()
        total = records.count()
        print(f"[DATA] {total} enregistrements trouvés dans SQLite.")
        
        if total > 0:
            data_to_insert = []
            for obj in records:
                row = {
                    "id": str(obj.id),
                    "beneficiaire": obj.beneficiaire,
                    "montant_initial": float(obj.montant_initial),
                    "montant_actuel": float(obj.montant_actuel),
                    "motif": obj.motif,
                    "statut": obj.statut,
                    "date_creation": obj.date_creation.isoformat() if obj.date_creation else None,
                    "date_rendu_total": obj.date_rendu_total.isoformat() if obj.date_rendu_total else None,
                    "archive": obj.archive,
                    "date_archivage": obj.date_archivage.isoformat() if obj.date_archivage else None,
                    "cree_par": obj.cree_par.id if obj.cree_par else None,
                    # On retire "justificatif" car la colonne n'existe pas dans le schéma Supabase fourni
                }
                data_to_insert.append(row)
            
            try:
                supabase_post("karfa", data_to_insert)
                print(f"[SUCCESS] Migration réussie : {len(data_to_insert)} karfas synchronisés.")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Erreur lors de l'insertion dans Supabase : {e}")
                if e.response is not None:
                    print(f"   Corps de l'erreur: {e.response.text}")

        # 4b. Migration des Mouvements Karfa (avec correction karfa_id)
        print(f"\n[INFO] Migration de MouvementKarfa vers 'mouvement_karfa'...")
        records = MouvementKarfa.objects.all()
        total = records.count()
        if total > 0:
            data_to_insert = []
            for obj in records:
                row = {
                    "id": str(obj.id),
                    "karfa_id": str(obj.karfa.id) if obj.karfa else None,
                    "type": obj.type,
                    "montant": float(obj.montant),
                    "solde_apres": float(obj.solde_apres),
                    "date": obj.date.isoformat() if obj.date else None,
                    "note": obj.note,
                    "effectue_par": obj.cree_par.id if obj.cree_par else None, # Correction nom attribut
                }
                data_to_insert.append(row)
            try:
                supabase_post("mouvement_karfa", data_to_insert)
                print(f"[SUCCESS] Migration réussie : {len(data_to_insert)} mouvements karfa synchronisés.")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Erreur lors de l'insertion dans Supabase : {e}")
                if e.response is not None:
                    print(f"   Corps de l'erreur: {e.response.text}")
        
        # 5. Migration des comptes Or
        migrate_model_to_supabase(CompteOr, "compte_or")
        
        # 6. Migration des paramètres et infos
        migrate_model_to_supabase(Parametres, "parametres")
        migrate_model_to_supabase(About, "about")
        
        print("\n[FIN] Migration terminée !")
    except Exception as e:
        print(f"[ERROR] Erreur générale : {e}")
