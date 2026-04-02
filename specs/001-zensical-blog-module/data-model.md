# Data Model: Zensical Blog Module (Sidecar, Bridge Mode)

**Phase**: 1 — Design  
**Date**: 2026-04-01  
**Source**: `spec.md` Key Entities + `references/specification.md` §5 + `references/page_map_naming_conventions.md` §3

---

## Layer Boundary Reminder

```
┌─────────────────────────────────────────────────────┐
│  MODEL LAYER  (builder.py)                          │
│  Inputs:  source files, config                      │
│  Outputs: BlogModel (pure in-memory data)           │
│  Rule:    NO file writes; NO Markdown generation    │
└────────────────────────┬────────────────────────────┘
                         │  BlogModel
┌────────────────────────▼────────────────────────────┐
│  EMISSION LAYER  (emitter.py)                       │
│  Inputs:  BlogModel, BlogConfig                     │
│  Outputs: files written to docs/.bloggen/ or        │
│           appended to canonical override files      │
│  Rule:    NO sorting; NO parsing; NO business logic │
└─────────────────────────────────────────────────────┘
```

---

## 1. BlogConfig

**Module**: `config.py`  
**Purpose**: Resolved, typed configuration for one build run. Constructed once;
immutable thereafter.

| Field | Type | Default | Validation |
|-------|------|---------|------------|
| `blog_dir` | `str` | `"blog"` | Non-empty, safe path segment |
| `posts_dir` | `str` | `"blog/posts"` | Non-empty, safe path segment |
| `docs_dir` | `Path` | derived from config file location | Must exist |
| `archives` | `Literal["yearly"]` | `"yearly"` | Only `"yearly"` in v1 |
| `pagination` | `int` | `10` | ≥ 1 |
| `excerpt_marker` | `str` | `"<!-- more -->"` | Non-empty |
| `excerpt_fallback` | `Literal["first_paragraph"]` | `"first_paragraph"` | Only `"first_paragraph"` in v1 |
| `drafts` | `Literal["hide","show","fail"]` | `"hide"` | One of the three values |
| `nav_label` | `str` | `"Blog"` | Non-empty |
| `nav_path` | `str` | `"blog/index.md"` | Non-empty |
| `enable_tags` | `bool` | `True` | — |
| `enable_categories` | `bool` | `True` | — |
| `enable_archive_landing` | `bool` | `True` | — |
| `tag_slug_map` | `dict[str, str]` | `{}` | Values must pass slugification post-check |
| `category_slug_map` | `dict[str, str]` | `{}` | Values must pass slugification post-check |
| `generated_root` | `Path` | `docs_dir / ".bloggen"` | Derived; not user-settable in v1 |
| `fail_on_warnings` | `bool` | `False` | — |

**Config resolution order** (highest → lowest):
1. CLI flags
2. `[project.extra.zensical_blog]` in `zensical.toml`
3. `plugins: - zensical_blog:` block in `mkdocs.yml` (compat; plain YAML parse)
4. Defaults above

**Invariant**: `generated_root` is always a subdirectory of `docs_dir`.

---

## 2. RawPost

**Module**: `parser.py`  
**Purpose**: Intermediate value from parsing a single source file. Passed to
model construction; never stored beyond the build function.

| Field | Type | Notes |
|-------|------|-------|
| `source_path` | `Path` | Absolute path to the `.md` file |
| `raw_metadata` | `dict[str, Any]` | All front matter keys, unvalidated |
| `raw_content` | `str` | Full body after front matter delimiters |

---

## 3. Post

**Module**: `models.py`  
**Purpose**: A single validated, resolved blog post. The core unit of the model
layer.

| Field | Type | Nullable | Notes |
|-------|------|----------|-------|
| `source_path` | `Path` | No | Absolute path to source `.md` |
| `title` | `str` | No | From front matter `title`; falls back to H1 in body; else filename stem |
| `date` | `date` | No | Parsed from front matter `date` (YYYY-MM-DD or ISO datetime → date only) |
| `draft` | `bool` | No | Default `False` |
| `tags` | `tuple[str, ...]` | No | Normalised (stripped); empty tuple if absent |
| `categories` | `tuple[str, ...]` | No | Normalised (stripped); empty tuple if absent |
| `slug` | `str` | No | Resolved slug (see §6 SlugRegistry) |
| `excerpt` | `str` | No | Extracted per config; never empty (falls back to first paragraph or first 200 chars) |
| `body` | `str` | No | Full Markdown body (excerpt marker removed if present) |
| `authors` | `tuple[str, ...]` | No | Stored for forward-compat; not rendered in v1 |
| `url_path` | `str` | No | `/<blog_dir>/<slug>/` — derived; set by builder |

**Validation rules**:
- `date` MUST be present; posts without a date are skipped with a warning.
- `slug` MUST contain only `[a-z0-9-]` and be non-empty after resolution.

**Sort key** (defined on model; used by builder):
```python
@property
def sort_key(self) -> tuple:
    return (-self.date.toordinal(), str(self.source_path))
```

---

## 4. SlugRegistry

**Module**: `slugifier.py`  
**Purpose**: Centralised registry that assigns canonical slugs to post
filenames and taxonomy labels, enforcing collision resolution as specified in
`references/page_map_naming_conventions.md` §3.3.

| Field | Type | Notes |
|-------|------|-------|
| `_assignments` | `dict[str, str]` | `raw_label → canonical_slug` |
| `_collisions` | `list[CollisionWarning]` | Populated when two labels map to the same base slug |

**Operations**:

