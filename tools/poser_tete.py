# -*- coding: utf-8 -*-
"""Pose l'en-tête de chaque page : canonical, Open Graph, hreflang, theme-color.

    python tools/poser_tete.py             pose
    python tools/poser_tete.py --verifier  échoue s'il manque quelque chose

POURQUOI UN SEUL OUTIL POUR SIX LIGNES DU REGISTRE
--------------------------------------------------
D1, D2, D3, E4, E6 et A10 décrivent six symptômes d'une même cause : personne
ne fabrique le `<head>`. Chaque page a été écrite à la main, donc chaque page
a oublié autre chose. Les corriger une par une garantit qu'on recommencera à
la page suivante.

Ici, le `<head>` se **calcule** :

  · `canonical` — l'adresse propre de la page, sur le domaine du site ;
  · `og:*` et `twitter:*` — sans quoi un lien partagé dans WhatsApp ou sur
    LinkedIn s'affiche en texte nu. Le titre et la description sont LUS dans
    la page, jamais réécrits : ils y sont déjà justes ;
  · `hreflang` — chaque page d'une famille multilingue déclare ses sœurs.
    ⚠️ Sans cela, Google indexe quatre versions du même tutoriel et en choisit
    une au hasard : un lecteur kreyòl reçoit la page française dans ses
    résultats, ce que B1 vient précisément de corriger côté navigation ;
  · `theme-color` — les deux valeurs, `media` à l'appui, depuis que le site a
    deux fonds. Une seule valeur peint la barre du téléphone en bleu nuit
    au-dessus d'une page blanche ;
  · `preconnect` vers `fonts.gstatic.com` — la feuille Google Fonts est déjà
    préconnectée, mais les FICHIERS de police viennent d'un autre hôte. Sans
    lui, la police attend une poignée de main de plus, et le texte clignote.

⚠️ CE QUI EST LU, PAS ÉCRIT. Le `<title>` et la description existent déjà dans
chaque page et sont souvent meilleurs que ce que je produirais. On les reprend.
La seule exception est A10 : trois titres finissent par « — Atmart » alors que
la marque de ce site est Lojik360.
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                            # noqa: BLE001
    pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://lojik360.atmart.ltd"
IMAGE = SITE + "/assets/brand/share-1200x630.jpg"

# Les redirections ne s'indexent pas : ni canonical, ni og, ni hreflang.
REDIRECTIONS = {"swot360.html", "swot360.fr.html", "swot360.en.html", "swot360.es.html"}

MARQUE = "<!-- tete : poser_tete.py -->"
BLOC = re.compile(re.escape(MARQUE) + r".*?" + re.escape(MARQUE), re.S)

LANGS = ("ht", "en", "es")


def pages():
    out = []
    for base, _, fs in os.walk(RACINE):
        if os.sep + "." in base or "node_modules" in base:
            continue
        for f in sorted(fs):
            if f.endswith(".html"):
                out.append(os.path.relpath(os.path.join(base, f), RACINE).replace(os.sep, "/"))
    return out


def familles():
    """{'pensee-critique': {'fr': 'tutoriels/pensee-critique.html', 'ht': …}}"""
    fam = {}
    d = os.path.join(RACINE, "tutoriels")
    if not os.path.isdir(d):
        return fam
    for f in sorted(os.listdir(d)):
        m = re.match(r"^(.+?)(?:\.(ht|en|es))?\.html$", f)
        if m:
            fam.setdefault(m.group(1), {})[m.group(2) or "fr"] = "tutoriels/" + f
    return fam


def _entre(t, motif):
    m = re.search(motif, t, re.S | re.I)
    return (m.group(1).strip() if m else "")


def echappe(s):
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;"))


def tete(page, t, fam):
    url = SITE + ("/" if page == "index.html" else "/" + page)
    titre = echappe(re.sub(r"<[^>]+>", "", _entre(t, r"<title[^>]*>(.*?)</title>")))
    descr = echappe(_entre(t, r'<meta\s+name="description"[^>]*content="([^"]*)"'))

    lignes = ['<link rel="canonical" href="%s" />' % url]

    # hreflang : la famille du tutoriel, si elle a plusieurs langues
    for base, membres in fam.items():
        if page in membres.values() and len(membres) > 1:
            for lg in ("fr", "ht", "en", "es"):
                if lg in membres:
                    lignes.append('<link rel="alternate" hreflang="%s" href="%s/%s" />'
                                  % (lg, SITE, membres[lg]))
            lignes.append('<link rel="alternate" hreflang="x-default" href="%s/%s" />'
                          % (SITE, membres.get("fr", membres[sorted(membres)[0]])))
            break

    lignes += [
        '<meta property="og:type" content="website" />',
        '<meta property="og:site_name" content="Lojik360" />',
        '<meta property="og:url" content="%s" />' % url,
        '<meta property="og:title" content="%s" />' % titre,
        '<meta property="og:description" content="%s" />' % descr,
        '<meta property="og:image" content="%s" />' % IMAGE,
        '<meta name="twitter:card" content="summary_large_image" />',
        '<meta name="twitter:title" content="%s" />' % titre,
        '<meta name="twitter:description" content="%s" />' % descr,
        '<meta name="twitter:image" content="%s" />' % IMAGE,
        # ⚠️ DEUX VALEURS. Le site a deux fonds ; une seule couleur peindrait
        # la barre du téléphone en bleu nuit au-dessus d'une page blanche.
        '<meta name="theme-color" content="#f4f8fb" media="(prefers-color-scheme: light)" />',
        '<meta name="theme-color" content="#0a1a2f" media="(prefers-color-scheme: dark)" />',
    ]
    return MARQUE + "\n  " + "\n  ".join(lignes) + "\n  " + MARQUE


def traiter(page, t, fam):
    # A10 : la marque de ce site est Lojik360, pas Atmart
    t = re.sub(r"(<title>[^<]*)—\s*Atmart\s*</title>", r"\1— Lojik360</title>", t)

    # E4 : les FICHIERS de police viennent d'un autre hôte que la feuille
    if "fonts.googleapis.com" in t and "fonts.gstatic.com" not in t:
        anc = '<link rel="preconnect" href="https://fonts.googleapis.com" />'
        if anc in t:
            t = t.replace(anc, anc + '\n  <link rel="preconnect" '
                          'href="https://fonts.gstatic.com" crossorigin />', 1)

    if page in REDIRECTIONS:
        return t

    bloc = tete(page, t, fam)
    if BLOC.search(t):
        return BLOC.sub(lambda _m: bloc, t, count=1)
    i = t.lower().find("</head>")
    return t if i < 0 else t[:i] + "  " + bloc + "\n" + t[i:]


def main():
    verifier = "--verifier" in sys.argv
    fam = familles()
    retard, touchees = [], 0
    for page in pages():
        p = os.path.join(RACINE, page)
        t = io.open(p, encoding="utf-8").read()
        neuf = traiter(page, t, fam)
        if neuf == t:
            continue
        if verifier:
            retard.append(page)
            continue
        io.open(p + ".tmp", "w", encoding="utf-8", newline="\n").write(neuf)
        os.replace(p + ".tmp", p)
        touchees += 1

    if verifier and retard:
        print("     Tête : %d page(s) en retard : %s"
              % (len(retard), " ".join(retard[:6])))
        return 1
    n_fam = sum(1 for m in fam.values() if len(m) > 1)
    print("     Tête : %d page(s) mise(s) à jour · %d famille(s) multilingue(s)"
          % (touchees, n_fam))
    return 0


if __name__ == "__main__":
    sys.exit(main())
