# -*- coding: utf-8 -*-
"""Build Lojik360 reader pages (axis: Deleguer) from the two new FR docx tutorials.
Usage: python newtuto_build.py
Outputs: tutoriels/prompting-ia.html and tutoriels/excel-ia.html in Lojik360_site.
"""
import zipfile, re, html, io, sys, unicodedata

def deacc(t):
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn").lower()

SITE = r"C:\Users\USUARIO\Power_BI_Claude\Lojik360_site"

def unesc(s):
    return (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"').replace("&#39;", "'"))

# ---------- restauration des accents (le docx source est en partie sans accents) ----------
ACCENTS = {
 "reponse":"réponse","reponses":"réponses","donnee":"donnée","donnees":"données",
 "resultat":"résultat","resultats":"résultats","verifier":"vérifier","verifie":"vérifie",
 "verifiez":"vérifiez","verifiee":"vérifiée","verifiees":"vérifiées","verifiable":"vérifiable",
 "verification":"vérification","verifications":"vérifications",
 "decision":"décision","decisions":"décisions","decideur":"décideur","decider":"décider","decidez":"décidez",
 "responsabilite":"responsabilité","premiere":"première","premieres":"premières",
 "etre":"être","etes":"êtes","modele":"modèle","modeles":"modèles","qualite":"qualité",
 "cout":"coût","couts":"coûts","tache":"tâche","taches":"tâches",
 "anonymisee":"anonymisée","anonymisees":"anonymisées","anonymiser":"anonymiser","anonymisez":"anonymisez",
 "hypothese":"hypothèse","hypotheses":"hypothèses","critere":"critère","criteres":"critères",
 "competence":"compétence","competences":"compétences","confidentialite":"confidentialité",
 "probleme":"problème","problemes":"problèmes","beneficiaire":"bénéficiaire","beneficiaires":"bénéficiaires",
 "element":"élément","elements":"éléments","eviter":"éviter","evitez":"évitez",
 "nommee":"nommée","nommees":"nommées","interpretation":"interprétation","interpretations":"interprétations",
 "methode":"méthode","methodes":"méthodes","accelerer":"accélérer","creer":"créer","creez":"créez",
 "deja":"déjà","controle":"contrôle","controles":"contrôles","controler":"contrôler",
 "coherence":"cohérence","coherent":"cohérent","coherente":"cohérente",
 "synthese":"synthèse","depart":"départ","theme":"thème","themes":"thèmes",
 "reussi":"réussi","reussie":"réussie","reussite":"réussite","executer":"exécuter","executez":"exécutez",
 "executant":"exécutant","acceptee":"acceptée","definition":"définition","definitions":"définitions",
 "revision":"révision","revisions":"révisions","scenario":"scénario","scenarios":"scénarios",
 "numero":"numéro","general":"général","generale":"générale","generique":"générique","generiques":"génériques",
 "ecrire":"écrire","ecrivez":"écrivez","ecrit":"écrit","ecrite":"écrite","ecrits":"écrits",
 "etape":"étape","etapes":"étapes","equipe":"équipe","equipes":"équipes","ecran":"écran",
 "echange":"échange","echanges":"échanges","evaluer":"évaluer","evaluez":"évaluez","evaluation":"évaluation",
 "etat":"état","etats":"états","egalement":"également","eleve":"élevé","eleves":"élevés",
 "elevee":"élevée","elevees":"élevées","ete":"été","ecart":"écart","ecarts":"écarts",
 "enonce":"énoncé","experience":"expérience","experiences":"expériences",
 "precis":"précis","precise":"précise","precises":"précises","precisez":"précisez","precision":"précision",
 "prealable":"préalable","preparation":"préparation","preparer":"préparer","preparez":"préparez",
 "presentation":"présentation","presenter":"présenter","presentez":"présentez",
 "protegee":"protégée","protegees":"protégées","proteger":"protéger","protegez":"protégez",
 "realiste":"réaliste","realisez":"réalisez","realiser":"réaliser","realite":"réalité",
 "recuperer":"récupérer","redaction":"rédaction","reduire":"réduire","reduisez":"réduisez",
 "reel":"réel","reelle":"réelle","reels":"réels","reelles":"réelles",
 "reference":"référence","references":"références","reflechir":"réfléchir","reflexe":"réflexe",
 "reflexion":"réflexion","regle":"règle","regles":"règles","regulier":"régulier","reguliere":"régulière",
 "repere":"repère","reperer":"repérer","reperez":"repérez","repetez":"répétez","repetition":"répétition",
 "repondez":"répondez","repondre":"répondre","repond":"répond","resumer":"résumer","resumez":"résumez",
 "reutilisable":"réutilisable","reutilisables":"réutilisables","revisez":"révisez",
 "role":"rôle","roles":"rôles","securite":"sécurité","securise":"sécurisé","securisee":"sécurisée",
 "selection":"sélection","selectionnez":"sélectionnez","separer":"séparer","separez":"séparez",
 "separation":"séparation","serie":"série","series":"séries","specifique":"spécifique","specifiques":"spécifiques",
 "strategie":"stratégie","strategies":"stratégies","succes":"succès","systeme":"système","systemes":"systèmes",
 "tres":"très","verite":"vérité","video":"vidéo","videos":"vidéos","zero":"zéro",
 "apres":"après","acces":"accès","progres":"progrès","interet":"intérêt","interets":"intérêts",
 "arret":"arrêt","arreter":"arrêter","arretez":"arrêtez","bibliotheque":"bibliothèque",
 "caractere":"caractère","caracteres":"caractères","categorie":"catégorie","categories":"catégories",
 "cle":"clé","cles":"clés","completez":"complétez","complete":"complète","completer":"compléter",
 "concu":"conçu","concue":"conçue","connaitre":"connaître","considerez":"considérez","cote":"côté",
 "creativite":"créativité","dediee":"dédiée","dedie":"dédié","defaut":"défaut","defauts":"défauts",
 "defi":"défi","defis":"défis","definir":"définir","definissez":"définissez","degre":"degré",
 "derniere":"dernière","dernieres":"dernières","desormais":"désormais","detail":"détail","details":"détails",
 "detaillee":"détaillée","detecter":"détecter","detectez":"détectez",
 "developpement":"développement","developper":"développer","developpez":"développez",
 "difficulte":"difficulté","difficultes":"difficultés","deleguer":"déléguer","deleguez":"déléguez",
 "delegation":"délégation","deroule":"déroule","deroulement":"déroulement",
 "deuxieme":"deuxième","troisieme":"troisième","different":"différent","differente":"différente",
 "differents":"différents","differentes":"différentes","difference":"différence","differences":"différences",
 "maitriser":"maîtriser","maitrise":"maîtrise","maniere":"manière","frontiere":"frontière",
 "fiabilite":"fiabilité","facilite":"facilité","fenetre":"fenêtre","genere":"génère","generer":"générer",
 "generez":"générez","generee":"générée","generees":"générées","grille":"grille",
 "idee":"idée","idees":"idées","identifie":"identifie","incoherence":"incohérence","incoherences":"incohérences",
 "independant":"indépendant","independante":"indépendante","integrer":"intégrer","integrez":"intégrez",
 "interpreter":"interpréter","interpretez":"interprétez","iterez":"itérez","iteration":"itération",
 "iterations":"itérations","lisibilite":"lisibilité","litteralement":"littéralement",
 "memoire":"mémoire","metier":"métier","metiers":"métiers","modelisation":"modélisation",
 "necessaire":"nécessaire","necessaires":"nécessaires","negatif":"négatif","negative":"négative",
 "operation":"opération","operations":"opérations","organisee":"organisée","parametres":"paramètres",
 "pedagogique":"pédagogique","penalite":"pénalité","perimetre":"périmètre","periode":"période",
 "periodes":"périodes","pertinence":"pertinence","possibilite":"possibilité","possibilites":"possibilités",
 "prevision":"prévision","previsions":"prévisions","prevu":"prévu","prevue":"prévue",
 "priorite":"priorité","priorites":"priorités","procedure":"procédure","procedures":"procédures",
 "propriete":"propriété","proprietes":"propriétés","protocole":"protocole",
 "recette":"recette","recommande":"recommandé","recommandee":"recommandée","recuperation":"récupération",
 "redige":"rédigé","redigez":"rédigez","rediger":"rédiger","reorganiser":"réorganiser",
 "requete":"requête","requetes":"requêtes","resilience":"résilience","resoudre":"résoudre",
 "reviser":"réviser","risquee":"risquée","salarie":"salarié","salaries":"salariés",
 "schema":"schéma","schemas":"schémas","semantique":"sémantique","severite":"sévérité",
 "societe":"société","specialiste":"spécialiste","supprimee":"supprimée","surete":"sûreté",
 "telecharger":"télécharger","telechargez":"téléchargez","temoin":"témoin","traite":"traité",
 "traitee":"traitée","transferer":"transférer","transferez":"transférez","utilite":"utilité",
 "variete":"variété","vederifiez":"vérifiez","visibilite":"visibilité","vulnerabilite":"vulnérabilité",
 "genere":"génère","déja":"déjà","securisez":"sécurisez","identite":"identité","ia":"IA","assistee":"assistée","empechent":"empêchent","empeche":"empêche",
}
_word_re = re.compile(r"[A-Za-z]+")

def fix_accents(t):
    # phrases d'abord (cas ambigus)
    t = re.sub(r"\bjusqu'a\b", "jusqu'à", t)
    t = re.sub(r"\bGrace a\b", "Grâce à", t); t = re.sub(r"\bgrace a\b", "grâce à", t)
    t = re.sub(r"\bc'est-a-dire\b", "c'est-à-dire", t)
    t = re.sub(r"\bbien sur\b", "bien sûr", t)
    t = re.sub(r"\baugmente par l'IA\b", "augmenté par l'IA", t)
    t = re.sub(r"\bExercice complete\b", "Exercice complété", t)
    t = re.sub(r"\bPlan genere\b", "Plan généré", t)
    t = re.sub(r"\b(avez|est|ont|sont) cree\b", r"\1 créé", t)
    t = re.sub(r"\bcree a partir\b", "créé à partir", t)
    t = re.sub(r"\bcree\b", "crée", t); t = re.sub(r"\bCree\b", "Crée", t)
    t = re.sub(r"\b(un|le|avec|du) resume\b", r"\1 résumé", t)
    t = re.sub(r"(: ) ?resume\b", r"\1résumé", t)
    t = re.sub(r"\b(qui|doit|elle|il) resume\b", r"\1 résume", t)
    t = re.sub(r" a (l')", r" à \1", t)
    t = re.sub(r"(?<!region) a la ", " à la ", t)
    t = re.sub(r" a (utiliser|conserver|faire|eviter|remplir|regarder|maitriser|construire|tester|"
               r"verifier|proteger|retenir|suivre|jour|nouveau|partir|coller|copier|garder|surveiller|"
               r"comparer|choisir|expliquer|observer|apprendre|mesurer|documenter|nettoyer|relier|"
               r"consolider|corriger|demander|comprendre|produire|poser|lire|ecrire|chaque|ce stade|"
               r"cette etape|votre|vos)\b", r" à \1", t)
    # mots ensuite
    def rep(m):
        w = m.group(0); lw = w.lower()
        r = ACCENTS.get(lw)
        if not r:
            return w
        if w.isupper():
            return w
        if w[0].isupper():
            return r[0].upper() + r[1:]
        return r
    return _word_re.sub(rep, t)

def clean(t):
    t = unesc(t).strip()
    t = re.sub(r"\.([A-ZÀ-Ü])", r". \1", t)          # "ia.Elle" -> "ia. Elle"
    t = re.sub(r"\s+", " ", t)
    # pas de renvoi au manuel PDF local sur le site public
    t = re.sub(r"Votre premier reflexe doit etre d'observer le document source.*?commencez par\s*:",
               "Commencez par :", t)
    return fix_accents(t)

def esc(t):
    return html.escape(clean(t), quote=False)

def parse(path):
    """Return ordered blocks: ('h1',txt) ('h2',txt) ('p',style,txt) ('table',[rows])."""
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    body = xml[xml.index("<w:body>"):]
    blocks = []
    for m in re.finditer(r"<w:tbl>.*?</w:tbl>|<w:p\b[^>]*>.*?</w:p>", body, re.S):
        el = m.group(0)
        if el.startswith("<w:tbl>"):
            rows = []
            for rm in re.finditer(r"<w:tr\b.*?</w:tr>", el, re.S):
                cells = []
                for cm in re.finditer(r"<w:tc>.*?</w:tc>", rm.group(0), re.S):
                    ptexts = []
                    for pm in re.finditer(r"<w:p\b[^>]*>.*?</w:p>", cm.group(0), re.S):
                        tx = "".join(re.findall(r"<w:t(?: [^>]*)?>(.*?)</w:t>", pm.group(0), re.S))
                        if tx.strip():
                            ptexts.append(clean(tx))
                    cells.append("\n".join(ptexts))
                rows.append(cells)
            blocks.append(("table", rows))
        else:
            sm = re.search(r'<w:pStyle w:val="([^"]+)"', el)
            style = sm.group(1) if sm else ""
            tx = "".join(re.findall(r"<w:t(?: [^>]*)?>(.*?)</w:t>", el, re.S))
            if not tx.strip():
                continue
            if style == "Heading1":
                blocks.append(("h1", clean(tx)))
            elif style == "Heading2":
                blocks.append(("h2", clean(tx)))
            else:
                blocks.append(("p", style, clean(tx)))
    return blocks

# ---------- model ----------
def build_model(blocks, drop_source_refs=False):
    doc = {"intro": [], "sessions": [], "extra": []}
    cur_session, cur_sec, zone = None, None, "pre"
    for b in blocks:
        if b[0] == "h1":
            t = b[1]
            sm = re.match(r"Session (\d+) ?[-–] ?(.*)", t)
            if sm:
                cur_session = {"num": int(sm.group(1)), "title": sm.group(2).strip(),
                               "meta": {}, "secs": []}
                doc["sessions"].append(cur_session)
                cur_sec = None; zone = "session"
            elif t.lower().startswith("index"):
                zone = "index"
            else:
                zone = "extra"
                cur_sec = {"head": t, "blocks": []}
                doc["extra"].append(cur_sec)
        elif b[0] == "h2":
            if zone == "session":
                cur_sec = {"head": b[1], "blocks": []}
                if drop_source_refs and deacc(b[1]).startswith("reference au document source"):
                    cur_sec["drop"] = True
                cur_session["secs"].append(cur_sec)
        else:
            if zone == "pre":
                doc["intro"].append(b)
            elif zone == "index":
                continue
            elif zone == "session":
                if cur_sec is None:  # meta paragraphs before first H2
                    if b[0] == "p":
                        t = b[2]
                        for lab, key in (("duree estimee:", "duree"),
                                         ("produit a construire:", "produit"),
                                         ("resultat d'apprentissage:", "resultat")):
                            if deacc(t).startswith(lab):
                                cur_session["meta"][key] = t[len(lab):].strip()
                                break
                else:
                    cur_sec["blocks"].append(b)
            elif zone == "extra" and cur_sec is not None:
                cur_sec["blocks"].append(b)
    doc["sessions"].sort(key=lambda s: s["num"])
    return doc

# ---------- rendering ----------
HEADMAP = {
    "Contexte de la session": "Contexte de la session",
    "Boussole Lojik360": "Boussole Lojik360",
    "Boussole IA Lojik360": "Boussole Lojik360",
    "Mots cles du titre": "Les mots clés du titre",
    "Concepts cles": "Les concepts clés",
    "Start Here / Commencer ici": "Commencez ici",
    "Do This Now / A faire maintenant": "À faire maintenant",
    "Worksheet / Fiche de travail": "Fiche de travail",
    "Choose Your Path / Choisissez votre voie": "Choisissez votre voie",
    "Prompts You Can Use": "Prompts à utiliser",
    "AI Prompt Lab / Prompts IA a utiliser": "Prompts IA à utiliser",
    "Examples of Results / Exemples de resultats": "Exemples de résultats",
    "Examples of AI Results / Exemples de resultats IA": "Exemples de résultats IA",
    "Excel Practice / Pratique Excel": "Pratique Excel",
    "Checkpoint / Point de controle": "Point de contrôle",
    "Small Project / Mini-projet": "Mini-projet",
    "Evidence to Save / Preuves a conserver": "Preuves à conserver",
}
HEADMAP_D = None  # rempli apres la definition de HEADMAP
AX_EMOJI = {"Deleguer": "🤖 Déléguer", "Superviser": "🔍 Superviser",
            "Renforcer l'humain": "🌱 Renforcer l'humain"}

HEADMAP_D = {deacc(k): v for k, v in HEADMAP.items()}

def render_table(rows, headkey):
    out = []
    if not rows:
        return out
    hk = deacc(headkey)
    body_rows = rows[1:] if len(rows) > 1 else rows
    if "boussole" in hk:
        lines = []
        for r in body_rows:
            if len(r) >= 2:
                ax = AX_EMOJI.get(r[0], r[0])
                lines.append("<strong>%s.</strong> %s" % (html.escape(ax, quote=False), html.escape(r[1], quote=False)))
        if lines:
            out.append("<div class='callout'>%s</div>" % "<br>".join(lines))
    elif "mots cles" in hk or "concepts cles" in hk:
        for r in body_rows:
            if len(r) >= 4:
                out.append("<div class='callout'><strong>%s</strong> — %s<br>%s<br><em>🏋 Essayez : %s</em></div>"
                           % tuple(html.escape(c, quote=False) for c in r[:4]))
            elif len(r) >= 2:
                out.append("<div class='callout'><strong>%s</strong> — %s</div>"
                           % tuple(html.escape(c, quote=False) for c in r[:2]))
    elif "worksheet" in hk:
        items = [r[0] for r in body_rows if r and r[0]]
        if items:
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % html.escape(i, quote=False) for i in items))
    elif "choose your path" in hk:
        for r in body_rows:
            if len(r) >= 2:
                out.append("<div class='callout'><strong>%s</strong><br>%s</div>"
                           % (html.escape(r[0], quote=False), html.escape(r[1], quote=False)))
    elif "prompt" in hk:  # Prompts You Can Use / AI Prompt Lab
        for r in body_rows:
            if len(r) >= 2:
                out.append("<div class='prompt-box'><strong>%s.</strong> %s</div>"
                           % (html.escape(r[0], quote=False), html.escape(r[1], quote=False).replace("\n", "<br>")))
            elif len(r) == 1 and r[0]:
                out.append("<div class='prompt-box'>%s</div>" % html.escape(r[0], quote=False))
    else:  # generic table
        thead = "<tr>%s</tr>" % "".join("<th>%s</th>" % html.escape(c, quote=False) for c in rows[0])
        trs = []
        for r in rows[1:]:
            tds = []
            for c in r:
                cc = html.escape(c, quote=False).replace("\n", "<br>")
                if cc.startswith("https://"):
                    cc = "<a href='%s' target='_blank' rel='noopener'>%s</a>" % (cc, cc)
                tds.append("<td>%s</td>" % cc)
            trs.append("<tr>%s</tr>" % "".join(tds))
        out.append("<div style='overflow-x:auto'><table class='tbl'>%s%s</table></div>" % (thead, "".join(trs)))
    return out