```
register_label(label: str, explicit_map: dict[str, str]) → str
  1. If label in explicit_map, return explicit_map[label] (skip algorithm)
  2. Compute base_slug = slugify(label)   # R-05 algorithm
  3. If base_slug not yet assigned, assign and return it
  4. If base_slug already assigned to a DIFFERENT label:
       - Re-sort all labels in this collision group by Unicode code-point order
       - Assign: group[0] → base_slug, group[1] → base_slug-2, ...
       - Record CollisionWarning
       - Return the slug for `label`
```

**Invariant**: The same `label` always receives the same slug within a single
build run. The registry is rebuilt fresh on every `build` invocation to
guarantee determinism.

---

## 5. TaxonomyTerm

**Module**: `models.py`  
**Purpose**: A single tag or category with its resolved slug and associated
posts.

| Field | Type | Notes |
|-------|------|-------|
| `kind` | `Literal["tag", "category"]` | — |
| `label` | `str` | Raw display label as authored |
| `slug` | `str` | Canonical slug from `SlugRegistry` |
| `posts` | `tuple[Post, ...]` | Posts with this term; in default sort order |
| `url_path` | `str` | `/<blog_dir>/<kind>/<slug>/` |

---

## 6. ArchivePeriod

**Module**: `models.py`  
**Purpose**: A single yearly grouping of posts. Named `ArchivePeriod` rather
than `ArchivePage` to separate the model from the emitted file.

| Field | Type | Notes |
|-------|------|-------|
| `year` | `int` | e.g. `2026` |
| `posts` | `tuple[Post, ...]` | Posts from this year; in default sort order |
| `url_path` | `str` | `/<blog_dir>/archive/<year>/` |

---

## 7. BlogModel

**Module**: `models.py`  
**Purpose**: Root aggregate built by `builder.py`. The complete in-memory
representation of the blog for one build run. Passed wholesale to `emitter.py`.

| Field | Type | Notes |
|-------|------|-------|
| `config` | `BlogConfig` | The resolved config for this run |
| `posts` | `tuple[Post, ...]` | All _visible_ posts in sort order (drafts excluded per config) |
| `draft_posts` | `tuple[Post, ...]` | Drafts (populated regardless; visibility gated by config) |
| `archives` | `tuple[ArchivePeriod, ...]` | Sorted descending by year |
| `tags` | `tuple[TaxonomyTerm, ...]` | Sorted by label (ascending, case-insensitive) |
| `categories` | `tuple[TaxonomyTerm, ...]` | Sorted by label (ascending, case-insensitive) |
| `warnings` | `tuple[BuildWarning, ...]` | Accumulated warnings from build pipeline |

**Constructor invariants**:
- `posts` contains only non-draft posts when `drafts = "hide"`.
- `posts` contains all posts (draft + non-draft) when `drafts = "show"`.
- When `drafts = "fail"` and `draft_posts` is non-empty, `builder.py` raises
  `DraftPostError` before returning a `BlogModel`.
- All tuples are immutable; `BlogModel` is effectively a read-only value object.

---

## 8. BuildWarning

**Module**: `models.py`  
**Purpose**: A structured warning emitted during model construction.

| Field | Type | Notes |
|-------|------|-------|
| `code` | `str` | e.g. `"MISSING_DATE"`, `"SLUG_COLLISION"`, `"MISSING_GITIGNORE"` |
| `message` | `str` | Human-readable explanation |
| `source_path` | `Path \| None` | The file that triggered the warning, if applicable |

---

## 9. BlogPlugin

**Module**: `plugin.py`  
**Purpose**: Thin Zensical plugin adapter. Registered under the
`zensical.plugins` entry point. Delegates entirely to `builder` + `emitter`.

| Method | Trigger | Behaviour |
|--------|---------|-----------|
| `on_pre_build(config)` | Called by Zensical before file collection | Loads `BlogConfig` from `zensical.toml`; calls `builder.build_blog_model()` then `emitter.emit_all()` |
| `on_post_build(config)` | Called by Zensical after site build | Emits nav assurance warning if required |

**Bridge mode**: When Zensical's module registry does not yet call these
methods, the CLI (`cli.py`) calls the same `builder` + `emitter` directly.

---

## 10. Canonical Override File Sentinel

**Not a class — an in-file protocol.**

Any canonical user-authored file that receives an appended listing will contain:

```
<!-- zensical-blog:generated:start -->
<!-- regenerated by zensical-blog; do not edit between these markers -->
...generated Markdown listing...
<!-- zensical-blog:generated:end -->
```

The emitter:
1. Reads the file.
2. If sentinel markers are present: replaces content between them.
3. If absent: appends the full sentinel block at EOF (preceded by a blank line).

User content outside the sentinel is never modified.

---

## State Transitions

```
Source .md files
    │
    ▼  discovery.py
List[Path]
    │
    ▼  parser.py
List[RawPost]
    │
    ▼  builder.py (model layer)
BlogModel  ←── BlogConfig ←── config.py ←── zensical.toml / mkdocs.yml / CLI
    │
    ▼  emitter.py (emission layer)
Files written to docs/.bloggen/  +  sentinel appends to canonical overrides
```

---

## Entity Relationships

```
BlogModel
├── config: BlogConfig
├── posts: Post[]          ──── (sorted, visibility-filtered)
├── draft_posts: Post[]
├── archives: ArchivePeriod[]
│       └── posts: Post[]  (subset of model.posts, by year)
├── tags: TaxonomyTerm[]
│       └── posts: Post[]  (subset of model.posts, by tag)
├── categories: TaxonomyTerm[]
│       └── posts: Post[]  (subset of model.posts, by category)
└── warnings: BuildWarning[]

Post ──── slug resolved via ──── SlugRegistry (post slugs)
TaxonomyTerm ──── slug resolved via ──── SlugRegistry (tag/category slugs)
```
