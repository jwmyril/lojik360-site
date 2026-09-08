# -*- coding: utf-8 -*-
"""Remplace les couleurs écrites en dur de `swot360.html` par des jetons.

    python tools/jetons_swot.py             applique
    python tools/jetons_swot.py --verifier  échoue s'il en reste

POURQUOI SEULEMENT CETTE PAGE
-----------------------------
Les treize autres pages du site tirent déjà toutes leurs couleurs de `:root`,
donc le thème clair les atteint sans rien changer. `swot360.html` — le
diagnostic Interview360 — en porte SOIXANTE-DIX-SEPT en clair, dans des
attributs `style` et un bloc `<style>` qui lui est propre.

Une couleur écrite en dur est invisible au thème : `#eaf2fb` reste blanc cassé
sur un fond devenu blanc. Aucun réglage global ne rattrape ça. On les remplace
donc une par une.

CE QUI RESTE DÉLIBÉRÉMENT LITTÉRAL
  · `<meta name="theme-color">` — une balise meta ne comprend pas `var()` ;
  · tout bloc `@media print` — le papier est toujours blanc, ses couleurs ne
    se thématisent pas.

⚠️ `#118848` EST GARDÉ TEL QUEL. C'est le vert « réussite » du diagnostic, et
il ne correspond à aucun jeton de la marque. L'inventer dans `:root` juste
pour cette page créerait un jeton que personne ne connaît ; le laisser
littéral est honnête, et il tient le contraste sur les deux fonds.
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
CIBLE = os.path.join(RACINE, "swot360.html")

# L'ordre compte : les formes longues d'abord (#ffffff avant #fff).
REMPLACEMENTS = [
    ("#ffffff", "var(--ink)"), ("#FFFFFF", "var(--ink)"),
    ("#fff", "var(--ink)"), ("#FFF", "var(--ink)"),
    ("#eaf2fb", "var(--ink)"),
    ("#9db2c7", "var(--ink-dim)"), ("#ccc", "var(--ink-dim)"),
    ("#999", "var(--ink-dim)"), ("#666", "var(--ink-dim)"),
    ("#0a1a2f", "var(--navy)"), ("#000", "var(--navy)"),
    ("#12233d", "var(--card)"), ("#102a4c", "var(--navy-2)"),
    ("#2ec4b6", "var(--teal)"), ("#21998e", "var(--teal-dark)"),
    ("#f4a261", "var(--amber)"), ("#e63946", "var(--red)"),
    ("#6a9fd8", "var(--bleu)"), ("#7aa2f7", "var(--bleu)"),
    ("#e07a7a", "var(--red)"),
]

TRANSLUCIDES = [
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0?\.0[1-9]\d*\s*\)", "var(--voile)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0?\.[1-9]\d*\s*\)", "var(--voile-fort)"),
    (r"rgba\(\s*46\s*,\s*196\s*,\s*182\s*,\s*0?\.[01]\d*\s*\)", "var(--teal-voile)"),
    (r"rgba\(\s*46\s*,\s*196\s*,\s*182\s*,\s*0?\.[2-9]\d*\s*\)", "var(--teal-bord)"),
    (r"rgba\(\s*244\s*,\s*162\s*,\s*97\s*,\s*(?:0|0?\.[0-9]\d*)\s*\)", "var(--amber-bord)"),
    (r"rgba\(\s*230\s*,\s*57\s*,\s*70\s*,\s*(?:0|0?\.[0-9]\d*)\s*\)", "var(--red-bord)"),
    (r"rgba\(\s*224\s*,\s*122\s*,\s*122\s*,\s*(?:0|0?\.[0-9]\d*)\s*\)", "var(--red-bord)"),
    (r"rgba\(\s*122\s*,\s*162\s*,\s*247\s*,\s*(?:0|0?\.[0-9]\d*)\s*\)", "var(--bleu-bord)"),
    (r"rgba\(\s*106\s*,\s*159\s*,\s*216\s*,\s*(?:0|0?\.[0-9]\d*)\s*\)", "var(--bleu-bord)"),
    (r"rgba\(\s*10\s*,\s*26\s*,\s*47\s*,\s*(?:0|0?\.[0-9]\d*)\s*\)", "var(--navy-voile)"),
]

# ⚠️ LE PAPIER RESTE BLANC, MEME EN MODE SOMBRE.
#
# `.cv-out` est l'APERCU DU CV : il represente une feuille imprimee, pas une
# surface de l'interface. Ma premiere passe y a transforme `background:#fff`
# en `var(--ink)` — ce qui donnait, en mode CLAIR, un fond `#0d1f38` sous un
# texte `#111`. Du noir sur du noir, sur l'ecran que le visiteur telecharge
# ensuite en document. C'est exactement la panne que ce fichier existe pour
# empecher, et elle est passee a un caractere pres.
#
# Meme raison pour la feuille d'export (`font-family:Calibri`) : elle part
# dans un fichier Word, ou `var()` n'existe pas.
GARDE = re.compile(r'<meta name="theme-color"[^>]*>'
                   r'|@media\s+print\s*\{(?:[^{}]|\{[^{}]*\})*\}'
                   r'|\.cv-out\{[^}]*\}'
                   # ⚠️ TOUTE CHAINE QUI PARLE EN POINTS EST DU DOCUMENT WORD,
                   # jamais de l'interface. Le web ne se mesure pas en `pt` ;
                   # l'export, si. C'est le signe le plus sûr, et il attrape
                   # les morceaux de feuille répartis sur plusieurs lignes de
                   # concaténation — dont un que ma passe précédente avait
                   # déjà transformé en `var()`, qui ne veut rien dire dans un
                   # fichier ouvert par Word.
                   r'|"[^"]*\d(?:\.\d+)?pt[^"]*"'
                   r'|#118848')

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
        print("  swot360 : %d couleur(s) encore en dur : %s"
              % (len(restants), " ".join(sorted(set(restants))[:8])))
        return 1
    if verifier:
        if neuf != s:
            print("  swot360 : des couleurs en dur sont revenues")
            return 1
        print("  swot360 : aucune couleur ecrite en dur")
        return 0
    if neuf != s:
        io.open(CIBLE + ".tmp", "w", encoding="utf-8", newline="\n").write(neuf)
        os.replace(CIBLE + ".tmp", CIBLE)
    print("  swot360 : toutes les couleurs passent par des jetons")
    return 0


if __name__ == "__main__":
    sys.exit(main())
