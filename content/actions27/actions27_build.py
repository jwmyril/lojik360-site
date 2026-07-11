# -*- coding: utf-8 -*-
"""Parse the two Lojik360 27-session docx files and build reader pages.
Usage:  python actions27_build.py            -> build EN pages (learner + facilitator)
        python actions27_build.py dump       -> also dump learner model to actions27_model_en.json
        python actions27_build.py fr         -> build FR learner pages from actions27_fr_*.json
"""
import zipfile, re, html, io, os, json, sys

L_DOCX = r"C:\Users\USUARIO\OneDrive\Documents\Haiti Adolescent Girls Network (HAGN)\Lojik360_27_Learner_Action_Tutorials_Improved.docx"
F_DOCX = r"C:\Users\USUARIO\OneDrive\Documents\Tutorials Atmart\Lojik360_27_Facilitator_Guide_Improved.docx"
OUT = r"C:\Users\USUARIO\Power_BI_Claude\Lojik360_site\tutoriels"
esc = lambda s: html.escape(s, quote=False)

def paras_of(p):
    xml = zipfile.ZipFile(p).read("word/document.xml").decode("utf-8", "ignore")
    out = []
    for m in re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.DOTALL):
        t = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", m, flags=re.DOTALL))
        t = html.unescape(t).strip()
        if t: out.append(t)
    return out

def section_slices(paras, headers, start, end):
    """Return dict header -> list of paras between this header and the next known header."""
    idx = {}
    for h in headers:
        for k in range(start, end):
            if paras[k] == h: idx[h] = k; break
    marks = sorted(idx.values()) + [end]
    out = {}
    for h, k in idx.items():
        nxt = min(m for m in marks if m > k)
        out[h] = paras[k+1:nxt]
    return out

def rows_of(body, ncols, colheads):
    """body starts with intro paras, then literal column headers, then rows of ncols."""
    intro = []
    i = 0
    while i < len(body) and body[i] != colheads[0]:
        intro.append(body[i]); i += 1
    i += len(colheads)
    rows = []
    while i + ncols - 1 < len(body):
        rows.append(body[i:i+ncols]); i += ncols
    return intro, rows

DOMAINS = ["Technology usage", "Management", "Strengthen the human"]

# ---------------- learner parse ----------------
LH = ["Start Here","Title Concepts to Master","Quick Self-Check","Do This Now","Worksheet",
      "Choose Your Path","Prompts You Can Use","Checkpoint","Small Project","Evidence to Save",
      "Common Mistakes to Avoid","Finish Line"]

def parse_learner():
    P = paras_of(L_DOCX)
    front = {}
    for p in P[:12]:
        if p.startswith("Purpose:"): front["purpose"] = p.split(":",1)[1].strip()
        if p.startswith("Format:"): front["format"] = p.split(":",1)[1].strip()
        if p.startswith("Safety note:"): front["safety"] = p.split(":",1)[1].strip()
    sess_idx = [k for k,x in enumerate(P) if re.match(r"^Session \d+:", x)]
    dom_intro = {}
    for d in DOMAINS:
        for k,x in enumerate(P):
            if x == d and k+1 < len(P) and P[k+1].startswith("Use these sessions"):
                dom_intro[d] = P[k+1]; break
    sessions = []
    for n,k in enumerate(sess_idx):
        end = sess_idx[n+1] if n+1 < len(sess_idx) else len(P)
        # trim trailing domain-header + intro line
        for d in DOMAINS:
            for j in range(k, end):
                if P[j] == d: end = j; break
        title = P[k].split(":",1)[1].strip()
        num = int(re.match(r"Session (\d+):", P[k]).group(1))
        meta = {}
        for p in P[k+1:k+5]:
            if p.startswith("Domain:"): meta["domain"] = p.split(":",1)[1].strip()
            if p.startswith("Estimated time:"): meta["time"] = p.split(":",1)[1].strip()
            if p.startswith("What you will build:"): meta["build"] = p.split(":",1)[1].strip()
        sec = section_slices(P, LH, k, end)
        c_intro, c_rows = rows_of(sec.get("Title Concepts to Master", []), 4,
                                  ["Concept","Definition","Explanation","Practice examples"])
        w_intro, w_rows = rows_of(sec.get("Worksheet", []), 2, ["Field","Your answer"])
        p_intro, p_rows = rows_of(sec.get("Choose Your Path", []), 2, ["Option","Consequence"])
        prompts = sec.get("Prompts You Can Use", [])
        sessions.append(dict(num=num, title=title, meta=meta,
            start=sec.get("Start Here", []),
            concepts_intro=c_intro, concepts=c_rows,
            selfcheck=sec.get("Quick Self-Check", []),
            actions=sec.get("Do This Now", []),
            ws_intro=w_intro, ws_fields=[r[0] for r in w_rows],
            path_intro=p_intro, paths=p_rows,
            prompts_intro=prompts[:1], prompts=prompts[1:],
            checkpoint=sec.get("Checkpoint", []),
            project=sec.get("Small Project", []),
            evidence=sec.get("Evidence to Save", []),
            mistakes=sec.get("Common Mistakes to Avoid", []),
            finish=sec.get("Finish Line", [])))
    return front, dom_intro, sessions

