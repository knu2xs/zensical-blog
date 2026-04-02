# Tasks: Zensical Blog Module (Sidecar, Bridge Mode)

**Feature branch**: `001-zensical-blog-module`  
**Date**: 2026-04-01  
**Input**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`  
**Organization**: Tasks grouped by user story for independent implementation and delivery.

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story label — US1–US6 (Setup and Foundational phases have no story label)
- Exact file paths are included in all descriptions

---

## Phase 1: Setup

**Purpose**: Project scaffolding and packaging infrastructure. No user story logic — just the skeleton every other task builds on.

- [X] T001 Create `pyproject.toml` with `[build-system]` (hatchling), `[project]` metadata, runtime deps (`python-frontmatter>=1.1`, `click>=8.1`, `ruamel.yaml>=0.18`), `[project.scripts]` entry point `zensical-blog = "zensical_blog.cli:cli"`, and `[project.entry-points."zensical.plugins"]` entry `zensical_blog = "zensical_blog.plugin:BlogPlugin"` in project root
- [X] T002 [P] Create `src/zensical_blog/__init__.py` with package version constant `__version__ = "0.1.0"` and public re-exports placeholder
- [X] T003 [P] Create `tests/__init__.py` (empty) and `tests/unit/__init__.py` (empty) and `tests/integration/__init__.py` (empty) in `tests/`
- [X] T004 [P] Create `tests/conftest.py` with shared `tmp_path`-based fixtures: `blog_scaffold` (creates `docs/blog/posts/`, `zensical.toml` with `[project.extra.zensical_blog]`) and `make_post` (writes a `.md` file with given front matter + body)
- [X] T005 [P] Create `README.md` with project title, install command (`pip install git+...`), and link to `specs/001-zensical-blog-module/quickstart.md`
- [X] T006 [P] Create `.ruff.toml` (or `[tool.ruff]` section in `pyproject.toml`) enforcing `line-length = 88`, `target-version = "py311"`, `select = ["E", "F", "I", "UP"]`

**Checkpoint**: `pip install -e .` succeeds; `zensical-blog --help` prints usage; `pytest --collect-only` finds test files.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that ALL user stories depend on. No user story can be started until this phase is complete.

**⚠️ CRITICAL**: These tasks MUST complete before any Phase 3+ work begins.

### Config loading (`config.py`)

- [X] T007 Implement `BlogConfig` dataclass in `src/zensical_blog/config.py` with all 15 fields from `data-model.md §1`, type annotations, field defaults, and `generated_root` derived property
- [X] T008 Implement `load_config(config_path: Path | None, docs_dir: Path | None, overrides: dict) -> BlogConfig` in `src/zensical_blog/config.py` — covers TOML path (`tomllib`, key `project.extra.zensical_blog`), YAML compat path (`ruamel.yaml`, key `plugins[].zensical_blog`), priority merge logic (CLI > TOML > YAML > defaults), and auto-detection (search cwd → parent dirs for `zensical.toml` then `mkdocs.yml`)
- [X] T009 [P] Write unit tests for `BlogConfig` construction and validation in `tests/unit/test_config.py`: valid TOML, valid YAML compat, CLI overrides win, missing config fallback to defaults, invalid `drafts` value raises, `generated_root` always inside `docs_dir`

### Slugification (`slugifier.py`)

- [X] T010 Implement `slugify(label: str) -> str` in `src/zensical_blog/slugifier.py` using NFKD normalize → strip combining marks → casefold → `re.sub(r"[^a-z0-9]+" ,"-")` → strip `"-"` → truncate 80 → fallback `"x"` (R-05 algorithm)
- [X] T011 Implement `SlugRegistry` class in `src/zensical_blog/slugifier.py` with `register_label(label, explicit_map) -> str` and collision resolution (sort colliding labels by Unicode code-point; assign `base`, `base-2`, …; accumulate `CollisionWarning`)
- [X] T012 [P] Write unit tests for `slugify` and `SlugRegistry` in `tests/unit/test_slugifier.py`: ASCII, accented chars, `"C#"` → `"c"`, `"C sharp"` → `"c-2"` collision, explicit map override, `"x"` empty fallback, max-80-char truncation, post slug derivation priority (front matter > filename-date-strip > slugify)

### Post parsing (`parser.py`)

- [X] T013 Implement `parse_post(path: Path) -> RawPost` in `src/zensical_blog/parser.py` using `frontmatter.load(path)` → `RawPost(source_path, raw_metadata, raw_content)`
- [X] T014 Implement `extract_excerpt(raw_content: str, marker: str, fallback: Literal["first_paragraph"]) -> str` in `src/zensical_blog/parser.py`: split on first `marker` occurrence → if absent → extract first paragraph (up to first blank line) → fallback to first 200 chars
- [X] T015 [P] Write unit tests for `parse_post` and `extract_excerpt` in `tests/unit/test_parser.py`: file with YAML front matter, file with no front matter, `<!-- more -->` split, first-paragraph fallback, 200-char fallback, `draft: true` flag propagation

### Models (`models.py`)

- [X] T016 Implement `Post`, `TaxonomyTerm`, `ArchivePeriod`, `BlogModel`, `BuildWarning` dataclasses in `src/zensical_blog/models.py` per `data-model.md` with full type annotations, `Post.sort_key` property, `BlogModel` immutability (all tuple fields), and `DraftPostError` exception
- [X] T017 [P] Write unit tests for all model constructors and `Post.sort_key` ordering in `tests/unit/test_models.py`: sort_key descending-date ordering, TaxonomyTerm, ArchivePeriod, BlogModel constructs without error

### File discovery (`discovery.py`)

- [X] T018 Implement `discover_posts(posts_dir: Path) -> list[Path]` in `src/zensical_blog/discovery.py` using `pathlib.Path.rglob("*.md")` sorted by path for determinism; return empty list (not error) when directory does not exist
- [X] T019 [P] Write unit tests for `discover_posts` in `tests/unit/test_discovery.py`: empty dir, single post, nested posts, non-`.md` files ignored, deterministic order

**Checkpoint**: All Phase 2 unit tests pass (`pytest tests/unit/`). `BlogConfig`, `SlugRegistry`, `parse_post`, all model classes, and `discover_posts` are importable. No user-story features yet.

---

## Phase 3: User Story 1 — Post Authoring & Blog Index Generation (Priority: P1) 🎯 MVP

**Goal**: Ingest posts from `docs/blog/posts/`, sort by date descending, generate a blog index listing at `docs/blog/index.md` (appended if file already exists, preserving user content via sentinel protocol).

**Independent Test**: Create two posts with different dates. Run `zensical-blog build`. Verify `docs/blog/index.md` (or its sentinel block) lists both posts newest-first. Run a second time — verify the sentinel block is replaced, not duplicated.

### Implementation

- [X] T020 [US1] Implement `build_blog_model(config: BlogConfig) -> BlogModel` in `src/zensical_blog/builder.py` (MODEL LAYER — no file writes): calls `discover_posts` → `parse_post` on each → resolve `Post` fields (title from front matter / H1 / filename; slug via `SlugRegistry`; excerpt via `extract_excerpt`; draft flag) → filter by `config.drafts` → sort by `post.sort_key` → raise `DraftPostError` if `drafts="fail"` and drafts exist → return `BlogModel` with `posts`, `draft_posts`, `archives`, `tags`, `categories`, `warnings`
- [X] T021 [US1] Implement sentinel protocol helper `apply_sentinel(file_path: Path, generated_block: str) -> None` in `src/zensical_blog/emitter.py`: read existing file → if sentinel markers present, replace between them; if absent, append blank line + full sentinel block; write only if content changed (byte-for-byte equality check)
- [X] T022 [US1] Implement `emit_blog_index(model: BlogModel) -> None` in `src/zensical_blog/emitter.py` (EMISSION LAYER — no business logic): generate `latest.md` under `docs/.bloggen/<blog_dir>/lists/` listing all `model.posts` with title, date, excerpt, and link; call `apply_sentinel` on canonical `docs/<blog_dir>/index.md`
- [X] T023 [US1] Implement `emit_all(model: BlogModel) -> None` in `src/zensical_blog/emitter.py` as the top-level emission orchestrator: creates `docs/.bloggen/` root; calls all emitter functions (starting with `emit_blog_index`; others wired in later phases)
- [X] T024 [P] [US1] Write integration test for full pipeline in `tests/integration/test_build_pipeline.py`: two-post scaffold with different dates → `build_blog_model` + `emit_all` → assert `docs/blog/index.md` sentinel block lists both posts newest-first; re-run and assert no duplicate sentinel
- [X] T025 [P] [US1] Write integration test for draft filtering in `tests/integration/test_build_pipeline.py`: post with `draft: true`, config `drafts="hide"` → draft absent from index; config `drafts="show"` → draft present; config `drafts="fail"` + draft → `DraftPostError` raised
- [X] T026 [P] [US1] Write integration test for canonical override in `tests/integration/test_override_append.py`: user-authored `docs/blog/index.md` with custom preamble → build → custom preamble preserved, sentinel block appended; second build → preamble preserved, no duplication

**Checkpoint**: `zensical-blog build` on a minimal scaffold generates `docs/blog/index.md` with posts sorted newest-first. Draft logic works. Sentinel idempotency verified. US1 is shippable as MVP.

---

## Phase 4: User Story 2 — Yearly Archive Pages (Priority: P2)

**Goal**: Generate `docs/blog/archive/index.md` (landing listing all years) and `docs/blog/archive/<year>.md` (per-year post listing) for all years present in the post corpus.

**Independent Test**: Posts spanning 2025 and 2026 → build → `docs/blog/archive/index.md` links both years; `docs/blog/archive/2025.md` lists only 2025 posts, `docs/blog/archive/2026.md` lists only 2026 posts.

### Implementation

- [X] T027 [US2] Extend `build_blog_model` in `src/zensical_blog/builder.py` to populate `model.archives`: group `model.posts` by year into `ArchivePeriod` tuples, sorted descending by year; respect `config.enable_archive_landing`
- [X] T028 [US2] Implement `emit_archive_landing(model: BlogModel) -> None` in `src/zensical_blog/emitter.py`: generate `docs/.bloggen/<blog_dir>/archive/index.generated.md` listing all years with links; call `apply_sentinel` on canonical `docs/<blog_dir>/archive/index.md`
- [X] T029 [US2] Implement `emit_archive_year(model: BlogModel, period: ArchivePeriod) -> None` in `src/zensical_blog/emitter.py`: generate `docs/.bloggen/<blog_dir>/archive/<year>.generated.md` listing posts for that year; call `apply_sentinel` on canonical `docs/<blog_dir>/archive/<year>.md`
- [X] T030 [US2] Wire `emit_archive_landing` and `emit_archive_year` (for all periods) into `emit_all` in `src/zensical_blog/emitter.py`
- [X] T031 [P] [US2] Write integration test in `tests/integration/test_build_pipeline.py`: posts with 2025 and 2026 dates → build → assert archive landing lists both years; year files list only correct posts; user-authored 2026 archive preserved via sentinel

**Checkpoint**: `zensical-blog build` generates working archive landing + per-year pages. US1 and US2 both independently testable.

---

## Phase 5: User Story 3 — Tag & Category Landing Pages (Priority: P3)

**Goal**: Generate `docs/blog/tag/index.md`, per-tag `docs/blog/tag/<slug>.md`, `docs/blog/category/index.md`, and per-category `docs/blog/category/<slug>.md` pages. Slug collision emits a warning but does not fail the build.

**Independent Test**: Posts with tags `data-engineering` and `how-to` → build → tag landing lists both; each tag page lists correctly tagged posts. Slug collision for `"C#"` / `"C sharp"` → warning emitted, both pages generated.

### Implementation

- [X] T032 [US3] Extend `build_blog_model` in `src/zensical_blog/builder.py` to populate `model.tags` and `model.categories`: iterate `model.posts`, collect unique labels, resolve slugs via `SlugRegistry` (with `config.tag_slug_map`/ `category_slug_map`), accumulate collision warnings into `model.warnings`; respect `config.enable_tags` / `config.enable_categories`
- [X] T033 [P] [US3] Implement `emit_tags_landing(model: BlogModel) -> None` in `src/zensical_blog/emitter.py`: generate `docs/.bloggen/<blog_dir>/tag/index.generated.md` listing all tags with post counts and links; call `apply_sentinel` on canonical `docs/<blog_dir>/tag/index.md`
- [X] T034 [P] [US3] Implement `emit_tag_page(model: BlogModel, term: TaxonomyTerm) -> None` in `src/zensical_blog/emitter.py`: generate `docs/.bloggen/<blog_dir>/tag/<slug>.generated.md` listing posts for this tag; call `apply_sentinel` on canonical `docs/<blog_dir>/tag/<slug>.md`
- [X] T035 [P] [US3] Implement `emit_categories_landing(model: BlogModel) -> None` in `src/zensical_blog/emitter.py` — mirror of `emit_tags_landing` for categories; canonical at `docs/<blog_dir>/category/index.md`
- [X] T036 [P] [US3] Implement `emit_category_page(model: BlogModel, term: TaxonomyTerm) -> None` in `src/zensical_blog/emitter.py` — mirror of `emit_tag_page` for categories
- [X] T037 [US3] Wire tag + category emitters into `emit_all` in `src/zensical_blog/emitter.py`
- [X] T038 [P] [US3] Write integration test for tags + categories in `tests/integration/test_build_pipeline.py`: posts with `tags: [data-engineering, how-to]` and `categories: [tutorials]` → build → assert landing pages list correct terms; per-term pages list correct posts; `enable_tags=False` suppresses tag pages
- [X] T039 [P] [US3] Write unit test for slug collision in `tests/unit/test_slugifier.py` (extend existing): `"C#"` and `"C sharp"` in same registry → collision assigns `"c"` and `"c-2"`, `CollisionWarning` recorded

**Checkpoint**: Full taxonomy pages generated. All warnings surface on slug collision. US1, US2, US3 independently testable.

---

## Phase 6: User Story 4 — Slug & Excerpt Control (Priority: P4)

**Goal**: `slug` front matter field overrides auto-derived slug; `<!-- more -->` marker controls excerpt; first-paragraph fallback when marker absent.

**Independent Test**: Post with `slug: my-custom-slug` → build → generated link uses `/blog/my-custom-slug/`. Post with `<!-- more -->` → excerpt is exactly the pre-marker content. Post without marker → excerpt is first paragraph.

### Implementation

- [X] T040 [US4] Extend post-slug resolution in `src/zensical_blog/builder.py` (within `build_blog_model`): priority — front-matter `slug` (verbatim, validate `[a-z0-9][a-z0-9-]*`) → filename date-strip → `slugify(stem)` → post-slug collision handling in `SlugRegistry`; emit `BuildWarning` for invalid explicit slug (fall back to algorithm)
- [X] T041 [US4] Verify `extract_excerpt` in `src/zensical_blog/parser.py` satisfies both marker and first-paragraph contracts (implementation already done in T014; this task validates against US4 acceptance scenarios with targeted tests)
- [X] T042 [P] [US4] Write focused unit tests in `tests/unit/test_parser.py` (extend): `slug` front matter → correct `Post.slug`; invalid slug chars in front matter → warning + algorithm fallback; post-slug collision → `slug-2` assigned; `<!-- more -->` exact split; first-paragraph fallback; 200-char fallback

**Checkpoint**: Slug overrides work end-to-end. Excerpt strategy contracts verified. US4 independently testable with existing build pipeline.

---

## Phase 7: User Story 5 — Nav Assurance & CLI Interface (Priority: P5)

**Goal**: `zensical-blog build` and `zensical-blog clean` work from the command line. Auto-detect `zensical.toml` / `mkdocs.yml`. Emit nav warning when Blog entry absent. `--apply-nav` patches `mkdocs.yml` non-destructively.

**Independent Test**: `zensical-blog build` on a `zensical.toml` scaffold → generated files in `docs/.bloggen/`. `zensical-blog clean` → `docs/.bloggen/` fully removed, no other files touched.

### Implementation

- [X] T043 [US5] Implement `zensical-blog build` command in `src/zensical_blog/cli.py` with all four flags (`--config`, `--docs-dir`, `--apply-nav`, `--fail-on-warnings`) per `contracts/cli.md`: resolve `BlogConfig` → `build_blog_model` → `emit_all` → emit warnings to `stderr` → `--fail-on-warnings` → `--apply-nav` nav patch → exit codes
- [X] T044 [US5] Implement `zensical-blog clean` command in `src/zensical_blog/cli.py` per `contracts/cli.md`: resolve `generated_root` → safety assert (`generated_root` is inside `docs_dir`) → `shutil.rmtree` → exit 0 (idempotent if not exists)
- [X] T045 [US5] Implement nav assurance in `src/zensical_blog/emitter.py` (called from `emit_all`): check `mkdocs.yml` nav for `BlogConfig.nav_label → nav_path` entry; emit `BuildWarning(code="MISSING_NAV_ENTRY", ...)` if absent; no-op when nav present
- [X] T046 [US5] Implement `--apply-nav` nav patching in `src/zensical_blog/cli.py`: load `mkdocs.yml` with `ruamel.yaml` round-trip; insert `{nav_label: nav_path}` as first nav entry if absent; write back preserving comments; emit warning and skip if config source is not `mkdocs.yml`
- [X] T047 [US5] Implement `.gitignore` advisory check in `src/zensical_blog/builder.py`: scan project root `.gitignore` for `docs/.bloggen/` pattern; if absent emit `BuildWarning(code="MISSING_GITIGNORE", ...)`
- [X] T048 [P] [US5] Write integration test for CLI `build` command in `tests/integration/test_build_pipeline.py`: use `click.testing.CliRunner` to invoke `build`; assert exit code 0; assert generated files exist; assert `--fail-on-warnings` returns exit code 1 when warnings present
- [X] T049 [P] [US5] Write integration test for CLI `clean` command in `tests/integration/test_clean.py`: scaffold with generated root → `clean` → dir removed; run again → idempotent exit 0; assert no files outside `docs/.bloggen/` are touched

**Checkpoint**: `zensical-blog build` and `zensical-blog clean` work as documented in `contracts/cli.md`. US5 independently testable.

---

## Phase 8: User Story 6 — Zensical Plugin Integration (Priority: P6, MANDATORY)

**Goal**: Implement the `BlogPlugin` adapter under the `zensical.plugins` entry point. In bridge mode, `on_pre_build()` delegates to `builder` + `emitter`. The plugin is forward-compatible with Zensical's future module API; no `mkdocs` import anywhere.

**Independent Test**: Confirm `zensical_blog.plugin:BlogPlugin` is importable and its `on_pre_build` method calls `build_blog_model` + `emit_all`. Confirm `mkdocs` is NOT in `sys.modules` after import. Entry point is registered correctly in `pyproject.toml`.

### Implementation

- [X] T050 [US6] Implement `BlogPlugin` class in `src/zensical_blog/plugin.py`: `on_pre_build(config: dict | None = None) -> None` loads `BlogConfig` (from passed config or auto-detect), calls `build_blog_model`, calls `emit_all`; `on_post_build(config: dict | None = None) -> None` checks nav assurance; no `mkdocs` import at any level; class does NOT subclass any external base class (per FR-032)
- [X] T051 [US6] Update `src/zensical_blog/__init__.py` to export `BlogPlugin` in the public API
- [X] T052 [P] [US6] Write unit test for `BlogPlugin` in `tests/unit/` (new file `tests/unit/test_plugin.py`): import `BlogPlugin` → assert `mkdocs` NOT in `sys.modules`; call `on_pre_build` with a `tmp_path` scaffold → blog index generated; verify entry point key `zensical_blog` maps to `zensical_blog.plugin:BlogPlugin` via `importlib.metadata.entry_points`

**Checkpoint**: Plugin registered and importable. `on_pre_build` drives the full build pipeline. No `mkdocs` dependency. US6 complete.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Finalise packaging, docs, and verification against quickstart.

- [X] T053 [P] Add `[project.optional-dependencies]` `dev` group in `pyproject.toml`: `pytest>=8`, `ruff>=0.4`, and `python-frontmatter` already in core deps; verify `pip install -e ".[dev]"` installs test tooling
- [X] T054 [P] Update `src/zensical_blog/__init__.py` public re-exports: `BlogConfig`, `BlogModel`, `BlogPlugin`, `build_blog_model`, `emit_all`
- [X] T055 [P] Run `ruff check src/ tests/` and fix all linting errors across all source and test files
- [X] T056 Run full test suite (`pytest`) and confirm all tests pass with exit code 0
- [X] T057 Validate `quickstart.md` end-to-end: follow steps 1–8 in `specs/001-zensical-blog-module/quickstart.md` against a real `tmp_path` scaffold; confirm all generated paths and outputs match documented expectations
- [X] T058 [P] Create `CHANGELOG.md` with `## [0.1.0] - 2026-04-01` entry listing all user stories delivered

