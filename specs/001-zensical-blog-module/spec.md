# Feature Specification: Zensical Blog Module (Sidecar, Bridge Mode)

**Feature Branch**: `001-zensical-blog-module`  
**Created**: 2026-04-01  
**Status**: Draft  
**Input**: Build a zensical-blog module using `references/specification.md` with clarification in `references/page_map_naming_conventions.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Post Authoring & Blog Index Generation (Priority: P1)

A docs maintainer drops Markdown files into `docs/blog/posts/`. When they run
`zensical-blog build`, the module generates a blog index at `docs/blog/index.md`
(or appends a post listing if the file already exists) without requiring the
maintainer to add individual posts to their `mkdocs.yml` nav.

**Why this priority**: This is the core deliverable — without it nothing else
has value. It proves the module can ingest posts, sort them by date, and produce
a navigable index. It is a complete, shippable increment on its own.

**Independent Test**: Create a project with two posts that have different dates.
Run `zensical-blog build`. Verify `docs/blog/index.md` (or the append block)
lists both posts in descending date order and that neither post appears in nav.

**Acceptance Scenarios**:

1. **Given** a `docs/blog/posts/` directory with two `.md` files each containing
   a `date` front-matter field, **When** `zensical-blog build` is run,
   **Then** both posts appear on the blog index page in newest-first order.

2. **Given** a manually authored `docs/blog/index.md` with custom introductory
   content, **When** `zensical-blog build` is run, **Then** the custom content
   is preserved and the generated post listing is appended after it.

3. **Given** a post with `draft: true`, **When** `zensical-blog build` is run
   with the default config (`drafts = "hide"`), **Then** the draft post does
   not appear on the blog index.

4. **Given** config with `drafts = "show"`, **When** `zensical-blog build` is
   run, **Then** draft posts appear on the blog index.

---

### User Story 2 - Yearly Archive Pages (Priority: P2)

A reader can browse all posts from a given year via a stable, bookmarkable
archive URL (e.g., `/blog/archive/2026/`). An archive landing page at
`/blog/archive/` lists all years for which posts exist.

**Why this priority**: Archives are the primary long-form navigation pattern
for blog content. They are explicitly locked in as the default granularity.
Yearly grouping is a simple, high-value deliverable independent of
tags/categories.

**Independent Test**: Publish posts with dates in two different years. Run
`zensical-blog build`. Verify the archive landing lists both years and each
year page lists only its posts.

**Acceptance Scenarios**:

1. **Given** posts with dates spanning 2025 and 2026, **When** `zensical-blog
   build` is run, **Then** `docs/blog/archive/2025.md` and
   `docs/blog/archive/2026.md` are generated (or append blocks created in
   user-authored files), each containing only posts from that year.

2. **Given** an existing user-authored `docs/blog/archive/2026.md`, **When**
   `zensical-blog build` is run, **Then** the user's custom content is
   preserved and the generated post list is appended.

3. **Given** the archive landing page at `docs/blog/archive/index.md`, **When**
   `zensical-blog build` is run, **Then** both year pages are linked from the
   landing.

---

### User Story 3 - Tag & Category Landing Pages (Priority: P3)

A reader can reach a tags landing page (`/blog/tag/`) from the blog index,
browse all tags, click through to a per-tag page, and see all posts with that
tag. The same flow applies to categories (`/blog/category/`).

**Why this priority**: Taxonomy navigation (tags & categories) is the second
most important discovery mechanism and is directly linked from the blog index
per the specification. It depends on User Story 1 (posts must exist) so is
sequenced after P1 and P2.

**Independent Test**: Create posts tagged with `data-engineering` and
`how-to`. Run `zensical-blog build`. Verify tag landing page lists both tags,
each linking to a page that lists only the correctly tagged posts.

**Acceptance Scenarios**:

1. **Given** posts with `tags: [data-engineering, how-to]`, **When**
   `zensical-blog build` is run, **Then** `docs/blog/tag/data-engineering.md`
   and `docs/blog/tag/how-to.md` are generated listing the correct posts.

2. **Given** the blog index page, **When** it is rendered, **Then** it contains
   links to both the tags landing page and the categories landing page.

3. **Given** posts with `categories: [tutorials]`, **When** `zensical-blog
   build` is run, **Then** `docs/blog/category/tutorials.md` is generated.

4. **Given** two labels that slugify to the same base slug (e.g., `"C#"` and
   `"C sharp"`), **When** `zensical-blog build` is run, **Then** the module
   emits a warning listing both labels and their assigned slugs (`c` and `c-2`)
   and generation continues without failure.

---

### User Story 4 - Slug & Excerpt Control (Priority: P4)

A maintainer can override the auto-generated URL slug for a post via `slug`
in front matter. Excerpts are controlled by the `<!-- more -->` marker; when
absent, the first paragraph is used as the fallback.

**Why this priority**: Slug overrides are essential for migration compatibility
(MkDocs blog plugin parity) and are independent of archives and taxonomy.
Excerpt control is closely related and small in scope.

**Independent Test**: Add `slug: my-custom-slug` to a post front matter. Run
`zensical-blog build`. Verify the generated post link uses `/blog/my-custom-slug/`.

**Acceptance Scenarios**:

1. **Given** a post with `slug: my-custom-slug`, **When** `zensical-blog build`
   is run, **Then** the post URL is `/blog/my-custom-slug/` regardless of
   the source filename.

2. **Given** a post body containing `<!-- more -->`, **When** the blog index
   is generated, **Then** the excerpt shown is exactly the content before the
   `<!-- more -->` marker.

3. **Given** a post body with no `<!-- more -->` marker, **When** the blog
   index is generated, **Then** the excerpt shown is the first paragraph of
   the post.

---

### User Story 5 - Nav Assurance & CLI Interface (Priority: P5)

A maintainer can run `zensical-blog build` and `zensical-blog clean` from the
command line. The CLI auto-detects configuration from `zensical.toml` or
`mkdocs.yml`. If the nav already contains `Blog: blog/index.md`, the module
leaves it untouched; if not, it emits a warning. With `--apply-nav`, it
patches the nav non-destructively.

**Why this priority**: The CLI is the primary user-facing interface but depends
on the generation logic (US1–US4) being in place first.

**Independent Test**: Run `zensical-blog build` on a project with a
`zensical.toml` containing `[project.extra.zensical_blog]`. Verify generated
files appear in `docs/.bloggen/`. Run `zensical-blog clean`. Verify the
generated root is fully removed.

**Acceptance Scenarios**:

1. **Given** a project with `zensical.toml`, **When** `zensical-blog build` is
   run without `--config`, **Then** the module auto-detects and reads
   `zensical.toml`.

2. **Given** a `mkdocs.yml` with `blog/index.md` already in nav, **When**
   `zensical-blog build` is run, **Then** nav is unchanged and no warning is
   emitted about nav.

3. **Given** a `mkdocs.yml` without a Blog entry, **When** `zensical-blog build`
   is run, **Then** the module emits a warning explaining the required nav entry.

4. **Given** `--apply-nav` flag, **When** `zensical-blog build` is run on a
   project whose nav lacks a Blog entry, **Then** `Blog: blog/index.md` is
   added to the nav as a top-level entry.

5. **Given** previously generated files in `docs/.bloggen/`, **When**
   `zensical-blog clean` is run, **Then** all files under `docs/.bloggen/` are
   removed and no files outside that directory are touched.

---

### User Story 6 - Zensical Plugin Integration — MANDATORY (Priority: P6)

A maintainer configures the module entirely in `zensical.toml` under
`[project.extra.zensical_blog]` and has the blog generation pipeline run
**automatically** as part of `zensical build` — with no separate
`zensical-blog build` step required. The module is designed as a
first-class Zensical plugin; in bridge mode (while Zensical's public plugin
API is unreleased), the standalone CLI is the invocation path, but the
plugin registration and config contract are forward-compatible with
Zensical's future module system.

**Why this priority**: `zensical.toml` is Zensical's primary project
configuration file and the correct home for all module settings. Without
seamless `zensical build` integration, users must remember a separate CLI
step before every build — error-prone and inconsistent with how Zensical
modules are intended to work. §6.1 of `references/specification.md`
explicitly makes `zensical.toml` under `[project.extra.zensical_blog]` the
recommended (Zensical-forward) configuration source.

**Independent Test**: Configure `[project.extra.zensical_blog]` in
`zensical.toml` with a populated `docs/blog/posts/` directory. Run
`zensical build` (relying on the registered Zensical plugin hook). Verify
that all blog pages are generated without a prior `zensical-blog build`
invocation.

**Acceptance Scenarios**:

1. **Given** `[project.extra.zensical_blog]` in `zensical.toml` with
   `blog_dir = "blog"`, **When** `zensical build` is run, **Then** the full
   generation pipeline (discover → parse → sort → emit) completes
   automatically and all blog pages appear in the site output.

2. **Given** only a `zensical.toml` (no `mkdocs.yml`), **When** the module
   resolves its configuration, **Then** all settings are sourced exclusively
   from `[project.extra.zensical_blog]` with no fallback errors.

3. **Given** plugin configuration with `drafts = "fail"` and a draft post
   present, **When** `zensical build` is run, **Then** the build exits
   non-zero and emits a clear error message identifying the draft post.

4. **Given** the module is active and `docs/blog/posts/` does not exist,
   **When** `zensical build` is run, **Then** the plugin emits a clear error
   and the build exits non-zero (matching standalone CLI behaviour).

---

### Edge Cases

- A post with no `date` front-matter field: module emits a warning and skips
  the post (does not fail the build by default).
- Two posts produce the same computed slug (from filename): resolve conflict by
  appending `-2`, `-3`, etc. and emit a warning.
- The `docs/blog/posts/` directory does not exist: module emits an error and
  exits non-zero.
- The generated root (`docs/.bloggen/`) is not in `.gitignore`: module emits a
  warning suggesting users add it.
- `blog_dir` is set to a path that does not exist: module creates it on first
  build.
- A tag label after slugification exceeds 80 characters: truncated at 80 chars
  with trailing `-` stripped, and a warning is emitted.
- Config source priority conflict (both `zensical.toml` and `mkdocs.yml`
  present): `zensical.toml` wins; a debug message is logged.
- Standalone CLI invoked manually while a `zensical build` is also running
  (e.g., in a watch loop): the plugin takes precedence; the standalone CLI
  run is a no-op if generated files are already up to date (FR-022 guards this).

## Requirements *(mandatory)*

### Functional Requirements

**Post Discovery & Processing**

- **FR-001**: The module MUST discover all `.md` files recursively under
  `posts_dir` (default `blog/posts`) and treat each as a blog post.
- **FR-002**: The module MUST parse YAML front matter from each post, extracting
  `date`, `draft`, `tags`, `categories`, `slug`, and `title` fields.
- **FR-003**: Posts with `draft: true` MUST be hidden from all generated pages
  when `drafts = "hide"` (default), visible when `drafts = "show"`, and cause
  a non-zero exit when `drafts = "fail"`.
- **FR-004**: Posts MUST be sorted in descending `date` order on all listing
  pages by default.
- **FR-005**: A post's URL slug MUST be computed from the source filename
  (stripped of date prefix if present) unless a `slug` front-matter field
  is provided, which overrides it entirely.

**Excerpt Extraction**

- **FR-006**: The module MUST extract the content before the first occurrence
  of `<!-- more -->` (configurable via `excerpt_marker`) as the post excerpt.
- **FR-007**: When the excerpt marker is absent, the module MUST fall back to
  the first paragraph of the post body as the excerpt (configurable via
  `excerpt_fallback = "first_paragraph"`).

**Page Generation — Index**

- **FR-008**: The module MUST write (or append to) `docs/<blog_dir>/index.md`
  with a listing of all non-draft posts including title, date, and excerpt.
- **FR-009**: The blog index MUST contain links to the tags landing page and
  the categories landing page.

**Page Generation — Archives**

- **FR-010**: The module MUST group posts by year and generate one page per
  year at canonical path `docs/<blog_dir>/archive/<year>.md`.
- **FR-011**: An archive landing page MUST be generated at
  `docs/<blog_dir>/archive/index.md` listing all years.

**Page Generation — Tags**

- **FR-012**: The module MUST generate a tags landing page at
  `docs/<blog_dir>/tag/index.md` listing all active tags (with post counts).
- **FR-013**: The module MUST generate one page per tag at
  `docs/<blog_dir>/tag/<tag_slug>.md` listing posts with that tag.

**Page Generation — Categories**

- **FR-014**: The module MUST generate a categories landing page at
  `docs/<blog_dir>/category/index.md` listing all active categories.
- **FR-015**: The module MUST generate one page per category at
  `docs/<blog_dir>/category/<category_slug>.md` listing posts in that category.

**Override Semantics**

- **FR-016**: When a user has authored a file at a canonical override path (any
  of the paths listed in §2.1 of `page_map_naming_conventions.md`), the module
  MUST preserve the user's content and APPEND the generated listing after it.
  The user's content MUST NOT be modified.

**Slugification**

- **FR-017**: Tag and category slugs MUST be computed using the deterministic
  algorithm: NFKD normalize → strip diacritics → lowercase → replace
  non-`[a-z0-9]` runs with `-` → collapse `-` → trim `-` → max 80 chars.
- **FR-018**: When two labels produce the same base slug, the module MUST assign
  the first label (by Unicode code-point sort order) the base slug, and
  subsequent labels `<base>-2`, `<base>-3`, etc., and MUST emit a warning.
- **FR-019**: The optional `tag_slug_map` and `category_slug_map` config fields
  MUST override the computed slug for any listed label, enabling maintainers to
  lock a slug even if the display label changes.

**Output Safety & Determinism**

- **FR-020**: The module MUST write generated artifacts ONLY under
  `docs/.bloggen/` (configurable generated root). No file outside this
  boundary and outside explicit user-authored override files MUST be written
  without an opt-in flag.
- **FR-021**: Given identical input (post content + config), all generated
  outputs MUST be byte-for-byte identical across runs (deterministic).
- **FR-022**: The module MUST NOT rewrite a generated file when the new content
  is unchanged (supports stable diffs and efficient incremental builds).

**Navigation Assurance**

- **FR-023**: When nav is defined and already contains `Blog: blog/index.md`,
  the module MUST leave nav untouched.
- **FR-024**: When nav is defined and does not contain a Blog entry, the module
  MUST emit a human-readable warning explaining the required nav entry.
- **FR-025**: When `--apply-nav` is passed, the module MUST add
  `Blog: blog/index.md` as a top-level nav entry (non-destructively, no
  other nav entries affected).

**Configuration**

- **FR-026**: Config MUST be read, in priority order, from: (1)
  `[project.extra.zensical_blog]` in `zensical.toml` — **primary source**;
  (2) the `zensical_blog` entry under `plugins:` in `mkdocs.yml` — secondary,
  for compatibility with projects that have not yet migrated to
  `zensical.toml`; (3) CLI flags — override both. When `zensical.toml` is
  present, the `mkdocs.yml` plugin block is ignored and a debug message is
  logged. Reading from `mkdocs.yml` requires only YAML parsing — the `mkdocs`
  package MUST NOT be imported.
- **FR-027**: The module MUST support config fields: `blog_dir`, `posts_dir`,
  `archives`, `pagination`, `excerpt_marker`, `excerpt_fallback`, `drafts`,
  `nav_label`, `nav_path`, `enable_tags`, `enable_categories`,
  `enable_archive_landing`, `tag_slug_map`, `category_slug_map`.

**CLI**

- **FR-028**: The module MUST provide a `build` command that runs the full
  generation pipeline and exits 0 on success, non-zero on error.
- **FR-029**: The module MUST provide a `clean` command that removes all files
  exclusively under the generated root and exits 0.
- **FR-030**: The CLI MUST accept `--config`, `--docs-dir`, `--apply-nav`, and
  `--fail-on-warnings` flags.

**Packaging**

- **FR-031**: The module MUST be installable via
  `pip install git+https://github.com/<org>/zensical-blog.git` using only the
  `pyproject.toml`; no extra setup steps are required.

