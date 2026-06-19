# nf-claw website

A **living digital interface** for the nf-claw repository — futuristic, dark, and
fully data-driven. Nothing about pipelines, versions, skills, parameters or docs is
hardcoded: every value on the site is read from the repository at build time.

> _Augen Pro meets GitHub, documentation portals and data-visualization platforms._

## Stack

- **Next.js 15** (App Router, React Server Components) · **TypeScript**
- **Tailwind CSS** (custom design system derived from the brand logo)
- **Framer Motion** (scroll storytelling, micro-interactions)
- **react-markdown** (documentation hub)

shadcn/ui was in the preferred stack; rather than vendor its CLI, the UI uses the same
Radix-style primitives reimplemented as local components in `src/components/ui` — same
philosophy, zero extra config.

## The repository is the CMS

The data layer (`src/lib/data`) is the single source of truth and reads, at build time:

| Source in the repo | Powers |
|---|---|
| `catalog.json` | the pipeline list |
| `pipelines/<name>/skill.md` (frontmatter + body) | run commands, samplesheet, required params, outputs |
| `pipelines/<name>/reference.md` | the full parameter explorer (every group + parameter) |
| `sources.tsv`, `.gitmodules` | upstream URLs and version policy |
| `pipelines/<name>/upstream/` (submodule) | pinned release date + nf-core module count |
| `.github/workflows/*.yml` | the CI/CD / automation panel |
| `README.md`, `docs/*.md`, `CONTRIBUTING.md`, … | the documentation hub |
| local `git log` / `git tag` | the update history + release timeline |

**Add a pipeline, push a release, edit a doc → the site reflects it on the next build.**
No page is maintained by hand. The design scales from 5 to 500 pipelines (the pipeline
constellation lays nodes onto concentric rings and the grid/cards reflow automatically).

## Develop

```bash
cd website
npm install
npm run dev        # http://localhost:3000
```

## Build

The site is exported as a fully static bundle (`output: "export"`) into `out/` — no
server runtime is required.

```bash
npm run build          # writes ./out
npx serve out          # preview the static bundle
```

For project-site hosting under a sub-path, set the base path at build time:

```bash
NEXT_PUBLIC_BASE_PATH=/nf-claw NEXT_PUBLIC_SITE_URL=https://<user>.github.io npm run build
```

## Deployment

1. **GitHub Pages (default).** `.github/workflows/deploy-pages.yml` builds the static
   bundle on every push to `main` and publishes it to Pages. It checks out the pinned
   submodules and full git history so the data layer can read release dates, module
   counts, tags and the commit log, and it derives the base path/origin from the Pages
   configuration. Every push — including the daily `auto-update` PR that bumps pipelines —
   rebuilds the site from the current repository state. No tokens required.
2. **Live GitHub augmentation (optional).** If a `GITHUB_TOKEN` (or `GH_TOKEN`) is present
   at build time, `src/lib/data/github.ts` augments the Activity section with live Actions
   runs and Releases via the REST API. Without it, the site falls back to local git tags
   and workflow definitions. The token is only ever read at build time and is never shipped
   to the client.

Override the data root with `NFCLAW_REPO_ROOT` if the website is built outside the repo.

## Design system

Defined in `tailwind.config.ts` and `src/app/globals.css`, derived from the logo
(white line-art T-rex + green apple on black):

- **Surfaces** — a near-black `ink` scale with subtle elevation
- **Primary** — apple-green `claw` scale
- **Secondary** — warm `cream` (the apple's bite)
- Consistent spacing, `glass` cards, ambient glows, film grain, and reduced-motion support
