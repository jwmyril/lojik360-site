# -*- coding: utf-8 -*-
"""Build the Kreyol (HT) reader pages of Lojik360 from the 4 user-provided docx:
 - prompting-ia.ht.html, excel-ia.ht.html
 - actions-{deleguer,superviser,renforcer}.ht.html (27 sessions split by axis)
 - recherche-qualitative.ht.html (new tutorial, axis Ranfose imen an)
"""
import zipfile, re, html, io, unicodedata

SITE = r"C:\Users\USUARIO\Power_BI_Claude\Lojik360_site"
BASE = r"C:\Users\USUARIO\OneDrive\Documents\Haiti Adolescent Girls Network (HAGN)"

def deacc(t):
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn").lower()

def unesc(s):
    return (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"').replace("&#39;", "'"))

def clean(t):
    t = unesc(t).strip()
    t = re.sub(r"\.([A-ZÀ-ÜÈ])", r". \1", t)
    t = re.sub(r"\s+", " ", t)
    # pa pibliye referans manyel PDF lokal la
    t = re.sub(r"Premye ensten ou ta dwe gade dokiman sous la.*?k(?:ò|o)manse (?:ak|avèk)\s*:",
               "Kòmanse ak:", t)
    return t

def parse(path):
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

META_LABELS = [  # (deacc prefix, key)
    ("estimasyon tan:", "duree"), ("estimasyon dire:", "duree"),
    ("ki sa ou pral bati:", "produit"), ("pwodwi yo dwe bati:", "produit"),
    ("pwodui pou konstwi:", "produit"), ("pwodwi pou konstwi:", "produit"),
    ("pwodui yo dwe bati:", "produit"), ("sa w pral bati:", "produit"),
    ("rezilta aprantisaj la:", "resultat"), ("rezilta aprantisaj:", "resultat"),
    ("enpak espere:", "impact"), ("domen:", "domaine"), ("jou:", "jour"),
    ("tem klasik excel:", "_skip"),
]

def build_model(blocks):
    doc = {"intro": [], "sessions": [], "extras": []}
    cur_session, cur_sec, zone = None, None, "pre"
    seen_index = False
    for b in blocks:
        if b[0] == "h1":
            t = b[1]
            sm = re.match(r"Sesyon (\d+)\s*[-–:]\s*(.*)", t)
            if sm:
                cur_session = {"num": int(sm.group(1)), "title": sm.group(2).strip(),
                               "meta": {}, "secs": []}
                doc["sessions"].append(cur_session)
                cur_sec = None; zone = "session"
            elif deacc(t).startswith("endeks"):
                zone = "index"; seen_index = True
            else:
                zone = "extra"
                cur_sec = {"head": t, "blocks": [], "pre_index": not seen_index}
                doc["extras"].append(cur_sec)
        elif b[0] == "h2":
            if zone == "session":
                cur_sec = {"head": b[1], "blocks": []}
                if deacc(b[1]).startswith("referans ak sous dokiman"):
                    cur_sec["drop"] = True
                cur_session["secs"].append(cur_sec)
        else:
            if zone == "pre":
                doc["intro"].append(b)
            elif zone == "index":
                continue
            elif zone == "session":
                if cur_sec is None:
                    if b[0] == "p":
                        dt = deacc(b[2])
                        for lab, key in META_LABELS:
                            if dt.startswith(lab):
                                if key != "_skip":
                                    cur_session["meta"][key] = b[2].split(":", 1)[1].strip()
                                break
                        else:
                            cur_session["meta"].setdefault("autres", []).append(b[2])
                else:
                    cur_sec["blocks"].append(b)
            elif zone == "extra" and cur_sec is not None:
                cur_sec["blocks"].append(b)
    doc["sessions"].sort(key=lambda s: s["num"])
    return doc

# ---------- rendering (HT) ----------
HEADMAP = {
 "komanse isit la": "Kòmanse isit la",
 "tit konsep pou met": "Mo kle nan tit la",
 "konsep tit kle yo": "Mo kle nan tit la",
 "mo kle tit": "Mo kle nan tit la",
 "konsep cles": "Mo kle yo",
 "tcheke pwop tet ou rapid": "Tcheke tèt ou rapid",
 "fe sa kounye a": "Fè sa kounye a",
 "fe kounye a": "Fè kounye a",
 "fey travay": "Fich travay",
 "chwazi chemen ou": "Chwazi chemen ou",
 "enstriksyon ou ka itilize": "Pronpt ou ka itilize",
 "envit ou ka itilize": "Pronpt ou ka itilize",
 "ia prompt lab": "Pronpt IA pou itilize",
 "pwen kontwol": "Kote pou mete kontwòl",
 "checkpoint": "Kote pou mete kontwòl",
 "ti pwoje": "Ti pwojè",
 "mini-pwoje": "Ti pwojè",
 "prev pou sove": "Prèv pou konsève",
 "prev pou kenbe": "Prèv pou konsève",
 "ere komen pou evite": "Erè komen pou evite",
 "liy fini": "🏁 Liy fini",
 "konteks sesyon an": "Kontèks sesyon an",
 "boussole ia lojik360": "Bousòl IA Lojik360",
 "boussole lojik360": "Bousòl Lojik360",
 "lojik360 konpa": "Bousòl Lojik360",
 "egzanp rezilta rapid": "Egzanp rezilta",
 "egzanp rezilta ia": "Egzanp rezilta IA",
 "egzanp rezilta": "Egzanp rezilta",
 "excel pratike": "Pratike Excel",
 "egzanp pou itilize": "Egzanp pou itilize",
}
def head_label(raw):
    first = raw.split("/")[0].strip()
    return HEADMAP.get(deacc(first), first)

AX_HT = {"ranfose moun": "🌱 Ranfòse moun", "ranfose imen an": "🌱 Ranfòse imen an",
         "delege": "🤖 Delege", "delege ak prekosyon": "🤖 Delege (ak prekosyon)",
         "deleguer": "🤖 Delege", "sipevize": "🔍 Sipèvize", "superviser": "🔍 Sipèvize"}

def E(t):
    return html.escape(t, quote=False)

def render_table(rows, headkey):
    out = []
    if not rows:
        return out
    hk = deacc(headkey)
    body_rows = rows[1:] if len(rows) > 1 else rows
    if "boussole" in hk or "konpa" in hk:
        lines = []
        for r in body_rows:
            if len(r) >= 2:
                ax = AX_HT.get(deacc(r[0]), r[0])
                lines.append("<strong>%s.</strong> %s" % (E(ax), E(r[-1])))
        if lines:
            out.append("<div class='callout'>%s</div>" % "<br>".join(lines))
    elif "konsep" in hk or "mo kle" in hk or "tit konsep" in hk:
        for r in body_rows:
            if len(r) >= 4:
                out.append("<div class='callout'><strong>%s</strong> — %s<br>%s<br><em>🏋 Eseye : %s</em></div>"
                           % tuple(E(c) for c in r[:4]))
            elif len(r) >= 2:
                out.append("<div class='callout'><strong>%s</strong> — %s</div>" % (E(r[0]), E(r[1])))
    elif "fey travay" in hk:
        items = [r[0] for r in body_rows if r and r[0]]
        if items:
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % E(i) for i in items))
    elif "chwazi chemen" in hk:
        for r in body_rows:
            if len(r) >= 2:
                mark = "✅" if deacc(r[1]).startswith("pi bon chwa") else "⚠️"
                out.append("<div class='callout'>%s <strong>%s</strong><br>%s</div>" % (mark, E(r[0]), E(r[1])))
    elif "envit" in hk or "enstriksyon" in hk or "prompt" in hk:
        for r in body_rows:
            if len(r) >= 2:
                out.append("<div class='prompt-box'><strong>%s.</strong> %s</div>"
                           % (E(r[0]), E(r[1]).replace("\n", "<br>")))
            elif len(r) == 1 and r[0]:
                out.append("<div class='prompt-box'>%s</div>" % E(r[0]))
    else:
        thead = "<tr>%s</tr>" % "".join("<th>%s</th>" % E(c) for c in rows[0])
        trs = []
        for r in rows[1:]:
            tds = []
            for c in r:
                cc = E(c).replace("\n", "<br>")
                if cc.startswith("https://"):
                    cc = "<a href='%s' target='_blank' rel='noopener'>%s</a>" % (cc, cc)
                tds.append("<td>%s</td>" % cc)
            trs.append("<tr>%s</tr>" % "".join(tds))
        out.append("<div style='overflow-x:auto'><table class='tbl'>%s%s</table></div>" % (thead, "".join(trs)))
    return out

