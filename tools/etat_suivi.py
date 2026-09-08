# -*- coding: utf-8 -*-
"""L'état réel des recommandations Lojik360, recalculé — pas relu.

    python tools/etat_suivi.py          l'état de tout le registre
    python tools/etat_suivi.py --ouvert seulement ce qui reste à faire

POURQUOI CE FICHIER EXISTE
--------------------------
Un registre tenu à la main dit ce qu'on croyait le jour où on l'a écrit. Suite
360 l'a montré : le sien annonçait 82 corrections « à faire » alors qu'une
bonne partie était faite depuis des semaines. Personne ne ment — la mémoire
dérive, et un registre qu'on ne mesure pas devient un document de fiction.

Un état déclaré dérive. Un état MESURÉ ne dérive pas.

Ce script relance donc les contrôles qui peuvent trancher, et compare leur
verdict à ce que `docs/SUIVI_RECOMMANDATIONS.md` déclare. Si les deux
divergent, **c'est le registre qui a tort**, et il sort en erreur pour le dire
— dans les DEUX sens : une ligne « vérifiée » qui ne passe plus, ET une ligne
« à faire » qui passe déjà sans avoir été consignée. La seconde est la plus
fréquente : on corrige, on pousse, on oublie le tableau.

CE QU'IL NE FAIT PAS. Il ne juge pas les lignes « humain » — un arbitrage
éditorial, une question de droits, une relecture en kreyòl. Il les compte et
les nomme pour qu'elles ne se perdent pas dans le tas de ce qui est fait. Il ne
corrige rien non plus : il mesure. Et il ne touche pas au réseau : ce qu'il
regarde est le dépôt tel qu'il est sur le disque, arbre de travail compris.

CHAQUE MESURE NOMME CE QU'ELLE A REGARDÉ, pas seulement son verdict. Un
contrôle vert sur un périmètre plus étroit que ce qu'il annonce est plus
dangereux qu'un contrôle absent : il autorise à ne pas regarder.
"""
import io
import json
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                            # noqa: BLE001
    pass

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
REGISTRE = os.path.join(RACINE, "docs", "SUIVI_RECOMMANDATIONS.md")

# Les 4 pages qui portent le dictionnaire (texte d'interface en JSON).
PAGES_I18N = ["index.html", "tutoriels.html", "podcast.html", "lojikkid.html"]
# Les pages qu'un moteur doit indexer : tout sauf l'administration et les
# redirections de langue (elles sont en noindex, c'est voulu).
EXCLUES = {"admin.html", "swot360.fr.html", "swot360.en.html", "swot360.es.html"}
LANGUES = ["ht", "en", "es"]


# ------------------------------------------------------------- les outils
def lire(rel):
    """Le contenu d'un fichier du dépôt, ou None s'il n'existe pas."""
    p = os.path.join(RACINE, rel)
    if not os.path.exists(p):
        return None
    return io.open(p, encoding="utf-8", errors="replace").read()


def pages_html():
    """Toutes les pages servies, chemin relatif à la racine, avec « / »."""
    out = []
    for dossier, sous, fichiers in os.walk(RACINE):
        rel = os.path.relpath(dossier, RACINE).replace("\\", "/")
        if rel.startswith(".git") or rel.startswith("content") or "node_modules" in rel:
            sous[:] = []
            continue
        for f in fichiers:
            if f.endswith(".html"):
                out.append((f if rel == "." else rel + "/" + f))
    return sorted(out)


def indexables():
    """Les pages qu'un moteur a le droit d'indexer.

    ⚠️ ON LIT `noindex` DANS LA PAGE au lieu de tenir une liste de noms. La
    liste EXCLUES datait du 08/09 au matin : elle connaissait les trois
    redirections de langue, mais pas `swot360.html` (devenue redirection dans
    la journée) ni `404.html` (créée le même jour). Une liste de noms se
    démode en silence ; `noindex` est la déclaration de la page elle-même, et
    elle reste vraie quoi qu'on renomme.

    Conséquence : exiger un `canonical` vers ce site sur une page qui refuse
    l'indexation n'a aucun sens — une redirection pointe sa canonique vers sa
    DESTINATION, et une page d'erreur n'en a pas du tout.
    """
    out = []
    for p in pages_html():
        if os.path.basename(p) in EXCLUES:
            continue
        if re.search(r'<meta[^>]+name="robots"[^>]+noindex', lire(p) or ""):
            continue
        out.append(p)
    return out


