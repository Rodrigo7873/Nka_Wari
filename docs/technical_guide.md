# Guide Technique & Architecture - N'Ka Wari

## 1. Description PWA et Stack Globale
N'Ka Wari a été pensée et développée avec une architecture souple en **Progressive Web App (PWA)** reposant sur :
- **Backend / API et Routage** : Python 3.10+ avec le framework Django 5+. Le système privilégie le rendu côté serveur (SSR) via des vues avec des templates légers en ajoutant des scripts minimalistes (Vanilla JS).
- **Base de données relationnelle** : PostgreSQL (configurée préférentiellement pour tourner sur _Supabase_), accessible via les outils natifs de Django ORM.
- **Frontend PWA** :
  - Design _Mobile-First_ soigné (CSS natif sans surcharge d'outil lourd tel Tailwind/React) en mettant l'accent sur les performances.
  - Animations CSS pures (Keyframes), et manipulation fine du DOM.
- **Offline Mode (Hors-ligne)** :
  - **Service Worker (`sw.js`)** servant de proxy, qui met en cache systématiquement (`CacheStorage`) les routes CSS, JS, et les vues web pour une utilisation Offline Failback.
  - **IndexedDB (`db.js`, `sync.js`)** s'occupant d'intercepter le navigateur pour conserver la file d'attente (Sync Queue) et réessayer l'appel serveur lors du retour de la connexion réseau (via events listeners d'évènements _online_/_offline_).

## 2. Structure principale du projet (Arborescence)
```text
/ d:\Mes projet\N'ka_Wari\
├── src/
│   ├── backend/                 # Coeur logique (Django)
│   │   ├── config/              # Fichiers cruciaux (settings, asgi, wsgi, urls globales)
│   │   ├── modules/             # Regroupant les applis "apps" créées :
│   │   │   ├── core/            # (Auth, Tableau DB, Profil, Paramètres)
│   │   │   ├── karfa/           # (Comptabilisation de l'or)
│   │   │   ├── dettes/          # (Engagement financier/Emprunts)
│   │   │   ├── comptes/         # (Suivi du fond de Caisse local)
│   │   │   └── pin/             # (Sécurité d'accès applicatif custom)
│   │   ├── static/              # Dossier statique intermédiaire et media upload.
│   │   └── manage.py            # Point de commande.
│   ├── frontend/
│   │   ├── static/              # Fichiers CSS / JS source (base.css, sync.js...)
│   │   │   └── manifest.json    # Intégration PWA pour s'installer comme une App native
│   │   └── templates/           # Layout HTML / Vues (base.html, modules...)
├── docs/                        # Livrables documentaires Markdown.
├── requirements.txt             # Paquets Python indispensables.
└── README.md
```

## 3. Installation et Configuration Locale

### 3.1. Prérequis
- Python 3.10 ou supérieur
- Accès à PostgreSQL (local ou URL de type Supabase distante `postgres://...`)
- Emulateur ou Navigateur basé Chromium (Google Chrome / Edge) pour les tests PWA.

### 3.2. Étapes de mise en oeuvre (Environnement)
1. **Création du Virtual Environment (venv) :**
   ```bash
   python -m venv env
   # Activation sur systèmes Unix/macOS :
   source env/bin/activate  
   # Activation sur Windows :
   env\Scripts\activate   
   ```

2. **Packages et Dépendances :**
   ```bash
   pip install -r requirements.txt
   ```
   *Ce qui installe typiquement `Django`, `psycopg2-binary`, `dj-database-url`, `python-dotenv`.*

3. **Environnement Custom `.env` (à la racine ou sous backend) :**
   Créez le fichier de configuration masqué contenant vos secrets pour activer la sécurité native :
   ```env
   SECRET_KEY="cette-cle-ne-doit-jamais-etre-partagee-au-public"
   DEBUG=True
   DATABASE_URL="postgres://votreutilisateur:motdepasse@serveur_supabase:5432/nom_base"
   ```

4. **Migrations et création structurelle (DB) :**
   Toutes les données de classes `Models` sont mappées via ces commandes :
   ```bash
   cd src/backend
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Création Super Administrateur / tests :**
   *(Optionnel mais utile pour déboguer avec Django-Admin `/admin`)*
   ```bash
   python manage.py createsuperuser
   ```

6. **Lancement du serveur HTTP de développement local :**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
   Rendez-vous sur http://localhost:8000 via votre terminal. Si debug PWA est requis, testez-le via les Outils de Développement de Chrome > Onglet _Application_ > Service Workers.

## 4. Points Clés Techniques Incontournables
- **Auth, Custom User Model & PIN (`pin_middleware`)** :
  L'authentification traditionnelle du package `django.contrib.auth` a été complétée par un modèle personnalisé `AbstractUser` pour autoriser la connexion par téléphone ou email (`backendCustom`). De plus, une couche *Middleware Custom (`core/middleware.py`)* lit régulièrement l'activité `request.session`. En cas d'absence (inactivité), le serveur ordonne une redirection forcée vers la page PIN (`verifier.html`), qui est un mécanisme purement applicatif et frontal sans déconnexion DB formelle, garantissant de ce fait un retour instantané rapide !
- **SyncQueue** (Offline Strategy) : En ajoutant dans chaque vue Django le support des en-têtes/statuts HTTP explicites (par exemple le retour de JSON `{"success": true}` et 200 vs 500 pour les Views `FormTemplate`), les fonctions asynchrones (ex: Bouton d'ajout nouveau Karfa) dans le JS frontal s'intègrent sans rechargement. Si la View échoue (car Offline), alors le script `sync.js` l'intercepte, le met dans la base Locale _IndexedDB_, puis redéclenchera un `fetch()` classique la prochaine fois que le navigateur émet l'évenement API HTML5 `addEventListener("online")`.