# ---------------- facilitator parse ----------------
FH = ["Domain Facilitation Note","Title Concepts to Teach","Before the Session","Opening Move",
      "Guided Action Support","Learner Worksheet Guidance","Choice Path Facilitation",
      "Prompt Safety and Use","Mini-Case Bridge","Debrief Questions","Artifact Review Criteria",
      "Common Mistakes to Watch For","Close the Session"]

def parse_facil():
    P = paras_of(F_DOCX)
    front = {}
    for p in P[:10]:
        if p.startswith("Purpose:"): front["purpose"] = p.split(":",1)[1].strip()
        if p.startswith("Facilitation principle:"): front["principle"] = p.split(":",1)[1].strip()
    hu = P.index("How to Use This Facilitator Guide")
    howto = []
    for p in P[hu+1:hu+10]:
        if p == "Session Index": break
        howto.append(p)
    front["howto"] = howto
    sess_idx = [k for k,x in enumerate(P) if re.match(r"^Session \d+:", x)]
    sessions = []
    for n,k in enumerate(sess_idx):
        end = sess_idx[n+1] if n+1 < len(sess_idx) else len(P)
        for d in DOMAINS:
            for j in range(k, end):
                if P[j] == d and j > k+3: end = min(end, j)
        title = P[k].split(":",1)[1].strip()
        num = int(re.match(r"Session (\d+):", P[k]).group(1))
        meta = {}
        for p in P[k+1:k+8]:
            for key, lab in [("domain","Domain:"),("time","Estimated time:"),("artifact","Learner artifact:"),
                             ("outcome","Learner outcome:"),("core","Core idea:"),("intent","Facilitator intent:")]:
                if p.startswith(lab): meta[key] = p.split(":",1)[1].strip()
        sec = section_slices(P, FH, k, end)
        note = dict(focus="", watch="")
        for p in sec.get("Domain Facilitation Note", []):
            if p.startswith("Focus:"): note["focus"] = p.split(":",1)[1].strip()
            if p.startswith("Watch for:"): note["watch"] = p.split(":",1)[1].strip()
        c_intro, c_rows = rows_of(sec.get("Title Concepts to Teach", []), 5,
                                  ["Concept","Definition","Explanation","Practice examples","Facilitator use"])
        g_intro, g_rows = rows_of(sec.get("Guided Action Support", []), 3,
                                  ["Learner action","Facilitator move","Evidence to look for"])
        cp_intro, cp_rows = rows_of(sec.get("Choice Path Facilitation", []), 2,
                                    ["Learner option","Facilitator interpretation"])
        ar_intro, ar_rows = rows_of(sec.get("Artifact Review Criteria", []), 3,
                                    ["Review criterion","What good looks like","Red flag"])
        mc = sec.get("Mini-Case Bridge", [])
        case, case_use = "", ""
        for p in mc:
            if p.startswith("Facilitator use:"): case_use = p.split(":",1)[1].strip()
            else: case = (case + " " + p).strip()
        pr = sec.get("Prompt Safety and Use", [])
        wg = sec.get("Learner Worksheet Guidance", [])
        sessions.append(dict(num=num, title=title, meta=meta, note=note,
            concepts_intro=c_intro, concepts=c_rows,
            before=sec.get("Before the Session", []),
            opening=sec.get("Opening Move", []),
            guided_intro=g_intro, guided=g_rows,
            ws_intro=wg[:1], ws_fields=wg[1:],
            cp_intro=cp_intro, cps=cp_rows,
            prompts_intro=pr[:1], prompts=pr[1:],
            case=case, case_use=case_use,
            debrief=sec.get("Debrief Questions", []),
            review=ar_rows,
            mistakes=sec.get("Common Mistakes to Watch For", []),
            close=sec.get("Close the Session", [])))
    return front, sessions

