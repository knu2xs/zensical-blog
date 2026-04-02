# Research: Zensical Blog Module (Sidecar, Bridge Mode)

**Phase**: 0 — Pre-design research  
**Date**: 2026-04-01  
**Resolves unknowns from**: `plan.md` Technical Context

---

## R-01: Zensical Plugin Entry Point & Bridge Mode Invocation

**Question**: How should the plugin be registered and invoked if Zensical's
public module API is not yet released?

**Decision**: Use a forward-declared `zensical.plugins` Python entry point in
`pyproject.toml`. In bridge mode (v1), the plugin class's lifecycle methods
(e.g., `on_pre_build`) are no-ops when Zensical does not call them; the
standalone `zensical-blog build` CLI is the primary invocation path. The entry
point is registered now so that when Zensical's module registry activates it,
no packaging change is needed — only the adapter method bodies change.

**Rationale**: Entry points are resolved lazily; registering `zensical.plugins`
now is zero-cost when the host (Zensical) does not enumerate it. This is the
standard pattern for forward-compatible Python plugin registration (cf.
pytest plugins, Sphinx extensions).

**Alternatives considered**:
- Wait until Zensical's API is released → rejected: delays plugin-mode UX and
  creates a packaging change later.
- Use MkDocs `BasePlugin` as a proxy → rejected by user requirement: `mkdocs`
  must not be a dependency.

**Bridge invocation contract**:
```
zensical-blog build   →  CLI entry point  →  builder + emitter
zensical build        →  Zensical enumerates zensical.plugins entry points
                          →  BlogPlugin.on_pre_build()  →  builder + emitter
```
Both paths call the same `builder.build_blog_model()` and
`emitter.emit_all()`. The plugin is a thin adapter only.

---

## R-02: YAML Front Matter Parsing — `python-frontmatter`

**Question**: Which library should parse YAML front matter from `.md` files?
What are the API patterns?

**Decision**: `python-frontmatter` (pip install name). Import as `frontmatter`.

**Key API**:
```python
import frontmatter

post = frontmatter.load("path/to/post.md")
post.metadata          # dict of front matter
post.content           # str body after front matter
```

**Rationale**: Purpose-built for YAML/TOML/JSON front matter in Markdown.
Handles edge cases (no front matter, empty front matter, nested YAML). Actively
maintained. 100-line implementation with no hidden cost.

**Alternatives considered**:
- `python-markdown` + custom regex → rejected: fragile, reinvents a solved
  problem.
- `pyyaml` raw parsing → rejected: requires manual front matter delimiter
  detection; error-prone.

---

## R-03: Round-Trip YAML Editing — `ruamel.yaml`

**Question**: How do we read and patch `mkdocs.yml` (for `--apply-nav` and
compat config reading) without destroying comments, ordering, or formatting?

**Decision**: `ruamel.yaml` with `YAML(typ='rt')` (round-trip mode).

**Key API**:
```python
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True
with open("mkdocs.yml") as f:
    data = yaml.load(f)

# patch
nav = data.setdefault("nav", [])
nav.insert(0, {"Blog": "blog/index.md"})

with open("mkdocs.yml", "w") as f:
    yaml.dump(data, f)
```

**Rationale**: PyYAML does not preserve comments or key ordering, making it
destructive for user-authored config files. `ruamel.yaml` is the canonical
round-trip YAML library in the Python ecosystem.

**Alternatives considered**:
- PyYAML → rejected: destroys comments and quote styles.
- Manual string patching → rejected: fragile, breaks on non-trivial YAML.

**Scope**: `ruamel.yaml` is used only in two places: (1) reading `plugins:`
block for compat config, (2) patching nav for `--apply-nav`. Both are in
`config.py`.

---

## R-04: TOML Parsing — stdlib `tomllib`

**Question**: How do we read `zensical.toml`?

**Decision**: `tomllib` from the Python 3.11 standard library.

**Key API**:
```python
import tomllib

with open("zensical.toml", "rb") as f:
    data = tomllib.load(f)

blog_config = data.get("project", {}).get("extra", {}).get("zensical_blog", {})
```

**Rationale**: Zero external dependency. Python 3.11+ is the declared minimum
runtime (see Technical Context). No backport needed.

**Alternatives considered**:
- `tomli` (third-party backport) → rejected: unnecessary given Python 3.11+
  requirement.
- `tomlkit` → rejected: adds a dependency for a stdlib capability; `tomlkit`'s
  round-trip features are not needed for config reading.

---

## R-05: Deterministic Slugification — `unicodedata` stdlib

**Question**: How do we implement the deterministic slug algorithm specified
in `references/page_map_naming_conventions.md` §3.2?

**Decision**: Pure `unicodedata` + `re` stdlib. No third-party library.

**Implementation pattern**:
```python
import unicodedata
import re

def slugify(label: str) -> str:
    label = label.strip()
    label = unicodedata.normalize("NFKD", label)
    label = "".join(
        c for c in label
        if unicodedata.category(c) != "Mn"   # strip combining marks
    )
    label = label.casefold()
    label = re.sub(r"[^a-z0-9]+", "-", label)
    label = label.strip("-")
    label = label[:80].rstrip("-")
    return label or "x"
```

**Rationale**: `unicodedata` is stdlib, locale-independent, and produces
identical output on CPython across platforms and future Rust-embedded runtimes.
The algorithm is exactly as specified; no third-party slugify library is needed
and all carry hidden behavioural differences.

