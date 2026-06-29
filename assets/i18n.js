// ===== Atmart i18n — sélecteur 4 langues (FR · HT · EN · ES), couverture complète =====
// Le français est la langue de base (texte dans le HTML). Les autres langues
// viennent de assets/i18n/<lang>.json. Aucune clé manquante = aucun mélange.
(function () {
  const LANGS = { fr: "Français", ht: "Kreyòl", en: "English", es: "Español" };
  const DEFAULT = "fr";
  const orig = new Map();
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