# ---------------- rendering ----------------
def head(title, desc, lang="en"):
    tpl = ('<!DOCTYPE html>\n<html lang="{lang}">\n<head>\n<meta charset="UTF-8" />\n'
     '<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
     '<title>{title}</title>\n<meta name="description" content="{desc}" />\n'
     '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
     '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet" />\n'
     '<link rel="stylesheet" href="../assets/style.css?v=3" />\n'
     '<style>html{{scroll-behavior:smooth}}.tuto-main h4{{color:var(--ink)}}.prompt-box{{background:var(--navy-2);border:1px solid var(--border);border-radius:10px;padding:.7rem .9rem;margin:.5rem 0;font-size:.9rem;color:var(--ink)}}</style>\n'
     '</head>\n<body>')
    return tpl.format(lang=lang, title=esc(title), desc=esc(desc))

L10N = {
 "en": dict(
   htmllang="en", tag="by Atmart",
   nav=["Home","Tutorials","Podcast","Lojikkid","Solutions (Atmart)"],
   foot="© 2026 Atmart LLC — Lojik360 is a brand of Atmart LLC.",
   crumb="Tutorials", about="About these sessions", sessions="Sessions",
   time_art='⏱ %s · 🎯 You will build: <strong>%s</strong>',
   s_start="Start here", s_concepts="Title concepts to master", s_try="🏋 Try:",
   s_check="Quick self-check", s_do="Do this now", s_ws="Worksheet",
   s_path="Choose your path", s_prompts="Prompts you can use", s_cp="Checkpoint",
   s_proj="Small project", s_ev="Evidence to save", s_mis="Common mistakes to avoid",
   s_finish="🏁 Finish line.", safety="⚠️ Safety note.",
   pick='Pick a session in the menu — one session is shown at a time. Facilitating a group? Use the <a href="%s">facilitator guide</a>.',
   pager="← All tutorials"),
 "fr": dict(
   htmllang="fr", tag="par Atmart",
   nav=["Accueil","Tutoriels","Podcast","Lojikkid","Solutions (Atmart)"],
   foot="© 2026 Atmart LLC — Lojik360 est une marque d'Atmart LLC.",
   crumb="Tutoriels", about="À propos de ces sessions", sessions="Sessions",
   time_art='⏱ %s · 🎯 Vous allez produire : <strong>%s</strong>',
   s_start="Commencez ici", s_concepts="Les concepts du titre à maîtriser", s_try="🏋 Essayez :",
   s_check="Auto-contrôle rapide", s_do="À faire maintenant", s_ws="Feuille de travail",
   s_path="Choisissez votre voie", s_prompts="Prompts à utiliser", s_cp="Point de contrôle",
   s_proj="Petit projet", s_ev="Preuves à conserver", s_mis="Erreurs courantes à éviter",
   s_finish="🏁 Ligne d'arrivée.", safety="⚠️ Note de sécurité.",
   pick='Choisissez une session dans le menu — une seule session s\'affiche à la fois. Vous animez un groupe ? Utilisez le <a href="%s">guide du facilitateur</a>.',
   pager="← Tous les tutoriels"),
}