**Zensical Plugin Integration — MANDATORY**

- **FR-032**: The module MUST register itself as a Zensical plugin under the
  `zensical.plugins` entry point (key `zensical_blog`) in `pyproject.toml`.
  This registration is forward-compatible with Zensical's future public
  module API. The `plugin.py` adapter MUST expose the lifecycle hooks that
  Zensical's module system will call (e.g., a pre-build stage equivalent to
  `on_files`) so that adopting the public API requires only updating the
  adapter — not the model or emission layers. The `mkdocs` package MUST NOT
  be a dependency; the adapter MUST NOT subclass `mkdocs.plugins.BasePlugin`.
- **FR-033**: All `[project.extra.zensical_blog]` fields defined in §6.3 of
  `references/specification.md` MUST be configurable directly in
  `zensical.toml` without any `mkdocs.yml` present. The config loader MUST
  produce an identical `BlogConfig` object regardless of whether the source
  is `zensical.toml`, `mkdocs.yml` (compatibility), or CLI flags.

### Key Entities

- **Post**: A single blog entry. Attributes: `source_path`, `title`, `date`,
  `draft`, `tags` (list), `categories` (list), `slug`, `excerpt`, `body`.
  Slug is computed or overridden. Relationship: belongs to one or more
  yearly archives, zero or more tags, zero or more categories.

