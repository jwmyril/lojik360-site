// ===== Atmart / Lojik360 — live-chat learning assistant widget =====
// Floating bubble on tutorial pages. Detects the page language (en/fr/ht/es),
// talks to the Cloudflare worker (data-endpoint on this script tag), and shows
// the reply. No data is stored; the conversation lives in memory only.
(function () {
  var script = document.currentScript;
  var ENDPOINT = (script && script.getAttribute("data-endpoint")) || "";

  // --- language (from <html lang>, fallback French) ---
  var raw = (document.documentElement.lang || "fr").slice(0, 2).toLowerCase();
  var LANG = ["en", "fr", "ht", "es"].indexOf(raw) >= 0 ? raw : "fr";

  var T = {
    fr: { title: "Assistant Lojik", sub: "Pose une question sur le tutoriel",
      open: "Discuter avec l’assistant", ph: "Écris ta question…", send: "Envoyer",
      hello: "Bonjour 👋 Je suis l’assistant IA de Lojik360. Pose-moi une question sur la pensée critique ou sur le tutoriel.",
      disc: "Assistant IA — peut se tromper. Vérifie les informations importantes.",
      err: "Désolé, une erreur est survenue. Réessaie dans un instant.",
      limit: "Tu as atteint la limite de messages pour aujourd’hui. Reviens demain 🙂",
      thinking: "…" },
    en: { title: "Lojik assistant", sub: "Ask about the tutorial",
      open: "Chat with the assistant", ph: "Type your question…", send: "Send",
      hello: "Hi 👋 I’m the Lojik360 AI assistant. Ask me anything about critical thinking or the tutorial.",
      disc: "AI assistant — can make mistakes. Verify anything important.",
      err: "Sorry, something went wrong. Please try again in a moment.",
      limit: "You’ve reached today’s message limit. Come back tomorrow 🙂",
      thinking: "…" },
    ht: { title: "Asistan Lojik", sub: "Poze yon kesyon sou leson an",
      open: "Pale ak asistan an", ph: "Ekri kesyon ou…", send: "Voye",
      hello: "Bonjou 👋 Mwen se asistan IA Lojik360 a. Poze m nenpòt kesyon sou lespri kritik oswa sou leson an.",
      disc: "Asistan IA — li ka fè erè. Verifye enfòmasyon ki enpòtan yo.",
      err: "Eskize, gen yon erè ki rive. Eseye ankò nan yon ti moman.",
      limit: "Ou rive nan limit mesaj pou jodi a. Tounen demen 🙂",
      thinking: "…" },
    es: { title: "Asistente Lojik", sub: "Pregunta sobre el tutorial",
      open: "Chatear con el asistente", ph: "Escribe tu pregunta…", send: "Enviar",
      hello: "Hola 👋 Soy el asistente de IA de Lojik360. Pregúntame lo que quieras sobre el pensamiento crítico o el tutorial.",
      disc: "Asistente de IA — puede equivocarse. Verifica lo importante.",
      err: "Lo siento, ocurrió un error. Inténtalo de nuevo en un momento.",
      limit: "Has alcanzado el límite de mensajes de hoy. Vuelve mañana 🙂",
      thinking: "…" },
  }[LANG];

  var messages = []; // {role, content}
  var busy = false;

  // --- build DOM ---
  var btn = document.createElement("button");
  btn.className = "atmart-chat-btn";
  btn.setAttribute("aria-label", T.open);
  btn.innerHTML = "<span aria-hidden='true'>💬</span>";

  var panel = document.createElement("div");
  panel.className = "atmart-chat-panel";
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-label", T.title);
  panel.hidden = true;
  panel.innerHTML =
    '<div class="acp-head"><div><strong>' + T.title + '</strong><span>' + T.sub + '</span></div>' +
    '<button class="acp-close" aria-label="X">×</button></div>' +
    '<div class="acp-log" aria-live="polite"></div>' +
    '<form class="acp-form"><input class="acp-input" type="text" autocomplete="off" placeholder="' +
    T.ph + '" aria-label="' + T.ph + '"><button class="acp-send" type="submit">' + T.send + '</button></form>' +
    '<div class="acp-disc">' + T.disc + '</div>';

  document.body.appendChild(btn);
  document.body.appendChild(panel);

  var log = panel.querySelector(".acp-log");
  var form = panel.querySelector(".acp-form");
  var input = panel.querySelector(".acp-input");

  function esc(s) {
    return s.replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function addBubble(role, text) {
    var d = document.createElement("div");
    d.className = "acp-msg acp-" + role;
    d.innerHTML = esc(text).replace(/\n/g, "<br>");
    log.appendChild(d);
    log.scrollTop = log.scrollHeight;
    return d;
  }

  var opened = false;
  function openPanel() {
    panel.hidden = false; btn.classList.add("is-open");
    document.documentElement.classList.add("chat-open");
    if (!opened || !log.children.length) { opened = true; addBubble("bot", T.hello); }
    setTimeout(function () { input.focus(); }, 50);
  }
  function closePanel() {
    panel.hidden = true; btn.classList.remove("is-open");
    document.documentElement.classList.remove("chat-open");
  }

  btn.addEventListener("click", function () { panel.hidden ? openPanel() : closePanel(); });
  panel.querySelector(".acp-close").addEventListener("click", closePanel);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !panel.hidden) closePanel(); });
  // Un clic/tap hors du panneau le ferme : il ne bloque jamais la lecture.
  document.addEventListener("click", function (e) {
    if (!panel.hidden && !panel.contains(e.target) && !btn.contains(e.target)) closePanel();
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var text = input.value.trim();
    if (!text || busy) return;
    if (!ENDPOINT) { addBubble("bot", T.err); return; }
    input.value = "";
    addBubble("user", text);
    messages.push({ role: "user", content: text });

    busy = true;
    var typing = addBubble("bot", T.thinking);
    typing.classList.add("acp-typing");

    fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: messages, lang: LANG }),
    })
      .then(function (r) {
        return r.json().then(function (d) { return { ok: r.ok, status: r.status, d: d }; });
      })
      .then(function (res) {
        typing.remove();
        if (res.status === 429 || (res.d && res.d.error === "rate_limited")) {
          addBubble("bot", T.limit);
        } else if (res.ok && res.d && res.d.reply) {
          addBubble("bot", res.d.reply);
          messages.push({ role: "assistant", content: res.d.reply });
        } else {
          addBubble("bot", T.err);
        }
      })
      .catch(function () { typing.remove(); addBubble("bot", T.err); })
      .finally(function () { busy = false; input.focus(); });
  });
})();