def NAV(L):
    items = [("../index.html", L["nav"][0], False), ("../tutoriels.html", L["nav"][1], True),
             ("../index.html#podcast", L["nav"][2], False), ("../lojikkid.html", L["nav"][3], False),
             ("https://atmart.ltd", L["nav"][4], False)]
    lis = "\n".join('      <li><a href="%s"%s>%s</a></li>' % (h, ' class="active"' if a else '', t) for h,t,a in items)
    return ('<header>\n  <nav class="nav">\n'
 '    <a href="../index.html" class="logo"><img src="../assets/logo.svg" alt="Lojik360" class="logo-img" />Lojik<span>360</span><small>%s</small></a>\n'
 '    <button class="nav-toggle" aria-label="Menu">☰</button>\n'
 '    <ul class="nav-links">\n%s\n    </ul>\n  </nav>\n</header>') % (L["tag"], lis)

def FOOT(L):
    return '<footer><div class="container"><div class="footer-bottom">%s</div></div></footer>' % L["foot"]
SCRIPTS = ('<script src="../assets/script.js"></script>\n'
 '<script src="../assets/chat.js?v=1" data-endpoint="https://atmart-chat.atmartllc.workers.dev"></script>')

def ul(items): return "  <ul>\n" + "\n".join("    <li>%s</li>" % esc(x) for x in items) + "\n  </ul>"
def ol(items): return "  <ol>\n" + "\n".join("    <li>%s</li>" % esc(x) for x in items) + "\n  </ol>"

BEST = ("best choice", "meilleur choix")
def render_learner_session(s, L):
    o = ['<section id="s%d">' % s["num"]]
    o.append('  <h2>Session %d — %s</h2>' % (s["num"], esc(s["title"])))
    o.append('  <p style="color:var(--ink-dim)">%s</p>'
             % (L["time_art"] % (esc(s["meta"].get("time","")), esc(s["meta"].get("build","")))))
    o.append('  <h3>%s</h3>' % L["s_start"])
    for p in s["start"]: o.append('  <p>%s</p>' % esc(p))
    o.append('  <h3>%s</h3>' % L["s_concepts"])
    for p in s["concepts_intro"]: o.append('  <p>%s</p>' % esc(p))
    for c in s["concepts"]:
        o.append('  <div class="callout"><strong>%s</strong> — %s<br>%s<br><em>%s %s</em></div>'
                 % (esc(c[0]), esc(c[1]), esc(c[2]), L["s_try"], esc(c[3])))
    o.append('  <h3>%s</h3>' % L["s_check"]); o.append(ul(s["selfcheck"]))
    o.append('  <h3>%s</h3>' % L["s_do"]); o.append(ol(s["actions"]))
    o.append('  <h3>%s</h3>' % L["s_ws"])
    for p in s["ws_intro"]: o.append('  <p>%s</p>' % esc(p))
    o.append(ul(s["ws_fields"]))
    o.append('  <h3>%s</h3>' % L["s_path"])
    for p in s["path_intro"]: o.append('  <p>%s</p>' % esc(p))
    for opt, cons in s["paths"]:
        mark = "✅" if any(cons.lower().startswith(b) for b in BEST) else "⚠️"
        o.append('  <div class="callout">%s <strong>%s</strong><br>%s</div>' % (mark, esc(opt), esc(cons)))
    o.append('  <h3>%s</h3>' % L["s_prompts"])
    for p in s["prompts_intro"]: o.append('  <p>%s</p>' % esc(p))
    for p in s["prompts"]: o.append('  <div class="prompt-box">%s</div>' % esc(p))
    o.append('  <h3>%s</h3>' % L["s_cp"]); o.append(ul(s["checkpoint"]))
    o.append('  <h3>%s</h3>' % L["s_proj"])
    for p in s["project"]: o.append('  <p>%s</p>' % esc(p))
    o.append('  <h3>%s</h3>' % L["s_ev"]); o.append(ul(s["evidence"]))
    o.append('  <h3>%s</h3>' % L["s_mis"]); o.append(ul(s["mistakes"]))
    for p in s["finish"]: o.append('  <div class="callout"><strong>%s</strong> %s</div>' % (L["s_finish"], esc(p)))
    o.append('</section>')
    return "\n".join(o)

