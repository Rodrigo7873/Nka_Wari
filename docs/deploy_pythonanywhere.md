# Guide de Déploiement sur PythonAnywhere

Ce guide détaille les étapes simples pour déployer N'Ka Wari sur **PythonAnywhere**, un hébergeur cloud simple et parfaitement adapté pour Python/Django.

## 1. Création du Compte & Console
1. Rendez-vous sur [PythonAnywhere](https://www.pythonanywhere.com/) et créez un compte gratuit (Beginner) ou payant selon vos besoins d'usage.
2. Une fois connecté, vous arrivez sur le **Dashboard** principal.
3. Allez dans l'onglet **Consoles** et lancez une nouvelle console **Bash**.

## 2. Récupération et Upload des Fichiers
Vous pouvez tout cloner depuis Git, ou uploader directement :
1. Dans la console Bash, clonez votre dépôt (si disponible) :
   ```bash
   git clone https://github.com/votre_profil/nkawari.git
   ```
2. *(Alternative Upload manuel)* : Allez dans l'onglet **Files**, et téléversez un ZIP compressé de votre code source, puis utilisez la console Bash pour le dézipper : `unzip source.zip`.

## 3. Configuration de l'Environnement et Base de données
1. **Créer l'environnement virtuel** :
   ```bash
   mkvirtualenv --python=python3.10 myenv
   workon myenv
   ```
2. **Installer les dépendances** :
   Déplacez-vous dans votre projet (là où se trouve `requirements.txt`) et installez vos librairies :
   ```bash
   pip install -r requirements.txt
   ```
3. **Variables d'environnement (Supabase & Securité)** :
   Créez un fichier `.env` à la racine de votre dossier `backend` (ou utilisez les variables de démarrage) :
   ```env
   DEBUG=False
   SECRET_KEY="<clé-sécurisée>"
   SUPABASE_URL="https://xxx.supabase.co"
   SUPABASE_KEY="votre-clé-api"
   DATABASE_URL="postgres://user:pass@serveur-supabase:5432/django"
   ```

## 4. Initialisation de l'Application Web (WSGI)
1. Allez dans l'onglet **Web** du Dashboard PythonAnywhere et cliquez sur **Add a new web app**.
2. Choisissez **Manual configuration** (Configuration manuelle) et votre version de Python (ex: 3.10).
3. **Code & Virtualenv** :
   - Indiquez le chemin vers votre environnement virtuel (ex: `/home/votre_username/.virtualenvs/myenv`).
   - Indiquez le chemin source (ex: `/home/votre_username/nkawari/src/backend`).
4. **Fichier WSGI (`wsgi.py`)** :
   Cliquez sur le fichier WSGI depuis l'onglet Web et modifiez-le pour pointer vers votre application Django :
   ```python
   import os
   import sys
   from dotenv import load_dotenv

   path = '/home/votre_username/nkawari/src/backend'
   if path not in sys.path:
       sys.path.append(path)

   # Charge le fichier .env
   project_folder = os.path.expanduser('~/nkawari/src/backend')
   load_dotenv(os.path.join(project_folder, '.env'))

   os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

## 5. Configuration des Fichiers Statiques
Pour que le design CSS, les icônes et le JS s'affichent :
1. Dans l'onglet **Web**, repérez la section **Static files**.
2. Ajoutez un nouveau chemin :
   - **URL** : `/static/`
   - **Directory** : `/home/votre_username/nkawari/src/backend/staticfiles/`
3. Assurez-vous d'avoir exécuté la collecte (Dans la console Bash) :
   ```bash
   python manage.py collectstatic --noinput
   ```

## 6. Lancement Final
1. En haut de l'onglet **Web**, cliquez sur le gros bouton vert **Reload votre_username.pythonanywhere.com**.
2. Visitez le lien généré (`https://votre_username.pythonanywhere.com`), votre site est en ligne avec le certificat HTTPS fourni gratuitement par PythonAnywhere. Il est désormais prêt pour l'étape de l'APK !
cls