# Guide de Déploiement - N'Ka Wari

Pour mettre en production le projet Django et son architecture PWA orientée base de données, la stack finale recommandée doit garantir fiabilité et sécurité (certificats SSL indispensables pour lancer l'App _Service Workers PWA_ du navigateur).
Exemple recommandé :
- **Serveur (OS)** : Machine Virtuelle ou VPS (ex: Ubuntu Server / Debian) ou via PaaS (Heroku/Render).
- **Interface Backend** : `Nginx` agissant en Reverse Proxy, relié à `Gunicorn` pour la gestion des _Threads_ Python en multi-traitements parallèles.
- **Base de données** : PostgreSQL managée (Supabase, AWS RDS...).
- **Fichiers Statiques** : Service et centralisation de la compression via `WhiteNoise` (fourni via Django) ou serveur Apache/Nginx direct.

---

## 1. Préparation du code et variables Secrètes
Votre fichier de configuration `.env` final devra être solidement sécurisé pour empêcher les modes débogage d'exposer d'éventuelles vulnérabilités :
```ini
# Désactiver le Debug Modérateur !
DEBUG=False

# Une très longue chaîne aléatoire (à générer via Secrets Manager / Python `secrets.token_urlsafe()`)
SECRET_KEY="<votre_vraie_clé_complexe_en_prod_-ne-jamais-exposer>"

# Chaîne de connexion complète standard PostgreSQL
DATABASE_URL="postgres://votre_pool_user:password_supabase@host:5432/db_name"

# Hostnames acceptés pour le pare-feu Django (Important)
ALLOWED_HOSTS=.votre-domaine.com,127.0.0.1,localhost

# Confiance croisée (CSRF) via HTTPS protégé 
CSRF_TRUSTED_ORIGINS=https://votre-domaine.com
```

---

## 2. Rassemblement et Stockage des Fichiers Statiques (CSS, JS, PWA)

Vos fichiers de design, images et le manifest de la PWA (`manifest.json`) sont hébergés dans le dossier `front-end` mais Django exige de les recenser tous avant la publication finale pour l'optimisation cache.
Rendez-vous dans la racine et lancez l'ingestion asynchrone :
```bash
python manage.py collectstatic --noinput
```
*Note critique : Vérifiez que le fichier à la racine de vos fichiers statiques, en particulier : `sw.js` (celui déclarant le _Service Worker_ du mode hors-ligne), puisse être capturé soit via `Template Route` Django, soit pointé au même namespace URL du projet, sinon les limites de contexte de sécurité (`scope`) interdiront son installation en mode PWA sur Safari/Chrome.*

---

## 3. Configuration et Lancement de l'Engine Serveur (Gunicorn)
Sur votre cible (Ubuntu/Linux) :
```bash
# Activation et compilation des modules finaux
source env/bin/activate
pip install gunicorn setuptools wheel
```

Tester si le serveur réagit correctement au lancement simple avant de le mettre en service planifié :
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

*(Idéalement, vous allez le gérer de manière pérenne et automatique par le gestionnaire système de lancement, ex: `systemd` / un service `systemctl` pour l'auto-démarrage au boot).*

---

## 4. Configuration du Reverse Proxy Nginx (Portes de l'application)

C'est ici que le SSL/TLS prend le relai.
Ouvrez et éditez un bloc `/etc/nginx/sites-available/nkawari` ou généré par `Certbot` :

```nginx
server {
    listen 80;
    server_name www.nkawari.com nkawari.com;
    
    # Rediriger tout de suite en HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name www.nkawari.com nkawari.com;

    # Certificats SSL ajoutés par Certbot automatisé...
    ssl_certificate /chemin/certbot/fullchain.pem;
    ssl_certificate_key /chemin/certbot/privkey.pem;

    # Gérer la route Proxy vers Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Distribuer directement le Worker à la racine
    location /sw.js {
        alias /votre/racine/src/backend/staticfiles/js/sw.js;
        add_header Cache-Control "no-cache";
    }

    # Fichiers CSS / Images 
    location /static/ {
        alias /votre/racine/src/backend/staticfiles/;
        expires max;
    }
}
```

Activez l'état du site sur Nginx et rechargez le processus métier (`sudo systemctl reload nginx`).

---

## 5. Routine de mise à jour Continue (CI / PULL)

À chaque validation d'un nouveau design ou d'une nouvelle fonction dans l'application locale que vous souhaitez rendre publique :
```bash
# 1. Pull depuis dépôt Github / Gitlab distant
git pull origin main

# 2. Re-préparer / Recréer l'environnement (si modules mis à jour)
source env/bin/activate
pip install -r requirements.txt

# 3. Validation structurale DB et UI caching
python manage.py migrate
python manage.py collectstatic --noinput

# 4. Redémarrage final à chaud des threads Gunicorn (0 interruption)
sudo systemctl restart gunicorn
```
C'est tout. N'Ka Wari tournera à grande échelle (Cloud Native).