AXES = {
 "Technology usage": dict(slug="actions-deleguer", ico="🤖", fslug="facilitateur-deleguer"),
 "Management": dict(slug="actions-superviser", ico="🔍", fslug="facilitateur-superviser"),
 "Strengthen the human": dict(slug="actions-renforcer", ico="🌱", fslug="facilitateur-renforcer"),
}
AXTXT = {
 "en": {
  "Technology usage": dict(dom="Technology usage", axis="🤖 Delegate", h1="Technology usage — 9 action sessions",
    lead="Delegate carefully: map the work, prompt with discipline, verify outputs, protect data and automate safely. Each session produces a real artifact in about an hour."),
  "Management": dict(dom="Management", axis="🔍 Supervise", h1="Management — 9 action sessions",
    lead="Supervise rigorously: publish a usage doctrine, run limited pilots, design human-in-the-loop control, govern risk and lead change without disengaging the team."),
  "Strengthen the human": dict(dom="Strengthen the human", axis="🌱 Strengthen the human", h1="Strengthen the human — 9 action sessions",
    lead="Grow what AI does not replace: judgment, communication, trust, creativity, attention, health and career resilience. Each session produces a real artifact."),
 },
 "fr": {
  "Technology usage": dict(dom="Usage de la technologie", axis="🤖 Déléguer", h1="Usage de la technologie — 9 sessions d'action",
    lead="Déléguez avec prudence : cartographiez le travail, promptez avec discipline, vérifiez les résultats, protégez les données et automatisez sans risque. Chaque session produit un livrable réel en une heure environ."),
  "Management": dict(dom="Management", axis="🔍 Superviser", h1="Management — 9 sessions d'action",
    lead="Supervisez avec rigueur : publiez une doctrine d'usage, menez des pilotes limités, concevez le contrôle humain dans la boucle, gouvernez les risques et conduisez le changement sans désengager l'équipe."),
  "Strengthen the human": dict(dom="Renforcer l'humain", axis="🌱 Renforcer l'humain", h1="Renforcer l'humain — 9 sessions d'action",
    lead="Développez ce que l'IA ne remplace pas : jugement, communication, confiance, créativité, attention, santé et résilience de carrière. Chaque session produit un livrable réel."),
 },
}

def learner_fn(slug, lang): return slug + (".html" if lang == "fr" else ".en.html")

def lang_switch(slug, cur):
    out = []
    for lbl, lng in [("FR","fr"),("HT",None),("EN","en"),("ES",None)]:
        if lng == cur: out.append('<a href="%s" class="active">%s</a>' % (learner_fn(slug,lng), lbl))
        elif lng:      out.append('<a href="%s">%s</a>' % (learner_fn(slug,lng), lbl))
        else:          out.append('<span class="lang-soon" title="bientôt">%s</span>' % lbl)
    return '<div class="lang-page-switch">%s</div>' % "".join(out)

def facil_switch():
    out = []
    for lbl, live in [("FR",False),("HT",False),("EN",True),("ES",False)]:
        if live: out.append('<a href="#" class="active">%s</a>' % lbl)
        else:    out.append('<span class="lang-soon" title="bientôt">%s</span>' % lbl)
    return '<div class="lang-page-switch">%s</div>' % "".join(out)

