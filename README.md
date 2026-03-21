# N'Ka Wari 

N'Ka Wari est une **Progressive Web App (PWA) de gestion métier** dédiée aux professionnels de l'orpaillage en Guinée (et en Afrique de l'Ouest). Elle permet de gérer de manière simple, robuste et sécurisée les opérations de karfa (réception/don d'or), les dettes (aides financières) et les différents comptes (Liquidité, Caisse) associés à l'activité, y compris en mode hors-ligne.

## Livrables
Toute la documentation complète du projet se trouve dans le sous-dossier `docs/` pour répondre aux exigences du CDC :
- **[Guide Utilisateur](docs/user_guide.md)** : Mode d'emploi couvrant toutes les fonctionnalités (Inscription, Karfa, Dettes, Profils).
- **[Guide Technique](docs/technical_guide.md)** : Manuel d'installation, configuration et architecture globale (Django, PWA).
- **[Déploiement](docs/deployment.md)** : Instructions pas à pas pour la mise en production via Nginx / Gunicorn.

## Caractéristiques Principales
1. **Interface Moderne** : Design soigné (Premium), notifications animées, icônes fluides, et thèmes dynamiques.
2. **Dashboard de Gestion Synthétique** : Aperçu net et clair du patrimoine global avec bouton de confidentialité ("Mode discret" pour cacher ou rendre flou les montants).
3. **Sécurité Forte avec Code PIN** : Connexion par mot de passe et un code PIN sécurisé (à 4 chiffres) pour le confort quotidien (re-connexion facile avec verrouillage automatique après expiration).
4. **App (Offline-First)** : Interface web intégrée fonctionnant comme une application native, permettant de comptabiliser vos chiffres même en pleine brousse (sans réseau). La "synchronisation au serveur" s'effectue automatiquement au retour du réseau.