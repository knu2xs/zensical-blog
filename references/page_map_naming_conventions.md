## Artifact 2 — Page Map + Naming Conventions (Canonical Filenames, Deterministic Slugs, Locked Routing)

> **Goal:** Lock down **routing**, **canonical filenames**, and **deterministic slugification** for tags/categories so the blog can evolve (bridge → native module) without **URL churn**. This design follows Zensical’s stated priorities: seamless compatibility (stable URLs/structure), a phased transition to a module system, and eventual component/CommonMark evolution. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534), [\[zensical.org\]](https://zensical.org/), [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)

***

### 1) Canonical Routing Contract (URLs that MUST remain stable)

These routes are the **public contract**. Once shipped, treat them as semver‑protected “do not change” unless a migration tool is provided.

#### 1.1 Blog as a sidecar (base path)

*   **Base path:** `/<blog_dir>/` (default `blog_dir = "blog"` → `/blog/`). [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
*   **Single nav entry required:** Top‑level `"Blog"` points to `blog/index.md`; individual posts are **not** added to nav. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

#### 1.2 Posts

*   **Route pattern:** `/<blog_dir>/<post_slug>/` → `/blog/<post_slug>/`. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
*   **Slug source:** front matter `slug` overrides computed slug.

#### 1.3 Archive (locked to yearly by default)

*   **Archive landing:** `/<blog_dir>/archive/` → `/blog/archive/` (lists years).
*   **Year page:** `/<blog_dir>/archive/<year>/` → `/blog/archive/2026/`. (Default granularity locked to **yearly** for this module.)

#### 1.4 Tags (landing + per-tag)

*   **Tags landing:** `/<blog_dir>/tag/` → `/blog/tag/` (lists tags).
*   **Per-tag:** `/<blog_dir>/tag/<tag_slug>/` → `/blog/tag/data-engineering/`.

#### 1.5 Categories (landing + per-category)

*   **Categories landing:** `/<blog_dir>/category/` → `/blog/category/` (lists categories).
*   **Per-category:** `/<blog_dir>/category/<category_slug>/` → `/blog/category/how-to/`.

> **Why these routes are safe to lock:** Zensical explicitly emphasizes keeping project structure and URLs stable for compatibility, and its phased strategy aims to evolve internals (modules/components) without breaking external links. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534), [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)

***

### 2) Canonical Filenames (User-facing, stable) vs Generated Filenames (bridge artifacts)

This module is third‑party today, so we separate **stable canonical pages** (user editable, stable path) from **generated pages** (fully regenerable). Zensical’s ecosystem plan explicitly notes third‑party modules will be possible later and that the public API is being held back until stable—so bridge artifacts must be clean and disposable. [\[zensical.org\]](https://zensical.org/), [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

#### 2.1 Canonical filenames (MUST NOT change)

These are the **override targets** and stable reference points.

**Blog entrypoint**

*   `docs/<blog_dir>/index.md`
    *   Example: `docs/blog/index.md`
    *   Route: `/blog/` [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

**Posts**

*   `docs/<blog_dir>/posts/**/*.md`
    *   Example: `docs/blog/posts/hello-world.md`
    *   Route: `/blog/<slug>/` [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

**Archives**

*   Landing: `docs/<blog_dir>/archive/index.md` → `/blog/archive/`
*   Year page: `docs/<blog_dir>/archive/<year>.md` → `/blog/archive/<year>/`

**Tags**

*   Landing: `docs/<blog_dir>/tag/index.md` → `/blog/tag/`
*   Per-tag: `docs/<blog_dir>/tag/<tag_slug>.md` → `/blog/tag/<tag_slug>/`

**Categories**

*   Landing: `docs/<blog_dir>/category/index.md` → `/blog/category/`
*   Per-category: `docs/<blog_dir>/category/<category_slug>.md` → `/blog/category/<category_slug>/`

#### 2.2 Generated filenames (bridge mode; safe to delete)

All generated files live under a single generated root:

*   **Generated root:** `docs/.bloggen/` (configurable, but default should be stable). [\[zensical.org\]](https://zensical.org/), [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)

Within that:

*   `docs/.bloggen/<blog_dir>/lists/latest.md`
*   `docs/.bloggen/<blog_dir>/archive/index.generated.md`
*   `docs/.bloggen/<blog_dir>/archive/<year>.generated.md`
*   `docs/.bloggen/<blog_dir>/tag/index.generated.md`
*   `docs/.bloggen/<blog_dir>/tag/<tag_slug>.generated.md`
*   `docs/.bloggen/<blog_dir>/category/index.generated.md`
*   `docs/.bloggen/<blog_dir>/category/<category_slug>.generated.md`

> **Lock-in rule:** canonical filenames define URLs; generated filenames are an implementation detail and may change without URL churn, because they are not routed directly. This matches Zensical’s philosophy of swapping internals while keeping outputs stable. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534), [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)

***

### 3) Deterministic Slugification Spec (Tags & Categories)

This is the primary mechanism to avoid future URL churn for taxonomy pages.

#### 3.1 Canonical input

*   Slugification input is the **raw label** exactly as authored in front matter (`tags:` / `categories:`), treated as a Unicode string.

#### 3.2 Algorithm (MUST be deterministic; no locale dependence)

Given `label`:

1.  `label = trim(label)`
2.  Unicode normalize to **NFKD**
3.  Strip combining marks (diacritics)
4.  Convert to lowercase using Unicode simple case-fold
5.  Replace any run of characters that are **not** `[a-z0-9]` with `-`
    *   This treats spaces, punctuation, underscores, slashes as separators
6.  Collapse multiple `-` to a single `-`
7.  Trim leading/trailing `-`
8.  If empty, set to `x`
9.  Enforce max length = **80** chars; if truncated, trim trailing `-`

> **Why this is future-proof:** it is locale-independent (no i18n requirement), deterministic, and stable across Python/Rust implementations (important for bridge now → native later). Zensical’s roadmap explicitly anticipates Python bindings and later deeper Rust-native processing, so algorithm stability across runtimes matters. [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin), [\[zensical.org\]](https://zensical.org/)

#### 3.3 Collision handling (MUST be deterministic)

Two different labels can map to the same slug (e.g., “C#” and “C sharp”).

**Policy:**

*   Compute base slug for all labels.
*   Group labels by base slug.
*   If a base slug group size > 1:
    *   Sort labels by their **original label** (Unicode code point order, stable)
    *   Assign first label the base slug unchanged
    *   Assign subsequent labels `"{base}-{n}"` where `n` starts at 2

Example:

*   `["C#", "C sharp", "C-sharp"]` → base slug `c` for all
    *   sorted: `"C#"`, `"C sharp"`, `"C-sharp"`
    *   slugs: `c`, `c-2`, `c-3`

**Output contract:**

*   Emit a warning listing collisions and final slugs (but do not fail by default).

> This supports determinism and avoids page overwrites, which is aligned with Zensical’s emphasis on explicit, predictable pipelines vs “mysterious plugin interference.” [\[zensical.org\]](https://zensical.org/), [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)

#### 3.4 Optional explicit slug maps (recommended to truly “lock” URLs)

To prevent churn when a label is renamed (e.g., “How-To” → “How To”), support an optional map in config:

*   `tag_slug_map`: `{ "How To": "how-to" }`
*   `category_slug_map`: `{ "How To": "how-to" }`

**Precedence:**

1.  Explicit map (if label matches key exactly)
2.  Algorithmic slugification
3.  Collision disambiguation suffix (if needed)

This gives maintainers a way to preserve URLs even when taxonomy labels evolve.

***

### 4) Post Slug Rules (for routing stability)

Material supports post slug overrides and dynamic post URLs; we lock a deterministic rule set to avoid churn.

#### 4.1 Post slug precedence

1.  front matter `slug` (after trimming)
2.  front matter `title`
3.  first H1 heading
4.  filename stem

Apply the same normalization/slug algorithm as §3 (with max length 80).

#### 4.2 Route

*   Always `/<blog_dir>/<post_slug>/` in sidecar mode. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

***

### 5) Override Precedence & Custom Page Semantics (Locked)

Material’s blog plugin supports custom pages at the location where auto-generated pages would exist and appends post lists after user content; we adopt the same behavior to ensure a familiar customization model.

#### 5.1 Canonical override rule (applies to all view pages)

For each canonical view page path listed in §2.1:

*   If the canonical file exists, treat it as **user-authored**, do not overwrite its content, and append a generated listing after it.
*   If the canonical file does not exist, generate a canonical stub (recommended for landing pages) or rely on a generated-only approach (not recommended because you want stable routing). [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

#### 5.2 “Generated region” markers (to minimize churn and avoid clobbering)

Canonical pages should contain (or have appended) a sentinel region:

```markdown
<!-- BLOG_SIDECAR:BEGIN generated -->
...generated content here...
<!-- BLOG_SIDECAR:END generated -->
```

**Update behavior:**

*   If markers exist, replace only the content between them.
*   If markers are absent, append the region at end of file.

This makes repeated runs stable and keeps git diffs minimal—important for deterministic “bridge” operation.

#### 5.3 Override precedence order (explicit)

When generating a given route (e.g., `/blog/tag/data/`):

1.  **Canonical user file exists?**
    *   Use it as base content.
2.  Determine the generated listing for that route.
3.  Append/replace the generated region.
4.  Never route directly from `.bloggen` outputs; `.bloggen` is implementation-only.

***

### 6) Locked “Page Wiring” Requirements (to ensure discoverability, no nav bloat)

#### 6.1 Blog index MUST link to taxonomy landings

Because you requested it explicitly, `docs/<blog_dir>/index.md` must include visible links to:

*   `/blog/archive/`
*   `/blog/tag/`
*   `/blog/category/`

This ensures taxonomy pages are discoverable without needing nav entries beyond “Blog”, matching the “only add blog index to nav” workflow. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)

#### 6.2 Only the blog index goes in the top-level nav

*   Expected nav entry: `Blog: blog/index.md` as top-level. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534)
*   Do not add posts, tags, categories, or archives to nav by default.

***

### 7) Route/Name Stability Rules (anti-churn guarantees)

To “avoid future URL churn,” enforce these invariants:

1.  **Canonical filenames in §2.1 define routing** and must not change without a migration tool. [\[forum.crys...l-lang.org\]](https://forum.crystal-lang.org/t/zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team/8534), [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin)
2.  **Slugification algorithm + collision policy** is part of the public contract; changes require a major version. [\[github.com\]](https://github.com/liang2kl/mkdocs-blogging-plugin), [\[zensical.org\]](https://zensical.org/)
3.  **Explicit slug maps** (if enabled) always win; they are the recommended mechanism for deliberate taxonomy renames without breaking URLs.
4.  `.bloggen` paths are not part of the public contract and may change freely.

***

## If you want, I can also generate…

1.  A **route-to-source resolution matrix** (“when a user requests `/blog/tag/x/`, what file is used and what gets appended”)
2.  A concrete default **canonical stub content** for:

*   `blog/tag/index.md`
*   `blog/category/index.md`
*   `blog/archive/index.md`
    so that links always land on stable pages even with zero authoring effort.

Just say the word.
