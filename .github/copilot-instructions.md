# zensical-blog Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-01

## Active Technologies

- Python 3.11 + `python-frontmatter` (YAML front matter parsing), `click` (CLI), `ruamel.yaml` (round-trip YAML read/write for `mkdocs.yml` compat + `--apply-nav`); `tomllib` (stdlib, Python 3.11+); `unicodedata` (stdlib, slugification). The `mkdocs` package is NOT a dependency. (001-zensical-blog-module)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11: Follow standard conventions

## Recent Changes

- 001-zensical-blog-module: Added Python 3.11 + `python-frontmatter` (YAML front matter parsing), `click` (CLI), `ruamel.yaml` (round-trip YAML read/write for `mkdocs.yml` compat + `--apply-nav`); `tomllib` (stdlib, Python 3.11+); `unicodedata` (stdlib, slugification). The `mkdocs` package is NOT a dependency.

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
