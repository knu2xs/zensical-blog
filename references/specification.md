# Spec: Zensical Sidecar Blog Module (3rd‑party, future‑API aligned)

> **Purpose:** Define a comprehensive specification for a third‑party Zensical “blog as sidecar” module that can ship **today** in “bridge mode” and later align with Zensical’s **public module API** once it is released.   
> **Key decisions already made:** [\[zensical.org\]](https://zensical.org/), [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534), [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)
>
> *   Blog is a **sidecar** to docs (not blog‑only). [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
> *   Archives are **yearly by default**. [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)
> *   **No multi-language** requirements for v1. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534), [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)
> *   This is a **third‑party module** now; later align with Zensical’s module API when it becomes public. [\[zensical.org\]](https://zensical.org/), [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
> *   “Blog” appears in **top-level nav**. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
> *   Blog index links to **tag and category landing pages**.

***

## 1. Background & Rationale

### 1.1 Why this must be “bridge-first”

*   Zensical is currently **alpha** and iterating rapidly, with a phased transition strategy: maximize compatibility first, then release the **module system**, then feature parity, then the **component system + CommonMark**. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534), [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)
*   Zensical is explicitly **holding back** a public module API until the module system matures, then expects to iterate via Spark before opening broadly. [\[zensical.org\]](https://zensical.org/), [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
*   Therefore, the module should ship today as an external generator (“bridge mode”) that does not depend on internal Zensical APIs, while designing internal contracts to map cleanly to future native modules. [\[zensical.org\]](https://zensical.org/), [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)

### 1.2 Compatibility targets

*   Zensical’s compatibility strategy is to map existing MkDocs plugin configuration to Zensical modules, and “blog” is explicitly tracked among prioritized plugin compat items. [\[zensical.org\]](https://zensical.org/)
*   Zensical’s compatibility promise includes keeping project structure, URLs/anchors, and template override patterns consistent for smooth transitions from Material for MkDocs. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534), [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)

***

## 2. Scope

### 2.1 In-scope (v1)

*   Sidecar blog located under a configurable `blog_dir` (default `blog`) within `docs_dir`. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
*   Posts are authored as Markdown files under `posts_dir` (default `blog/posts`). [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
*   Generate:
    *   Blog index at `blog/index.md` (user-authored or generated) with a post listing appended. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
    *   Yearly archives (`/blog/archive/<year>/` or equivalent) by default. [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)
    *   Tag landing page + per-tag pages, linked from blog index.
    *   Category landing page + per-category pages, linked from blog index.
*   Excerpts using `<!-- more -->` marker (default), with fallback excerpt strategy.
*   Slug support (auto-generated; override via `slug` front matter).
*   Optional RSS feed generation (v1 optional, but design the contract for it). [\[zensical.org\]](https://zensical.org/)
*   Minimal “nav assurance”: ensure “Blog” exists as a **top-level** nav entry pointing to `blog/index.md` (non-destructive by default). [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

### 2.2 Out-of-scope (v1)

*   Multi-language routing/archives (explicitly not required). [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin), [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
*   Replacing Zensical’s internal runtime tasks directly (until public API). [\[zensical.org\]](https://zensical.org/), [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
*   Comment systems, CMS/admin UI, or hosting-specific integrations beyond generating static artifacts. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534), [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)

***

## 3. Users & Use Cases

### 3.1 Primary user personas

*   Docs-as-code maintainers who want a blog alongside documentation with minimal configuration, consistent with Material/MkDocs expectations. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
*   Teams migrating from Material for MkDocs blog plugin behavior who want stable URLs and compatible override patterns. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

### 3.2 User stories (acceptance-focused)

1.  As a maintainer, I can add posts under `docs/blog/posts/` and have them appear automatically on `docs/blog/index.md` without adding individual posts to nav. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
2.  As a reader, I can browse a yearly archive page listing posts from that year by default.
3.  As a reader, I can click “Tags” and “Categories” from the blog index to reach landing pages listing all tags/categories.
4.  As a maintainer, I can override an archive/tag/category page by creating the file where the generator would create it, and the post list will be appended after my custom content.
5.  As a maintainer, I can keep my existing Zensical/MkDocs site structure and URLs stable (no unexpected path churn). [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534), [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)

***

## 4. Information Architecture & URL Map

### 4.1 Default URL conventions (sidecar)

*   Blog index: `/blog/` (source: `docs/blog/index.md`). [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
*   Post pages: `/blog/<slug>/` (derived from `blog/posts/<file>.md`, or `slug` override).
*   Archives landing: `/blog/archive/` (lists years).
*   Year pages: `/blog/archive/<year>/` (default granularity = yearly).
*   Tags landing: `/blog/tag/` (lists tags).
*   Tag pages: `/blog/tag/<tag>/` (lists posts with that tag).
*   Categories landing: `/blog/category/` (lists categories).
*   Category pages: `/blog/category/<category>/` (lists posts with that category).

### 4.2 Page generation set (minimum)

*   `blog/index.md` (user-authored optional; post list appended).
*   `blog/archive/index.md` (landing; year list + optional content).
*   `blog/archive/<year>.md` (year pages).
*   `blog/tag/index.md` (landing).
*   `blog/tag/<tag>.md` (per-tag).
*   `blog/category/index.md` (landing).
*   `blog/category/<category>.md` (per-category).

***

## 5. Content Model & Metadata

### 5.1 Post front matter (compatible set)

Posts are Markdown with YAML front matter supporting at least:

*   `date` (required for ordering and archives).
*   `draft` (optional; controls visibility depending on build mode).
*   `tags` (optional; participates in tag pages).
*   `categories` (optional; participates in category pages).
*   `slug` (optional override for URL slug).

Optional but recommended parity fields:

*   `authors` (optional; future extension, not required by this spec). [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)
*   `pin` (optional; pinned sorting support may be deferred).
*   `readtime` (optional override; else compute).
*   `links` (optional “related links” list; may be v2).

### 5.2 Excerpt rules

*   Excerpt is the content before `<!-- more -->` marker.
*   If marker absent, excerpt fallback is configurable (default: first paragraph).

### 5.3 Sorting rules

*   Default ordering: descending by `date`.
*   Draft handling defaults to hidden (configurable).

***

## 6. Configuration

### 6.1 Bridge mode config sources (priority order)

1.  `zensical.toml` under `[project.extra.blog_sidecar]` (recommended for Zensical-forward projects). [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
2.  `mkdocs.yml` plugin config under `plugins: - blog_sidecar:` (recommended for migration flows). [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534), [\[zensical.org\]](https://zensical.org/)
3.  CLI flags override both (for CI and local experimentation). [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin), [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

### 6.2 Required configuration fields

*   `blog_dir` (default `"blog"`).
*   `posts_dir` (default `"blog/posts"`).

### 6.3 Optional configuration fields (with defaults)

*   `archives = "yearly"` (default; supports `"yearly"` only in v1, may add `"monthly"` later). [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)
*   `pagination = 10` (default; applies to blog index and optionally taxonomy pages).
*   `excerpt_marker = "<!-- more -->"` (default).
*   `excerpt_fallback = "first_paragraph"` (default).
*   `drafts = "hide"` (default; values: `hide | show | fail`).
*   `nav_label = "Blog"` (default).
*   `nav_path = "blog/index.md"` (default).
*   `enable_tags = true` (default; generate landing + per-tag).
*   `enable_categories = true` (default; generate landing + per-category).
*   `enable_archive_landing = true` (default).

### 6.4 Example `zensical.toml` configuration snippet

```toml
[project]
site_name = "My Docs"

[project.extra.blog_sidecar]
blog_dir = "blog"
posts_dir = "blog/posts"
archives = "yearly"
pagination = 10
excerpt_marker = "<!-- more -->"
excerpt_fallback = "first_paragraph"
drafts = "hide"
nav_label = "Blog"
nav_path = "blog/index.md"
enable_tags = true
enable_categories = true
enable_archive_landing = true
```

This uses `[project.extra]` as the stable place for custom behavior values and template integration today. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

***

## 7. Generation & Override Semantics

### 7.1 Bridge output location (generated artifacts)

*   Generated Markdown pages MUST be written under a single generated root, e.g. `docs/.bloggen/…`, to keep the working tree clean and allow deterministic cleanup. [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin), [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
*   The module MUST NOT require users to add generated pages to nav beyond the single Blog entry, consistent with the “don’t add individual posts” behavior.

### 7.2 Visibility wiring strategy (sidecar safe)

*   The user-facing `docs/blog/index.md` remains the stable entrypoint and is the only page expected in nav.
*   Landing pages `docs/blog/tag/index.md` and `docs/blog/category/index.md` MUST be linked from the blog index.

### 7.3 Override precedence (Material-like)

If a user creates an override page at the canonical location, the generator MUST:

1.  Preserve user content.
2.  Append the generated listing after the content.
    This behavior matches Material’s documented “custom index pages” pattern for archive/category pages.

Canonical override locations include:

*   `docs/blog/index.md`
*   `docs/blog/archive/index.md` and `docs/blog/archive/<year>.md`
*   `docs/blog/tag/index.md` and `docs/blog/tag/<tag>.md`
*   `docs/blog/category/index.md` and `docs/blog/category/<category>.md`

***

## 8. Navigation Behavior (Top-level “Blog”)

### 8.1 Non-destructive nav assurance (default)

*   If navigation is defined and already contains `Blog: blog/index.md`, do nothing. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
*   If navigation is defined and does not contain Blog, emit a warning explaining the required nav entry, rather than rewriting config by default. [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin), [\[zensical.org\]](https://zensical.org/)
*   Provide an opt-in flag (e.g. `--apply-nav`) to patch `mkdocs.yml` nav to add `Blog: blog/index.md` as top-level. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

### 8.2 Zero-nav behavior

*   If no nav is defined, the module MAY synthesize a minimal nav that includes `Blog` (mirroring the documented behavior that blog can add navigation automatically when nav is not defined).

***

## 9. Rendering Contract (Bridge now, Components later)

### 9.1 Bridge mode rendering approach

*   The bridge should generate Markdown that relies on existing theme/templates to render post lists, minimizing template dependencies. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534), [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)
*   The design MUST keep a clean boundary between:
    *   **Model building** (discover/parse/sort/group)
    *   **Emission** (write markdown pages)
        so that later emission can be replaced by native module artifacts without changing logic. [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin), [\[zensical.org\]](https://zensical.org/)

### 9.2 Future native mode alignment

*   Zensical’s roadmap indicates a future component system with Markdown/HTML ASTs and modular rendering, so the module should center on stable “post/index models” rather than coupling to Python Markdown output. [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin), [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

***

## 10. CLI Interface (Bridge Mode)

### 10.1 Commands

*   `build`: generate or update `.bloggen` pages and any required append blocks. [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin), [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
*   `clean`: remove generated outputs (only within the generated root). [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin), [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

### 10.2 Key flags (minimum)

*   `--config zensical.toml|mkdocs.yml` (optional; auto-detect by default). [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
*   `--docs-dir docs` (optional; default derived from config). [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
*   `--apply-nav` (optional; patch nav as top-level “Blog”). [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
*   `--fail-on-warnings` (optional; CI enforcement). [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin), [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

***

## 11. Non-Functional Requirements

### 11.1 Determinism & incremental friendliness

*   Outputs MUST be deterministic given identical inputs (post content + config), enabling stable diffs and future compatibility with Zensical’s differential build philosophy. [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin), [\[zensical.org\]](https://zensical.org/)
*   The generator SHOULD avoid rewriting files when the rendered content is unchanged (stable formatting), supporting efficient previews and clean version control diffs. [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin), [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

### 11.2 Safety

*   The generator MUST only write within a controlled generated root (e.g., `docs/.bloggen`) and explicitly configured canonical override pages (append blocks), to avoid destructive behavior. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534), [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)

***

## 12. Acceptance Criteria (testable)

1.  **Index listing:** A post in `docs/blog/posts/` appears on the blog index page without adding the post to nav.
2.  **Yearly archives:** Posts are grouped into `/blog/archive/<year>/` pages by default.
3.  **Tags landing:** Blog index links to a tags landing page listing all tags; each tag links to its tag page listing posts.
4.  **Categories landing:** Blog index links to a categories landing page listing all categories; each category links to its category page listing posts.
5.  **Custom overrides:** If `docs/blog/archive/2026.md` exists, its content remains and the generated post list is appended.
6.  **Slug override:** Setting `slug` in post front matter produces the expected URL.
7.  **Excerpts:** Adding `<!-- more -->` yields an excerpt exactly matching the marker split.
8.  **Top-level nav:** If nav contains `Blog: blog/index.md`, the module does not modify nav; if it does not, the module warns (and optionally patches with `--apply-nav`). [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

***

## 13. Open Questions (optional for v1, but worth deciding early)

1.  **Pagination scope:** Apply pagination only to blog index, or also to tag/category/year pages?
2.  **Pinned posts:** Support `pin: true` ordering semantics now or later?
3.  **RSS:** Generate feed in v1 (bridge) or defer but define the model contract now? [\[zensical.org\]](https://zensical.org/)

***

## 14. Suggested “SpecKit-ready” structure (copy/paste outline)

Use this as a direct scaffold for `speckit.spec`:

*   **Overview**
*   **Goals / Non-goals**
*   **Assumptions / Constraints**
*   **User Stories**
*   **IA / Routes**
*   **Content Model**
*   **Configuration**
*   **Generation Rules**
*   **Override Rules**
*   **Navigation Rules**
*   **CLI / Developer UX**
*   **Non-functional Requirements**
*   **Acceptance Criteria**
*   **Future Migration Plan**
*   **Open Questions**

This structure aligns well with Zensical’s phased approach (compatibility → modules → components) and keeps your third-party work durable. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534), [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin), [\[zensical.org\]](https://zensical.org/)

***

If you want, I can produce a **second artifact**: a “page map + naming conventions” section with canonical filenames for the generated pages (and a deterministic slugification spec for tags/categories) so you can lock down routing and avoid future URL churn. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
