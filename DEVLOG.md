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

### 14h15 à 14h35 · Recherche UX et réorganisation
- Recherche sur la psychologie des listes de tâches et les interfaces de référence (Things 3, Todoist, Microsoft To Do, Linear). Principaux enseignements :
  - une liste groupée et des vues courtes réduisent le temps de décision (lois de Hick et de Miller) ;
  - montrer la progression motive à terminer (gradient d'objectif, Kivetz et al., 2006) ;
  - les petites victoires sont le premier moteur de motivation, et un revers pèse 2 à 3 fois plus qu'un progrès (Amabile & Kramer) ;
  - l'idée qu'on se souvient mieux des tâches inachevées (effet Zeigarnik) n'est pas confirmée par la méta-analyse de Ghibellini & Meier (2025), contrairement à la tendance à reprendre une tâche interrompue (effet Ovsiankina).
- Nouvelles vues : Aujourd'hui (en retard et du jour), À venir (7 prochains jours), À faire, Terminées.
- Liste groupée par moment : En retard, Aujourd'hui, Demain, Dans les 7 jours, Plus tard, Sans échéance. Les terminées sont groupées par date de fin.
- En-tête avec la date du jour et la progression « X sur Y faites aujourd'hui ». Nouvelle colonne `completed_at` pour dater chaque tâche terminée.
- Une tâche ajoutée sans échéance depuis « Aujourd'hui » indique qu'elle a rejoint « À faire », pour ne jamais donner l'impression qu'elle a disparu.
- Réorganisation des dossiers : infrastructure dans `app/core/`, CSS rangé en `base/`, `layout/` et `components/`, licences tierces dans `licenses/`, tests rangés comme le code.
- 51 tests automatisés.

### 14h50 à 15h30 · Refonte en Kanban (style Bordio / Trello)
- Retour d'utilisation : une liste unique ne convient pas. Passage à un **tableau Kanban** en colonnes verticales : Nouvelles, Planifiées, En cours, Terminées. Dans chaque colonne, les cartes sont classées automatiquement par priorité.
- **Planner semaine** : 7 colonnes de jours et une colonne « Sans date ». Les anciennes vues Aujourd'hui et À venir sont remplacées par ce planner.
- **Glisser-déposer** avec SortableJS (licence MIT, hébergée dans le projet) : fonctionne à la souris et au doigt, contrairement au glisser-déposer natif du navigateur. Après chaque déplacement, la zone du tableau est rechargée depuis le serveur, qui reste la seule source de vérité.
- **Fiche de tâche à onglets** : Détails, Sous-tâches (avec progression), Commentaires (notes datées), Fichiers et liens. Les onglets marchent aussi sans JavaScript.
- Nouvelle colonne `status` qui remplace `is_done`, nouvelles tables `subtasks`, `comments`, `links`, `attachments`, toutes reliées à la tâche avec suppression en cascade. Version du schéma vérifiée au démarrage.
- **Fichiers joints sécurisés** : PDF, PNG, JPG, 5 Mo, signature du contenu vérifiée, nom aléatoire, stockage hors du dossier public, téléchargement forcé avec CSP `sandbox`, fichiers supprimés du disque avec la tâche.
- **Liens** limités à `http` et `https`, ouverts avec `noopener noreferrer`.
- Les requêtes classiques restent limitées à 16 Ko : seule la route d'envoi de fichier accepte un corps plus gros.
- Code découpé : `tasks/data/` (requêtes SQL), `tasks/routes/` (routes), formulaires de détail séparés.
- Serveur MCP mis à jour : déplacer une tâche, ajouter une sous-tâche ou un commentaire.
- Design : cartes de couleur unie selon la priorité, sans barre colorée sur le côté, contrastes de texte de 5:1 minimum.
- 74 tests automatisés, `pip-audit` sans vulnérabilité.

### 15h35 · Palette plus douce
- Retour d'utilisation : gris trop sombres et couleurs trop ternes.
- Gris éclaircis (fond `#F8FAFB`, colonnes `#F0F3F6`, bordures `#D5DDE2`).
- Cartes en pastels plus lumineux : Haute `#FFE3DE`, Moyenne `#FFF1CF`, Basse `#DFEEFF`, Aucune blanc.
- La couleur vive passe sur les icônes et le cercle de la carte ; le texte reste foncé et neutre. Contraste du texte toujours au-dessus de 5:1, icônes au-dessus de 3:1.

### 15h50 · Audit de sécurité
- Relecture complète du code, avec `bandit` et `pyflakes` en plus des tests.
- Identifiants trop grands dans l'URL (ex. `/tasks/99999999999999999999`) : ils provoquaient une erreur 500. Un convertisseur de route limite maintenant les identifiants à l'intervalle accepté par SQLite, réponse 404.
- Semaine du planner hors calendrier (`week=9999-12-31`) : retour à la semaine courante au lieu d'une erreur.
- Limites des sous-tâches, commentaires, liens et fichiers vérifiées dans la requête `INSERT` elle-même, pour qu'aucun envoi simultané ne puisse les dépasser.
- Requêtes de suppression des détails écrites en dur, sans construction de chaîne.
- Glisser-déposer : si le réseau coupe, la page se recharge au lieu de rester dans un état faux.
- Corps envoyés sans `Content-Length` : la lecture s'arrête à 16 Ko.
- 77 tests automatisés, `pip-audit` sans vulnérabilité.

### 16h00 · Audit complet avec le skill de sécurité
- Passage en revue des 25 catégories du skill `skill-file-security`, en ne gardant que celles qui concernent le projet.
- **Fichiers joints** : les images sont décodées puis réenregistrées avec Pillow. Un faux PNG est refusé, les métadonnées (GPS, appareil) disparaissent, l'orientation de la photo est gardée, les images géantes sont refusées. Les PDF avec JavaScript, actions de lancement ou fichiers cachés sont refusés, même quand le mot est camouflé (`/J#61vaScript`).
- **Noms trompeurs** : les caractères invisibles d'inversion de texte sont supprimés des titres, commentaires et noms de fichiers (`facture[inversion]fdp.exe` devient `facturefdp.exe`). Tags normalisés en Unicode pour éviter deux tags identiques à l'œil.
- **Liens** : le vrai domaine s'affiche à côté du titre, en Punycode pour les domaines qui imitent un autre avec des lettres cyrilliques.
- **Requêtes d'un autre site** : toute écriture signalée par le navigateur comme venant d'un autre site est refusée (403), en plus du jeton CSRF. Cookie de session passé en `SameSite=Strict`.
- **En-têtes** : Trusted Types dans la CSP, `Cross-Origin-Embedder-Policy`, pages jamais mises en cache.
- **SQL** : plus aucune requête assemblée à l'exécution, les filtres facultatifs passent par des paramètres nommés. `bandit` ne signale plus rien.
- **IA** : mode lecture seule pour le serveur MCP (`MCP_READ_ONLY=1`).
- **Dépendances** : toutes épinglées, y compris les indirectes. GitHub Actions lance les tests et `pip-audit` à chaque push, Dependabot propose les mises à jour.
- 90 tests automatisés, `pip-audit` et `bandit` sans alerte.

### 17h55 · Inspection complète des PDF
- Les PDF modernes rangent souvent leurs objets dans des flux compressés : un JavaScript caché à l'intérieur échappait à la recherche simple. Ces flux sont maintenant décompressés et analysés, sans antivirus.
- Plafond de 20 Mo décompressés contre les bombes de décompression. Un PDF chiffré, ou compressé d'une façon que l'application ne sait pas lire, est refusé plutôt qu'accepté sans vérification.
- Vérifié sur 521 PDF réels (dont 100 avec flux compressés) : aucun refusé à tort. Un PDF avec JavaScript caché dans un flux compressé est bien refusé.
- **Bug trouvé en testant de vrais fichiers** : tout envoi de plus de 16 Ko était refusé (413), parce que la limite mémoire des formulaires était plus petite que les morceaux lus par Werkzeug (64 Ko). Limite passée à 128 Ko, avec un test qui envoie une photo et un PDF de plusieurs Mo.
- 99 tests automatisés.

### 19h15 · Qualité du code
- Revue avec `ruff`, `radon` (complexité) et `vulture` (code mort) : aucune fonction trop complexe, aucun code mort.
- Style uniformisé avec `ruff format` (lignes de 120 caractères maximum) et règles `ruff` ajoutées au projet, vérifiées par GitHub Actions à chaque push.
- `render_page` simplifiée : elle prenait 7 paramètres, la fiche ouverte est maintenant décrite par `new_panel` ou `edit_panel`.
- Erreur de tag relancée sans la trace interne (`raise ... from None`).
- 99 tests automatisés, `ruff`, `bandit` et `pip-audit` sans alerte.
