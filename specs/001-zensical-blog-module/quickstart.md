# Quickstart: Zensical Blog Module

**Date**: 2026-04-01

---

## Prerequisites

- Python 3.11 or later
- An existing Zensical or MkDocs project with a `docs/` directory
- `zensical.toml` at the project root (recommended) or `mkdocs.yml`

---

## 1. Install

```bash
pip install git+https://github.com/<org>/zensical-blog.git
```

Or pin a specific commit/tag:

```bash
pip install git+https://github.com/<org>/zensical-blog.git@v0.1.0
```

For development, clone and install in editable mode:

```bash
git clone https://github.com/<org>/zensical-blog.git
pip install -e "./zensical-blog[dev]"
```

---

## 2. Configure (`zensical.toml` — recommended)

Add a `[project.extra.zensical_blog]` table to your `zensical.toml`:

```toml
[project]
site_name = "My Docs"

[project.extra.zensical_blog]
blog_dir = "blog"
posts_dir = "blog/posts"
drafts = "hide"
```

All other fields are optional and have sensible defaults. See
`contracts/config-schema.md` for the full field reference.

### Alternative: `mkdocs.yml` (migration / compat)

```yaml
plugins:
  - zensical_blog:
      blog_dir: blog
      drafts: hide
```

> Migrate to `zensical.toml` when ready — it takes priority and is the
> Zensical-forward approach.

---

## 3. Add Posts

Create Markdown files under `docs/blog/posts/`. Each file **must** have a
`date` field in its YAML front matter:

```markdown
---
title: Hello, World!
date: 2026-04-01
tags: [announcements]
categories: [general]
---

This is the opening paragraph, which becomes the excerpt.

<!-- more -->

Rest of the post content goes here.
```

File naming convention (recommended, not required):

```
docs/blog/posts/YYYY-MM-DD-my-post-title.md
```

The date prefix is stripped when computing the slug, so the URL becomes
`/blog/my-post-title/`.

---

## 4. Add to `.gitignore`

The generated root (`docs/.bloggen/`) should not be committed:

```
# .gitignore
docs/.bloggen/
```

The module will warn if this is missing.

---

## 5. Build

### Standalone (explicit pre-build step)

```bash
zensical-blog build
```

Then run your normal site build:

```bash
zensical build   # or: mkdocs build
```

### Automatic (Zensical plugin — when Zensical's module system is active)

When the `zensical.plugins` entry point is active, `zensical build` triggers
the blog generation automatically. No separate step needed.

### CI (fail on warnings)

```bash
zensical-blog build --fail-on-warnings
zensical build
```

---

## 6. Check the Output

After `build`, the following pages are generated (with default config):

| Page | Location |
|------|----------|
| Blog index | `docs/blog/index.md` (appended) |
| Archive landing | `docs/blog/archive/index.md` (appended) |
| Year 2026 | `docs/blog/archive/2026.md` (appended) |
| Tags landing | `docs/blog/tag/index.md` (appended) |
| Per-tag | `docs/blog/tag/<slug>.md` (appended) |
| Categories landing | `docs/blog/category/index.md` (appended) |
| Per-category | `docs/blog/category/<slug>.md` (appended) |

Generated Markdown artifacts (safe to delete):

```
docs/.bloggen/blog/
├── lists/latest.md
├── archive/
│   ├── index.generated.md
│   └── 2026.generated.md
├── tag/
│   ├── index.generated.md
│   └── announcements.generated.md
└── category/
    ├── index.generated.md
    └── general.generated.md
```

---

## 7. Customise a Page

Create the canonical file before running `build`. Your content is preserved;
the generated listing is appended after it:

```markdown
<!-- docs/blog/archive/2026.md -->
# 2026 in Review

What a year it's been...

<!-- zensical-blog:generated:start -->
<!-- This section is managed by zensical-blog. Do not edit between markers. -->
...generated post list...
<!-- zensical-blog:generated:end -->
```

On subsequent builds, only the content between the sentinel markers is
replaced.

---

## 8. Clean

Remove all generated artifacts:

```bash
zensical-blog clean
```

Only files under `docs/.bloggen/` are removed. User-authored files and
sentinel blocks within canonical files are not touched.

---

## 9. Nav Setup

### If you use `zensical.toml` nav

Add the blog to your nav:

```toml
[[project.nav]]
Blog = "blog/index.md"
```

### If you use `mkdocs.yml` nav

```yaml
nav:
  - Home: index.md
  - Blog: blog/index.md
```

If the Blog nav entry is absent, `zensical-blog build` emits a warning. Use
`--apply-nav` to patch it automatically:

```bash
zensical-blog build --apply-nav   # patches mkdocs.yml nav in place
```

---

## 10. Lock Tag/Category Slugs (optional but recommended)

To prevent URL churn when a tag label is renamed:

```toml
[project.extra.zensical_blog.tag_slug_map]
"C#" = "csharp"
"How To" = "how-to"
```

Once set, renaming `"How To"` to `"How-To"` in front matter will not change
the URL `/blog/tag/how-to/`.
