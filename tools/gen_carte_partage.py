# -*- coding: utf-8 -*-
"""Fabrique l'image de partage 1200×630 annoncée par les balises Open Graph.

    python tools/gen_carte_partage.py

⚠️ SANS ELLE, OPEN GRAPH MENT. `poser_tete.py` déclare
`og:image = /assets/brand/share-1200x630.jpg` sur les 39 pages. Si le fichier
n'existe pas, chaque partage sur WhatsApp, Facebook ou LinkedIn affiche un
cadre vide — c'est-à-dire pire que pas de balise du tout, parce que le réseau
a essayé et échoué.

1200 × 630 est le format que lisent ces trois-là. On la dessine ici plutôt que
de la déposer à la main : elle suit la marque, et le jour où le logo change,
elle change avec lui.
"""
import io
import os
import sys

from PIL import Image, ImageDraw, ImageFont

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                            # noqa: BLE001
    pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARQUE = os.path.join(RACINE, "assets", "brand")

TAILLE = (1200, 630)
NAVY = (10, 26, 47, 255)
TEAL = (46, 196, 182, 255)
ENCRE = (234, 242, 251, 255)
DOUX = (159, 179, 200, 255)


def police(px, gras=True):
    """Une police du système, ou celle de PIL si la machine n'en a aucune."""
    noms = ("segoeuib.ttf", "arialbd.ttf") if gras else ("segoeui.ttf", "arial.ttf")
    for nom in noms:
        for base in (r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu"):
            p = os.path.join(base, nom)
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, px)
                except Exception:                            # noqa: BLE001
                    pass
    return ImageFont.load_default()


def main():
    im = Image.new("RGBA", TAILLE, NAVY)
    d = ImageDraw.Draw(im)

    # une bande d'accent en bas : elle donne le ton même en miniature
    d.rectangle([0, TAILLE[1] - 10, TAILLE[0], TAILLE[1]], fill=TEAL)

    x = 96
    logo = os.path.join(MARQUE, "logo-dark-96.png")
    if os.path.exists(logo):
        l = Image.open(logo).convert("RGBA").resize((150, 150), Image.LANCZOS)
        im.alpha_composite(l, (x, 168))
        x += 150 + 44

    d.text((x, 196), "Lojik", font=police(96), fill=ENCRE)
    largeur = d.textlength("Lojik", font=police(96))
    d.text((x + largeur, 196), "360", font=police(96), fill=TEAL)

    d.text((x, 312), "Penser et créer à l'ère de l'IA",
           font=police(40, False), fill=ENCRE)
    d.text((x, 372), "Tutoriels gratuits · 4 langues · une marque d'Atmart LLC",
           font=police(30, False), fill=DOUX)

    sortie = os.path.join(MARQUE, "share-1200x630.jpg")
    im.convert("RGB").save(sortie, "JPEG", quality=86, optimize=True)
    print("  %-26s %dx%d" % ("share-1200x630.jpg", *TAILLE))


if __name__ == "__main__":
    main()
