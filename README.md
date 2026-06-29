# Lojik360

The education & strategy brand of **Atmart LLC** — *penser et créer à l'ère de l'IA*.

Static site (HTML/CSS/JS, no framework), hosted on **GitHub Pages** at
**lojik360.atmart.ltd**. Four languages (FR base + HT/EN/ES via `assets/i18n`).

Lojik360 is organized around one thesis: don't compete with AI on speed, don't
ignore it — **delegate** what it does well, **supervise** what it does
imperfectly, and **strengthen** what stays human (judgment, creativity,
relationship, responsibility). Atmart (atmart.ltd) is the sibling commerce
portal that sells data, SaaS and solutions.

## Deploy

Commit + push to `main` → live in ~1 minute (GitHub Pages, custom domain via the
`CNAME` file). No build step.

## Structure

- `index.html` — home: hero + manifesto + the 3 axes + podcast teaser.
- `assets/` — `style.css` (shared design system with Atmart), `i18n.js` (4-lang
  engine + selector), `script.js`, `logo.svg`, `i18n/{ht,en,es}.json`.

Migration in progress: tutorials, podcast and the kids section ("Lojik360
Junior") move here from atmart.ltd. Until then, a few links point to atmart.ltd.
