# -*- coding: utf-8 -*-
"""Nomme le cache du service worker d'après le contenu publié.

    python tools/version_cache.py             met à jour sw.js
    python tools/version_cache.py --verifier  échoue si sw.js est en retard

POURQUOI CE FICHIER EXISTE
--------------------------
Le service worker sert ce qu'il a en cache tant que le NOM du cache ne change
pas. Oublier de le changer après une modification, c'est publier pour
personne : les visiteurs déjà venus gardent l'ancienne page, parfois des jours,
et rien ne le signale.

Sur un autre site de la maison, l'oubli s'est produit deux fois — dont une où
j'ai cru dix minutes qu'une fonction était cassée alors que le navigateur
servait un fichier d'avant la correction. Un garde-fou qui repose sur la
mémoire n'en est pas un. Le nom est donc calculé.

CE QU'ON HACHE : ce que le visiteur télécharge vraiment — les pages, la
feuille, les scripts, les dictionnaires. Pas les outils de fabrication :
changer un commentaire dans un script Python ne doit purger le cache de
personne.
"""
import hashlib
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                            # noqa: BLE001
    pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def servis():
    out = []
    for base, _, fs in os.walk(RACINE):
        rel = os.path.relpath(base, RACINE)
        if rel.startswith((".", "tools", "docs")) or "node_modules" in rel:
            continue
        for f in sorted(fs):
            if f.endswith((".html", ".css", ".js", ".json", ".webmanifest")):
                p = os.path.relpath(os.path.join(base, f), RACINE).replace(os.sep, "/")
                if p != "sw.js":
                    out.append(p)
    return sorted(out)


def empreinte():
    """Huit caractères qui changent si et seulement si le contenu change."""
    h = hashlib.sha256()
    for nom in servis():
        h.update(nom.encode("utf-8"))
        with io.open(os.path.join(RACINE, nom), "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:8]


def main():
    verifier = "--verifier" in sys.argv
    p = os.path.join(RACINE, "sw.js")
    if not os.path.exists(p):
        print("     Cache : sw.js absent")
        return 1
    s = io.open(p, encoding="utf-8").read()
    m = re.search(r'const CACHE = "([^"]+)"', s)
    if not m:
        print("     Cache : ligne CACHE introuvable dans sw.js")
        return 1

    voulu = "lojik360-" + empreinte()
    if m.group(1) == voulu:
        print("     Cache : %s — à jour (%d fichiers servis)" % (voulu, len(servis())))
        return 0
    if verifier:
        print("     Cache : sw.js dit %s, le contenu vaut %s" % (m.group(1), voulu))
        print("     Les visiteurs déjà venus garderaient l'ancienne version.")
        return 1

    s = s[:m.start(1)] + voulu + s[m.end(1):]
    io.open(p + ".tmp", "w", encoding="utf-8", newline="\n").write(s)
    os.replace(p + ".tmp", p)
    print("     Cache : %s -> %s" % (m.group(1), voulu))
    return 0


if __name__ == "__main__":
    sys.exit(main())
