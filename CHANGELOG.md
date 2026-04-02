# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-01

### Added

- **US1 — Post Authoring & Blog Index Generation** (P1 MVP)
  - `discover_posts` scans `docs/<blog_dir>/posts/` recursively for `.md` files.
  - `build_blog_model` parses front matter, derives slugs, filters drafts, and returns an immutable `BlogModel`.
  - `emit_blog_index` writes a dated post listing to `docs/<blog_dir>/index.md` via the sentinel protocol (idempotent, user preamble preserved).

- **US2 — Yearly Archive Pages** (P2)
  - Archive landing page at `docs/<blog_dir>/archive/index.md` listing all years.
  - Per-year pages at `docs/<blog_dir>/archive/<year>.md` listing posts for that year.

- **US3 — Tag & Category Landing Pages** (P3)
  - Tag landing at `docs/<blog_dir>/tag/index.md`; per-tag pages at `docs/<blog_dir>/tag/<slug>.md`.
  - Category landing at `docs/<blog_dir>/category/index.md`; per-category pages at `docs/<blog_dir>/category/<slug>.md`.
  - Slug collision detection — colliding labels receive `base`, `base-2`, … assignments with a `CollisionWarning` emitted.

- **US4 — Slug & Excerpt Control** (P4)
  - `slug` front matter field overrides auto-derived slug (validated; invalid values fall back to algorithm with a warning).
  - `<!-- more -->` marker controls excerpt split; first-paragraph fallback when absent.

- **US5 — Nav Assurance & CLI Interface** (P5)
  - `zensical-blog build` — full generation pipeline with `--config`, `--docs-dir`, `--apply-nav`, `--fail-on-warnings`.
  - `zensical-blog clean` — removes `docs/.bloggen/` idempotently.
  - `--apply-nav` patches `mkdocs.yml` nav non-destructively via `ruamel.yaml` round-trip.
  - Advisory `MISSING_GITIGNORE` warning when `.gitignore` does not cover `docs/.bloggen/`.
  - Advisory `MISSING_NAV_ENTRY` warning when mkdocs.yml nav lacks the Blog entry.

- **US6 — Zensical Plugin Integration** (P6)
  - `BlogPlugin` adapter registered as `zensical_blog` under the `zensical.plugins` entry point.
  - `on_pre_build` delegates to `build_blog_model` + `emit_all`; no `mkdocs` dependency anywhere.
  - Class does not subclass any external base class (bridge-mode compatible).

### Technical

- Python 3.11 minimum; `src/` layout; hatchling build backend.
- Runtime dependencies: `python-frontmatter>=1.1`, `click>=8.1`, `ruamel.yaml>=0.18`.
- Sentinel protocol: `<!-- zensical-blog:generated:start/end -->` markers for idempotent canonical file updates.
- Deterministic two-key sort: `(-date.toordinal(), str(source_path))`.
- NFKD slug algorithm: normalize → strip combining marks → casefold → `[a-z0-9-]+` → max 80 chars → fallback `"x"`.
- 96-test suite (62 unit + 34 integration); `ruff check` clean.
