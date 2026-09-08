# Suivi des recommandations — Lojik360 (lojik360.atmart.ltd)

Ouvert le 08/09/2026, au terme d'une relecture adversariale du site entier par
un agent critique indépendant du développeur : doctrine produit et contenu,
langue et i18n, sécurité et données personnelles, référencement, accessibilité
et performance, chaîne de fabrication. Périmètre : les 42 pages HTML du dépôt
`lojik360-site` (HEAD `1b2a664` + l'arbre de travail du 08/09), le site en
ligne tel que servi ce jour, et le Worker `atmart-chat` qu'il appelle.

## Verdict du 08/09/2026 : 🔴 BLOQUÉ

Le site est en ligne, sans erreur de console, avec des contrastes mesurés à
plus de 7:1 et des dictionnaires complets sur 105 clés. **Ce qui bloque n'est
pas la qualité de ce qui existe, c'est ce qui manque autour** : un tutoriel dont
le jeu de données est mort, un lecteur kreyòl envoyé sur des pages françaises,
un jeton GitHub posé dans `localStorage` sur une origine qui charge un script
tiers, et une collecte d'e-mails et de réponses d'entretien **sans aucune page
de confidentialité**. Six lignes bloquantes (A1, A2, B1, B2, C1, C2) ; le
verdict passe à « À CORRIGER » quand elles sont toutes vérifiées, et à
« PUBLIABLE » quand les 🟠 le sont aussi.

## Comment lire ce registre

**« vérifié » veut dire qu'un contrôle a été exécuté**, pas qu'on s'en souvient.
Lancer `python tools/etat_suivi.py` AVANT de répondre à « où en est-on » : il
recalcule ce qui est recalculable, compare au tableau, et **sort en erreur si
ce tableau ment** — dans les deux sens (une ligne « vérifiée » qui ne passe
plus, ou une ligne « à faire » qui passe déjà et n'a pas été consignée).

Les lignes marquées **humain** ne sont vérifiables par aucun programme — une
relecture en kreyòl, un arbitrage éditorial, une question de droits. Elles
restent ouvertes tant qu'une personne ne les ferme pas, et c'est normal.

Gravité : 🔴 **bloquant** — ne pas pousser en l'état · 🟠 **à corriger** —
affaiblit sans disqualifier · 🔵 **à arbitrer** — une décision, pas un défaut.

Pour fermer une ligne : faire la correction, relancer le script, et seulement
alors passer l'état à **vérifié** en écrivant dans la colonne Preuve ce qui a
été fait et ce que le contrôle a regardé. Ne jamais fermer une ligne « à moitié ».

---

## A — Doctrine produit et contenu

| # | Recommandation | Gravité | État | Preuve |
|---|---|---|---|---|
| A1 | Réparer les liens internes morts : `tutoriels/excel-premiere-analyse.html` pointe sur `../data/transferts_diaspora_2000_2025.csv` (le jeu de données du tutoriel, resté sur atmart.ltd) et sur `../formations.html`. Un tutoriel dont le fichier à télécharger tombe en 404 ne peut pas être suivi | 🔴 | **vérifié** | **corrigé le 08/09/2026** : les deux cibles existent bien, mais sur atmart.ltd. Les liens relatifs deviennent absolus (`https://atmart.ltd/...`), vérifiés à 200 tous les deux. Le tutoriel se suit de nouveau. |
| A2 | Corriger la clé i18n du lien « Datasets » du pied de page d'`index.html` : il porte `data-i18n="nav.podcast"`, donc il s'affiche « Podkas » en kreyòl et « Podcast » en anglais et espagnol | 🔴 | **vérifié** | **corrigé** : le lien porte enfin `nav.datasets`. ⚠️ Les trois libellés sont **repris d'atmart.ltd**, où la clé existait déjà (Datasets / Datos / Done) — inventer un mot kréyol ici aurait créé deux vocabulaires pour un même produit. |
| A3 | Unifier la navigation d'`index.html` avec les autres pages : « Podcast » y mène à `#podcast` (ancre locale) alors que `podcast.html` existe et que toutes les autres pages y mènent ; le bouton « Commencer » n'existe que sur l'accueil | 🟠 | **à faire** | 08/09 : `index.html` nav → `#podcast` ; `tutoriels.html`, `podcast.html`, `lojikkid.html` → `podcast.html` |
| A4 | Trancher les deux cartes « Bientôt » de `tutoriels.html` (« Vérifier avant de croire », « Communication efficace ») : les construire ou les retirer. Une promesse affichée depuis juillet sans date est une dette visible | 🟠 | **à faire** | 08/09 : 2 cartes `tut.soon` sans lien ni contenu |
| A5 | Publier l'épisode 01 du podcast (script prêt dans `content/podcast/ep01-script.md`) ou retirer « chaque semaine » de l'accueil et du podcast. La page annonce « Saison 1 en préparation » depuis juillet 2026 et la navigation de tout le site y envoie | 🔵 | **à faire — humain** | 08/09 : `podcast.html` ne contient aucun lien Spotify, Apple ou YouTube ; 8 épisodes annoncés, 0 publié. Le contrôle passe dès qu'un lien d'écoute réel apparaît |
| A6 | Arbitrer la porte d'entrée : le bouton principal du héros de l'accueil est « Préparer mon entretien (gratuit) » → `swot360.html`, un produit de la Suite 360 qui mène à des liens Stripe. L'école gratuite met son produit payant devant ses trois axes | 🔵 | **à arbitrer — humain** | 08/09 : `index.html` héros, 1er bouton `btn-primary` = Entèvyou360 ; les 3 axes viennent en 2e position |
| A7 | Arbitrer la présence de 14 liens `buy.stripe.com` dans `swot360.html` sur un site dont le CLAUDE.md dit « Lojik360 est l'école gratuite ; Atmart est le portail commercial ». Soit la doctrine s'écrit « sauf Entèvyou360 », soit le diagnostic gratuit renvoie vers 360.atmart.ltd pour la partie payante | 🔵 | **à arbitrer — humain** | 08/09 : 9 + 5 liens Stripe, 4 renvois vers 360.atmart.ltd déjà présents |
| A8 | Confirmer par écrit les droits de publication des tutoriels générés depuis des `.docx` du dossier « Haiti Adolescent Girls Network (HAGN) » (27 séances, recherche qualitative, prompting, Excel). Si ces documents ont été produits pour HAGN, Lojik360 doit avoir le droit de les publier sous sa marque | 🔵 | **à arbitrer — humain** | 08/09 : 5 chemins sources dans `content/*.py` pointent sur ce dossier OneDrive |
| A9 | Unifier le nom du produit dans les pages de redirection : `swot360.fr.html` dit « Entretien360 », `swot360.es.html` « Entrevista360 », `swot360.en.html` et la navigation « Entèvyou360 ». C'est le titre qui sort dans l'aperçu WhatsApp, un par langue | 🟠 | **à faire** | 08/09 : 3 noms différents pour un seul produit. Le nom retenu depuis le commit `1ce0d52` (08/08) est Entèvyou360 ; ⚠️ la note de projet `atmart-noms-produits` dit encore Interview360 |
| A10 | Corriger les `<title>` des 3 pages `pensee-critique.{html,ht,es}` qui finissent par « — Atmart » : ce sont des pages Lojik360, et c'est le titre qui sort dans les résultats de recherche | 🟠 | **à faire** | 08/09 : `Pensée critique — Atmart`, `Panse kritik — Atmart`, `Pensamiento crítico — Atmart` ; la version EN dit déjà « Lojik360 » |

## B — Langue et internationalisation

| # | Recommandation | Gravité | État | Preuve |
|---|---|---|---|---|
| B1 | Rendre les liens vers les tutoriels sensibles à la langue choisie : un lecteur qui a choisi Kreyòl sur `tutoriels.html` (page entièrement traduite) clique « Kòmanse » et atterrit sur `prompting-ia.html`, en français, alors que `prompting-ia.ht.html` existe. Idem depuis les 3 axes de l'accueil et depuis `lojikkid.html`. Solution : `data-href-ht` / `data-href-en` / `data-href-es` sur chaque carte dont la variante existe, et `i18n.js` réécrit `href` au changement de langue | 🔴 | **vérifié** | **corrigé** : chaque lien de tutoriel déclare ses variantes en `data-href-<lang>`, **générées depuis le disque** — déclarer à la main une version qui n'existe pas donnerait un 404, pire que le défaut d'origine. ⚠️ **Ma première version était fausse** : elle ne touchait que les liens ayant une variante dans la langue choisie, si bien qu'en passant du kréyol à l'anglais un tutoriel sans version anglaise **gardait son adresse kréyol**. Vu au navigateur, corrigé : on repart toujours du français. |
| B2 | Retirer le français resté dans `assets/i18n/ht.json` : « 3 axes yo », « Wè 3 axes yo », « Leson gratis, ranje selon 3 axes yo », « kesyon debrief » — le mot *axes* est français, le kreyòl dit *aks* | 🔴 | **vérifié** | **corrigé** : « axes » → « fason » (le site glose lui-même ses axes par « Trois façons » — la traduction était dans le texte), et « kesyon debrief » → « kesyon bilan », reformulé depuis le sens plutôt qu'adapté. ⚠️ **À relire par l'utilisateur**, qui est l'autorité native. |
| B3 | Traduire `<title>` et `<meta name="description">` des 4 pages à dictionnaire (`index`, `tutoriels`, `podcast`, `lojikkid`) : la langue change, l'onglet du navigateur reste « Tutoriels — Lojik360 ». `i18n.js` traite déjà tout élément `[data-i18n]`, `<title data-i18n="…">` marche sans changer le moteur ; ajouter `data-i18n-content` pour la description | 🟠 | **à faire** | 08/09 : 0 `<title data-i18n` sur les 4 pages ; onglet resté en français après passage en kreyòl |
| B4 | Donner aux 4 sous-pages `lojikkid-*.html` les 4 langues, comme `lojikkid.html` qui les annonce : un enfant qui a choisi Kreyòl sur la page d'entrée tombe sur des activités en français seulement | 🟠 | **à faire** | 08/09 : `lojikkid.html` porte `i18n.js` et 130 clés ; `lojikkid-{argent,creer,numerique,penser}.html` n'ont ni `data-i18n` ni variante `.ht/.en/.es` |
| B5 | Traduire les `aria-label` de la navigation (« Menu », « Langue / Lang ») sur les pages à dictionnaire via `data-i18n-aria` — le mécanisme existe déjà dans `i18n.js` | 🟠 | **à faire** | 08/09 : `aria-label="Menu"` en dur sur toutes les pages ; le sélecteur de langue reçoit son libellé depuis `i18n.js` sans clé |
| B6 | Traduire les 8 cartes d'épisodes de `podcast.html` (titres kreyòl, descriptions françaises en dur, sans `data-i18n`) : en anglais et en espagnol la page devient bilingue kreyòl-français sous une enveloppe traduite | 🟠 | **à faire** | 08/09 : 8 `<div class="card"><h3>…</h3><p>` sans clé dans une page qui porte `i18n.js` |
| B7 | Décider quoi faire des 20 pastilles « bientôt » du sélecteur de langue des tutoriels (`lang-soon`) : publier une matrice de couverture honnête (quel tutoriel existe dans quelle langue) et masquer les langues absentes plutôt que de promettre. Aujourd'hui : 3 guides facilitateur en anglais seul, recherche qualitative en kreyòl seul, management sans kreyòl | 🔵 | **à arbitrer — humain** | 08/09 : 20 `lang-soon` sur 9 pages ; couverture ES = 2 tutoriels sur 12 |

## C — Sécurité et données personnelles

| # | Recommandation | Gravité | État | Preuve |
|---|---|---|---|---|
| C1 | Sortir le jeton GitHub d'`admin.html` de `localStorage` (`lojik_admin_token`) : la page est servie sur la même origine que les tutoriels, qui chargent `cusdis.com/js/cusdis.es.js` — un script tiers. Un script tiers compromis sur cette origine lit le jeton et obtient l'écriture sur le dépôt. Au minimum `sessionStorage` (ou mémoire seule), et un rappel d'expiration courte ; mieux : servir `admin.html` depuis une autre origine | 🔴 | **vérifié** | **corrigé** : le jeton vit en mémoire, jamais écrit. ⚠️ Le défaut n'était pas théorique — `localStorage` est lisible par **tout** script de la même origine, et le site charge `cusdis.com` sur cinq pages : un tiers compromis obtenait le droit de **republier le site**, pages enfants comprises. L'ancien jeton est purgé à l'ouverture, et la purge n'utilise **pas** `getItem` — lire la clé pour savoir s'il faut l'effacer réintroduisait l'accès qu'on supprimait. |
| C2 | Créer `confidentialite.html` (4 langues) et la lier depuis le pied de page et à côté de chaque formulaire : le site collecte des e-mails (newsletter, `/subscribe`), des réponses d'entretien et des informations de carrière (`swot360.html` → Worker → modèle de langue), des commentaires (Cusdis) et des conversations (assistant IA). Aucune page ne dit ce qui est gardé, où, combien de temps, ni comment le retirer | 🔴 | **vérifié** | **corrigé** : `confidentialite.html` écrite d'après le **code**, site et Worker. Elle dit que l'e-mail est conservé **sans délai automatique** (aucun TTL sur `sub:<email>`) plutôt que d'annoncer une durée que rien ne ferait respecter ; que les messages du chat **ne sont écrits nulle part** ; que l'IP dort ~25 h dans les compteurs. Liée depuis 38 pieds de page et les 4 redirections. |
| C3 | Ajouter une phrase de consentement sous les formulaires d'abonnement (`index.html`, `podcast.html`) : ce qu'on recevra, à quelle fréquence, comment se désabonner, lien vers la confidentialité | 🟠 | **à faire** | 08/09 : « Zéro spam » est la seule mention ; aucun `nl.consent` |
| C4 | Repointer les fils Cusdis sur ce domaine : `data-page-url="https://atmart.ltd/tutoriels/…"` sur 5 pages — les commentaires sont rattachés à l'ancienne adresse, et Cusdis y renvoie | 🟠 | **à faire** | 08/09 : 25 `data-page-url` sur atmart.ltd dans `pensee-critique.{html,ht,en,es}` (6 chacune) et `excel-premiere-analyse.html` (1) |
| C5 | Poser une Content-Security-Policy et `Permissions-Policy` par une règle de réponse Cloudflare (le site est derrière le proxy — `Server: cloudflare`, et GitHub Pages ne permet pas d'en-têtes personnalisés). Origines à autoriser : fonts, `atmart-chat.atmartllc.workers.dev`, `api.github.com`, `cusdis.com`, `buy.stripe.com` | 🔵 | **à arbitrer — humain** | 08/09 : en-têtes reçus = HSTS, `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff` ; pas de CSP. Une CSP mal réglée casse le chat et le diagnostic : à tester en `Report-Only` d'abord |
| C6 | Décider du sort d'`admin.html` : il publie directement dans `tutoriels/`, or le CLAUDE.md dit que ces pages sont **générées** et qu'une édition à la main sera écrasée au prochain build. Soit l'outil édite les sources (`content/*.json`, `.docx`), soit il refuse les pages générées et le dit | 🔵 | **à arbitrer — humain** | 08/09 : la liste déroulante propose les 29 pages de `tutoriels/`, dont les 27 séances générées par `actions27_build.py` |

## D — Référencement et métadonnées

| # | Recommandation | Gravité | État | Preuve |
|---|---|---|---|---|
| D1 | Poser `og:title`, `og:description`, `og:image` (et `twitter:card`) sur les 4 pages de tête (`index`, `tutoriels`, `podcast`, `lojikkid`) : un lien partagé sur WhatsApp ou Facebook — le canal de diffusion déclaré — sort aujourd'hui sans image ni titre propre. Seul `swot360` en a | 🟠 | **à faire** | 08/09 : 0 `property="og:` sur 41 pages sur 42 |
| D2 | Poser `<link rel="canonical">` sur toutes les pages indexables : les copies restées sur atmart.ltd pointent bien ici, mais les pages d'ici ne se déclarent pas elles-mêmes | 🟠 | **à faire** | 08/09 : 0 canonical dans le dépôt ; `atmart.ltd/tutoriels/pensee-critique.html` → canonical vers lojik360 (bien) |
| D3 | Poser les `hreflang` alternates entre les variantes d'un même tutoriel (`x.html` / `x.ht.html` / `x.en.html` / `x.es.html`) : le sélecteur visuel existe, la déclaration aux moteurs non | 🟠 | **à faire** | 08/09 : 0 `hreflang` sur 29 pages de tutoriels ; 9 familles ont ≥ 2 langues |
| D4 | Assainir `sitemap.xml` : retirer les 3 redirections `swot360.{fr,en,es}.html` (elles portent `noindex` — se contredire coûte de la confiance au moteur), déclarer `/` au lieu de `/index.html`, ajouter `<lastmod>` | 🟠 | **à faire** | 08/09 : 3 URL noindex listées, 0 `lastmod`, `index.html` en clair |
| D5 | Créer `404.html` à la racine (GitHub Pages la sert automatiquement) avec la navigation, les 4 langues et le thème : aujourd'hui une adresse fautive tombe sur la page GitHub générique, en anglais, sans lien vers le site | 🟠 | **à faire** | 08/09 : `lojik360.atmart.ltd/nonexistent-page` → page GitHub par défaut |

## E — Accessibilité, thème et performance

| # | Recommandation | Gravité | État | Preuve |
|---|---|---|---|---|
| E1 | Donner au bouton ☰ `aria-expanded` (posé dans le HTML, basculé par `script.js`) et `aria-controls` : un lecteur d'écran ne sait pas si le menu est ouvert | 🟠 | **à faire** | 08/09 : `.nav-toggle` sans `aria-expanded` ; `script.js` fait un simple `classList.toggle` |
| E2 | Étendre `:focus-visible` à tous les liens et boutons : seul `.theme-btn` a un anneau de focus, et trois règles posent `outline: none` sur des champs. Au clavier, on ne voit pas où l'on est | 🟠 | **à faire** | 08/09 : 1 `:focus-visible` dans `style.css`, 3 `outline: none` sans remplacement |
| E3 | Rendre le site installable et lisible hors connexion (`manifest.webmanifest` + `sw.js` qui précache les pages de tête et les tutoriels, jamais `/api/`) : le premier public est sur téléphone avec des données coûteuses, et les tutoriels font 60 à 100 Ko chacun. Les sites frères (atmart.ltd, Suite 360) le font déjà | 🟠 | **à faire** | 08/09 : `/manifest.webmanifest` et `/sw.js` → 404 en ligne |
| E4 | Ajouter `<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>` partout où Google Fonts est chargé (ou auto-héberger Inter et Space Grotesk dans `assets/fonts/`) : la police bloque le premier rendu sur réseau lent | 🟠 | **à faire** | 08/09 : preconnect vers `fonts.googleapis.com` seulement, sur 39 pages |
| E5 | Sortir les dictionnaires et les gabarits de `swot360.html` dans des fichiers chargés par langue : la page pèse 289 Ko dont 225 Ko de script en ligne à analyser avant le premier clic, sur téléphone d'entrée de gamme | 🟠 | **à faire** | 08/09 : 4 blocs `<script>` en ligne, le plus gros = 225 193 caractères ; 142 attributs `style=` |
| E6 | Poser `<meta name="theme-color">` sur les pages de tête et sur `swot360.html`, avec les deux valeurs (`media="(prefers-color-scheme: …)"`) puisque le thème clair arrive : la barre du navigateur mobile suit le fond | 🟠 | **à faire** | 08/09 : 0 `theme-color` sur `index`, `tutoriels`, `podcast`, `lojikkid`, `swot360` |

## F — Chaîne de fabrication et dépôt

| # | Recommandation | Gravité | État | Preuve |
|---|---|---|---|---|
| F1 | Ne pas laisser l'arbre de travail diverger du site servi : pendant cette relecture, 40 fichiers (le thème clair/sombre) étaient modifiés sans commit, `style.css?v=11` en local contre `?v=1` en ligne. Le développeur a commité pendant la relecture (`8060abe`, 08/09 09:59) — la ligne reste ouverte tant que des fichiers suivis sont modifiés sans être commités, et se ferme d'elle-même quand l'arbre est propre | 🟠 | **vérifié** | 08/09 09:51 : `git status` → 40 ` M`, +1 310 lignes ; 09:59 commit `8060abe` (thème sur 39 pages) ; 10:1x commit `f29fe0b` (bouton d'en-tête lisible sur les deux fonds), arbre propre, **en ligne `style.css?v=12`**. Fermée par la mesure F1 d'`etat_suivi.py` (périmètre : les fichiers servis — `docs/`, `tools/`, `content/` exclus), qui la rouvrira si l'arbre diverge à nouveau |
| F2 | Ajouter `.gitignore` (`node_modules/`, `__pycache__/`, `content/podcast/out/`) et `.gitattributes` (`* text=auto eol=lf`) : le projet Remotion de `content/podcast/` vit avec ses `node_modules` à côté des pages servies, et Git avertit « LF will be replaced by CRLF » sur 40 fichiers | 🟠 | **à faire** | 08/09 : ni `.gitignore` ni `.gitattributes` ; `content/podcast/node_modules` présent sur disque |
| F3 | Versionner tous les scripts inclus (`?v=`) : `index.html` charge `script.js?v=2`, mais `tutoriels.html`, `swot360.html`, les 5 pages Lojikkid et les 29 tutoriels chargent `assets/script.js`, `chat.js` ou `quiz.js` sans version — les navigateurs garderont l'ancien indéfiniment sur une page et pas sur l'autre (piège déjà mordu sur atmart.ltd) | 🟠 | **à faire** | 08/09 : 35 inclusions sans `?v=` sur 35 pages (mesure `tools/etat_suivi.py` F3) ; `i18n.js?v=1` partout alors que B1/B3 vont le modifier |
| F4 | Faire tourner ce registre en intégration continue : `.github/workflows/verif.yml` qui lance `python tools/etat_suivi.py` à chaque push, pour que « ce qui est poussé est ce qui est servi » soit au moins « ce qui est poussé a été mesuré » | 🟠 | **à faire** | 08/09 : pas de dossier `.github/` |
| F5 | Mettre le CLAUDE.md à jour : il dit « Pas de test » et « 97 fichiers » ; il doit nommer `tools/etat_suivi.py`, `tools/poser_theme.py --verifier` et `tools/jetons_swot.py --verifier`, et dire de les lancer avant `git push` | 🟠 | **à faire** | 08/09 : CLAUDE.md sans mention des contrôles |
| F6 | Garder au vert les deux contrôles déjà écrits par le développeur (`poser_theme.py --verifier`, `jetons_swot.py --verifier`) : ils sont bons, ils doivent rester exécutés | 🟠 | **vérifié** | 08/09 : les deux sortent en 0 sur l'arbre de travail (relancés par `etat_suivi.py` à chaque exécution) |

---

## Ce qui tient, et qu'il ne faut pas casser

- **0 erreur de console** sur l'accueil, la bibliothèque, un tutoriel et le diagnostic, en ligne.
- **Contrastes mesurés** : teal sur navy 8,06:1, texte atténué 8,12:1 ; en thème clair (arbre de travail) 6,2:1 et plus. Le développeur a écrit *pourquoi* le teal de marque est inutilisable en clair — c'est le bon réflexe.
- **Dictionnaires complets** : 105 clés utilisées, 0 manquante dans en/ht/es (la seule « clé » signalée est un exemple de code dans le tutoriel *Construire une application*). 26 clés inutilisées à nettoyer un jour, sans urgence.
- **42 pages avec `<title>`, `description`, un seul `<h1>`, 0 image sans `alt`, 0 `id` dupliqué.**
- **Le Worker répond** (`/subscribe`, `/swot360` → 405 sur GET, donc vivant) et **les liens externes** vers atmart.ltd et 360.atmart.ltd répondent 200.
- **Les copies restées sur atmart.ltd** portent un `canonical` vers ici : la migration ne crée pas de contenu dupliqué aux yeux des moteurs.
- **`admin.html`** est bien en `noindex` et exclu par `robots.txt`.
- **Les adresses ne se renomment pas** (`swot360.html`) : la règle est écrite et tenue.