- **BlogIndex**: The top-level blog listing page. Contains an ordered list of
  Post excerpts. One per site.

- **ArchivePage**: A listing page scoped to a single year. Contains all Posts
  for that year in descending date order.

- **TaxonomyTerm**: A single tag or category label with its canonical slug,
  display label, and the list of Posts associated with it.

- **TaxonomyLanding**: A listing page for all terms in one taxonomy (tags or
  categories). One per taxonomy.

- **BlogConfig**: The resolved configuration for the module. Read from
  `zensical.toml` or `mkdocs.yml`. Fields mirror §6 of `specification.md`.

- **SlugRegistry**: A mapping from raw label → canonical slug across all
  TaxonomyTerms. Enforces deterministic collision resolution.

- **ZensicalPlugin**: The Zensical plugin adapter that wires the generation
  pipeline into the Zensical build lifecycle. Registered under the
  `zensical.plugins` entry point. Invokes `builder` and `emitter` during the
  pre-build stage. Performs nav assurance post-build. Has no business logic
  of its own; it is a thin adapter. Does not depend on the `mkdocs` package.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A maintainer with an existing `docs/blog/posts/` directory can
  install the module and get a working blog index, archive, tag, and category
  structure in a single `zensical-blog build` run without modifying any
  existing files.

- **SC-002**: All blog pages (index, archive, tag, category) generated from
  the same input content are byte-for-byte identical across repeated runs,
  enabling clean version-control diffs.

