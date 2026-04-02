# Contract: Configuration Schema

**Module**: `src/zensical_blog/config.py`  
**Date**: 2026-04-01  
**Source**: `references/specification.md` §6 + `data-model.md` §1

---

## Config Sources (priority, highest to lowest)

1. **CLI flags** — passed to `zensical-blog build / clean`
2. **`zensical.toml`** — `[project.extra.zensical_blog]` table — **primary**
3. **`mkdocs.yml`** — `plugins: - zensical_blog:` block — compat/migration
4. **Defaults** — as listed below

When `zensical.toml` is present and contains `[project.extra.zensical_blog]`,
the `mkdocs.yml` plugin block is **ignored entirely** (a debug log message is
emitted). Reading from `mkdocs.yml` uses only plain YAML parsing (`ruamel.yaml`);
the `mkdocs` package is NOT imported.

---

## Fields

### `blog_dir`

| | |
|---|---|
| **Type** | `str` |
| **Default** | `"blog"` |
| **Description** | Directory within `docs_dir` that contains the blog. Also used as the URL base path prefix. |
| **Validation** | Non-empty; must be a valid single-level path segment (no `/`, no `..`). |
| **`zensical.toml`** | `blog_dir = "blog"` |
| **`mkdocs.yml`** | `blog_dir: blog` |

### `posts_dir`

| | |
|---|---|
| **Type** | `str` |
| **Default** | `"blog/posts"` |
| **Description** | Directory (relative to `docs_dir`) where post `.md` files are discovered recursively. |
| **Validation** | Non-empty; safe relative path. MUST be inside `docs_dir`. |
| **`zensical.toml`** | `posts_dir = "blog/posts"` |

### `archives`

| | |
|---|---|
| **Type** | `"yearly"` |
| **Default** | `"yearly"` |
| **Description** | Granularity of archive pages. Only `"yearly"` is supported in v1. |
| **Validation** | Must equal `"yearly"`. |

### `pagination`

| | |
|---|---|
| **Type** | `int` |
| **Default** | `10` |
| **Description** | Number of post excerpts per page on the blog index. In v1, applies to the blog index only. |
| **Validation** | ≥ 1. |

### `excerpt_marker`

| | |
|---|---|
| **Type** | `str` |
| **Default** | `"<!-- more -->"` |
| **Description** | HTML comment used to split a post into excerpt + remainder. Must appear on its own line; first occurrence is used. |
| **Validation** | Non-empty string. |

### `excerpt_fallback`

| | |
|---|---|
| **Type** | `"first_paragraph"` |
| **Default** | `"first_paragraph"` |
| **Description** | Strategy when `excerpt_marker` is absent. `"first_paragraph"` uses content up to the first blank line. |
| **Validation** | Must equal `"first_paragraph"` in v1. |

### `drafts`

| | |
|---|---|
| **Type** | `"hide" \| "show" \| "fail"` |
| **Default** | `"hide"` |
| **Description** | Controls visibility of posts with `draft: true`. `"hide"` excludes them silently. `"show"` includes them. `"fail"` exits non-zero if any draft is found. |
| **Validation** | One of `"hide"`, `"show"`, `"fail"`. |

### `nav_label`

| | |
|---|---|
| **Type** | `str` |
| **Default** | `"Blog"` |
| **Description** | The display label used for the top-level nav entry. |
| **Validation** | Non-empty. |

### `nav_path`

| | |
|---|---|
| **Type** | `str` |
| **Default** | `"blog/index.md"` |
| **Description** | The path value for the top-level nav entry (relative to `docs_dir`). |
| **Validation** | Non-empty; ends with `.md`. |

### `enable_tags`

| | |
|---|---|
| **Type** | `bool` |
| **Default** | `true` |
| **Description** | Generate tag landing page and per-tag pages. When `false`, no tag pages are generated and tag front matter is ignored. |

### `enable_categories`

| | |
|---|---|
| **Type** | `bool` |
| **Default** | `true` |
| **Description** | Generate category landing page and per-category pages. When `false`, no category pages are generated. |

### `enable_archive_landing`

| | |
|---|---|
| **Type** | `bool` |
| **Default** | `true` |
| **Description** | Generate the `/blog/archive/` landing page listing all years. Year pages are always generated regardless of this flag. |

### `tag_slug_map`

| | |
|---|---|
| **Type** | `dict[str, str]` |
| **Default** | `{}` |
| **Description** | Explicit label → slug overrides for tags. Prevents URL churn when a tag label is renamed. Overrides the computed slug. |
| **Validation** | Values must be non-empty and contain only `[a-z0-9-]`. |
| **`zensical.toml`** | `[project.extra.zensical_blog.tag_slug_map]` table |

### `category_slug_map`

| | |
|---|---|
| **Type** | `dict[str, str]` |
| **Default** | `{}` |
| **Description** | Explicit label → slug overrides for categories. |
| **Validation** | Same as `tag_slug_map`. |
| **`zensical.toml`** | `[project.extra.zensical_blog.category_slug_map]` table |

---

## Complete `zensical.toml` Example

```toml
[project]
site_name = "My Docs"

[project.extra.zensical_blog]
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

[project.extra.zensical_blog.tag_slug_map]
"C#" = "csharp"
"How To" = "how-to"

[project.extra.zensical_blog.category_slug_map]
"Getting Started" = "getting-started"
```

---

## `mkdocs.yml` Compat Example (migration path)

```yaml
plugins:
  - zensical_blog:
      blog_dir: blog
      posts_dir: blog/posts
      drafts: hide
      enable_tags: true
      enable_categories: true
      tag_slug_map:
        "C#": csharp
```

> **Note**: When `zensical.toml` is present, this block is ignored. Migrate
> to `zensical.toml` for full Zensical-forward compatibility.

---

## Post Front Matter Fields

These fields are read from each post `.md` file. They are not part of
`BlogConfig` but are part of the input contract.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `title` | `str` | Recommended | Fallback: first H1 in body; then filename stem (slugified, capitalised). |
| `date` | `str` (YYYY-MM-DD or ISO 8601) | **Yes** | Posts without a `date` are skipped with a warning. |
| `draft` | `bool` | No | Default `false`. |
| `tags` | `list[str]` | No | Empty list if absent. |
| `categories` | `list[str]` | No | Empty list if absent. |
| `slug` | `str` | No | Overrides computed post slug. Must be `[a-z0-9][a-z0-9-]*`. |
| `authors` | `list[str]` | No | Stored; not rendered in v1. |
| `pin` | `bool` | No | Stored; deferred to v2. |