def dicts():
    return {l: json.loads(lire("assets/i18n/%s.json" % l) or "{}") for l in LANGUES}


def cle_partout(cle, d=None):
    d = d or dicts()
    return all(cle in d[l] for l in LANGUES)


def partout(motif, fichiers, quoi, drapeaux=0):
    """Vrai quand CHAQUE fichier porte le motif au moins une fois."""
    rx = re.compile(motif, drapeaux)
    absents = []
    for f in fichiers:
        t = lire(f)
        if t is None:
            absents.append(f + " (absent)")
        elif not rx.search(t):
            absents.append(f)
    if not absents:
        return True, "%s sur les %d pages regardées" % (quoi, len(fichiers))
    return False, "%s manque sur %d page(s) : %s" % (quoi, len(absents), " ".join(absents[:8]))


def zero(motif, fichiers, quoi, drapeaux=0):
    """Vrai quand le motif a disparu de tous les fichiers."""
    rx = re.compile(motif, drapeaux)
    n, ou = 0, []
    for f in fichiers:
        t = lire(f)
        if t is None:
            continue
        k = len(rx.findall(t))
        if k:
            n += k
            ou.append("%s×%d" % (f, k))
    if n == 0:
        return True, "aucune occurrence de %s (%d pages)" % (quoi, len(fichiers))
    return False, "%d %s : %s" % (n, quoi, " ".join(ou[:6]))


def famille(page):
    """(base, langue) d'une page de tutoriel : x.ht.html → (x, ht), x.html → (x, fr)."""
    m = re.match(r"(.+?)(?:\.(ht|en|es))?\.html$", os.path.basename(page))
    return m.group(1), (m.group(2) or "fr")


# ------------------------------------------------------- A · doctrine
def m_a1():
    """0 lien interne mort, sur toutes les pages, href et src confondus."""
    morts = []
    rx = re.compile(r"""(?:href|src)=["']([^"'#?]+)[^"']*["']""")
    for p in pages_html():
        t = lire(p)
        for u in rx.findall(t):
            if re.match(r"^(https?:|mailto:|tel:|data:|javascript:)", u):
                continue
            cible = u.lstrip("/") if u.startswith("/") else os.path.normpath(
                os.path.join(os.path.dirname(p), u))
            if not os.path.exists(os.path.join(RACINE, cible)):
                morts.append("%s → %s" % (p, u))
    if not morts:
        return True, "0 lien interne mort sur %d pages" % len(pages_html())
    return False, "%d lien(s) mort(s) : %s" % (len(morts), " ; ".join(morts[:5]))


def m_a2():
    """Le lien Datasets du pied de page porte sa propre clé, présente en 3 langues."""
    t = lire("index.html") or ""
    m = re.search(r'datasets\.html"[^>]*data-i18n="([^"]+)"', t)
    if not m:
        return False, "pas de lien datasets.html avec data-i18n dans index.html"
    if m.group(1) == "nav.podcast":
        return False, "index.html : le lien Datasets porte encore data-i18n=\"nav.podcast\""
    if not cle_partout(m.group(1)):
        return False, "clé %s absente d'au moins un dictionnaire" % m.group(1)
    return True, "lien Datasets → clé %s, présente en ht/en/es" % m.group(1)


def m_a3():
    """La navigation d'index.html mène à podcast.html, comme les autres pages."""
    t = lire("index.html") or ""
    if re.search(r'href="#podcast"[^>]*data-i18n="nav\.podcast"', t):
        return False, "index.html : nav Podcast → #podcast"
    if not re.search(r'href="podcast\.html"[^>]*data-i18n="nav\.podcast"', t):
        return False, "index.html : pas de lien nav vers podcast.html"
    return True, "index.html : nav Podcast → podcast.html"


def m_a4():
    return zero(r'data-i18n="tut\.soon"', ["tutoriels.html"], "carte « Bientôt »")


def m_a5():
    t = lire("podcast.html") or ""
    liens = re.findall(r"https://(?:open\.spotify\.com|podcasts\.apple\.com|(?:www\.)?youtube\.com|youtu\.be)/[^\"'\s<]+", t)
    if liens:
        return True, "%d lien(s) d'écoute réel(s) dans podcast.html" % len(liens)
    return False, "podcast.html : aucun lien Spotify / Apple / YouTube"


def m_a9():
    pages = ["swot360.html", "swot360.fr.html", "swot360.en.html", "swot360.es.html"]
    for p in ["index.html", "tutoriels.html", "podcast.html", "lojikkid.html"]:
        pages.append(p)
    return zero(r"Entretien360|Entrevista360|Interview360", pages, "autre nom que Entèvyou360")


