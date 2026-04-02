# zensical-blog

A sidecar blog generator plugin for [Zensical](https://zensical.io) documentation sites.

Generates a fully-linked blog (post index, yearly archives, tag and category pages)
as deterministic Markdown files — no Zensical internals required.

## Install

```bash
pip install git+https://github.com/<org>/zensical-blog.git
```

Pin a specific release:

```bash
pip install git+https://github.com/<org>/zensical-blog.git@v0.1.0
```

## Quickstart

### 1. Add to `.gitignore`

```
docs/.bloggen/
```

The module warns if this entry is missing.

### 2. Configure `zensical.toml`

Add a `[project.extra.zensical_blog]` table. All fields are optional — the
minimal config is just the section header:

```toml
[project.extra.zensical_blog]
blog_dir   = "blog"          # relative to docs/
posts_dir  = "blog/posts"    # where .md posts live, relative to docs/
drafts     = "hide"          # hide | show | fail
```

#### All options and defaults

| Key | Default | Description |
|-----|---------|-------------|
| `blog_dir` | `"blog"` | Root URL path for the blog, relative to `docs/`. |
| `posts_dir` | `"blog/posts"` | Directory scanned for `.md` post files, relative to `docs/`. |
| `drafts` | `"hide"` | `"hide"` — drafts excluded; `"show"` — drafts included; `"fail"` — build errors if any draft exists. |
| `archives` | `"yearly"` | Archive grouping strategy. Only `"yearly"` is supported. |
| `pagination` | `10` | Posts per listing page (reserved; pagination rendering not yet wired). |
| `excerpt_marker` | `"<!-- more -->"` | HTML comment that splits post body into excerpt + remainder. |
| `excerpt_fallback` | `"first_paragraph"` | Strategy when `excerpt_marker` is absent. Only `"first_paragraph"` is supported. |
| `nav_label` | `"Blog"` | Label used when patching the `mkdocs.yml` nav with `--apply-nav`. |
| `nav_path` | `"blog/index.md"` | Path used when patching the nav. |
| `enable_tags` | `true` | Generate tag landing and per-tag pages. |
| `enable_categories` | `true` | Generate category landing and per-category pages. |
| `enable_archive_landing` | `true` | Generate the yearly archive landing page. |
| `tag_slug_map` | `{}` | Explicit label → slug overrides for tags, e.g. `{"C#" = "csharp"}`. |
| `category_slug_map` | `{}` | Explicit label → slug overrides for categories. |
| `fail_on_warnings` | `false` | Exit 1 if any `BuildWarning` is emitted (same as `--fail-on-warnings` CLI flag). |

#### Full example

```toml
[project.extra.zensical_blog]
blog_dir              = "blog"
posts_dir             = "blog/posts"
drafts                = "hide"
pagination            = 10
excerpt_marker        = "<!-- more -->"
nav_label             = "Blog"
nav_path              = "blog/index.md"
enable_tags           = true
enable_categories     = true
enable_archive_landing = true

[project.extra.zensical_blog.tag_slug_map]
"C#" = "csharp"

[project.extra.zensical_blog.category_slug_map]
"How-To" = "how-to"
```

#### Alternative: `mkdocs.yml` (compat)

```yaml
plugins:
  - zensical_blog:
      blog_dir: blog
      drafts: hide
```

`zensical.toml` takes priority over `mkdocs.yml` when both exist.

### 3. Write posts

Create `.md` files under `docs/blog/posts/`. Each file **must** have a `date`
field in its YAML front matter:

```markdown
---
title: Hello, World!
date: 2026-04-01
tags: [announcements]
categories: [general]
---

Opening paragraph — this becomes the excerpt when no `<!-- more -->` is present.

<!-- more -->

Rest of the post content.
```

Recommended filename convention (not required):

```
docs/blog/posts/YYYY-MM-DD-my-post-title.md
```

The date prefix is stripped when computing the slug, so the post URL becomes
`/blog/my-post-title/`.

### 4. Build

**Standalone** — run before your normal site build:

```bash
zensical-blog build
zensical build   # or: mkdocs build
```

**As a Zensical plugin** — when the `zensical.plugins` entry point is active,
`zensical build` triggers blog generation automatically. No extra step needed.

**CI** — fail the build if any warning is emitted:

```bash
zensical-blog build --fail-on-warnings
```

**Patch `mkdocs.yml` nav** automatically on first run:

```bash
zensical-blog build --apply-nav
```

### 5. Generated output

With default config the following pages are created or updated:

| Page | Location |
|------|----------|
| Blog index | `docs/blog/index.md` |
| Archive landing | `docs/blog/archive/index.md` |
| Per-year | `docs/blog/archive/<year>.md` |
| Tags landing | `docs/blog/tag/index.md` |
| Per-tag | `docs/blog/tag/<slug>.md` |
| Categories landing | `docs/blog/category/index.md` |
| Per-category | `docs/blog/category/<slug>.md` |

All pages use a **sentinel protocol** — your hand-authored content above the
markers is preserved across rebuilds:

```
<!-- zensical-blog:generated:start -->
...managed content — do not edit between markers...
<!-- zensical-blog:generated:end -->
```

### 6. Clean

Remove all generated artifacts under `docs/.bloggen/`:

```bash
zensical-blog clean
```

---

## CLI reference

```
zensical-blog build [OPTIONS]

  --config PATH        Path to zensical.toml or mkdocs.yml. Auto-detected when omitted.
  --docs-dir PATH      Override the docs/ directory.
  --apply-nav          Patch mkdocs.yml nav to add the Blog entry if absent.
  --fail-on-warnings   Exit 1 if any BuildWarning is emitted. Recommended for CI.

zensical-blog clean [OPTIONS]

  --config PATH        Path to config file. Auto-detected when omitted.
```

---

## Development

```bash
git clone https://github.com/<org>/zensical-blog.git
cd zensical-blog
pip install -e ".[dev]"
pytest
ruff check src/ tests/
```