def render_blocks(sec):
    parts = []
    pend_list = None  # (tag, items)
    def flush():
        nonlocal pend_list
        if pend_list:
            tag, items = pend_list
            parts.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % i for i in items), tag))
            pend_list = None
    for b in sec["blocks"]:
        if b[0] == "table":
            flush(); parts.extend(render_table(b[1], sec["head"]))
        else:
            _, style, tx = b
            if "document source" in tx.lower() and "C:\\" in tx:
                continue  # never publish local file paths
            e = html.escape(tx, quote=False)
            if style in ("ListNumber", "ListParagraph", "ListBullet"):
                tag = "ul" if style == "ListBullet" else "ol"
                if pend_list and pend_list[0] == tag:
                    pend_list[1].append(e)
                else:
                    flush(); pend_list = (tag, [e])
            else:
                flush()
                if tx.startswith("Consigne:"):
                    parts.append("<p style='color:var(--ink-dim)'>%s</p>" % e)
                else:
                    parts.append("<p>%s</p>" % e)
    flush()
    return parts

def render_session(s):
    p = ["<section id='s%d'>" % s["num"],
         "<h2>Session %d — %s</h2>" % (s["num"], html.escape(s["title"], quote=False))]
    meta = s["meta"]
    if meta.get("duree") or meta.get("produit"):
        p.append("<p style='color:var(--ink-dim)'>⏱ %s · 🎯 Vous allez produire : <strong>%s</strong></p>"
                 % (html.escape(meta.get("duree", ""), quote=False), html.escape(meta.get("produit", ""), quote=False)))
    if meta.get("resultat"):
        p.append("<p><em>%s</em></p>" % html.escape(meta["resultat"], quote=False))
    for sec in s["secs"]:
        if sec.get("drop"):
            continue
        h = HEADMAP_D.get(deacc(sec["head"]), sec["head"].split("/")[-1].strip())
        p.append("<h3>%s</h3>" % html.escape(h, quote=False))
        p.extend(render_blocks(sec))
    p.append("</section>")
    return "\n".join(p)