def render_blocks(sec):
    parts = []
    hk = deacc(sec["head"])
    prompts_sec = ("envit" in hk or "enstriksyon" in hk)
    first_p = True
    pend = None
    def flush():
        nonlocal pend
        if pend:
            tag, items = pend
            parts.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % i for i in items), tag))
            pend = None
    for b in sec["blocks"]:
        if b[0] == "table":
            flush(); parts.extend(render_table(b[1], sec["head"]))
        else:
            _, style, tx = b
            dt = deacc(tx)
            if ("c:\\" in dt) or ("oceanofpdf" in dt) or dt.startswith("sous dokiman"):
                continue
            e = E(tx)
            if style in ("ListNumber", "ListParagraph"):
                if pend and pend[0] == "ol":
                    pend[1].append(e)
                else:
                    flush(); pend = ("ol", [e])
            elif style == "ListBullet":
                if pend and pend[0] == "ul":
                    pend[1].append(e)
                else:
                    flush(); pend = ("ul", [e])
            else:
                flush()
                if prompts_sec and not first_p:
                    parts.append("<div class='prompt-box'>%s</div>" % e)
                elif prompts_sec and first_p:
                    parts.append("<p style='color:var(--ink-dim)'>%s</p>" % e)
                elif dt.startswith(("reg sou itilizasyon:", "kouman pou itilize yo:", "konsiy:")):
                    parts.append("<p style='color:var(--ink-dim)'>%s</p>" % e)
                else:
                    parts.append("<p>%s</p>" % e)
            if b[0] == "p":
                first_p = False
    flush()
    return parts

