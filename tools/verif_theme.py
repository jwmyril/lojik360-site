# -*- coding: utf-8 -*-
"""Un seul contrôle avant de publier.

    python tools/verif_theme.py

Il rejoue les trois outils du thème en mode `--verifier` et rend un code non
nul si l'un d'eux échoue. À lancer avant tout `git push`.

⚠️ POURQUOI CE CONTRÔLE EXISTE. Le 03/09/2026, le thème clair a été posé sur
les 39 pages, vérifié à l'œil, et il était cassé : l'en-tête gardait un
`rgba(10, 26, 47, 0.92)` écrit en dur dans `style.css`, ce qui donnait un
logo à **1,06:1** sur fond clair — invisible — et des liens de navigation à
2,66:1, sous le seuil AA.

La cause n'était pas une faute d'inattention mais un angle mort : j'avais
converti les PAGES et pas la FEUILLE. Vérifier les pages sans vérifier la
feuille, c'est vérifier la moitié du site. Ce fichier ferme les deux.
"""
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                            # noqa: BLE001
    pass

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)

ETAPES = [
    ("jetons_css.py", "aucune couleur en dur dans la feuille"),
    ("jetons_swot.py", "aucune couleur en dur dans swot360"),
    ("poser_theme.py", "les 39 pages portent le selecteur"),
]


def main():
    echecs = []
    for i, (script, quoi) in enumerate(ETAPES, 1):
        print("[%d/%d] %s" % (i, len(ETAPES), quoi))
        r = subprocess.run([sys.executable, os.path.join(ICI, script), "--verifier"],
                           cwd=RACINE, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        for ligne in (r.stdout or "").strip().split("\n"):
            if ligne:
                print("   " + ligne)
        if r.returncode != 0:
            err = (r.stderr or "").strip()
            if err:
                print("   " + err.split("\n")[-1])
            echecs.append(quoi)

    print()
    if echecs:
        print("CONTROLE EN ECHEC : " + " | ".join(echecs))
        return 1
    print("Theme vert. Publier : git add -A && git commit && git push")
    return 0


if __name__ == "__main__":
    sys.exit(main())
