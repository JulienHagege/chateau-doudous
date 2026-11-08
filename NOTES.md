# Le Château des Doudous, notes de reprise

Jeu de maths pour Meryl, la fille de Julien (6 ans, CP, forte en maths), créé les 7 et 8 novembre 2026 avec Claude Code. Pixel art PixelLab, même esprit que Hyrule Conjugaison (Hugo). Dernière mise à jour des notes : 2026-11-08.

## Reprendre le projet en cinq minutes

1. Sources : ce dossier (Dropbox `Applications/Chateau des Doudous`) ou le dépôt GitHub `JulienHagege/chateau-doudous` (`git clone`). Les deux contiennent la même chose, sauf `.git` absent de Dropbox.
2. Construire : `python3 build.py` (concatène `src/part-*.html`, injecte `img/*.png` en data URI, écrit `chateau-doudous.html` pour l'artifact et `index.html` autonome).
3. Tester : `sh tests/run-test.sh` (Chrome headless, 1 à 2 minutes, imprime les lignes de résumé et « aucune erreur »). `tests/test.html` contient le scénario ; `<!--GAME-->` y est remplacé par le jeu.
4. Publier, toujours les trois canaux : (a) artifact claude.ai via l'outil Artifact, fichier `chateau-doudous.html`, URL https://claude.ai/artifact/M53jBPAF8NWtGTfTh3DjCP (capabilities `db` + `user` déjà déclarées) ; (b) `git add -A && git commit && git push` → https://julienhagege.github.io/chateau-doudous/ se redéploie seul en une minute ; (c) `rsync` du dossier vers Dropbox (sans `.git`, sans captures).
5. Ne jamais mêler un appel MCP (PixelLab, Artifact) et une commande Bash dans la même réponse Claude Code : le hook rtk fait échouer la revue du mode auto.

Compte PixelLab (Tier 1) : 8 jobs simultanés max, pas de `create_room`. Style des doudous ancré sur Vachou (objet pro flash 64 px, `style_image` = son URL), décors 192x128 ancrés sur l'image du château (`source_image_id 14e9cd70-b492-5cf9-af08-1e45374bbd0c`). Sprites de l'héroïne : personnage v3 48 px, id `ba857aa5-5808-41a9-9ad4-23ab9b9ee8bc` (sud, nord, est, ouest dans `img/hero*.png`).

Sauvegarde : localStorage `chateau-doudous-v1` sur chaque appareil + document db `data/users/<id>/save` sur le compte claude.ai de Julien (lisible avec ArtifactData, champ `state.lastErr` pour diagnostiquer un bug à distance). Fusion : le plus grand nombre de réponses jouées gagne.

## Les trois canaux de publication (à mettre à jour ensemble)

| Canal | Quoi | Comment |
|---|---|---|
| Artifact claude.ai (synchro entre iPad et Mac via le compte de Julien) | `chateau-doudous.html` (sans doctype) | Outil Artifact, `url` = https://claude.ai/artifact/M53jBPAF8NWtGTfTh3DjCP, capabilities `{db:{}, user:{}}` |
| GitHub Pages (public) | `index.html` | `python3 build.py && git add -A && git commit && git push` dans le dépôt `JulienHagege/chateau-doudous`, site https://julienhagege.github.io/chateau-doudous/ |
| Dropbox (copie hors ligne + sources) | tout le dossier | `~/Library/CloudStorage/Dropbox/Applications/Chateau des Doudous/` |

`build.py` concatène `src/part-*.html`, injecte les PNG de `img/` en data URI (`/*IMG*/`), écrit le source artifact et la version autonome. Il refuse tout tiret cadratin.

## Architecture (un seul fichier, 5 morceaux)

- `part-1-style` : tokens `:root` (thème sombre unique, château de conte), accueil, album, carte, salle, résultat, modale. `part-1b` : orage.
- `part-2-html` : écrans Home, Album, Carte (canvas 20 x 12 tuiles), Salle, Résultat, Orage, modale prénom.
- `part-3-core` : `DOUDOUS` (16, du plus précieux au moins précieux), `FLOORS` (chrono 0 / 25 / 12 / 18 s), `ROOMS` (ordre d'exploration, `rect` et `door` en tuiles, `n` épreuves), état `S`, rangs, son (`SFX`, `MUSIC` séquenceur Web Audio, une boucle par étage + orage).
- `part-4-games` : `GAMES[id].gen(level)` renvoie une question `{prompt, kind:'qcm'|'num'|'custom', options?, answer, render?, show, timeMult?}`. Niveau 1 à la première visite, 2 puis 3 aux rejouées.
- `part-5-engine` : moteur de salle (`startRoom`, `submit`, `endRoom`), carte (`drawMap`, brouillard = salles non débloquées), orage (`startStorm`), accueil, synchro db (`data/users/<id>/save`, fusion par nombre de réponses jouées comme Hyrule), démarrage.

## Règles de jeu (validées par Julien le 2026-11-07)

- Ordre : Crabou près de l'entrée… Vachou (la plus précieuse) au sommet de la Tour, accessible quand les 15 autres sont délivrés. Toutes les salles d'un étage sont ouvertes dès l'arrivée à l'étage, dans l'ordre qu'elle veut (demande de Julien) ; l'étage suivant s'ouvre quand tous les doudous de l'étage sont retrouvés ; le donjon quand les 15 autres le sont.
- Étages : RDC sans chrono (formes, contenances, longueurs, doubles/moitiés, symétrie) ; 1er chrono 25 s (compléments 10/20/30, monnaie, heures/jours/durées, tables 2-3-5-10, soustractions) ; 2e chrono 12 s (additions jusqu'à 100, arrondi, dés et jetons, additions éclair, toutes les tables) ; Tour : boss 15 épreuves en 3 vagues.
- Fonds de salle : 16 images PixelLab 192x128 (`img/bg_<salle>.png`, style ancré sur le château) affichées derrière chaque mini-jeu (`.stage::before`, voile `.stage::after`) et derrière le doudou sur l'écran de résultat. Les énoncés citent le doudou et la salle (Chioune et ses os, Rose et ses coussins, le coffre de Fanfan, les bulles de Lamantou…).
- Niveaux 1 à 5 par salle, contenu différent à chaque niveau (voir `GAMES`, helper `L(level, [...])`) ; au-delà, on reste à 5. Chrono ×0,92 par niveau, billes +3 par niveau.
- Acquis : `S.facts` (a×b : r, w, s = réussites de suite ; sûr à s ≥ 2 ; b×a compte aussi), `S.skills` (par salle : r, w ; acquis à 16 réponses et 90 %). `TABLE_ORDER` = 2, 10, 5, 3, 4, 6, 7, 8, 9 ; `activeTables()` = maîtrisées + les deux suivantes ; `pickFact` privilégie les faits jamais vus ou ratés. Sose : tables actives parmi 2-10-5-3-4 ; Pengouins : toutes les actives ; orage : actives parmi celles de l'étage ; donjon : niveau réussi de chaque salle. Table maîtrisée (10 faits sûrs) = célébration (`maybeCelebrate`, +100 billes, +1 étoile) entre deux épreuves. Carnet (`renderCarnet`) : 9 tables avec les 10 faits colorés, 16 notions avec statut, bouton Réviser = salle `revision` (10 questions : faits ratés + notions en cours, sans effet sur les salles).
- Grenier (Meryl, kangourou clair, ajouté le 2026-11-08, salle `rangement` dans la Tour, à droite du donjon ; le donjon est maintenant [2,1,10,6], porte [7,7], couloir horizontal y 8-9) : comparer deux nombres (2 chiffres puis 3), pair ou impair, « entre deux nombres », « le plus proche de », vrai ou faux, et ranger 3 à 5 boîtes dans l'ordre en les touchant (`order3/4/5`). 17 doudous.
- Salle de jeux (Fanfan, remplace la Salle du trésor le 2026-11-08, migration `complements100` → `des`) : lancer de dés animé (`rollDice`), somme des points ; niveau 1 : 2 dés, 2 : 3 dés, 3 : 2 dés + jetons à l'unité, 4 : 3 dés + jetons en piles de 5, 5 : 4 dés + piles de 10. Bouton « Revoir le lancer ». Fond `img/bg_des.png`.
- Billes (monnaie) : 10/15/20/30 par bonne réponse selon l'étage + bonus vitesse, +50 par salle (+300 au donjon), +20 par citrouille. Chaque erreur coûte la moitié du gain de l'étage (5/8/10/15), une citrouille manquée 10 ; le total ne descend jamais sous 0 (demande de Julien, 2026-11-07). Rangs jusqu'à « Légende des doudous » (4500).
- Étoile : salle réussie sans faute (3 au donjon). 4 étoiles = 1 cœur permanent (5 de base, 10 max). Une erreur = un cœur perdu dans la salle ; 0 cœur = la salle échoue, on rejoue.
- Erreur : la bonne réponse s'affiche avec une explication (`q.explain`, HTML libre via `q.explainHtml` : points par paires pour pair/impair, chiffre décisif souligné pour comparer et ranger, et le dessin de la forme via `q.explainShape`), puis la même épreuve est refaite sans chrono jusqu'à la bonne réponse (`redoQuestion`, comme Hyrule ; bandeau jaune en bas de la scène, au même endroit que le message d'erreur) ; le refaire ne rapporte ni ne coûte rien, la question revient aussi plus tard dans la salle. Jamais la même épreuve que les trois précédentes (`run.seen`).
- En salle : badge doré « Niveau N » avec cinq points dans l'en-tête (demande de Julien), vert « Révision » pour la révision.
- Quitter ou finir une salle ramène sur la carte au bon étage, l'héroïne devant la porte de cette salle (`openMap(étage, salle)`, `lastRoom`) ; la révision ramène à l'accueil.
- Carte : chaque salle montre son décor PixelLab (fenêtre), couloirs pavés avec tapis et torches, portes voûtées, halo de lanterne autour de l'héroïne, silhouette et « ? » tant que le doudou n'est pas retrouvé.
- Orage (remplace l'idée de Lune de sang) : jamais la première salle ni le donjon, dès que 2 salles ont été jouées depuis le dernier, selon l'étage (`STORM_BY_FLOOR`) : RDC 7 %, 4 citrouilles lentes, tables de 2 et 10 avec facteur ≤ 5 ; 1er 11 %, 5 citrouilles, tables 2-3-5-10 ; 2e et Tour 15 %, 6 citrouilles (fréquences baissées de 30 % le 2026-11-08) rapides, toutes les tables. 3 cœurs. Bouton test dans l'espace parents (prend l'étage de la salle en cours).
- Récit : les doudous sont perdus ou cachés, jamais enfermés (demande de Julien). Vocabulaire : « retrouver », « se cache ici », point d'interrogation sur le doudou noirci dans l'en-tête de salle.
- Carte : l'héroïne marche au clavier (flèches, ZQSD/WASD) ou au pavé tactile sous la carte (`heroMove`, `walkable`). Les portes sont des cases à part : dernière rangée de la salle pour les salles du haut (y=4), rangée 7 pour celles du bas, [9,8] pour le donjon ; marcher dessus entre dans la salle, l'escalier en [19,5] monte. Toucher une salle fonctionne toujours.
- Musique : une boucle par salle (`room_<id>` dans `MUSIC_TRACKS`) + accueil, 3 étages, tour, orage ; mélodie + basse + percussions (`perc` : x = grosse caisse, h = charley). Chaque motif est développé en neuf sections (`MUSIC.variants` : motif, aéré, octave, +5, ralenti, basse seule, rétrograde, +7, reprise) dans un ordre tiré au sort à chaque passage : une boucle dure plus d'une minute et ne se répète jamais à l'identique (Julien trouvait les boucles courtes énervantes). Le séquenceur programme les notes 2 s à l'avance.
- Orage plein écran : pluie, éclairs dessinés (`bolt`), secousses, château en fond, yeux de citrouilles qui rôdent ; quand elle répond juste, l'héroïne bondit vers la citrouille (sprite de dos), coup de lanterne en arc, explosion en morceaux ; coup reçu = recul + voile rouge.
- Galerie des sauts : repères de départ (bleu) et d'arrivée (jaune) avec étiquette en cm sur la règle dès le niveau 3 (demande de Julien : on ne voyait pas où tombe Hugo). En plus de mesurer un ruban, comparer, unités et conversions, Hugo saute pour de vrai sur la règle (`hopAnim`) : « de combien a-t-il sauté ? » et « touche la règle là où il va atterrir » (drapeau posé au clic, puis saut animé).
- Symétrie : niveau 1 très doux (4x4, 2 cases près de l'axe, consigne qui dit combien de cases colorier), puis 6x5 (4 cases), 6x6 (axe horizontal), 10x6 ou 8x8 au niveau 4 (11 cases), 12x7 ou 10x8 au niveau 5 (16 cases, deux couleurs) ; taille des cases adaptée à la largeur d'écran.
- Arrondi : la ligne des dizaines n'indique pas où se trouve le nombre ; pile au milieu (5 ou 50), les deux arrondis sont acceptés (demandes de Julien).
- Intro : six tableaux façon livre de contes (`startIntro`), jouée au premier « Entrer dans le château » (`S.introSeen`), rejouable depuis l'accueil.
- Formes : niveau 1 formes de base, niveau 2 + losange, trapèze, parallélogramme, ovale, hexagone, pentagone, octogone et « combien de côtés », niveau 3 solides en volume (cube, pavé droit, boule, cylindre, cône, pyramide).
- Bibliothèque : les quantités sont dessinées en livres sur des étagères (`shelfSvg`, paquets de 10 au-delà de 20) : deux étagères pour le double, une étagère pleine et des paniers vides pour la moitié et le quart, trois ou quatre étagères pour le triple et le quadruple (demande de Julien).
- Aquarium : bulles irisées, la bonne éclate comme du savon (`popBubble`, gouttelettes, son `SFX.pop`), la mauvaise rougit et tremble.
- Cour des os (Chioune) et Salle du trésor (Fanfan) : chrono × 1,5 au niveau 1 (demandes de Julien).
- Boutons de réponse et pavé : fond opaque à 86 %, chiffres plus gros et gras avec ombre (lisibilité sur les fonds, demande de Julien).
- Affichage des épreuves : `q.story` (phrase, petite) + `q.prompt` (calcul, très gros, classe `.prompt.calc`) ; `splitPrompt` découpe automatiquement « Phrase. 5 + ? = 10 » (demande de Julien : pas besoin de lire la phrase pour répondre).
- Typo FR : `fr()` pose l'espace insécable avant ! ? : dans les textes affichés.
- Style : jamais de tiret cadratin, phrases courtes et simples (elle lit bien mais débute), typo FR.
