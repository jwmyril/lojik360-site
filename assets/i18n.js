// ===== Atmart i18n — sélecteur 4 langues (FR · HT · EN · ES), couverture complète =====
// Le français est la langue de base (texte dans le HTML). Les autres langues
// viennent de assets/i18n/<lang>.json. Aucune clé manquante = aucun mélange.
(function () {
  const LANGS = { fr: "Français", ht: "Kreyòl", en: "English", es: "Español" };
  const DEFAULT = "fr";
  const orig = new Map();
  // Empeche une boucle de redirection si un fichier frere manque.
  let navigation_en_cours = false;
  const base = (location.pathname.includes("/tutoriels/")) ? "../" : "";

  function capture() {
    document.querySelectorAll("[data-i18n]").forEach((el) => orig.set(el, el.textContent));
    document.querySelectorAll("[data-i18n-html]").forEach((el) => orig.set(el, el.innerHTML));
    document.querySelectorAll("[data-i18n-ph]").forEach((el) => orig.set(el, el.getAttribute("placeholder")));
    document.querySelectorAll("[data-i18n-aria]").forEach((el) => orig.set(el, el.getAttribute("aria-label")));
  }

  async function apply(lang) {
    if (!LANGS[lang]) lang = DEFAULT;
    let dict = {};
    if (lang !== DEFAULT) {
      try { dict = await fetch(base + "assets/i18n/" + lang + ".json", { cache: "no-cache" }).then((r) => r.json()); }
      catch (e) { dict = {}; }
    }
    const val = (key, fb) => (lang === DEFAULT ? fb : (dict[key] != null ? dict[key] : fb));
    document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = val(el.dataset.i18n, orig.get(el)); });
    document.querySelectorAll("[data-i18n-html]").forEach((el) => { el.innerHTML = val(el.dataset.i18nHtml, orig.get(el)); });
    document.querySelectorAll("[data-i18n-ph]").forEach((el) => { el.setAttribute("placeholder", val(el.dataset.i18nPh, orig.get(el))); });
    document.querySelectorAll("[data-i18n-aria]").forEach((el) => { el.setAttribute("aria-label", val(el.dataset.i18nAria, orig.get(el))); });

    // ===== B1 : la langue doit changer la DESTINATION, pas seulement le texte
    //
    // 1. Les liens qui declarent une variante (data-href-ht="…") pointent
    //    vers elle. Sans cela, un lecteur en kreyol cliquait « Kommanse » et
    //    tombait sur le tutoriel francais, alors que la version kreyol
    //    existait : son choix de langue ne comptait pas.
    //    ⚠️ ON REPART TOUJOURS DU FRANCAIS. Une premiere version ne
    //    touchait qu'aux liens ayant une variante dans la langue choisie :
    //    en passant de kreyol a anglais, un tutoriel sans version anglaise
    //    GARDAIT son adresse kreyol. Le lecteur anglophone recevait du
    //    kreyol parce qu'il etait passe par la. Vu au navigateur.
    const cle = (lg) => "href" + lg.charAt(0).toUpperCase() + lg.slice(1);
    document.querySelectorAll("a[data-href-ht], a[data-href-en], a[data-href-es]")
      .forEach((a) => {
        if (!a.dataset.hrefFr) a.dataset.hrefFr = a.getAttribute("href");
        a.setAttribute("href", a.dataset[cle(lang)] || a.dataset.hrefFr);
      });

    // 2. ⚠️ SUR UNE PAGE DEJA TRADUITE, ON NAVIGUE — on ne repeint pas.
    //    Le corps d'un tutoriel est ecrit en dur dans son fichier : traduire
    //    seulement l'enveloppe (menu, pied de page, boutons) donnait une page
    //    a MOITIE traduite, ce que la doctrine du projet interdit. Si le
    //    fichier frere existe et qu'on n'y est pas, on y va.
    const alt = document.documentElement.dataset[cle(lang)];
    if (alt && !location.pathname.endsWith("/" + alt) && !navigation_en_cours) {
      navigation_en_cours = true;
      localStorage.setItem("atmart_lang", lang);
      location.href = alt;
      return;
    }

    document.documentElement.lang = lang;
    localStorage.setItem("atmart_lang", lang);
    document.querySelectorAll(".lang-opt").forEach((b) => b.classList.toggle("active", b.dataset.lang === lang));
    const cur = document.querySelector(".lang-current");
    if (cur) cur.textContent = "🌐 " + lang.toUpperCase();
  }

  function buildSelector() {
    const nav = document.querySelector(".nav-links");
    if (!nav) return;
    const li = document.createElement("li");
    li.className = "lang-select";
    const btn = document.createElement("button");
    btn.type = "button"; btn.className = "lang-current"; btn.textContent = "🌐 FR";
    btn.setAttribute("aria-label", "Langue / Lang");
    const menu = document.createElement("div");
    menu.className = "lang-menu";
    Object.keys(LANGS).forEach((code) => {
      const o = document.createElement("button");
      o.type = "button"; o.className = "lang-opt"; o.dataset.lang = code; o.textContent = LANGS[code];
      o.addEventListener("click", (e) => { e.stopPropagation(); apply(code); menu.classList.remove("open"); });
      menu.appendChild(o);
    });
    btn.addEventListener("click", (e) => { e.stopPropagation(); menu.classList.toggle("open"); });
    document.addEventListener("click", () => menu.classList.remove("open"));
    li.appendChild(btn); li.appendChild(menu); nav.appendChild(li);
  }

  capture();
  buildSelector();
  apply(localStorage.getItem("atmart_lang") || DEFAULT);
})();
