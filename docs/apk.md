# Guide de Génération d'APK (PWA to APK)

Transformer la PWA N'Ka Wari en une véritable application Android natif `.apk` (ou `.aab` pour le Play Store) est très simple grâce aux outils modernes comme PWABuilder. L'application est déjà conçue techniquement et validée (Score 100% PWA sur Lighthouse) pour cela.

## Prérequis Indispensables
1. **Application en ligne et sécurisée** : Votre PWA doit être déployée sur votre serveur final (ex: `https://votre-app-nkawari.com`).
2. **Certificat SSL (HTTPS)** : Sans un cadenas sécurisé, aucune génération d'APK ne fonctionnera.
3. **Le fichier Manifest & SW** : C'est déjà configuré dans le code (Service worker valide, toutes les icônes PWA de 72px à 512px générées).

---

## Méthode 1 : Utilisation de PWABuilder (Recommandé par Microsoft/Android)

Cette méthode génère un composant "Trusted Web Activity" (TWA), le standard certifié par le Google Play Store.

### Étape 1 : Analyser le lien
1. Rendez-vous sur le site officiel : [PWABuilder.com](https://www.pwabuilder.com/).
2. Saisissez l'URL de votre application N'Ka Wari en ligne (ex: `https://www.nkawari.com`).
3. Cliquez sur **Start**.

### Étape 2 : Vérification du Score
1. PWABuilder va analyser l'URL. Grâce aux optimisations apportées au code, vous devriez obtenir la mention `Great!` ou des notes maxées sur Security, Manifest, et Service Worker.
2. Si un avertissement apparaît sur un point de configuration, vérifiez simplement que l'URL testée est exactement la bonne (avec et sans www).

### Étape 3 : Génération et Compilation
1. En haut à droite ou en bas de la page, cliquez sur le bouton **Package for Stores** (ou *Build My PWA*).
2. Sélectionnez l'option **Android**.
3. Dans la boîte de dialogue Android :
   - Assurez-vous que le Bundle ID (ex: `com.orpaillage.nkawari`) correspond à vos besoins futurs sur le Play Store.
   - Entrez un nom ("N'Ka Wari") et le mode Affichage (choisissez *Standalone* ou *Fullscreen*).
4. Cliquez sur **Generate** (ou *Download*).
5. Un fichier ZIP sera téléchargé sur votre ordinateur.

### Étape 4 : Extraction et Installation (Sideloading)
1. Décompressez le `.zip` de PWABuilder.
2. Vous y trouverez un fichier avec l'extension `.apk` (généralement dans le dossier `/app/build/outputs/apk/release` ou à la racine de l'archive selon la mise à jour de l'outil).
3. Transférez le fichier `.apk` sur votre téléphone Android.
4. Ouvrez le fichier sur le téléphone et autorisez *l'installation depuis des sources inconnues* si celà est demandé.
5. L'icône N'Ka Wari sera ajoutée sur l'accueil de votre téléphone. L'application se lancera nativement.

---

## Méthode 2 : Méthode Simple PWA2APK / BubbleWrap

Si vous souhaitez éviter PWABuilder ou l'utiliser en ligne de commande locale, la méthode BubbleWrap CLI de Google est disponible pour les développeurs.

### Instructions CLI
1. Assurez-vous d'avoir Node.js d'installé et le JDK Java / SDK Android.
2. Installez Bubblewrap via npm :
   ```bash
   npm install -g @GoogleChromeLabs/bubblewrap
   ```
3. Démarrez l'initialisation dans votre dossier vide :
   ```bash
   bubblewrap init --manifest=https://votre-domaine.com/manifest.json
   ```
4. Suivez l'assistant interactif (gardez la plupart des composants par défaut).
5. Compilez pour obtenir votre APK (et .aab) :
   ```bash
   bubblewrap build
   ```
6. Le fichier `app-release-signed.apk` apparaîtra dans votre dossier. Testez-le directement par adb ou transférez-le.

---

## Mode d'installation Rapide par le Navigateur (Non-APK)
Rappelez-vous qu'on n'a même pas forcément besoin d'un APK : Les utilisateurs visitant le site en URL pure pourront utiliser la fonctionnalité **"Ajouter à l'écran d'accueil"** (Invite A2HS) que le navigateur Mobile (Chrome/Safari) affichera automatiquement grâce au fameux script `manifest.json`.
