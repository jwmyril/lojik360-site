// ===== Lojik360 — interactions =====

// Mobile nav toggle
const toggle = document.querySelector(".nav-toggle");
const links = document.querySelector(".nav-links");
if (toggle && links) {
  toggle.addEventListener("click", () => links.classList.toggle("open"));
}

// Category filters (tutorials + datasets pages)
document.querySelectorAll(".filters").forEach((bar) => {
  const buttons = bar.querySelectorAll(".filter-btn");
  const targetGrid = document.querySelector(bar.dataset.target);
  if (!targetGrid) return;
  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      buttons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const cat = btn.dataset.filter;
      targetGrid.querySelectorAll(".card").forEach((card) => {
        const show = cat === "all" || (card.dataset.cat || "").split(" ").includes(cat);
        card.style.display = show ? "" : "none";
      });
    });
  });
});

// Search arriving from the homepage (?q=...) — filters tutorial cards by text
const params = new URLSearchParams(window.location.search);
const q = (params.get("q") || "").trim().toLowerCase();
if (q) {
  const grid = document.querySelector("#tuto-grid");
  if (grid) {
    grid.querySelectorAll(".card").forEach((card) => {
      card.style.display = card.textContent.toLowerCase().includes(q) ? "" : "none";
    });
    const head = document.querySelector(".hero p.lead");
    if (head) head.textContent = 'Résultats pour « ' + q + ' » — effacez la recherche pour tout revoir.';
  }
}

// Live search on a page grid (e.g. tools page): input.page-search filters its data-target grid
document.querySelectorAll("input.page-search").forEach((input) => {
  const grid = document.querySelector(input.dataset.target);
  if (!grid) return;
  input.closest("form") && input.closest("form").addEventListener("submit", (e) => e.preventDefault());
  input.addEventListener("input", () => {
    const term = input.value.trim().toLowerCase();
    grid.querySelectorAll(".card").forEach((card) => {
      card.style.display = !term || card.textContent.toLowerCase().includes(term) ? "" : "none";
    });
  });
});

// Tutorial reader: scrollspy (highlight current chapter in the sidebar) + mobile toggle
const toc = document.querySelector(".tuto-toc");
if (toc) {
  const links = [...toc.querySelectorAll("a[href^='#']")];
  const sections = links
    .map((a) => document.querySelector(a.getAttribute("href")))
    .filter(Boolean);
  const spy = () => {
    const y = window.scrollY + 130;
    let current = sections[0];
    for (const s of sections) { if (s.offsetTop <= y) current = s; }
    if (!current) return;
    links.forEach((a) => a.classList.toggle("active", a.getAttribute("href") === "#" + current.id));
  };
  window.addEventListener("scroll", spy, { passive: true });
  spy();

  // Smooth-scroll + close mobile panel on click
  const toggle = document.querySelector(".tuto-toc-toggle");
  links.forEach((a) => a.addEventListener("click", () => {
    if (window.innerWidth <= 860) toc.classList.remove("open");
  }));
  if (toggle) toggle.addEventListener("click", () => toc.classList.toggle("open"));
}

// Newsletter form (placeholder — replace with your provider, e.g. Substack/Mailchimp embed)
const form = document.querySelector(".newsletter-form");
if (form) {
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const email = form.querySelector("input").value;
    alert("Mèsi! / Merci " + email + " — votre inscription sera activée dès que le service de newsletter sera connecté.");
  });
}
