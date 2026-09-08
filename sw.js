// Lojik360 — cache statique.
//
// ⚠️ DEUX RÈGLES QUI NE SE NÉGOCIENT PAS.
//
// 1. LES PAGES EN *NETWORK-FIRST*. Un cache-first sans revalidation garde une
//    page périmée jusqu'au prochain changement de nom de cache. Un visiteur
//    déjà venu lirait une ancienne version d'un tutoriel — ou, pire, une
//    ancienne page de confidentialité — sans jamais savoir pourquoi. Le réseau
//    gagne quand il répond ; le cache ne sert que hors ligne.
//
// 2. RIEN DE CE QUI PART AU WORKER N'ENTRE ICI. Le chat de l'assistant et
//    l'inscription à l'infolettre passent par
//    `atmart-chat.atmartllc.workers.dev`. Mettre ces réponses en cache
//    reviendrait à écrire sur le disque du visiteur ce que la page de
//    confidentialité promet de ne conserver nulle part.
//
// ⚠️ LE NOM DU CACHE EST UNE EMPREINTE, calculée par tools/version_cache.py
// depuis le contenu réellement servi. Le changer à la main a déjà été oublié
// deux fois sur un autre site de la maison : oublier, c'est publier pour
// personne, sans message d'erreur.
const CACHE = "lojik360-db362ec3";

const CORE = [
  "/", "/index.html", "/404.html", "/tutoriels.html", "/podcast.html",
  "/lojikkid.html", "/confidentialite.html",
  "/assets/style.css", "/assets/script.js", "/assets/i18n.js",
  "/assets/i18n/ht.json", "/assets/i18n/en.json", "/assets/i18n/es.json",
  "/assets/brand/logo-96.png", "/assets/brand/logo-dark-96.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE)
      // `addAll` échoue en bloc si une seule URL manque : on ajoute une par
      // une pour qu'un fichier renommé n'empêche pas toute l'installation.
      .then((c) => Promise.allSettled(CORE.map((u) => c.add(u))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((n) => Promise.all(n.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const u = new URL(e.request.url);

  // Le Worker : jamais de cache. Voir la règle 2 ci-dessus.
  if (u.hostname.endsWith("workers.dev")) return;

  // Les tiers (polices, Cusdis) : on laisse le navigateur faire.
  if (u.origin !== location.origin) return;

  if (e.request.method !== "GET") return;

  const estPage = e.request.mode === "navigate"
    || (e.request.headers.get("accept") || "").includes("text/html");

  if (estPage) {
    e.respondWith(
      fetch(e.request)
        .then((rep) => {
          if (rep && rep.ok) {
            const c = rep.clone();
            caches.open(CACHE).then((ch) => ch.put(e.request, c));
          }
          return rep;
        })
        .catch(() => caches.match(e.request, { ignoreSearch: true })
          .then((r) => r || caches.match("/404.html") || caches.match("/index.html")))
    );
    return;
  }

  // Les ressources portent un `?v=` qui change avec leur contenu : le cache
  // d'abord est sûr, et `ignoreSearch` évite de rater une entrée précachée
  // sans clé de version.
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then((r) => r || fetch(e.request).then((rep) => {
      if (rep && rep.ok) {
        const c = rep.clone();
        caches.open(CACHE).then((ch) => ch.put(e.request, c));
      }
      return rep;
    }))
  );
});