PAGE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title} | Lojik360</title>
<meta name="description" content="{desc}" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="../assets/style.css?v=6" />
<style>html{{scroll-behavior:smooth}}.tuto-main h4{{color:var(--ink)}}.prompt-box{{background:var(--navy-2);border:1px solid var(--border);border-radius:10px;padding:.7rem .9rem;margin:.5rem 0;font-size:.9rem;color:var(--ink)}}</style>
</head>
<body>
<header>
  <nav class="nav">
    <a href="../index.html" class="logo"><img src="../assets/logo.svg" alt="Lojik360" class="logo-img" />Lojik<span>360</span><small>par Atmart</small></a>
    <button class="nav-toggle" aria-label="Menu">☰</button>
    <ul class="nav-links">
      <li><a href="../index.html">Accueil</a></li>
      <li><a href="../tutoriels.html" class="active">Tutoriels</a></li>
      <li><a href="../index.html#podcast">Podcast</a></li>
      <li><a href="../lojikkid.html">Lojikkid</a></li>
      <li><a href="https://atmart.ltd">Solutions (Atmart)</a></li>
    </ul>
  </nav>
</header>
<div class="tuto-shell">
  <aside class="tuto-sidebar">
    <div class="tuto-sidebar-head"><span class="ico">{ico}</span><h2>{short}</h2><span class="lvl">🤖 Déléguer</span><div class="lang-page-switch"><a href="{fn}" class="active">FR</a><a href="{fnht}">HT</a><span class="lang-soon" title="bientôt">EN</span><span class="lang-soon" title="bientôt">ES</span></div></div>
    <button class="tuto-toc-toggle">☰ Sessions</button>
    <ul class="tuto-toc">
      <li><a href="#intro">À propos de ces sessions</a></li>
      <li class="toc-group">Sessions</li>
{toc}
    </ul>
  </aside>
  <main class="tuto-main">
    <p class="breadcrumb"><a href="../tutoriels.html">Tutoriels</a> › 🤖 Déléguer</p>
    <h1>{title}</h1>
    <p class="lead">{lead}</p>
{intro}
{sessions}
    <div class="tuto-pager"><a href="../tutoriels.html" class="btn btn-outline">← Tous les tutoriels</a></div>
  </main>
