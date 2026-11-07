# Le Château des Doudous, notes de reprise

Jeu de maths pour la fille de Julien (6 ans, CP, forte en maths), créé le 2026-11-07 avec Claude Code. Pixel art PixelLab, même esprit que Hyrule Conjugaison (Hugo).

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
- Étages : RDC sans chrono (formes, contenances, longueurs, doubles/moitiés, symétrie) ; 1er chrono 25 s (compléments 10/20/30, monnaie, heures/jours/durées, tables 2-3-5-10, soustractions) ; 2e chrono 12 s (additions jusqu'à 100, arrondi, compléments 50/100, additions éclair, toutes les tables) ; Tour : boss 15 épreuves en 3 vagues.
- Fonds de salle : 16 images PixelLab 192x128 (`img/bg_<salle>.png`, style ancré sur le château) affichées derrière chaque mini-jeu (`.stage::before`, voile `.stage::after`) et derrière le doudou sur l'écran de résultat. Les énoncés citent le doudou et la salle (Chioune et ses os, Rose et ses coussins, le coffre de Fanfan, les bulles de Lamantou…).
- Niveaux 1 à 5 par salle, contenu différent à chaque niveau (voir `GAMES`, helper `L(level, [...])`) ; au-delà, on reste à 5. Chrono ×0,92 par niveau, billes +3 par niveau.
- Acquis : `S.facts` (a×b : r, w, s = réussites de suite ; sûr à s ≥ 2 ; b×a compte aussi), `S.skills` (par salle : r, w ; acquis à 16 réponses et 90 %). `TABLE_ORDER` = 2, 10, 5, 3, 4, 6, 7, 8, 9 ; `activeTables()` = maîtrisées + les deux suivantes ; `pickFact` privilégie les faits jamais vus ou ratés. Sose : tables actives parmi 2-10-5-3-4 ; Pengouins : toutes les actives ; orage : actives parmi celles de l'étage ; donjon : niveau réussi de chaque salle. Table maîtrisée (10 faits sûrs) = célébration (`maybeCelebrate`, +100 billes, +1 étoile) entre deux épreuves. Carnet (`renderCarnet`) : 9 tables avec les 10 faits colorés, 16 notions avec statut, bouton Réviser = salle `revision` (10 questions : faits ratés + notions en cours, sans effet sur les salles).
- Billes (monnaie) : 10/15/20/30 par bonne réponse selon l'étage + bonus vitesse, +50 par salle (+300 au donjon), +20 par citrouille. Chaque erreur coûte la moitié du gain de l'étage (5/8/10/15), une citrouille manquée 10 ; le total ne descend jamais sous 0 (demande de Julien, 2026-11-07). Rangs jusqu'à « Légende des doudous » (4500).
- Étoile : salle réussie sans faute (3 au donjon). 4 étoiles = 1 cœur permanent (5 de base, 10 max). Une erreur = un cœur perdu dans la salle ; 0 cœur = la salle échoue, on rejoue.
- Erreur : la bonne réponse s'affiche avec une explication (`q.explain`, et le dessin de la forme via `q.explainShape`), puis la même épreuve est refaite sans chrono jusqu'à la bonne réponse (`redoQuestion`, comme Hyrule) ; le refaire ne rapporte ni ne coûte rien, la question revient aussi plus tard dans la salle. Jamais la même épreuve que les trois précédentes (`run.seen`).
- Carte : chaque salle montre son décor PixelLab (fenêtre), couloirs pavés avec tapis et torches, portes voûtées, halo de lanterne autour de l'héroïne, silhouette et « ? » tant que le doudou n'est pas retrouvé.
- Orage (remplace l'idée de Lune de sang) : jamais la première salle ni le donjon, dès que 2 salles ont été jouées depuis le dernier, selon l'étage (`STORM_BY_FLOOR`) : RDC 10 %, 4 citrouilles lentes, tables de 2 et 10 avec facteur ≤ 5 ; 1er 16 %, 5 citrouilles, tables 2-3-5-10 ; 2e et Tour 22 %, 6 citrouilles rapides, toutes les tables. 3 cœurs. Bouton test dans l'espace parents (prend l'étage de la salle en cours).
- Récit : les doudous sont perdus ou cachés, jamais enfermés (demande de Julien). Vocabulaire : « retrouver », « se cache ici », point d'interrogation sur le doudou noirci dans l'en-tête de salle.
- Carte : l'héroïne marche au clavier (flèches, ZQSD/WASD) ou au pavé tactile sous la carte (`heroMove`, `walkable`). Les portes sont des cases à part : dernière rangée de la salle pour les salles du haut (y=4), rangée 7 pour celles du bas, [9,8] pour le donjon ; marcher dessus entre dans la salle, l'escalier en [19,5] monte. Toucher une salle fonctionne toujours.
- Musique : une boucle par salle (`room_<id>` dans `MUSIC_TRACKS`) + accueil, 3 étages, tour, orage ; mélodie + basse + percussions (`perc` : x = grosse caisse, h = charley). Chaque motif est développé en neuf sections (`MUSIC.variants` : motif, aéré, octave, +5, ralenti, basse seule, rétrograde, +7, reprise) dans un ordre tiré au sort à chaque passage : une boucle dure plus d'une minute et ne se répète jamais à l'identique (Julien trouvait les boucles courtes énervantes). Le séquenceur programme les notes 2 s à l'avance.
- Orage plein écran : pluie, éclairs dessinés (`bolt`), secousses, château en fond, yeux de citrouilles qui rôdent ; quand elle répond juste, l'héroïne bondit vers la citrouille (sprite de dos), coup de lanterne en arc, explosion en morceaux ; coup reçu = recul + voile rouge.
- Galerie des sauts : repères de départ (bleu) et d'arrivée (jaune) avec étiquette en cm sur la règle dès le niveau 3 (demande de Julien : on ne voyait pas où tombe Hugo). En plus de mesurer un ruban, comparer, unités et conversions, Hugo saute pour de vrai sur la règle (`hopAnim`) : « de combien a-t-il sauté ? » et « touche la règle là où il va atterrir » (drapeau posé au clic, puis saut animé).
- Arrondi : la ligne des dizaines n'indique pas où se trouve le nombre (demande de Julien).
- Intro : six tableaux façon livre de contes (`startIntro`), jouée au premier « Entrer dans le château » (`S.introSeen`), rejouable depuis l'accueil.
- Formes : niveau 1 formes de base, niveau 2 + losange, trapèze, parallélogramme, ovale, hexagone, pentagone, octogone et « combien de côtés », niveau 3 solides en volume (cube, pavé droit, boule, cylindre, cône, pyramide).
- Typo FR : `fr()` pose l'espace insécable avant ! ? : dans les textes affichés.
- Style : jamais de tiret cadratin, phrases courtes et simples (elle lit bien mais débute), typo FR.
