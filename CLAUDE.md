# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Le contenu, les commentaires et les messages de commit sont **en français** (commits sans
accents). Écrire dans la même langue et le même ton : phrases nettes, le commentaire dit
*pourquoi*, et rien n'est affirmé qui n'ait été vérifié.

## Ce qu'est Lojik360

La marque éducation et stratégie d'**Atmart LLC** — *penser et créer à l'ère de l'IA*.
Lojik360 est l'**école gratuite** ; Atmart (atmart.ltd) est le portail commercial qui vend
données, SaaS et solutions. Une seule thèse organise tout : ne pas concourir avec l'IA sur la
vitesse, ne pas l'ignorer — **déléguer** ce qu'elle fait bien, **superviser** ce qu'elle fait
imparfaitement, **renforcer** ce qui reste humain. Les trois axes se retrouvent jusque dans les
noms de fichiers (`actions-deleguer`, `actions-superviser`, `actions-renforcer`).

## La technique, en une ligne

Site **statique** : HTML/CSS/JS à la main, **aucun framework, aucune étape de construction**.
97 fichiers, `assets/` sous les 1 000 lignes de JS au total. Ne pas introduire de bundler,
de gestionnaire de paquets ni de framework sans une raison qui tienne : l'absence de chaîne de
construction est ce qui rend le déploiement instantané et le dépôt lisible.

## Déployer

```bash
git add -A && git commit -m "..." && git push
```

`main` → **GitHub Pages** → en ligne en ~1 minute, sur **lojik360.atmart.ltd** (domaine
personnalisé porté par le fichier `CNAME` — ne pas le supprimer, il se perdrait au prochain
déploiement). Distant : `github.com/jwmyril/lojik360-site`. Pas de test, pas de compilation :
ce qui est poussé est ce qui est servi. Relire avant de pousser.

## Les quatre langues — deux mécanismes, pas un

C'est le point d'architecture qu'il faut comprendre avant de toucher au texte.

**Texte d'interface → un seul fichier, traductions en JSON.** Le français est la langue de
base, écrite en clair dans le HTML ; `assets/i18n.js` (60 lignes) remplace le contenu des
éléments portant `data-i18n`, `data-i18n-html`, `data-i18n-ph` ou `data-i18n-aria` à partir de
`assets/i18n/{ht,en,es}.json`. La langue choisie est retenue dans `localStorage`
(`atmart_lang`). La règle est écrite en tête du moteur : **aucune clé manquante = aucun
mélange**. Ajouter une chaîne, c'est l'ajouter dans les trois JSON en même temps — une clé
absente retombe silencieusement en français, ce qui ne se voit pas à la relecture.

**Texte long (tutoriels) → un fichier par langue.** `tutoriels/` contient 29 pages en
`nom.html` / `nom.ht.html` / `nom.en.html`. Un tutoriel de plusieurs milliers de mots ne passe
pas par des clés JSON. Ces pages sont **générées**, voir plus bas.

## Les pages `swot360.{fr,en,es}.html` ne sont pas des traductions

Ce sont des **redirections**, et les confondre avec des pages réelles ferait perdre du temps.
Chacune pose `atmart_lang` dans `localStorage`, redirige vers `swot360.html`, et porte
`robots: noindex`. Leur seule raison d'être : donner un lien partageable par langue dont
l'aperçu WhatsApp et les balises `og:` sortent dans la bonne langue. Modifier le produit se
fait dans `swot360.html` ; ces quatre-là ne portent que des métadonnées.

## Une adresse ne se renomme pas

`swot360.html` héberge aujourd'hui le diagnostic gratuit d'**Interview360** — produit rebaptisé
deux fois (SWOT360 → Entèvyou360 → Interview360) sans que l'adresse bouge. C'est délibéré :
tout lien partagé sur WhatsApp, tout favori, tout QR code imprimé continue de fonctionner.
La même règle vaut sur le site Atmart, où les pages gardent leurs anciens noms.

**Piège associé, qui a mordu deux fois :** les titres s'écrivent `Nom<em>360</em>`. Un
remplacement de texte sur « Nom360 » ne les touche pas. Après tout renommage, vérifier les
`<h1>`, les `<title>` et les métadonnées un par un.

## Le contenu généré

`content/` ne contient pas de page servie : ce sont des **fabriques Python**, à lancer à la
main quand la source change.

- `kreyol_build.py` — produit les pages kreyòl des tutoriels ;
- `newtuto_build.py` — produit un nouveau tutoriel ;
- `actions27/actions27_build.py` — produit les 27 séances réparties sur les trois axes, à
  partir des JSON voisins (`_fr_human`, `_fr_mgmt`, `_fr_tech`, `_model_en`).

Ces scripts lisent des `.docx` dans
`OneDrive/Documents/Haiti Adolescent Girls Network (HAGN)` et écrivent dans `tutoriels/`.
**Conséquence : une page de `tutoriels/` éditée à la main sera écrasée au prochain build.**
Corriger la source ou le script, pas la sortie.

Ces chemins Windows sont codés en dur dans les scripts. C'est assumé — ils tournent sur une
seule machine — mais c'est à savoir avant de s'étonner qu'ils échouent ailleurs.

## Le reste de `assets/`

`style.css` (596 lignes) est le **système de design partagé avec le site Atmart** : une
modification ici doit être pensée pour les deux. `script.js` porte la navigation, `quiz.js` et
`chat.js` ne servent que dans `tutoriels/` — `chat.js` parle au Worker Cloudflare dont l'adresse
est passée par l'attribut `data-endpoint` de sa balise `<script>`, jamais écrite dans le
fichier. `assets/brand/` tient les logos et favicons Atmart.

## Voisinage

- `Power_BI_Claude/Atmart_website` — le portail commercial, même système de design, a son
  propre CLAUDE.md. Le renommage des produits touche **les deux dépôts plus le Worker**.
- `Power_BI_Claude/Atmart_chat_worker` — le Worker Cloudflare.
- `~/atmart/` (WSL) — les dépôts des produits de la Suite 360 et l'application Arpentaj.

## Migration en cours

Les tutoriels, le podcast et la section enfants (« Lojik360 Junior ») déménagent d'atmart.ltd
vers ici. Tant que ce n'est pas fini, quelques liens pointent encore vers atmart.ltd : ce n'est
pas un défaut à corriger au hasard d'un passage.