</div>
<footer><div class="container"><div class="footer-bottom">© 2026 Atmart LLC — Lojik360 est une marque d'Atmart LLC.</div></div></footer>
<script src="../assets/script.js"></script>
<script src="../assets/chat.js?v=4" data-endpoint="https://atmart-chat.atmartllc.workers.dev"></script>
</body>
</html>
"""

def render_intro(doc, hint):
    parts = ["<section id='intro'>", "<h2>À propos de ces sessions</h2>"]
    for b in doc["intro"]:
        if b[0] != "p":
            continue
        tx = b[2]
        low = deacc(tx)
        if ("tutoriel apprenant" in low or "version " in low or "note source" in low
                or "document source" in low or "mode d'utilisation du document" in low
                or tx == "Excel a l'ere de l'IA"):
            continue
        e = html.escape(tx, quote=False)
        if low.startswith(("regle de confidentialite:", "confidentialite:")):
            body = e.split(":", 1)[1].strip()
            parts.append("<div class='callout warn'><strong>⚠️ Confidentialité.</strong> %s</div>" % body)
        elif low.startswith("positionnement:"):
            parts.append("<p>%s</p>" % e.split(":", 1)[1].strip())
        elif low.startswith(("mode d'emploi:", "angle ia:")):
            lab = "Mode d'emploi" if low.startswith("mode") else "L'angle IA"
            parts.append("<p><strong>%s.</strong> %s</p>" % (lab, e.split(":", 1)[1].strip()))
        else:
            parts.append("<p>%s</p>" % e)
    parts.append("<p style='color:var(--ink-dim)'>%s</p>" % hint)
    parts.append("</section>")
    return "\n".join(parts)

def render_extra(doc):
    out = []
    for sec in doc["extra"]:
        # ne pas publier les références au manuel PDF local
        sec["blocks"] = [b for b in sec["blocks"]
                         if not (b[0] == "p" and ("pdf" in b[2].lower() or "document source" in b[2].lower()))]
        out.append("<section id='sources'>")
        out.append("<h2>%s</h2>" % html.escape(sec["head"], quote=False))
        out.append("<p>Ce tutoriel est original : les cas, exercices et prompts ont été conçus pour Lojik360. "
                   "Les sessions suivent les grands thèmes classiques d'Excel (classeurs, mise en forme, formules, "
                   "graphiques, tableaux croisés dynamiques, Power Query, scénarios, finance). "
                   "Pour approfondir chaque fonctionnalité IA, utilisez les ressources officielles Microsoft ci-dessous.</p>")
        out.extend(render_blocks(sec))
        out.append("</section>")
    return "\n".join(out)

def build(path, fn, title, short, ico, lead, desc, drop_source_refs=False):
    blocks = parse(path)
    doc = build_model(blocks, drop_source_refs=drop_source_refs)
    toc = "\n".join("      <li><a href='#s%d'>%d. %s</a></li>" % (s["num"], s["num"], html.escape(s["title"], quote=False))
                    for s in doc["sessions"])
    if doc["extra"]:
        toc += "\n      <li><a href='#sources'>Sources et limites</a></li>"
    hint = "Choisissez une session dans le menu — une seule session s'affiche à la fois."
    sessions = "\n".join(render_session(s) for s in doc["sessions"])
    if doc["extra"]:
        sessions += "\n" + render_extra(doc)
    pg = PAGE.format(title=title, short=short, ico=ico, lead=lead, desc=desc,
                     fn=fn, fnht=fn.replace(".html", ".ht.html"), toc=toc, intro=render_intro(doc, hint), sessions=sessions)
    out = SITE + "\\tutoriels\\" + fn
    io.open(out, "w", encoding="utf-8", newline="\n").write(pg)
    # validation
    nsec = len(doc["sessions"])
    empty = [ (s["num"], sec["head"]) for s in doc["sessions"] for sec in s["secs"]
              if not sec.get("drop") and not sec["blocks"] ]
    print("%s: %d sessions, %d KB, empty sections: %s" % (fn, nsec, len(pg)//1024, empty or "none"))

build(r"C:\Users\USUARIO\OneDrive\Documents\Haiti Adolescent Girls Network (HAGN)\Lojik360_Prompting_Assistant_IA_Tutoriel_Apprenants_Contexte_Ameliore.docx",
      "prompting-ia.html",
      "Prompting & assistant IA — 10 sessions d'action",
      "Prompting & assistant IA", "✍️",
      "Apprenez à utiliser un assistant IA sans perdre le jugement humain : déléguer une production, superviser la qualité et renforcer votre intention. Chaque session produit un livrable réel.",
      "Prompting et assistants IA : 10 sessions d'action pour déléguer, superviser et renforcer l'humain. Rôle, tâche, contexte, format, itération, vérification, confidentialité, templates.")

build(r"C:\Users\USUARIO\OneDrive\Documents\Haiti Adolescent Girls Network (HAGN)\Lojik360_Excel_a_l_ere_de_l_IA_Tutoriel_Apprenants_Contextes_Detailles.docx",
      "excel-ia.html",
      "Excel à l'ère de l'IA — 12 sessions d'action",
      "Excel à l'ère de l'IA", "📊",
      "Excel n'est plus une simple grille de calcul : structurez vos données, déléguez à l'IA ce qui peut l'être, vérifiez chaque résultat et gardez la décision humaine. 12 sessions, un livrable par session.",
      "Excel à l'ère de l'IA : 12 sessions d'action — tables, formules, graphiques, TCD, Power Query, scénarios, finance — avec prompts IA et vérification humaine.",
      drop_source_refs=True)