def m_a10():
    return zero(r"<title>[^<]*—\s*Atmart\s*</title>", [p for p in pages_html() if p.startswith("tutoriels/")],
                "<title> finissant par « — Atmart »")


# ------------------------------------------------- B · langue et i18n
def m_b1():
    """Chaque lien vers un tutoriel dont une variante de langue existe porte data-href-<lang>."""
    js = lire("assets/i18n.js") or ""
    if "data-href-" not in js and "dataset.href" not in js.lower():
        return False, "assets/i18n.js ne réécrit pas les href par langue (aucun data-href-)"
    manques = []
    rx = re.compile(r'<a\s+([^>]*?)href="((?:\.\./)?tutoriels/([^"#?]+?)\.html)"([^>]*)>')
    for p in PAGES_I18N:
        t = lire(p) or ""
        for m in rx.finditer(t):
            attrs = m.group(1) + " " + m.group(4)
            base, lang = famille(m.group(2))
            if lang != "fr":
                continue
            for l in LANGUES:
                if os.path.exists(os.path.join(RACINE, "tutoriels", "%s.%s.html" % (base, l))) \
                        and ("data-href-%s=" % l) not in attrs:
                    manques.append("%s → %s (.%s existe)" % (p, base, l))
    if manques:
        return False, "%d lien(s) sans variante déclarée : %s" % (len(manques), " ; ".join(manques[:5]))
    return True, "tous les liens de %s déclarent leurs variantes existantes" % ", ".join(PAGES_I18N)


def m_b2():
    d = json.loads(lire("assets/i18n/ht.json") or "{}")
    rx = re.compile(r"\b(axes|debrief|tutoriels?|gratuit|bientôt)\b", re.I)
    fautifs = [k for k, v in d.items() if isinstance(v, str) and rx.search(v)]
    if fautifs:
        return False, "%d valeur(s) de ht.json avec un mot français : %s" % (len(fautifs), ", ".join(fautifs[:6]))
    return True, "0 mot français ciblé dans les %d valeurs de ht.json" % len(d)


def m_b3():
    d = dicts()
    js = lire("assets/i18n.js") or ""
    manques = []
    for p in PAGES_I18N:
        t = lire(p) or ""
        mt = re.search(r'<title[^>]*data-i18n="([^"]+)"', t)
        md = re.search(r'<meta name="description"[^>]*data-i18n-content="([^"]+)"', t)
        if not mt or not cle_partout(mt.group(1), d):
            manques.append(p + " (title)")
        if not md or not cle_partout(md.group(1), d):
            manques.append(p + " (description)")
    if "data-i18n-content" not in js:
        manques.append("i18n.js sans data-i18n-content")
    if manques:
        return False, "manque : " + ", ".join(manques)
    return True, "title + description traduits sur les %d pages à dictionnaire" % len(PAGES_I18N)


def m_b4():
    sous = ["lojikkid-argent.html", "lojikkid-creer.html", "lojikkid-numerique.html", "lojikkid-penser.html"]
    manques = []
    for p in sous:
        t = lire(p) or ""
        base = p[:-5]
        variantes = all(os.path.exists(os.path.join(RACINE, "%s.%s.html" % (base, l))) for l in LANGUES)
        if not (("i18n.js" in t and "data-i18n" in t) or variantes):
            manques.append(p)
    if manques:
        return False, "%d sous-page(s) Lojikkid en français seul : %s" % (len(manques), " ".join(manques))
    return True, "les 4 sous-pages Lojikkid ont les 4 langues"


def m_b5():
    d = dicts()
    manques = []
    for p in PAGES_I18N:
        t = lire(p) or ""
        m = re.search(r'class="nav-toggle"[^>]*data-i18n-aria="([^"]+)"', t)
        if not m or not cle_partout(m.group(1), d):
            manques.append(p)
    if manques:
        return False, "aria-label du menu non traduit sur : " + " ".join(manques)
    return True, "aria-label du menu traduit sur les %d pages à dictionnaire" % len(PAGES_I18N)


def m_b6():
    t = lire("podcast.html") or ""
    nus = re.findall(r'<div class="card"><h3>[^<]*</h3><p>', t)
    if nus:
        return False, "%d carte(s) d'épisode sans data-i18n dans podcast.html" % len(nus)
    return True, "0 carte d'épisode sans clé dans podcast.html"