def render_learner_page(domain, front, intro, sessions, lang):
    a = AXES[domain]; t = AXTXT[lang][domain]; L = L10N[lang]
    ss = [s for s in sessions if s["meta"].get("domain") == domain]
    facil = a["fslug"] + ".en.html"
    o = [head("%s | Lojik360" % t["h1"], t["lead"][:155], L["htmllang"]), NAV(L)]
    o.append('<div class="tuto-shell">\n  <aside class="tuto-sidebar">')
    o.append('    <div class="tuto-sidebar-head"><span class="ico">%s</span><h2>%s</h2><span class="lvl">%s</span>%s</div>'
             % (a["ico"], esc(t["dom"]), esc(t["axis"]), lang_switch(a["slug"], lang)))
    o.append('    <button class="tuto-toc-toggle">☰ %s</button>\n    <ul class="tuto-toc">' % L["sessions"])
    o.append('      <li><a href="#intro">%s</a></li>' % L["about"])
    o.append('      <li class="toc-group">%s</li>' % L["sessions"])
    for s in ss:
        o.append('      <li><a href="#s%d">%d. %s</a></li>' % (s["num"], s["num"], esc(s["title"])))
    o.append('    </ul>\n  </aside>\n  <main class="tuto-main">')
    o.append('    <p class="breadcrumb"><a href="../tutoriels.html">%s</a> › %s</p>' % (L["crumb"], esc(t["axis"])))
    o.append('    <h1>%s</h1>\n    <p class="lead">%s</p>' % (esc(t["h1"]), esc(t["lead"])))
    o.append('<section id="intro">\n  <h2>%s</h2>' % L["about"])
    o.append('  <p>%s</p>' % esc(intro))
    o.append('  <p>%s</p>' % esc(front.get("format","")))
    o.append('  <div class="callout warn"><strong>%s</strong> %s</div>' % (L["safety"], esc(front.get("safety",""))))
    o.append('  <p style="color:var(--ink-dim)">%s</p>' % (L["pick"] % facil))
    o.append('</section>')
    for s in ss: o.append(render_learner_session(s, L))
    o.append('    <div class="tuto-pager"><a href="../tutoriels.html" class="btn btn-outline">%s</a></div>' % L["pager"])
    o.append('  </main>\n</div>')
    o.append(FOOT(L)); o.append(SCRIPTS); o.append('</body>\n</html>')
    return "\n".join(o)