def render_session(s, local_num=None):
    n = local_num if local_num is not None else s["num"]
    p = ["<section id='s%d'>" % n,
         "<h2>Sesyon %d — %s</h2>" % (n, E(s["title"]))]
    meta = s["meta"]
    line = []
    if meta.get("duree"):
        line.append("⏱ " + E(meta["duree"]))
    if meta.get("jour"):
        line.append("📅 " + E(meta["jour"]))
    if meta.get("produit"):
        line.append("🎯 Ou pral bati : <strong>%s</strong>" % E(meta["produit"]))
    if line:
        p.append("<p style='color:var(--ink-dim)'>%s</p>" % " · ".join(line))
    if meta.get("resultat"):
        p.append("<p><em>%s</em></p>" % E(meta["resultat"]))
    if meta.get("impact"):
        p.append("<p><em>%s</em></p>" % E(meta["impact"]))
    for sec in s["secs"]:
        if sec.get("drop"):
            continue
        p.append("<h3>%s</h3>" % E(head_label(sec["head"])))
        p.extend(render_blocks(sec))
    p.append("</section>")
    return "\n".join(p)

PAGE = """<!DOCTYPE html>
<html lang="ht">
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
    <a href="../index.html" class="logo"><img src="../assets/logo.svg" alt="Lojik360" class="logo-img" />Lojik<span>360</span><small>pa Atmart</small></a>
    <button class="nav-toggle" aria-label="Menu">☰</button>
    <ul class="nav-links">
      <li><a href="../index.html">Akèy</a></li>
      <li><a href="../tutoriels.html" class="active">Leson</a></li>
      <li><a href="../index.html#podcast">Podkas</a></li>
      <li><a href="../lojikkid.html">Lojikkid</a></li>
      <li><a href="https://atmart.ltd">Solisyon (Atmart)</a></li>
    </ul>
  </nav>
</header>
<div class="tuto-shell">
  <aside class="tuto-sidebar">
    <div class="tuto-sidebar-head"><span class="ico">{ico}</span><h2>{short}</h2><span class="lvl">{lvl}</span><div class="lang-page-switch">{langsw}</div></div>
    <button class="tuto-toc-toggle">☰ Sesyon yo</button>
    <ul class="tuto-toc">
      <li><a href="#intro">Sou sesyon sa yo</a></li>
      <li class="toc-group">Sesyon yo</li>
{toc}
    </ul>
  </aside>
  <main class="tuto-main">
    <p class="breadcrumb"><a href="../tutoriels.html">Leson</a> › {lvl}</p>
    <h1>{title}</h1>
    <p class="lead">{lead}</p>
{intro}
{sessions}
    <div class="tuto-pager"><a href="../tutoriels.html" class="btn btn-outline">← Tout leson yo</a></div>
  </main>
</div>
<footer><div class="container"><div class="footer-bottom">© 2026 Atmart LLC — Lojik360 se yon mak Atmart LLC.</div></div></footer>
<script src="../assets/script.js"></script>
<script src="../assets/chat.js?v=4" data-endpoint="https://atmart-chat.atmartllc.workers.dev"></script>
</body>
</html>
"""
HINT = "Chwazi yon sesyon nan meni an — yon sèl sesyon parèt chak fwa."