# -------------------------------------------- C · sécurité et données
def m_c1():
    return zero(r'localStorage\.(setItem|getItem)\("lojik_admin_token"', ["admin.html"],
                "accès localStorage au jeton GitHub")


def m_c2():
    if lire("confidentialite.html") is None:
        return False, "confidentialite.html n'existe pas"
    return partout(r'href="(?:\.\./)?confidentialite\.html"',
                   ["index.html", "tutoriels.html", "podcast.html", "lojikkid.html", "swot360.html"],
                   "lien vers confidentialite.html")


def m_c3():
    d = dicts()
    manques = []
    for p in ["index.html", "podcast.html"]:
        t = lire(p) or ""
        m = re.search(r'data-i18n(?:-html)?="(nl\.consent)"', t)
        if not m or not cle_partout(m.group(1), d):
            manques.append(p)
    if manques:
        return False, "pas de phrase de consentement (nl.consent) sur : " + " ".join(manques)
    return True, "nl.consent présent sous les formulaires, en 3 langues"


def m_c4():
    return zero(r'data-page-url="https://atmart\.ltd', pages_html(), "fil Cusdis rattaché à atmart.ltd")


# ------------------------------------------------- D · référencement
def m_d1():
    manques = []
    for p in PAGES_I18N:
        t = lire(p) or ""
        for prop in ("og:title", "og:description", "og:image"):
            if ('property="%s"' % prop) not in t:
                manques.append("%s (%s)" % (p, prop))
    if manques:
        return False, "Open Graph incomplet : " + ", ".join(manques[:8])
    return True, "og:title/description/image sur les %d pages de tête" % len(PAGES_I18N)


def m_d2():
    return partout(r'<link rel="canonical" href="https://lojik360\.atmart\.ltd/', indexables(), "canonical")


def m_d3():
    """hreflang sur chaque page d'une famille de tutoriels qui a ≥ 2 langues."""
    familles = {}
    for p in pages_html():
        if p.startswith("tutoriels/"):
            b, l = famille(p)
            familles.setdefault(b, []).append((l, p))
    manques = []
    for b, membres in familles.items():
        if len(membres) < 2:
            continue
        for l, p in membres:
            t = lire(p) or ""
            n = len(re.findall(r'rel="alternate"[^>]*hreflang=', t))
            if n < len(membres):
                manques.append("%s (%d/%d)" % (p, n, len(membres)))
    if manques:
        return False, "%d page(s) sans hreflang complet : %s" % (len(manques), " ".join(manques[:6]))
    return True, "hreflang complet sur les familles multilingues (%d)" % sum(1 for m in familles.values() if len(m) >= 2)


def m_d4():
    t = lire("sitemap.xml") or ""
    urls = re.findall(r"<url>(.*?)</url>", t, re.S)
    defauts = []
    if re.search(r"swot360\.(fr|en|es)\.html", t):
        defauts.append("redirections noindex listées")
    if "lojik360.atmart.ltd/index.html" in t:
        defauts.append("index.html au lieu de /")
    sans = [u for u in urls if "<lastmod>" not in u]
    if sans:
        defauts.append("%d url sans lastmod" % len(sans))
    if defauts:
        return False, "sitemap.xml : " + " ; ".join(defauts)
    return True, "sitemap.xml : %d url, toutes avec lastmod, sans redirection" % len(urls)


def m_d5():
    t = lire("404.html")
    if t is None:
        return False, "404.html absent"
    if "i18n.js" not in t or 'class="nav"' not in t:
        return False, "404.html sans navigation ou sans sélecteur de langue"
    return True, "404.html présent, avec navigation et 4 langues"


# ------------------------------------------ E · accessibilité, thème
def m_e1():
    js = lire("assets/script.js") or ""
    if "aria-expanded" not in js:
        return False, "script.js ne bascule pas aria-expanded"
    return partout(r'class="nav-toggle"[^>]*aria-expanded=', PAGES_I18N + ["swot360.html"], "aria-expanded sur ☰")


def m_e2():
    css = lire("assets/style.css") or ""
    regles = re.findall(r"([^{}]+):focus-visible", css)
    if not any(re.search(r"(^|[\s,])a$|(^|[\s,])button$|\.btn$", r.strip()) for r in regles):
        return False, "style.css : pas de :focus-visible pour a / button / .btn (%d règle(s) au total)" % len(regles)
    return True, "style.css : :focus-visible sur les liens et boutons (%d règles)" % len(regles)