def render_facil_session(s):
    o = ['<section id="s%d">' % s["num"]]
    o.append('  <h2>Session %d — %s</h2>' % (s["num"], esc(s["title"])))
    o.append('  <p style="color:var(--ink-dim)">%s · ⏱ %s · 🎯 Artifact: <strong>%s</strong></p>'
             % (esc(s["meta"].get("domain","")), esc(s["meta"].get("time","")), esc(s["meta"].get("artifact",""))))
    for lab, key in [("Learner outcome","outcome"),("Core idea","core"),("Facilitator intent","intent")]:
        if s["meta"].get(key): o.append('  <p><strong>%s.</strong> %s</p>' % (lab, esc(s["meta"][key])))
    o.append('  <div class="callout"><strong>🧭 Domain note.</strong> %s<br><strong>Watch for:</strong> %s</div>'
             % (esc(s["note"]["focus"]), esc(s["note"]["watch"])))
    o.append('  <h3>Title concepts to teach</h3>')
    for p in s["concepts_intro"]: o.append('  <p>%s</p>' % esc(p))
    for c in s["concepts"]:
        o.append('  <div class="callout"><strong>%s</strong> — %s<br>%s<br><em>🏋 Try: %s</em><br>👩‍🏫 %s</div>'
                 % (esc(c[0]), esc(c[1]), esc(c[2]), esc(c[3]), esc(c[4])))
    o.append('  <h3>Before the session</h3>'); o.append(ul(s["before"]))
    o.append('  <h3>Opening move</h3>'); o.append(ul(s["opening"]))
    o.append('  <h3>Guided action support</h3>')
    for p in s["guided_intro"]: o.append('  <p>%s</p>' % esc(p))
    for act, move, ev in s["guided"]:
        o.append('  <div class="callout"><strong>%s</strong><br>👉 %s<br>🔎 <em>Evidence: %s</em></div>'
                 % (esc(act), esc(move), esc(ev)))
    o.append('  <h3>Learner worksheet guidance</h3>')
    for p in s["ws_intro"]: o.append('  <p>%s</p>' % esc(p))
    o.append(ul(s["ws_fields"]))
    o.append('  <h3>Choice path facilitation</h3>')
    for p in s["cp_intro"]: o.append('  <p>%s</p>' % esc(p))
    for opt, interp in s["cps"]:
        mark = "✅" if interp.lower().startswith("best choice") else "⚠️"
        o.append('  <div class="callout">%s <strong>%s</strong><br>%s</div>' % (mark, esc(opt), esc(interp)))
    o.append('  <h3>Prompt safety and use</h3>')
    for p in s["prompts_intro"]: o.append('  <p>%s</p>' % esc(p))
    for p in s["prompts"]: o.append('  <div class="prompt-box">%s</div>' % esc(p))
    o.append('  <h3>Mini-case bridge</h3>')
    o.append('  <div class="callout"><em>%s</em><br>👩‍🏫 %s</div>' % (esc(s["case"]), esc(s["case_use"])))
    o.append('  <h3>Debrief questions</h3>'); o.append(ul(s["debrief"]))
    o.append('  <h3>Artifact review criteria</h3>')
    o.append('  <table class="tbl"><tr><th>Criterion</th><th>What good looks like</th><th>Red flag</th></tr>')
    for crit, good, red in s["review"]:
        o.append('    <tr><td><strong>%s</strong></td><td>%s</td><td>%s</td></tr>' % (esc(crit), esc(good), esc(red)))
    o.append('  </table>')
    o.append('  <h3>Common mistakes to watch for</h3>'); o.append(ul(s["mistakes"]))
    o.append('  <h3>Close the session</h3>'); o.append(ul(s["close"]))
    o.append('</section>')
    return "\n".join(o)

FAXES = {
 "Technology usage": dict(slug="facilitateur-deleguer", ico="🤖", label="🤖 Delegate",
    h1="Facilitator Guide — Technology usage (sessions 1–9)"),
 "Management": dict(slug="facilitateur-superviser", ico="🔍", label="🔍 Supervise",
    h1="Facilitator Guide — Management (sessions 10–18)"),
 "Strengthen the human": dict(slug="facilitateur-renforcer", ico="🌱", label="🌱 Strengthen the human",
    h1="Facilitator Guide — Strengthen the human (sessions 19–27)"),
}

