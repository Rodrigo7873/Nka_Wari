# Générer et Tester le Fichier APK (Application Android)

Maintenant que votre application Django PWA est en ligne sur PythonAnywhere, elle est prête à être transformée en une application qui s'installe officiellement sur n'importe quel téléphone Android.

## 1. Récupération de l'URL Publique Sécurisée
La condition *sine qua non* pour créer l'APK est que votre application soit accessible en **HTTPS**. Sur PythonAnywhere, c'est inclus.
- Le lien de production est : `https://tonusername.pythonanywhere.com`

## 2. Compilation de l'APK (PWA to APK)
Deux méthodes majeures sont recommandées pour empaqueter (packager) votre code en `.apk` et même récupérer le `.aab` (format requis pour la console Google Play Store).

### Méthode A : PWABuilder (Recommandé par Microsoft - Le plus simple)
Cette méthode repose sur un "Trusted Web Activity" respectant intégralement les conditions de sécurité Google Play.
1. Rendez-vous sur le site officiel : **[PWABuilder.com](https://www.pwabuilder.com)**.
2. Saisissez votre URL publique obtenue (ex: `https://tonusername.pythonanywhere.com`).
3. Appuyez sur **Start** (Le service va analyser les icônes, le manifeste JSON et le Service Worker générés).
4. Le service va certifier un bon score grâce au Manifest et SW existants.
5. Cliquez sur **Package for Stores** (Générer le fichier).
6. Optez pour le paquet Android. Modifiez le nom du bundle (`com.nkawari.app`) et le nom de l'application si besoin.
7. Un téléchargement ZIP va se lancer. 
8. Dézippez-le pour récupérer votre fichier `app-release.apk`.

### Méthode B : Application PWA2APK (ou Bubblewrap CLI localement)
Si le site plante ou que vous désirez contrôler la signature via votre console localement, vous pouvez utiliser un outil CLI comme **Bubblewrap** développé par Google.
1. Installez Node.js sur votre poste de travail.
2. Installez CLI bubblewrap via npm :
   ```bash
   npm i -g @GoogleChromeLabs/bubblewrap
   ```
3. Dans un dossier dédié sur votre PC :
   ```bash
   bubblewrap init --manifest=https://tonusername.pythonanywhere.com/static/manifest.json
   bubblewrap build
   ```
4. Vous récupérerez le fichier `.apk` en sortie locale via l'outil. (Vous aurez peut-être besoin du SDK Android fourni et configuré durant cette étape).

## 3. Installation et Test Actif
1. Vous avez extrait le fichier `.apk`.
2. Connectez votre mobile à votre PC en USB ou envoyez le `.apk` par email/Bluetooth/Drive.
3. Sur votre téléphone Android : 
   - Autorisez **"L'installation d'applications provenant de sources inconnues"** depuis vos Paramètres > Sécurité.
   - Cliquez sur l'APK pour l'installer.
4. L'application N'Ka Wari s'affiche dans votre grille d'application sur le téléphone avec la belle icône ronde ou "squircle", au lieu d'être coincée dans le navigateur Chrome.

> **💡 Aide : Mode Standard sans Installation** : Les orpailleurs n'ayant pas envie/les moyens de générer et manipuler un `.apk` peuvent tout aussi bien ouvrir l'url `https://tonusername.pythonanywhere.com` depuis Google Chrome sur leur téléphone, et cliquer sur *Menu* > *Ajouter à l'écran d'accueil*. Le comportement sera identique (Full-Screen / Hors Ligne) !