**Checkpoint**: `pip install -e .[dev] && pytest && ruff check src/ tests/` — all green. Quickstart verified. Package ready for `pip install git+...`.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)       ──► no dependencies; start immediately
Phase 2 (Foundational) ──► requires Phase 1; BLOCKS phases 3–9
Phase 3 (US1 / P1)   ──► requires Phase 2; no inter-story deps
Phase 4 (US2 / P2)   ──► requires Phase 2; no inter-story deps
Phase 5 (US3 / P3)   ──► requires Phase 2; no inter-story deps
Phase 6 (US4 / P4)   ──► requires Phase 2; builds on builder.py from Phase 3
Phase 7 (US5 / P5)   ──► requires Phases 3–6 complete (CLI wraps all generation)
Phase 8 (US6 / P6)   ──► requires Phase 7 complete (plugin wraps CLI logic)
Phase 9 (Polish)     ──► requires all user story phases complete
```

### User Story Dependencies

| Story | Depends on | Independently testable? |
|-------|-----------|------------------------|
| US1 (P1) | Foundational (Phase 2) | ✅ Yes — core pipeline |
| US2 (P2) | Foundational + builder.py from US1 | ✅ Yes — separate archive emitters |
| US3 (P3) | Foundational + builder.py from US1 | ✅ Yes — separate taxonomy emitters |
| US4 (P4) | Foundational + slug/excerpt from US1 | ✅ Yes — targeted unit tests |
| US5 (P5) | US1–US4 complete | ✅ Yes — CLI wraps complete pipeline |
| US6 (P6) | US5 complete | ✅ Yes — plugin is a thin adapter |

### Parallel Opportunities Within Phases

**Phase 1**: T002–T006 all parallelisable (different files, no deps).  
**Phase 2**: T009, T012, T015, T017, T019 are unit-test tasks, all parallelisable; T007 must precede T008; T010 must precede T011.  
**Phase 3**: T024–T026 (tests) parallelisable after T020–T023.  
**Phase 5**: T033–T036 (per-taxonomy emitters) all parallelisable.  
**Phase 9**: T053–T055 + T058 all parallelisable.

---

## Parallel Execution Example: User Story 1 (Phase 3)

```
[T020]  build_blog_model skeleton
    └──► [T021] sentinel protocol in emitter.py
    └──► [T022] emit_blog_index
            └──► [T023] emit_all orchestrator
                    └──► [T024] integration: pipeline test  ──┐
                    └──► [T025] integration: draft test     ──┼── all parallelisable
                    └──► [T026] integration: override test  ──┘
