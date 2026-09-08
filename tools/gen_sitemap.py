# -*- coding: utf-8 -*-
"""Fabrique `sitemap.xml` depuis les pages réellement publiées.

    python tools/gen_sitemap.py             écrit le sitemap
    python tools/gen_sitemap.py --verifier  échoue s'il est périmé

POURQUOI IL EST GÉNÉRÉ
----------------------
Écrit à la main, il mentait de trois façons à la fois : il listait
`index.html` au lieu de `/`, il gardait les redirections `swot360.*`, et aucune
de ses 38 URL ne portait de `lastmod`.

⚠️ LE `lastmod` EST LE PIÈGE. Prendre la date du fichier ferait dater TOUTES
les pages du dernier build : on annoncerait à Google que 39 pages ont changé
alors qu'une seule a bougé, et il apprendrait à ne plus nous croire. On lit
donc la date du dernier commit qui a TOUCHÉ la page, et on retombe sur la date
du fichier seulement si git est indisponible.

Ce qui n'entre pas : `404.html` et `admin.html` (aucune raison d'être
indexées), et les quatre redirections `swot360.*`, qui portent `noindex` —
demander l'indexation d'une page qui refuse d'être indexée est une
contradiction que les moteurs comptent contre le site.
"""
import io
import os
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                            # noqa: BLE001
    pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://lojik360.atmart.ltd"
CIBLE = os.path.join(RACINE, "sitemap.xml")

EXCLUES = {"404.html", "admin.html",
           "swot360.html", "swot360.fr.html", "swot360.en.html", "swot360.es.html"}

PRIORITES = {"index.html": "1.0", "tutoriels.html": "0.9",
             "lojikkid.html": "0.8", "podcast.html": "0.8",
             "confidentialite.html": "0.3"}


def pages():
    out = []
    for base, _, fs in os.walk(RACINE):
        if os.sep + "." in base or "node_modules" in base:
            continue
        for f in sorted(fs):
            if not f.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(base, f), RACINE).replace(os.sep, "/")
            if rel in EXCLUES or os.path.basename(rel) in EXCLUES:
                continue
            out.append(rel)
    return sorted(out)


def derniere_modif(rel):
    """La date du dernier commit qui a touché ce fichier."""
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel],
                           cwd=RACINE, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        d = (r.stdout or "").strip()
        if d:
            return d
    except Exception:                                        # noqa: BLE001
        pass
    p = os.path.join(RACINE, rel)
    return time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(p)))


def xml():
    lignes = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for rel in pages():
        loc = SITE + "/" + ("" if rel == "index.html" else rel)
        pr = PRIORITES.get(rel, "0.6")
        lignes.append("  <url><loc>%s</loc><lastmod>%s</lastmod>"
                      "<priority>%s</priority></url>" % (loc, derniere_modif(rel), pr))
    lignes.append("</urlset>")
    return "\n".join(lignes) + "\n"


def main():
    verifier = "--verifier" in sys.argv
    voulu = xml()
    actuel = io.open(CIBLE, encoding="utf-8").read() if os.path.exists(CIBLE) else ""
    n = voulu.count("<url>")
    if actuel == voulu:
        print("     Sitemap : %d url, à jour" % n)
        return 0
    if verifier:
        print("     Sitemap : périmé (%d url attendues)" % n)
        return 1
    io.open(CIBLE + ".tmp", "w", encoding="utf-8", newline="\n").write(voulu)
    os.replace(CIBLE + ".tmp", CIBLE)
    print("     Sitemap : %d url, toutes avec lastmod" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
