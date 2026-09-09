/* mesure360.js — le compteur commun aux six sites Atmart.
 *
 * SOURCE UNIQUE. Ce fichier vit ici et nulle part ailleurs ; tools/poser-mesure.py
 * le recopie dans chaque <site>/assets/mesure360.js. Ne pas l'editer cote site :
 * la copie serait ecrasee a la prochaine pose, en silence.
 *
 * CE QU'IL ENVOIE, et rien de plus :
 *   app   le site (six valeurs possibles, refusees si autres cote Worker)
 *   name  « view » pour une page vue, ou une action de la liste EV_UNIV
 *   page  le chemin nu, sans parametres ni ancre
 *   lang  la langue de la page
 *   src   d'ou vient le visiteur : utm_source, sinon le domaine referent
 *
 * CE QU'IL N'ENVOIE PAS : aucune adresse IP (le Worker n'en garde pas non
 * plus), aucun identifiant, aucun cookie, aucun stockage local, aucun parcours
 * individuel. Le visiteur unique est reconstitue cote serveur par une empreinte
 * du jour, salee et tronquee, qui ne survit pas a 48 h.
 *
 * POURQUOI sendBeacon AVEC UN Blob text/plain. Un fetch en application/json
 * declenche une requete preliminaire CORS (OPTIONS) : deux allers-retours pour
 * un compteur, et une panne silencieuse le jour ou un domaine manque dans la
 * liste. Un Blob text/plain est une « requete simple » : elle part sans
 * preliminaire, survit a la fermeture de l'onglet, et le Worker la lit
 * exactement pareil.
 *
 * POSE :  <script src="/assets/mesure360.js" data-app="driver360" defer></script>
 */
(function () {
  "use strict";

  var POINT = "https://atmart-chat.atmartllc.workers.dev/ev";

  var balise = document.currentScript || document.querySelector("script[data-app]");
  var APP = (balise && balise.getAttribute("data-app")) || "";
  if (!APP) return;

  // On ne mesure pas le travail en cours : sinon une apres-midi de mise au
  // point pese autant qu'une journee de vrais visiteurs.
  var h = location.hostname;
  if (h === "localhost" || h === "127.0.0.1" || h === "" || h.indexOf("192.168.") === 0) return;

  function langue() {
    var l = (document.documentElement.getAttribute("lang") || "").toLowerCase().slice(0, 2);
    return (l === "ht" || l === "fr" || l === "en" || l === "es") ? l : "fr";
  }

  // La provenance tient en un mot : une campagne nommee, ou le domaine qui a
  // envoye le visiteur, ou « direct ». Le Worker la nettoie une seconde fois.
  function provenance() {
    try {
      var u = new URLSearchParams(location.search).get("utm_source");
      if (u) return u.toLowerCase().slice(0, 32);
      if (!document.referrer) return "direct";
      var r = new URL(document.referrer).hostname.replace(/^www\./, "");
      if (r === location.hostname) return "";        // navigation interne : on ne recompte pas
      // linkedin.com, l.facebook.com, com.google.android.gm… on garde le nom.
      var bouts = r.split(".");
      return (bouts.length > 2 ? bouts[bouts.length - 2] : bouts[0]).slice(0, 32);
    } catch (e) { return "direct"; }
  }

  function envoie(nom, extra) {
    var corps = {
      app: APP,
      name: nom || "view",
      page: location.pathname,
      lang: langue()
    };
    var s = provenance();
    if (s) corps.src = s;
    if (extra && typeof extra === "object") {
      // Un seul champ libre est accepte cote Worker : le nom de l'evenement.
      // Tout le reste est ignore, on ne l'envoie donc pas.
      if (extra.page) corps.page = String(extra.page);
    }
    var texte = JSON.stringify(corps);
    try {
      if (navigator.sendBeacon) {
        navigator.sendBeacon(POINT, new Blob([texte], { type: "text/plain;charset=UTF-8" }));
        return;
      }
    } catch (e) { /* on retombe sur fetch */ }
    try {
      fetch(POINT, { method: "POST", body: texte, keepalive: true, mode: "no-cors" });
    } catch (e) { /* la mesure ne doit JAMAIS casser la page */ }
  }

  // Une page vue, une fois, au chargement.
  envoie("view");

  // Les sites peuvent signaler une action : mesure360("telecharge").
  // Noms acceptes : view, clic, telecharge, partage, install, achat_clic,
  // erreur, recherche. Tout autre nom est ignore par le Worker.
  window.mesure360 = envoie;
})();