def render_intro(paras, extra_secs=None, axis_lead=None):
    parts = ["<section id='intro'>", "<h2>Sou sesyon sa yo</h2>"]
    if axis_lead:
        parts.append("<p>%s</p>" % E(axis_lead))
    for b in paras:
        if b[0] != "p":
            continue
        tx = b[2]; dt = deacc(tx)
        if (len(tx) < 90 and ":" not in tx) or dt.startswith(("sous not", "sous dokiman", "mode d'itilizasyon")) \
           or "oceanofpdf" in dt or "c:\\" in dt or dt.startswith(("vesyon", "vesyon", "itilizate")):
            continue
        e = E(tx)
        if dt.startswith(("not sekirite:", "not prekosyon:", "regle de konfidansyalite:", "konfidansyalite:")):
            parts.append("<div class='callout warn'><strong>⚠️ %s.</strong> %s</div>"
                         % (E(tx.split(":", 1)[0]), e.split(":", 1)[1].strip()))
        elif ":" in tx[:30]:
            lab, body = e.split(":", 1)
            parts.append("<p><strong>%s.</strong> %s</p>" % (lab, body.strip()))
        else:
            parts.append("<p>%s</p>" % e)
    if extra_secs:
        for sec in extra_secs:
            parts.append("<h3>%s</h3>" % E(sec["head"]))
            parts.extend(render_blocks(sec))
    parts.append("<p style='color:var(--ink-dim)'>%s</p>" % HINT)
    parts.append("</section>")
    return "\n".join(parts)

def render_sources(sec):
    out = ["<section id='sources'>", "<h2>%s</h2>" % E(sec["head"])]
    out.append("<p>Leson patikilye sa a se yon travay orijinal : ka yo, egzèsis yo ak envit yo te fèt pou Lojik360. "
               "Sesyon yo swiv gwo tèm klasik Excel yo (liv travay, fòma, fòmil, grafik, tablo kwaze, Power Query, "
               "senaryo, finans). Pou ale pi lwen ak fonksyon IA yo, sèvi ak resous ofisyèl Microsoft ki anba yo.</p>")
    sec["blocks"] = [b for b in sec["blocks"]
                     if not (b[0] == "p" and ("pdf" in deacc(b[2]) or "dokiman sous" in deacc(b[2]) or "manyel" in deacc(b[2])))]
    out.extend(render_blocks(sec))
    out.append("</section>")
    return "\n".join(out)

def write_page(fn, title, short, ico, lvl, lead, desc, langsw, toc, intro, sessions):
    pg = PAGE.format(title=title, short=short, ico=ico, lvl=lvl, lead=lead, desc=desc,
                     langsw=langsw, toc=toc, intro=intro, sessions=sessions)
    io.open(SITE + "\\tutoriels\\" + fn, "w", encoding="utf-8", newline="\n").write(pg)
    return len(pg)

