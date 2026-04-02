# Implementation Plan: Zensical Blog Module (Sidecar, Bridge Mode)

**Branch**: `001-zensical-blog-module` | **Date**: 2026-04-01 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/001-zensical-blog-module/spec.md`

## Summary

Build a pip-installable Python module (`zensical-blog`) that operates as a
**pre-build generator** for Zensical / MkDocs documentation sites, injecting
a sidecar blog (index, yearly archives, tag and category pages) via
deterministic Markdown file generation. The module ships today in "bridge
mode" — producing files under `docs/.bloggen/` with no dependency on
Zensical's (unreleased) public module API — while maintaining clean model-
layer boundaries so the emission layer can later be swapped for native
Zensical components.

Key approach: **filesystem-first, stdlib-heavy, zero Zensical coupling**.
Post discovery and model building are pure Python; emission writes Markdown
strings to files. A `click`-based CLI provides `build` and `clean` commands
with auto-detection of `zensical.toml` / `mkdocs.yml`.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: `python-frontmatter` (YAML front matter parsing), `click` (CLI), `ruamel.yaml` (round-trip YAML read/write for `mkdocs.yml` compat + `--apply-nav`); `tomllib` (stdlib, Python 3.11+); `unicodedata` (stdlib, slugification). The `mkdocs` package is NOT a dependency.  
**Storage**: Files — reads Markdown sources from `docs/`; writes generated Markdown to `docs/.bloggen/`; reads config from `zensical.toml` or `mkdocs.yml`  
**Testing**: `pytest` with `tmp_path` fixtures for filesystem isolation; `ruff` for linting  
**Target Platform**: Any OS with Python 3.11+ (developer machine / CI)  
**Project Type**: CLI tool + installable Python package (`src`-layout)  
**Performance Goals**: Must not rewrite unchanged files; typical docs site (≤1000 posts) completes `build` in <2 s  
**Constraints**: All writes bounded to `docs/.bloggen/` + canonical override files; byte-for-byte deterministic output; pip-installable from GitHub without extra steps  
**Scale/Scope**: Typical docs-as-code site — 10–1000 posts, 1–50 tags/categories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Gate | Status |
|---|-----------|------|--------|
| I | Python Standards & Packaging | Source in `src/zensical_blog/`; PEP 8 via `ruff`; type annotations on all public interfaces; `pyproject.toml` with `[build-system]` | ✅ PASS |
| II | Bridge-First, API-Forward | No Zensical internal imports at any level; `mkdocs` is NOT a dependency; plugin adapter targets the `zensical.plugins` entry point for forward-compatibility with Zensical's future module API; all model boundaries documented in `data-model.md` | ✅ PASS |
| III | Test-First | `pytest` test runner; integration tests cover full `discover → parse → sort → emit` pipeline; unit tests cover all model + utility logic; tests written before implementation | ✅ PASS |
| IV | Deterministic & Safe Output | All writes bounded to `docs/.bloggen/`; append-only for canonical override files; no rewrites when content unchanged | ✅ PASS |
| V | Clean Model/Emission Separation | `builder.py` = model layer (no file writes); `emitter.py` = emission layer (no business logic); boundary enforced in code review | ✅ PASS |
| VI | Simplicity & YAGNI | No RSS in v1; no taxonomy pagination in v1; no `authors` rendering in v1; no Jinja2 (plain string generation is sufficient); no complexity violations | ✅ PASS |

**Pre-Phase-0 gate: ALL PASS. Proceeding to research.**

---

### Post-Phase-1 Design Re-check

*Re-evaluated after generating `research.md`, `data-model.md`, `contracts/`, and `quickstart.md`.*

| # | Principle | Post-Design Findings | Status |
|---|-----------|----------------------|--------|
| I | Python Standards & Packaging | All 10 data-model entities map directly to the planned source files. Public interfaces (`BlogConfig`, `Post`, `BlogModel`, `BlogPlugin`) carry explicit field types. No new packaging concerns. | ✅ PASS |
| II | Bridge-First, API-Forward | `contracts/config-schema.md` confirms `mkdocs.yml` parsing is plain `ruamel.yaml` dict — zero MkDocs imports. `contracts/url-routing.md` and `data-model.md` document all model boundaries. `zensical.plugins` entry point is forward-declared only. | ✅ PASS |
| III | Test-First | 6 unit tests + 3 integration tests cover every entity and all critical paths: `SlugRegistry` collision resolution, sentinel protocol idempotency, full pipeline round-trip, and `clean`. No entity or algorithm is untested. | ✅ PASS |
| IV | Deterministic & Safe Output | Two write targets confirmed safe: (a) `docs/.bloggen/` for new generated artifacts; (b) sentinel-bounded append sections in canonical files. `Post.sort_key` (`(-date.toordinal(), str(source_path))`) is deterministic. Content-unchanged check required before any write. | ✅ PASS |
| V | Clean Model/Emission Separation | `BlogModel` (from `builder.py`) is an immutable aggregate — no I/O. `emitter.py` performs all file writes with no business logic. `BlogPlugin.on_pre_build()` calls them sequentially. `--apply-nav` flag isolated to `cli.py`. Boundary is clean. | ✅ PASS |
| VI | Simplicity & YAGNI | `BuildWarning` adds necessary operational feedback (missing gitignore, missing nav). `SlugRegistry` collision resolution is a bounded algorithm. Sentinel protocol is required for idempotent canonical-file updates. No RSS, no pagination, no authors, no Jinja2. `--apply-nav` is opt-in and bounded to `mkdocs.yml`. No complexity violations. | ✅ PASS |

**Post-Phase-1 gate: ALL PASS. Phase 1 design is complete.**

## Project Structure

### Documentation (this feature)

```text
specs/001-zensical-blog-module/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── cli.md           # CLI command/flag contract
│   ├── config-schema.md # Config field definitions
│   └── url-routing.md   # Locked URL routing contract
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created here)
```

### Source Code (repository root)

```text
src/
└── zensical_blog/
    ├── __init__.py          # public re-exports; package version
    ├── config.py            # BlogConfig dataclass + loader (toml/yaml/cli)
    ├── discovery.py         # post file discovery (pathlib.Path glob)
    ├── parser.py            # front matter + excerpt parsing (python-frontmatter)
    ├── slugifier.py         # deterministic slug algorithm + SlugRegistry
    ├── models.py            # Post, TaxonomyTerm, ArchivePage, BlogIndex, etc.
    ├── builder.py           # orchestrates model construction (MODEL LAYER — no writes)
    ├── emitter.py           # generates + writes Markdown pages (EMISSION LAYER)
    ├── cli.py               # click CLI: build / clean commands + flags
    └── plugin.py            # Zensical plugin adapter; wires builder+emitter into
                             #   Zensical's pre-build lifecycle hook; registered
                             #   under zensical.plugins entry point; no mkdocs dep

tests/
├── conftest.py              # shared fixtures (tmp_path blog scaffolds)
├── unit/
│   ├── test_config.py
│   ├── test_discovery.py
│   ├── test_parser.py
│   ├── test_slugifier.py
│   ├── test_models.py
│   └── test_emitter.py
└── integration/
    ├── test_build_pipeline.py   # full discover→parse→sort→emit round-trip
    ├── test_override_append.py  # user-authored file preservation
    └── test_clean.py            # clean removes only generated root

pyproject.toml                # [project.entry-points."zensical.plugins"]
                               #   zensical_blog = "zensical_blog.plugin:BlogSidecarPlugin"
README.md
CHANGELOG.md
```

**Structure Decision**: Single-project layout. `src/zensical_blog/` is the
sole package. Tests are co-located at root level in `tests/`. No backend/
frontend split needed — this is a CLI + library package with no web server.

## Complexity Tracking

> No complexity violations in this plan. Table omitted per Principle VI.