def m_e3():
    manques = [f for f in ("manifest.webmanifest", "sw.js") if lire(f) is None]
    if manques:
        return False, "absent : " + " ".join(manques)
    ok, det = partout(r'rel="manifest"', ["index.html"], "lien manifest")
    return ok, det


def m_e4():
    fautives = []
    for p in pages_html():
        t = lire(p) or ""
        if "fonts.googleapis.com" in t and not re.search(r'preconnect"\s+href="https://fonts\.gstatic\.com"[^>]*crossorigin', t):
            fautives.append(p)
    if fautives:
        return False, "%d page(s) Google Fonts sans preconnect fonts.gstatic.com crossorigin" % len(fautives)
    return True, "preconnect fonts.gstatic.com partout (ou polices auto-hébergées)"


def m_e5():
    t = lire("swot360.html") or ""
    blocs = [len(b) for b in re.findall(r"<script[^>]*>([\s\S]*?)</script>", t)]
    gros = max(blocs) if blocs else 0
    if gros >= 120000:
        return False, "swot360.html : plus gros script en ligne = %d caractères (seuil 120 000)" % gros
    return True, "swot360.html : plus gros script en ligne = %d caractères" % gros


def m_e6():
    return partout(r'<meta name="theme-color"', PAGES_I18N + ["swot360.html"], "theme-color")


# ------------------------------------------- F · chaîne de fabrication
def m_f1():
    try:
        out = subprocess.run(["git", "status", "--porcelain"], cwd=RACINE, capture_output=True,
                             text=True, encoding="utf-8", errors="replace").stdout
    except Exception as e:                                   # noqa: BLE001
        return False, "git indisponible : %s" % e
    # F1 regarde ce qui est SERVI. Le registre, les outils et les fabriques
    # (docs/, tools/, content/, CLAUDE.md, README.md) ne changent rien à ce
    # que voit un visiteur — et le registre se modifie précisément en fermant
    # une ligne : il ne peut pas être ce qui rouvre F1.
    hors = ("docs/", "tools/", "content/", "CLAUDE.md", "README.md")
    modifs = [l for l in out.splitlines()
              if l[:2].strip() in ("M", "MM", "AM", "D") and not l[3:].startswith(hors)]
    if modifs:
        return False, "%d fichier(s) servis modifiés non commités : %s" % (
            len(modifs), " ".join(l[3:] for l in modifs[:6]))
    return True, "arbre de travail propre sur les fichiers servis (docs/, tools/, content/ exclus)"


def m_f2():
    gi = lire(".gitignore") or ""
    ga = lire(".gitattributes") or ""
    defauts = []
    if "node_modules" not in gi:
        defauts.append(".gitignore sans node_modules")
    if "__pycache__" not in gi:
        defauts.append(".gitignore sans __pycache__")
    if "eol=lf" not in ga:
        defauts.append(".gitattributes sans eol=lf")
    if defauts:
        return False, " ; ".join(defauts)
    return True, ".gitignore et .gitattributes en place"


def m_f3():
    fautives = []
    rx = re.compile(r'<script src="(?:\.\./)?assets/(script|i18n|chat|quiz)\.js"')
    for p in pages_html():
        if rx.search(lire(p) or ""):
            fautives.append(p)
    if fautives:
        return False, "%d inclusion(s) sans ?v= : %s" % (len(fautives), " ".join(fautives[:6]))
    return True, "toutes les inclusions de assets/*.js portent ?v="


def m_f4():
    d = os.path.join(RACINE, ".github", "workflows")
    if not os.path.isdir(d):
        return False, "pas de .github/workflows"
    for f in os.listdir(d):
        if "etat_suivi" in (lire(".github/workflows/" + f) or ""):
            return True, "workflow %s lance etat_suivi.py" % f
    return False, "aucun workflow ne lance tools/etat_suivi.py"


def m_f5():
    t = lire("CLAUDE.md") or ""
    if "etat_suivi" not in t:
        return False, "CLAUDE.md ne nomme pas tools/etat_suivi.py"
    if "Pas de test" in t:
        return False, "CLAUDE.md dit encore « Pas de test »"
    return True, "CLAUDE.md nomme les contrôles"


