# -*- coding: utf-8 -*-
"""Pose le sélecteur de fond clair/sombre sur toutes les pages.

    python tools/poser_theme.py             pose
    python tools/poser_theme.py --verifier  échoue s'il manque une page

POURQUOI LE SCRIPT EST *AVANT* LE PREMIER AFFICHAGE
---------------------------------------------------
⚠️ La classe doit être posée sur `<html>` AVANT que le navigateur peigne quoi
que ce soit. Le faire depuis `script.js`, chargé en bas de page, ferait
apparaître la page en sombre puis basculer en clair sous les yeux du visiteur
— le « flash ». Désagréable partout ; sur un téléphone en plein soleil, il
fait rater la première seconde de lecture, c'est-à-dire précisément le public
pour qui on ajoute le mode clair.

Le script est donc INLINE, dans le `<head>`, avant la feuille de style.

TROIS ÉTATS, PAS DEUX
---------------------
`clair`, `sombre`, ou rien du tout. « Rien » veut dire « suis le système », et
c'est le défaut : quelqu'un dont le téléphone est en mode nuit doit arriver
sur un site sombre sans avoir rien demandé. Le bouton fait donc tourner les
trois états, et il AFFICHE lequel est actif — sinon on ne sait pas si on est
en « clair » ou en « automatique qui se trouve être clair ».

⚠️ `localStorage` PEUT LEVER UNE EXCEPTION, pas seulement renvoyer vide :
navigation privée stricte, cookies bloqués, iframe cloisonnée. Un `try` autour
de la lecture ET de l'écriture, sinon la page entière meurt avant de s'afficher
— sur un site dont le premier public est sur téléphone, ce serait un écran
blanc pour une préférence de couleur.
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

# Les redirections de langue ne portent aucun style : elles partent aussitôt.
IGNORER = {"swot360.en.html", "swot360.es.html", "swot360.fr.html"}

MARQUE = "<!-- theme clair/sombre -->"

# La feuille a change : une cle neuve, la meme pour toutes les pages.
VERSION_CSS = 12

BASCULE = MARQUE + """
  <script>/* fond clair/sombre — AVANT le premier affichage, sinon la page clignote */
  (function(){var c=null;try{c=localStorage.getItem("atmart_theme")}catch(e){}
  if(c==="clair"||c==="sombre") document.documentElement.className+=" "+c;})();
  </script>""" + MARQUE

BOUTON = ('<li><button class="theme-btn" id="theme-btn" type="button" '
          'aria-live="polite">◐ Auto</button></li>')

APPLI = MARQUE + """
<script>/* le bouton : clair -> sombre -> automatique -> clair */
(function(){
  var b=document.getElementById("theme-btn"); if(!b) return;
  var LBL={clair:"\\u25cb Clair", sombre:"\\u25cf Sombre", auto:"\\u25d0 Auto"};
  function lire(){try{return localStorage.getItem("atmart_theme")||"auto"}catch(e){return "auto"}}
  function peindre(v){
    var h=document.documentElement;
    h.classList.remove("clair","sombre");
    if(v!=="auto") h.classList.add(v);
    b.textContent=LBL[v];
    b.setAttribute("aria-label",
      v==="auto" ? "Fond : automatique, selon votre appareil. Changer."
                 : "Fond : "+(v==="clair"?"clair":"sombre")+". Changer.");
  }
  peindre(lire());
  b.addEventListener("click",function(){
    var o=["clair","sombre","auto"], v=o[(o.indexOf(lire())+1)%3];
    try{ v==="auto" ? localStorage.removeItem("atmart_theme")
                    : localStorage.setItem("atmart_theme",v); }catch(e){}
    peindre(v);
  });
})();
</script>""" + MARQUE

BLOC = re.compile(re.escape(MARQUE) + r".*?" + re.escape(MARQUE), re.S)


def pages():
    out = []
    for base, _, fichiers in os.walk(RACINE):
        if os.sep + "." in base or "node_modules" in base:
            continue
        for f in sorted(fichiers):
            if f.endswith(".html") and f not in IGNORER:
                out.append(os.path.join(base, f))
    return out


def traiter(s):
    fait = 0
    # 1. la bascule, dans le <head>, avant la feuille de style
    if BLOC.search(s):
        s = BLOC.sub(lambda _m: BASCULE, s, count=1)
    else:
        m = re.search(r'\n\s*<link rel="stylesheet" href="[^"]*style\.css', s)
        if not m:
            return s, 0
        s = s[:m.start()] + "\n  " + BASCULE + s[m.start():]
        fait += 1

    # ⚠️ UNE SEULE CLÉ DE CACHE POUR UNE SEULE FEUILLE. Les pages en portaient
    # SIX différentes (?v=1, 2, 3, 5, 6, 10) : celles restées en ?v=1 auraient
    # gardé l'ancienne feuille dans le cache du navigateur, donc jamais reçu
    # le thème clair — publié pour personne, sans message d'erreur.
    s = re.sub(r"style\.css\?v=\d+", "style.css?v=%d" % VERSION_CSS, s)

    # 2. le bouton, dans la barre de navigation
    if 'id="theme-btn"' not in s:
        m = re.search(r'(<ul class="nav-links">)', s)
        if m:
            s = s[:m.end()] + "\n      " + BOUTON + s[m.end():]
            fait += 1
        else:
            # Les pages sans barre de navigation — l'administration — reçoivent
            # un bouton flottant plutôt que rien : le choix de fond ne dépend
            # pas de la présence d'un menu.
            m = re.search(r"<body[^>]*>", s)
            if m:
                s = (s[:m.end()]
                     + '\n<button class="theme-btn" id="theme-btn" type="button"'
                       ' aria-live="polite" style="position:fixed;top:0.8rem;'
                       'right:0.8rem;z-index:99">◐ Auto</button>'
                     + s[m.end():])
                fait += 1

    # 3. l'applicateur, en fin de page
    if "theme-btn\")" not in s.split("</body>")[0].rsplit(MARQUE, 1)[0] \
            or s.count(MARQUE) < 4:
        m = re.search(r"</body>", s, re.I)
        if m and s.count(MARQUE) < 4:
            s = s[:m.start()] + APPLI + "\n" + s[m.start():]
            fait += 1
    return s, fait


def main():
    verifier = "--verifier" in sys.argv
    manquantes, touchees = [], 0
    for p in pages():
        s = io.open(p, encoding="utf-8").read()
        neuf, _ = traiter(s)
        rel = os.path.relpath(p, RACINE)
        if 'id="theme-btn"' not in neuf:
            manquantes.append(rel)
            continue
        if neuf != s:
            if verifier:
                manquantes.append(rel)
                continue
            io.open(p + ".tmp", "w", encoding="utf-8", newline="\n").write(neuf)
            os.replace(p + ".tmp", p)
            touchees += 1

    if manquantes:
        print("  %d page(s) sans selecteur : %s"
              % (len(manquantes), " ".join(manquantes[:6])))
        return 1
    print("  Theme : %d page(s) modifiee(s), %d page(s) au total portent le selecteur"
          % (touchees, len(pages())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