def validate(name, sessions):
    empty = [(s["num"], sec["head"]) for s in sessions for sec in s["secs"]
             if not sec.get("drop") and not sec["blocks"]]
    nometa = [s["num"] for s in sessions if not s["meta"].get("produit")]
    print("%s: %d sessions, empty=%s, sans-produit=%s" % (name, len(sessions), empty or "0", nometa or "0"))

def toc_of(sessions, renum=False):
    lines = []
    for i, s in enumerate(sessions, 1):
        n = i if renum else s["num"]
        lines.append("      <li><a href='#s%d'>%d. %s</a></li>" % (n, n, E(s["title"])))
    return "\n".join(lines)

def sw(items):
    """items: list of (label, href_or_None, active_bool)"""
    out = []
    for lab, href, act in items:
        if href is None:
            out.append("<span class='lang-soon' title='byento'>%s</span>" % lab)
        else:
            out.append("<a href='%s'%s>%s</a>" % (href, " class='active'" if act else "", lab))
    return "".join(out)

# ================= 1) PROMPTING HT =================
doc = build_model(parse(BASE + r"\Lojik360_Prompting_Assistant_IA_Tutoriel_Apprenants_Contexte_Ameliore_Kreyol.docx"))
validate("prompting.ht", doc["sessions"])
n = write_page("prompting-ia.ht.html",
    "Prompting & asistan IA — 10 sesyon aksyon", "Prompting & asistan IA", "✍️", "🤖 Delege",
    "Aprann sèvi ak yon asistan IA san ou pa pèdi jijman imen ou : delege yon pwodiksyon, sipèvize kalite a, epi ranfòse entansyon ou. Chak sesyon pwodui yon rezilta reyèl.",
    "Prompting ak asistan IA an kreyòl : 10 sesyon aksyon pou delege, sipèvize epi ranfòse moun. Wòl, travay, kontèks, fòma, iterasyon, verifikasyon, konfidansyalite, template.",
    sw([("FR", "prompting-ia.html", False), ("HT", "prompting-ia.ht.html", True), ("EN", None, False), ("ES", None, False)]),
    toc_of(doc["sessions"]),
    render_intro(doc["intro"]),
    "\n".join(render_session(s) for s in doc["sessions"]))