```

---

## Implementation Strategy

**MVP scope (Phase 1 + Phase 2 + Phase 3 only)**:  
Install, configure, and run `zensical-blog build` to get a working blog index. Covers the core deliverable (US1) without taxonomy or archive pages. Shippable after T001–T026.

**Incremental delivery order**:
1. T001–T006 — scaffolding
2. T007–T019 — foundational models and utilities (all unit-tested)
3. T020–T026 — blog index + sentinel protocol (US1 MVP)
4. T027–T031 — archive pages (US2)
5. T032–T039 — taxonomy pages (US3)
6. T040–T042 — slug + excerpt control (US4)
7. T043–T049 — CLI interface + nav assurance (US5)
8. T050–T052 — plugin adapter (US6)
9. T053–T058 — polish + verification

**Total task count**: 58 tasks  
**Tasks per user story**:

| Phase | Story | Tasks |
|-------|-------|-------|
| Phase 1 | Setup | T001–T006 (6 tasks) |
| Phase 2 | Foundational | T007–T019 (13 tasks) |
| Phase 3 | US1 (P1) | T020–T026 (7 tasks) |
| Phase 4 | US2 (P2) | T027–T031 (5 tasks) |
| Phase 5 | US3 (P3) | T032–T039 (8 tasks) |
| Phase 6 | US4 (P4) | T040–T042 (3 tasks) |
| Phase 7 | US5 (P5) | T043–T049 (7 tasks) |
| Phase 8 | US6 (P6) | T050–T052 (3 tasks) |
| Phase 9 | Polish | T053–T058 (6 tasks) |

**Parallel opportunities identified**: 28 tasks marked `[P]` (48% of total).
