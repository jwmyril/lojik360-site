# -*- coding: utf-8 -*-
"""Fait passer les couleurs de `style.css` par des jetons.

    python tools/jetons_css.py             applique
    python tools/jetons_css.py --verifier  échoue s'il en reste

POURQUOI CE FICHIER EXISTE, ET CE QU'IL A ATTRAPÉ
-------------------------------------------------
J'ai converti les PAGES et oublié la FEUILLE. Mesuré au navigateur, en mode
clair, sur la page d'accueil :

    en-tête        rgba(10, 26, 47, 0.92)   — bleu nuit, écrit en dur
    texte du logo  rgb(13, 31, 56)          — bleu nuit, venu du jeton
    contraste      1,06:1

Le logo était INVISIBLE, et les liens de navigation tenaient 2,66:1, sous le
seuil AA de 4,5. Le fond clair rendait la barre de navigation illisible, dans
tout le site à la fois — c'est-à-dire l'inverse exact de ce qu'on ajoutait.

Une couleur écrite en dur dans la feuille est aussi aveugle au thème qu'une
couleur écrite en dur dans une page. Vérifier les pages sans vérifier la
feuille, c'est vérifier la moitié du site.

CE QUI RESTE DÉLIBÉRÉMENT LITTÉRAL
  · les blocs de définition des jetons eux-mêmes (`:root`, `.clair`,
    `.sombre`) — c'est là que les valeurs vivent ;
  · `rgba(0,0,0,…)` des ombres portées : une ombre est noire sur les deux
    fonds, elle ne se thématise pas ;
  · les quatre couleurs de catégorie du tableau de bord (#2fd573 vert,
    #4dabf7 bleu, #b197fc violet, #3b82f6) : elles distinguent des séries
    entre elles, pas du texte d'un fond. Les changer casserait la lecture du
    graphique sans rien gagner.
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
CIBLE = os.path.join(RACINE, "assets", "style.css")

REMPLACEMENTS = [
    ("#16365c", "var(--border)"),
    ("#ff8a94", "var(--red)"),
    ("#116d64", "var(--teal)"),
    ("#2ec4b6", "var(--teal)"),
    ("#fff", "var(--ink)"),
    ("#000", "var(--navy)"),
]

TRANSLUCIDES = [
    # ⚠️ L'EN-TETE, la cause du 1,06:1. Elle doit suivre le fond de la page.
    (r"rgba\(\s*10\s*,\s*26\s*,\s*47\s*,\s*0?\.\d+\s*\)", "var(--navy-voile)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0?\.0[1-9]\d*\s*\)", "var(--voile)"),
    (r"rgba\(\s*46\s*,\s*196\s*,\s*182\s*,\s*0?\.[01]\d*\s*\)", "var(--teal-voile)"),
    (r"rgba\(\s*46\s*,\s*196\s*,\s*182\s*,\s*0?\.[2-9]\d*\s*\)", "var(--teal-bord)"),
    (r"rgba\(\s*244\s*,\s*162\s*,\s*97\s*,\s*0?\.\d+\s*\)", "var(--amber-bord)"),
    (r"rgba\(\s*230\s*,\s*57\s*,\s*70\s*,\s*0?\.\d+\s*\)", "var(--red-bord)"),
    (r"rgba\(\s*47\s*,\s*213\s*,\s*115\s*,\s*0?\.\d+\s*\)", "var(--vert-voile)"),
    (r"rgba\(\s*77\s*,\s*171\s*,\s*247\s*,\s*0?\.\d+\s*\)", "var(--bleu-voile)"),
    (r"rgba\(\s*177\s*,\s*151\s*,\s*252\s*,\s*0?\.\d+\s*\)", "var(--violet-voile)"),
]

# Les définitions de jetons, les ombres noires et les couleurs de série.
GARDE = re.compile(
    r"(?::root|html\.clair|html\.sombre|html:not\(\.sombre\))[^{]*\{[^}]*\}"
    r"|@media[^{]*\{(?:[^{}]|\{[^{}]*\})*\}"
    r"|rgba\(\s*0\s*,\s*0\s*,\s*0\s*,[^)]*\)"
    r"|#2fd573|#4dabf7|#b197fc|#3b82f6")

RESTE = re.compile(r"#[0-9a-fA-F]{3,6}\b|rgba?\([0-9]")


def traiter(s):
    protege = []

    def de_cote(m):
        protege.append(m.group(0))
        return "\x00%d\x00" % (len(protege) - 1)

    s = GARDE.sub(de_cote, s)
    for a, b in REMPLACEMENTS:
        s = s.replace(a, b)
    for motif, b in TRANSLUCIDES:
        s = re.sub(motif, b, s)
    for i, brut in enumerate(protege):
        s = s.replace("\x00%d\x00" % i, brut)
    return s


def main():
    verifier = "--verifier" in sys.argv
    s = io.open(CIBLE, encoding="utf-8").read()
    neuf = traiter(s)
    restants = RESTE.findall(GARDE.sub("", neuf))

    if restants:
        print("  style.css : %d couleur(s) encore en dur : %s"
              % (len(restants), " ".join(sorted(set(restants))[:8])))
        return 1
    if verifier:
        if neuf != s:
            print("  style.css : des couleurs en dur sont revenues")
            return 1
        print("  style.css : aucune couleur ecrite en dur")
        return 0
    if neuf != s:
        io.open(CIBLE + ".tmp", "w", encoding="utf-8", newline="\n").write(neuf)
        os.replace(CIBLE + ".tmp", CIBLE)
    print("  style.css : toutes les couleurs passent par des jetons")
    return 0


if __name__ == "__main__":
    sys.exit(main())
