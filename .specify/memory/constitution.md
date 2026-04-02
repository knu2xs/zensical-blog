<!--
SYNC IMPACT REPORT
==================
Version change: (none) → 1.0.0
Added sections: Core Principles (I–VI), Tech Stack & Packaging Constraints,
  Development Workflow, Governance
Removed sections: all template placeholders replaced
Modified principles: N/A (initial version)
Templates reviewed:
  ✅ .specify/templates/plan-template.md  — Constitution Check gate is
     already parameterized ("Gates determined based on constitution file");
     no hard-coded principle names to update.
  ✅ .specify/templates/spec-template.md  — No constitution references;
     placeholder-only; no changes required.
  ✅ .specify/templates/tasks-template.md — No constitution references;
     placeholder-only; no changes required.
Follow-up TODOs: none — all fields resolved.
-->

# Zensical Blog Constitution

## Core Principles

### I. Python Standards & Packaging (NON-NEGOTIABLE)

All source code MUST reside in `src/zensical_blog/`. Every Python file MUST
conform to PEP 8; this is enforced by a linter (e.g., `ruff` or `flake8`) as
part of the standard test run. Type annotations are REQUIRED on all public
interfaces (functions, methods, dataclasses). Installation MUST be controlled
by `pyproject.toml`, supporting `pip install git+https://…` directly from the
GitHub repository with no additional setup steps.

**Rationale**: PEP 8 and `src`-layout are the Python community standard for
installable packages. A `pyproject.toml`-first approach keeps build metadata
in one place and makes pip-from-GitHub trivial.

### II. Bridge-First, API-Forward Design (NON-NEGOTIABLE)

The module MUST ship today as an external generator ("bridge mode") that does
NOT bind to any internal Zensical API. All internal boundaries (post model,
archive model, taxonomy model) MUST be designed so they can map cleanly to
Zensical's future public module API without a breaking rewrite. Private or
undocumented Zensical internals MUST NOT be imported or monkey-patched.

**Rationale**: Zensical is in alpha; its public module API is not yet stable.
Coupling to internals now would force a full rewrite when the public API
ships. Bridge mode ships value today while protecting the investment.

### III. Test-First (NON-NEGOTIABLE)

TDD is mandatory. For every feature: tests MUST be written and reviewed before
implementation begins; tests MUST be confirmed to fail (red); only then is the
implementation written (green); refactor last. `pytest` is the test runner.
Integration tests are REQUIRED for the full generation pipeline (discover →
parse → sort → emit). Unit tests are REQUIRED for all model and utility logic.

**Rationale**: A static-site generator produces file-system artifacts; without
a test-first discipline regressions are invisible until a site breaks in
production.

### IV. Deterministic & Safe Output (NON-NEGOTIABLE)

All generated outputs MUST be byte-for-byte identical given the same inputs
(post content + configuration). The generator MUST write only within the
designated generated root (`docs/.bloggen/`) and explicit user-authored
override files (append-only, never overwriting user content). No file outside
these boundaries MUST ever be created, modified, or deleted without an
explicit user opt-in flag (e.g., `--apply-nav`).

**Rationale**: Determinism enables stable diffs and reliable CI. The safety
boundary prevents data loss and ensures the module can never corrupt a user's
existing documentation tree.

### V. Clean Model/Emission Separation

The codebase MUST maintain a strict architectural boundary between:

- **Model layer** — discover, read, parse, sort, and group posts; no I/O
  beyond reading source files.
- **Emission layer** — translate models into Markdown pages and write to the
  generated root; no business logic.

Crossing the boundary (e.g., writing files from within model code, or
deriving sort order in the emission layer) MUST be rejected in code review.

**Rationale**: This boundary makes it possible to swap the emission layer for
a native Zensical component emitter when the public API is available, without
touching any model or parsing logic.

### VI. Simplicity & YAGNI

Features are implemented only when required by the current specification. No
speculative abstractions, premature generalization, or complexity layers that
are not justified by an explicit requirement in the active spec. Every
non-trivial abstraction MUST be accompanied by a recorded justification in the
plan's Complexity Tracking table.

**Rationale**: This project's surface area expands as Zensical matures; over-
engineering early creates drag when alignment to the future native API
requires structural changes.

## Tech Stack & Packaging Constraints

- **Language**: Python 3.11 or later.
- **Source layout**: `src/zensical_blog/` (PEP 517 `src`-layout).
- **Build & install**: `pyproject.toml` with `[build-system]`; MUST be
  installable via `pip install git+https://github.com/<org>/zensical-blog.git`.
- **Test runner**: `pytest`; tests live in `tests/`.
- **Linting/formatting**: `ruff` (or equivalent PEP-8 enforcer); runs as part
  of the standard test invocation.
- **Zensical dependency**: treated as an optional/soft integration; the core
  generation logic MUST NOT import Zensical internals at module level.
- **No external runtime dependencies** beyond the Python standard library and
  a YAML/TOML parser unless justified in the plan.

## Development Workflow

- All work proceeds on feature branches; PRs target `main`.
- Before any implementation begins, the **Constitution Check** gate in the
  plan MUST be marked passing:
  - Principle I: source layout confirmed, `pyproject.toml` present.
  - Principle II: no internal Zensical imports planned.
  - Principle III: test scaffolding committed and failing before code.
  - Principle IV: generated root path is `docs/.bloggen/`; no unbounded writes.
  - Principle V: model and emission layers identified in the plan structure.
  - Principle VI: no complexity violations in the plan, or each is logged in
    the Complexity Tracking table.
- The Constitution Check MUST be re-verified after Phase 1 design (before
  tasks are generated).
- A `CHANGELOG.md` entry MUST accompany every version bump.
- All PRs require at least one review confirming constitution compliance before
  merge.

## Governance

This constitution supersedes all other development practices. Any conflict
between a decision document, PR description, or team convention and this
constitution resolves in favor of the constitution.

**Amendment procedure**: Amendments MUST include (a) documented rationale,
(b) a version increment following the semantic versioning policy below, and
(c) updates to all dependent templates and workflow documents. Amendments are
recorded via a PR that modifies this file and is approved by at least one
maintainer.

**Versioning policy**:
- MAJOR bump — backward-incompatible governance change: a principle is
  removed, fundamentally redefined, or a NON-NEGOTIABLE designation is
  added or removed.
- MINOR bump — a new principle or section is added, or materially expanded
  guidance is introduced.
- PATCH bump — clarifications, wording improvements, typo fixes, or
  non-semantic refinements.

**Compliance review**: Every PR description MUST contain a "Constitution
Check" section confirming no principles are violated, or documenting an
approved exception with justification.

**Version**: 1.0.0 | **Ratified**: 2026-04-01 | **Last Amended**: 2026-04-01