def render_facil_page(domain, front, sessions):
    a = FAXES[domain]
    ss = [s for s in sessions if s["meta"].get("domain") == domain]
    others = " · ".join('<a href="%s.en.html">%s</a>' % (FAXES[d]["slug"], esc(d)) for d in DOMAINS if d != domain)
    o = [head("%s | Lojik360" % a["h1"],
              "Facilitator companion to the Lojik360 action sessions (%s): opening moves, guided action support, debrief questions and artifact review criteria." % domain), NAV(L10N["en"])]
    o.append('<style>.tbl{width:100%;border-collapse:collapse;margin:.6rem 0;font-size:.88rem}.tbl th,.tbl td{border:1px solid var(--border);padding:.45rem .6rem;text-align:left;vertical-align:top}.tbl th{color:var(--teal)}</style>')
    o.append('<div class="tuto-shell">\n  <aside class="tuto-sidebar">')
    o.append('    <div class="tuto-sidebar-head"><span class="ico">👩‍🏫</span><h2>Facilitator Guide</h2><span class="lvl">%s</span>%s</div>' % (esc(a["label"]), facil_switch()))
    o.append('    <button class="tuto-toc-toggle">☰ Sessions</button>\n    <ul class="tuto-toc">')
    o.append('      <li><a href="#intro">How to use this guide</a></li>')
    o.append('      <li class="toc-group">Sessions</li>')
    for s in ss:
        o.append('      <li><a href="#s%d">%d. %s</a></li>' % (s["num"], s["num"], esc(s["title"])))
    o.append('    </ul>\n  </aside>\n  <main class="tuto-main">')
    o.append('    <p class="breadcrumb"><a href="../tutoriels.html">Tutorials</a> › Facilitator guide › %s</p>' % esc(domain))
    o.append('    <h1>%s</h1>' % esc(a["h1"]))
    o.append('    <p class="lead">Run these Lojik360 action sessions with a group — aligned to the three moves: delegate carefully, supervise rigorously, strengthen what stays human.</p>')
    o.append('<section id="intro">\n  <h2>How to use this guide</h2>')
    o.append('  <p>%s</p>' % esc(front.get("purpose","")))
    o.append('  <div class="callout"><strong>Facilitation principle.</strong> %s</div>' % esc(front.get("principle","")))
    o.append(ul(front.get("howto", [])))
    o.append('  <p style="color:var(--ink-dim)">Learner version of these sessions: <a href="%s.en.html">%s</a>. Other facilitator volumes: %s. Pick a session in the menu — one is shown at a time.</p>'
             % (AXES[domain]["slug"], esc(domain), others))
    o.append('</section>')
    for s in ss: o.append(render_facil_session(s))
    o.append('    <div class="tuto-pager"><a href="../tutoriels.html" class="btn btn-outline">← All tutorials</a></div>')
    o.append('  </main>\n</div>')
    o.append(FOOT(L10N["en"])); o.append(SCRIPTS); o.append('</body>\n</html>')
    return "\n".join(o)

# ---------------- run ----------------
SC = os.path.dirname(os.path.abspath(__file__))
mode = sys.argv[1] if len(sys.argv) > 1 else "en"

if mode in ("en", "dump"):
    front_l, dom_intro, sess_l = parse_learner()
    print("learner sessions:", len(sess_l))
    if mode == "dump":
        json.dump(dict(front=front_l, dom_intro=dom_intro, sessions=sess_l),
                  io.open(os.path.join(SC, "actions27_model_en.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("dumped actions27_model_en.json")
    for d in DOMAINS:
        fn = learner_fn(AXES[d]["slug"], "en")
        htmlout = render_learner_page(d, front_l, dom_intro.get(d,""), sess_l, "en")
        io.open(os.path.join(OUT, fn), "w", encoding="utf-8").write(htmlout)
        print("built", fn, len(htmlout), "chars")
    front_f, sess_f = parse_facil()
    for d in DOMAINS:
        fn = FAXES[d]["slug"] + ".en.html"
        fp = render_facil_page(d, front_f, sess_f)
        io.open(os.path.join(OUT, fn), "w", encoding="utf-8").write(fp)
        print("built", fn, len(fp), "chars")

elif mode == "fr":
    KEY = {"Technology usage": "tech", "Management": "mgmt", "Strengthen the human": "human"}
    for d in DOMAINS:
        p = os.path.join(SC, "actions27_fr_%s.json" % KEY[d])
        m = json.load(io.open(p, encoding="utf-8"))
        for s in m["sessions"]:
            s["meta"]["domain"] = d  # normalize for the filter
        fn = learner_fn(AXES[d]["slug"], "fr")
        htmlout = render_learner_page(d, m["front"], m["dom_intro"], m["sessions"], "fr")
        io.open(os.path.join(OUT, fn), "w", encoding="utf-8").write(htmlout)
        print("built", fn, len(htmlout), "chars |", len(m["sessions"]), "sessions")
print("done")
