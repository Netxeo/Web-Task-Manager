# Devlog

Journal de développement du projet, dans l'ordre chronologique.

## Lundi 26 octobre 2026

### 13h00 · Démarrage
- Lecture du cahier des charges : créer, modifier, supprimer et terminer des tâches, en Python, avec une base de données justifiée.
- Création du dépôt public.

### 13h00 à 13h20 · Recherche
- Étude de 10 gestionnaires de tâches : Monday.com, ClickUp, Asana, MeisterTask, Notion, Bubble Plan, Todoist, Microsoft To Do, TickTick et Trello.
- Conventions retenues : navigation dans une barre latérale gauche, ajout rapide toujours visible, case de complétion à gauche du titre, panneau de modification à droite, tâches terminées atténuées.
- Palette tirée d'Adobe Color (« Sticky Task 2 Adjusted ») et vérifiée en contraste WCAG : gris `#404040` pour le texte, bleu `#2E5CE6` pour l'action, vert `#4AB5A0` pour « terminé ».
- Comparaison des bases de données gratuites. SQLite retenue : aucun serveur, aucun port ouvert, aucun identifiant, gratuite sans quota. Les offres cloud gratuites ont été écartées à cause de leurs quotas et de la mise en pause des projets inactifs.
- Licence : PolyForm Noncommercial 1.0.0, pensée pour le logiciel (les licences Creative Commons sont déconseillées pour du code).

### 13h20 à 13h45 · Mise en place
- Choix de Flask : pages rendues par le serveur avec échappement automatique Jinja2, et extensions de sécurité éprouvées (CSRF, limitation de débit).
- Squelette de l'application : fabrique d'application, configuration par variables d'environnement, connexion SQLite par requête, schéma `STRICT` avec contraintes `CHECK`.
- Sécurité de base : en-têtes HTTP stricts (CSP sans script inline, anti-clickjacking, nosniff), protection CSRF, limitation de débit, pages d'erreur sans fuite d'information, refus de démarrer sans clé secrète solide.
- Mise en page : barre latérale gauche et zone principale, version mobile.
- Premiers tests automatisés : page d'accueil, 404, en-têtes de sécurité, clé secrète, contraintes de la base.
- `pip-audit` : aucune vulnérabilité connue dans les dépendances.

### 13h40 · Typographie
- Comparaison de 5 polices sur une vraie liste de tâches : Atkinson Hyperlegible Next, Source Sans 3, IBM Plex Sans, Lexend et Inter.
- Critère principal : une liste de tâches se lit des centaines de fois par jour, la police doit être calme et ne jamais faire hésiter entre deux caractères.
- Choix : **Atkinson Hyperlegible Next** pour le texte, **Atkinson Hyperlegible Mono** pour les dates et compteurs. Conçue par le Braille Institute pour la lisibilité : I, l et 1 ont chacun une forme distincte, le zéro est barré pour ne jamais être confondu avec un O.
- Écartées : Inter (I majuscule et l minuscule identiques), Lexend (trop large pour une liste), IBM Plex Sans (plus froide), Source Sans 3 (bonne, mais I et l proches).
- Polices hébergées dans le projet (licence SIL OFL 1.1 jointe) : aucune requête vers un service tiers, compatible avec la CSP `font-src 'self'`. Graisses 400 et 600 uniquement, pour rester léger à l'œil.

### Prochaine étape
Les cinq fonctionnalités du cahier des charges : afficher, ajouter, modifier, supprimer, marquer comme terminée.