print("prompting-ia.ht.html %d KB" % (n // 1024))

# ================= 2) EXCEL HT =================
doc = build_model(parse(BASE + r"\Lojik360_Excel_a_l_ere_de_l_IA_Tutoriel_Apprenants_Contextes_Detailles_Kreyol.docx"))
validate("excel.ht", doc["sessions"])
post = [s for s in doc["extras"] if not s["pre_index"]]
sessions_html = "\n".join(render_session(s) for s in doc["sessions"])
if post:
    sessions_html += "\n" + render_sources(post[0])
toc = toc_of(doc["sessions"])
if post:
    toc += "\n      <li><a href='#sources'>Sous ak limit</a></li>"
n = write_page("excel-ia.ht.html",
    "Excel nan epòk IA a — 12 sesyon aksyon", "Excel nan epòk IA a", "📊", "🤖 Delege",
    "Excel pa yon senp grid kalkil ankò : estriktire done ou yo, delege bay IA sa ki ka delege, verifye chak rezilta epi kenbe desizyon an nan men moun. 12 sesyon, yon rezilta pa sesyon.",
    "Excel nan epòk IA a an kreyòl : 12 sesyon aksyon — tab, fòmil, grafik, tablo kwaze, Power Query, senaryo, finans — ak envit IA epi verifikasyon imen.",
    sw([("FR", "excel-ia.html", False), ("HT", "excel-ia.ht.html", True), ("EN", None, False), ("ES", None, False)]),
    toc,
    render_intro(doc["intro"]),
    sessions_html)
print("excel-ia.ht.html %d KB" % (n // 1024))

# ================= 3) 27 SESSIONS HT (3 pages) =================
doc = build_model(parse(BASE + r"\Lojik360_27_Learner_Action_Tutorials_Improved_Kreyol.docx"))
validate("a27.ht", doc["sessions"])
axis_leads = {deacc(s["head"]): (s["blocks"][0][2] if s["blocks"] and s["blocks"][0][0] == "p" else "")
              for s in doc["extras"] if not s["pre_index"]}
AXCFG = [
 dict(rng=(1, 9), fn="actions-deleguer.ht.html", axkey="itilizasyon teknoloji",
      title="Itilizasyon teknoloji — 9 sesyon aksyon", short="Itilizasyon teknoloji", ico="🤖",
      lvl="🤖 Delege", base="actions-deleguer",
      desc="Delege ak anpil atansyon : trase kat travay la, ekri bon envit, verifye rezilta IA yo, pwoteje done yo epi otomatize san danje. An kreyòl."),
 dict(rng=(10, 18), fn="actions-superviser.ht.html", axkey="jesyon",
      title="Jere transfòmasyon IA — 9 sesyon aksyon", short="Jere transfòmasyon IA", ico="🔍",
      lvl="🔍 Sipèvize", base="actions-superviser",
      desc="Doktrin itilizasyon, pilòt limite, kontwòl moun-nan-bouk, risk ak etik, kondwi chanjman. 9 sesyon aksyon an kreyòl."),
 dict(rng=(19, 27), fn="actions-renforcer.ht.html", axkey="ranfose imen an",
      title="Ranfòse imen an — 9 sesyon aksyon", short="Ranfòse imen an", ico="🌱",
      lvl="🌱 Ranfòse imen an", base="actions-renforcer",
      desc="Jijman, kominikasyon, konfyans, kreyativite anba kontrent, atansyon, sante ak rezilyans karyè. 9 sesyon aksyon an kreyòl."),
]
for cfg in AXCFG:
    ss = [s for s in doc["sessions"] if cfg["rng"][0] <= s["num"] <= cfg["rng"][1]]
    lead = axis_leads.get(cfg["axkey"], "")
    toc = "\n".join("      <li><a href='#s%d'>%d. %s</a></li>" % (i, i, E(s["title"]))
                    for i, s in enumerate(ss, 1))
    sessions_html = "\n".join(render_session(s, local_num=i) for i, s in enumerate(ss, 1))
    n = write_page(cfg["fn"], cfg["title"], cfg["short"], cfg["ico"], cfg["lvl"],
        lead or cfg["desc"], cfg["desc"],
        sw([("FR", cfg["base"] + ".html", False), ("HT", cfg["fn"], True),
            ("EN", cfg["base"] + ".en.html", False), ("ES", None, False)]),
        toc, render_intro(doc["intro"], axis_lead=None), sessions_html)
    print("%s %d KB (%d sesyon)" % (cfg["fn"], n // 1024, len(ss)))

# ================= 4) RECHERCHE QUALITATIVE HT =================
doc = build_model(parse(BASE + r"\HAGN_Methodes_Recherche_Qualitative_Sessions_Apprenants_Renforcer_Humain_Prompts_Resultats_Kreyol.docx"))
validate("rech.ht", doc["sessions"])
pre = [s for s in doc["extras"] if s["pre_index"]]
n = write_page("recherche-qualitative.ht.html",
    "Metòd rechèch kalitatif — 14 sesyon aksyon", "Rechèch kalitatif", "🎤", "🌱 Ranfòse imen an",
    "Rechèch kalitatif fòme ladrès IA pa ranplase : koute, jijman, senpati, responsablite. 14 sesyon pou chèchè sou teren : entèvyou, gwoup konsantre, obsèvasyon, analiz ak sentèz QuIP.",
    "Metòd rechèch kalitatif an kreyòl : 14 sesyon aksyon pou chèchè sou teren — entèvyou apwofondi, kesyon ouvè, gwoup konsantre, obsèvasyon, kodaj ak analiz, sentèz QuIP.",
    sw([("FR", None, False), ("HT", "recherche-qualitative.ht.html", True), ("EN", None, False), ("ES", None, False)]),
    toc_of(doc["sessions"]),
    render_intro(doc["intro"], extra_secs=pre),
    "\n".join(render_session(s) for s in doc["sessions"]))
print("recherche-qualitative.ht.html %d KB" % (n // 1024))