**Alternatives considered**:
- `python-slugify` → rejected: adds a dependency; its `unicode_slug` option
  uses a different normalization approach that may diverge from the spec.
- `awesome-slugify` → rejected: unmaintained.

---

## R-06: CLI Framework — `click`

**Question**: Which CLI framework best fits `build` / `clean` subcommands with
typed options?

**Decision**: `click` with a `@click.group()` root and `@root.command()`
subcommands.

**Key pattern**:
```python
import click

@click.group()
def cli() -> None:
    """zensical-blog — Sidecar blog generator for Zensical."""

@cli.command()
@click.option("--config", type=click.Path(), default=None)
@click.option("--docs-dir", type=click.Path(), default=None)
@click.option("--apply-nav", is_flag=True, default=False)
@click.option("--fail-on-warnings", is_flag=True, default=False)
def build(...) -> None: ...

@cli.command()
def clean() -> None: ...
```

**Entry point** in `pyproject.toml`:
```toml
[project.scripts]
zensical-blog = "zensical_blog.cli:cli"
```

**Rationale**: `click` provides subcommand dispatch, auto-generated `--help`,
type coercion, and clean testability (`CliRunner`). For two subcommands with
typed flags, `click` is standard practice and substantially lower boilerplate
than `argparse`.

**Alternatives considered**:
- `argparse` (stdlib) → rejected: verbose subcommand setup; poor `--help` UX.
- `typer` → rejected: adds a `typer` + `rich` dependency chain; overkill for
  two commands.

---

## R-07: `src`-Layout Packaging with `pyproject.toml`

**Question**: Which PEP 517 build backend should be used to support
`pip install git+https://…` from a `src`-layout project?

**Decision**: `hatchling` as the build backend.

**Minimal `pyproject.toml` structure**:
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "zensical-blog"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1",
    "python-frontmatter>=1.1",
    "ruamel.yaml>=0.18",
]

[project.scripts]
zensical-blog = "zensical_blog.cli:cli"

[project.entry-points."zensical.plugins"]
zensical_blog = "zensical_blog.plugin:BlogPlugin"

[tool.hatch.build.targets.wheel]
packages = ["src/zensical_blog"]
```

**Rationale**: `hatchling` is the default backend for new Python projects
(used by Hatch, endorsed by PyPA). It natively supports `src`-layout via
`[tool.hatch.build.targets.wheel] packages = ["src/..."]` with zero extra
configuration. Works with `pip install git+https://…` out of the box.

**Alternatives considered**:
- `flit_core` → viable but requires `__version__` in `__init__.py` and has
  less flexible package discovery.
- `setuptools` → more config required for `src`-layout; works but less modern.

---

## R-08: Determinism Strategy — Two-Key Post Sort

**Question**: How do we guarantee byte-for-byte deterministic output when two
posts share the same date?

**Decision**: Sort posts by `(date, source_path)` — date descending, then
source_path ascending (Unicode order). `source_path` is always unique (no two
files share the same absolute path), so this produces a total ordering.

**Rationale**: Without a secondary sort key, Python's `sorted()` preserves
insertion order (filesystem glob order), which varies across OS and filesystem
implementations. Adding `source_path` as a tiebreaker makes output identical
regardless of discovery order.

---

## R-09: Override Append — Sentinel Comment Strategy

**Question**: How do we append a generated listing to a user-authored file
idempotently (i.e., replace the listing on subsequent builds rather than
double-appending)?

**Decision**: Use an HTML comment sentinel block:

```markdown
<!-- zensical-blog:generated:start -->
...generated listing...
<!-- zensical-blog:generated:end -->
```

On each build: if the sentinel block exists in the file, replace the content
between the markers. If absent, append the full sentinel block at the end.
User content before the block is never touched.

**Rationale**: Idempotent, human-readable, survives manual edits to user
content without accidental data loss. The sentinel is a valid HTML comment
and is invisible in rendered Markdown.

**Alternatives considered**:
- Always overwrite the file → rejected: destroys user content (violates FR-016).
- Track generated files in a manifest → rejected: adds state that becomes stale;
  more complex than a sentinel.

---

## R-10: Generated Root & `.gitignore` Detection

**Question**: How should the module detect whether `docs/.bloggen/` is in
`.gitignore` to emit the advisory warning?

**Decision**: Read `.gitignore` from the project root (same directory as
`zensical.toml` or `mkdocs.yml`) and check if `.bloggen` or `docs/.bloggen`
appears as a non-commented line. If absent, emit a `WARNING` log message
(not an error) recommending the user add it.

**Implementation**: Simple line-by-line scan — no `gitpython` or subprocess
dependency needed for this advisory check.

---

## Summary Table

| ID | Decision | Library/Approach |
|----|----------|-----------------|
| R-01 | Plugin bridge | `zensical.plugins` entry point (forward-declared); CLI is primary in v1 |
| R-02 | Front matter parsing | `python-frontmatter` |
| R-03 | YAML round-trip | `ruamel.yaml` |
| R-04 | TOML parsing | `tomllib` (stdlib) |
| R-05 | Slugification | `unicodedata` + `re` (stdlib) |
| R-06 | CLI framework | `click` |
| R-07 | Build backend | `hatchling` |
| R-08 | Determinism | Two-key sort: `(date desc, source_path asc)` |
| R-09 | Idempotent append | HTML comment sentinel block |
| R-10 | `.gitignore` check | Simple line scan, advisory warning only |

**All NEEDS CLARIFICATION items from Technical Context resolved. Proceeding to Phase 1.**