- **SC-003**: The module can be installed from its GitHub repository URL using
  a single `pip install git+…` command with no additional setup steps.

- **SC-004**: Running `zensical-blog build` followed by `zensical-blog clean`
  leaves the working tree in exactly the state it was before `build` ran (no
  stray files).

- **SC-005**: A post URL produced today (`/blog/<slug>/`) remains valid after
  the module later migrates to Zensical's native module API, as the slug and
  routing contract are locked and documented.

- **SC-006**: All acceptance criteria in §12 of `references/specification.md`
  pass as automated tests.

- **SC-007**: A maintainer can configure `[project.extra.zensical_blog]` in
  `zensical.toml` and run `zensical build` without any other steps; all blog
  pages appear in the build output with no separate `zensical-blog build`
  invocation required.

## Assumptions

- Zensical's public module API is not yet available; the module ships entirely
  in bridge mode and does not call Zensical internal APIs.
- The Python runtime is 3.11 or later; no backport compatibility is required.
- Users have an existing Zensical or MkDocs project with a `docs/` directory.
- The module operates in two invocation modes: (a) **standalone CLI** via
  `zensical-blog build` (explicit pre-build step, useful in CI or scripted
  workflows) and (b) **Zensical plugin** registered under the `zensical.plugins`
  entry point, which hooks automatically into `zensical build` when Zensical's
  module system is active. Both modes run exactly the same generation pipeline.
  The `mkdocs` package is NOT a dependency; no MkDocs-internal APIs are used.
- Pagination applies to the blog index only in v1 (tag/category/year page
  pagination is deferred to v2).
- RSS feed generation is out of scope for v1; the post model is designed to
  support feed generation in a future increment without structural changes.
- Multi-language routing is out of scope for v1.
- The `authors` front-matter field is recognised and stored on the Post model
  but is not rendered in v1 (forward-compatibility only).
- `pin: true` post ordering is deferred to v2.
- The module assumes `docs/.bloggen/` is added to `.gitignore`; a warning is
  emitted if it is not, but generation is not blocked.
- "No nav defined" behaviour (auto-synthesise a minimal nav) is implemented as
  documented in §8.2 of `specification.md`.

