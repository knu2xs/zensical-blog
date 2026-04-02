# Contract: CLI Commands & Flags

**Module**: `src/zensical_blog/cli.py`  
**Entry point**: `zensical_blog.cli:cli` → installed as `zensical-blog`  
**Date**: 2026-04-01

---

## Root Command

```
zensical-blog [--help]
```

`--help` prints available subcommands. No flags on the root group.

---

## `zensical-blog build`

Run the full blog generation pipeline.

### Signature

```
zensical-blog build [OPTIONS]
```

### Options

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--config PATH` | `Path \| None` | auto-detect | Path to `zensical.toml` or `mkdocs.yml`. Auto-detection searches the current working directory for `zensical.toml` first, then `mkdocs.yml`. |
| `--docs-dir PATH` | `Path \| None` | derived from config | Override the `docs/` directory path. Useful in CI when the working directory differs from the project root. |
| `--apply-nav` | flag | off | Patch the nav in `mkdocs.yml` (non-destructively) to add `Blog: blog/index.md` as a top-level entry if absent. Only valid when `mkdocs.yml` is the active config. |
| `--fail-on-warnings` | flag | off | Exit 1 on any `BuildWarning` instead of proceeding. Recommended for CI. |

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success; all pages generated. |
| `1` | Fatal error (missing `posts_dir`, unreadable config, etc.). |
| `1` | `--fail-on-warnings` set and at least one warning was emitted. |
| `1` | Config has `drafts = "fail"` and at least one draft post exists. |

### Stdout / stderr

- Progress messages → `stderr` (via Python `logging`, level `INFO`).
- Warnings → `stderr` (level `WARNING`).
- No structured output to `stdout` (reserved for future `--json` flag).

### Behaviour contract

1. Resolve `BlogConfig` from flags → `zensical.toml` → `mkdocs.yml` →
   defaults.
2. Call `builder.build_blog_model(config) → BlogModel`.
3. Call `emitter.emit_all(model)`.
4. Emit all `model.warnings` to `stderr`.
5. If `--fail-on-warnings` and `len(model.warnings) > 0`: exit 1.
6. If `--apply-nav`: patch `mkdocs.yml` nav (only when `mkdocs.yml` is
   config source; emit warning and skip otherwise).
7. Exit 0 on clean completion.

---

## `zensical-blog clean`

Remove all files under the generated root (`docs/.bloggen/` by default).

### Signature

```
zensical-blog clean [--config PATH]
```

### Options

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--config PATH` | `Path \| None` | auto-detect | Same auto-detection logic as `build`. Used to resolve `generated_root`. |

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | Generated root removed (or did not exist — idempotent). |
| `1` | Generated root resolution failed (bad config). |

### Behaviour contract

1. Resolve `BlogConfig` (only needs `docs_dir` and `generated_root`).
2. If `generated_root` does not exist: log `INFO "nothing to clean"`, exit 0.
3. Assert `generated_root` is a subdirectory of `docs_dir` (safety check).
4. Remove `generated_root` tree (`shutil.rmtree`).
5. **MUST NOT** touch any file outside `generated_root`.
6. Exit 0.

---

## Auto-detection Logic (shared between subcommands)

```
1. If --config is given: use that file; error if it does not exist.
2. Else: look for zensical.toml in cwd, then parent dirs up to fs root.
3. Else: look for mkdocs.yml in cwd, then parent dirs up to fs root.
4. Else: fatal error "no config file found".
```

Config file directory becomes the implicit project root for all relative
path resolution.
