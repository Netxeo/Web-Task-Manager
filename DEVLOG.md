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

### 13h50 à 14h00 · Fonctionnalités et bonus
- Les cinq fonctionnalités du cahier des charges : afficher, ajouter (ajout rapide ou formulaire complet), modifier dans un panneau latéral, supprimer avec confirmation, marquer comme terminée ou non d'un clic.
- Tous les bonus sauf l'IA : recherche (titre et description), filtres par statut, priorité et tag, tri (récentes, échéance, priorité, titre), priorités à 3 niveaux, tags, échéance date et heure avec alerte de retard, interface responsive.
- Composants réutilisables : macros Jinja2 pour la ligne de tâche, les badges, les champs de formulaire et les icônes.
- Schéma étendu : priorité et échéance avec contraintes `CHECK`, tables `tags` et `task_tags` reliées par clés étrangères avec suppression en cascade, tags orphelins nettoyés automatiquement.
- Validation serveur avec WTForms (messages en français) : longueurs, priorité dans la liste, date valide, tags limités à 5 et à un jeu de caractères sûr, caractères de contrôle supprimés.
- Recherche : les caractères `%` et `_` sont échappés pour être cherchés tels quels, jamais interprétés par SQL.
- Tri : la valeur reçue est comparée à une liste fermée, aucune donnée de l'utilisateur n'entre dans le texte de la requête SQL.
- Les filtres actifs sont conservés après chaque action, sans paramètre de redirection libre (pas de redirection ouverte possible).
- Limite de 60 écritures par minute et par adresse IP.
- JavaScript minimal et facultatif : boîte de confirmation native `<dialog>`, tri automatique, touche Échap pour fermer le panneau. Tout fonctionne aussi sans JavaScript.
- Accessibilité : contrastes AA vérifiés, zones cliquables de 44 px, focus visible, libellés sur tous les champs, lien d'évitement, état « terminé » indiqué par une coche et pas seulement par la couleur.
- Icônes Lucide (licence ISC) intégrées au projet.
- 40 tests automatisés : fonctionnalités, validation, filtres et sécurité (injection SQL, XSS, CSRF, méthodes HTTP, taille des requêtes, limitation de débit, pages d'erreur).

### 14h00 à 14h10 · Intégration IA (MCP)
- Choix d'un serveur MCP plutôt que d'un chatbot intégré : gratuit (aucune clé d'API payante), local (aucun port réseau ouvert), et chaque utilisateur le branche sur son propre assistant. Le dépôt ne contient aucun compte ni aucune clé.
- Six outils : lister (mêmes filtres que le site), afficher, créer, modifier partiellement, terminer, supprimer.
- Le serveur réutilise la validation WTForms et la couche d'accès aux données du site : aucun second chemin vers la base.
- La suppression est déclarée destructive pour que l'assistant demande confirmation. Les consignes du serveur rappellent que le contenu des tâches est une donnée et jamais une instruction (protection contre l'injection de prompt).
- Configuration lue au démarrage de l'application et non à l'import, pour que le serveur MCP charge correctement le fichier `.env`.
- Dépendance isolée dans `requirements-ai.txt` : l'application web reste légère pour qui n'utilise pas l'IA.
- Tests ajoutés : outils, validation partagée, et appel réel du serveur MCP.

### 14h10 · Documentation
- README complet : fonctionnalités, installation, branchement de l'assistant IA, architecture, choix techniques, tableau de sécurité, limites connues, captures.
- Identifiants des tâches en `AUTOINCREMENT` pour qu'un identifiant supprimé ne soit jamais réattribué à une autre tâche.