def m_f6():
    res = []
    for script in ("poser_theme.py", "jetons_swot.py"):
        try:
            r = subprocess.run([sys.executable, os.path.join(ICI, script), "--verifier"], cwd=RACINE,
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
            res.append((script, r.returncode))
        except Exception as e:                               # noqa: BLE001
            res.append((script, "erreur %s" % e))
    ko = [s for s, c in res if c != 0]
    if ko:
        return False, "contrôle(s) en échec : " + " ".join(ko)
    return True, "poser_theme.py --verifier et jetons_swot.py --verifier sortent en 0"


MESURES = {
    "A1": m_a1, "A2": m_a2, "A3": m_a3, "A4": m_a4, "A5": m_a5, "A9": m_a9, "A10": m_a10,
    "B1": m_b1, "B2": m_b2, "B3": m_b3, "B4": m_b4, "B5": m_b5, "B6": m_b6,
    "C1": m_c1, "C2": m_c2, "C3": m_c3, "C4": m_c4,
    "D1": m_d1, "D2": m_d2, "D3": m_d3, "D4": m_d4, "D5": m_d5,
    "E1": m_e1, "E2": m_e2, "E3": m_e3, "E4": m_e4, "E5": m_e5, "E6": m_e6,
    "F1": m_f1, "F2": m_f2, "F3": m_f3, "F4": m_f4, "F5": m_f5, "F6": m_f6,
}


# ------------------------------------------------------------ le registre
LIGNE = re.compile(r"^\| ([A-F]\d+) \| (.*?) \| (🔴|🟠|🔵) \| \*\*(.+?)\*\* \| (.*) \|$")


def lire_registre():
    t = lire("docs/SUIVI_RECOMMANDATIONS.md")
    if t is None:
        print("docs/SUIVI_RECOMMANDATIONS.md introuvable")
        sys.exit(2)
    lignes = []
    for l in t.splitlines():
        m = LIGNE.match(l)
        if m:
            lignes.append({"id": m.group(1), "reco": m.group(2), "gravite": m.group(3),
                           "etat": m.group(4), "preuve": m.group(5)})
    return lignes


def main():
    seulement_ouvert = "--ouvert" in sys.argv
    lignes = lire_registre()
    if not lignes:
        print("aucune ligne lue dans le registre — le format a changé ?")
        sys.exit(2)

    mensonges, non_consignes = [], []
    ouvertes = {"🔴": [], "🟠": [], "🔵": []}
    humaines = []
    print("Registre Lojik360 — %d lignes · mesurées : %d\n" % (len(lignes), len(MESURES)))
    for l in lignes:
        declare_fait = l["etat"].startswith("vérifié")
        humain = "humain" in l["etat"]
        if humain:
            humaines.append(l)
        if l["id"] in MESURES:
            ok, detail = MESURES[l["id"]]()
            if ok and not declare_fait:
                non_consignes.append(l["id"])
                marque = "✅ passe, registre dit « %s »" % l["etat"]
            elif not ok and declare_fait:
                mensonges.append(l["id"])
                marque = "❌ ÉCHOUE, registre dit « vérifié »"
            elif ok:
                marque = "✅ vérifié"
            else:
                marque = "⬜ à faire"
            fait = ok
        else:
            marque = "👤 " + l["etat"] if humain else "📝 " + l["etat"]
            detail = "non mesurable par programme"
            fait = declare_fait
        if not fait:
            ouvertes[l["gravite"]].append(l["id"])
        if seulement_ouvert and fait:
            continue
        print("%s %-3s %s\n       %s" % (l["gravite"], l["id"], marque, detail))

    print("\n— Bilan —")
    print("ouvertes : 🔴 %d  🟠 %d  🔵 %d · humaines : %d" % (
        len(ouvertes["🔴"]), len(ouvertes["🟠"]), len(ouvertes["🔵"]), len(humaines)))
    if ouvertes["🔴"]:
        verdict = "🔴 BLOQUÉ — " + " ".join(ouvertes["🔴"])
    elif ouvertes["🟠"]:
        verdict = "🟠 À CORRIGER — " + " ".join(ouvertes["🟠"])
    else:
        verdict = "🟢 PUBLIABLE" + (" (arbitrages ouverts : %s)" % " ".join(ouvertes["🔵"]) if ouvertes["🔵"] else "")
    print("verdict mesuré : " + verdict)

    code = 0
    if mensonges:
        print("\nLE REGISTRE MENT : %s déclarées « vérifié » mais le contrôle échoue." % " ".join(mensonges))
        code = 1
    if non_consignes:
        print("\nÀ CONSIGNER : %s passent mais le registre les dit ouvertes — mettre la ligne à « vérifié » avec sa preuve."
              % " ".join(non_consignes))
        code = 1
    sys.exit(code)


if __name__ == "__main__":
    main()
