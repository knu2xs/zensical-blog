"""Click CLI entry point with ``build`` and ``clean`` subcommands."""

from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path

import click

from zensical_blog.builder import build_blog_model
from zensical_blog.config import load_config
from zensical_blog.emitter import emit_all
from zensical_blog.models import DraftPostError

log = logging.getLogger(__name__)


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )


@click.group()
def cli() -> None:
    """zensical-blog — Sidecar blog generator for Zensical documentation sites."""
    _configure_logging()


@cli.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to zensical.toml or mkdocs.yml. Auto-detected when omitted.",
)
@click.option(
    "--docs-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Override the docs/ directory path.",
)
@click.option(
    "--apply-nav",
    is_flag=True,
    default=False,
    help="Patch mkdocs.yml nav to add the Blog entry if absent.",
)
@click.option(
    "--fail-on-warnings",
    is_flag=True,
    default=False,
    help="Exit 1 if any BuildWarning is emitted. Recommended for CI.",
)
def build(
    config_path: Path | None,
    docs_dir: Path | None,
    apply_nav: bool,
    fail_on_warnings: bool,
) -> None:
    """Run the full blog generation pipeline."""
    try:
        cfg = load_config(
            config_path=config_path,
            docs_dir=docs_dir,
            overrides=(
                {"fail_on_warnings": fail_on_warnings} if fail_on_warnings else {}
            ),
        )
    except FileNotFoundError as exc:
        click.echo(f"ERROR: {exc}", err=True)
        sys.exit(1)

    try:
        model = build_blog_model(cfg)
    except DraftPostError as exc:
        click.echo(f"ERROR: {exc}", err=True)
        sys.exit(1)

    emit_all(model)

    # Emit all warnings to stderr
    for warning in model.warnings:
        log.warning(warning.message)

    if fail_on_warnings and model.warnings:
        click.echo(
            f"ERROR: {len(model.warnings)} warning(s) emitted"
            " and --fail-on-warnings is set.",
            err=True,
        )
        sys.exit(1)

    if apply_nav:
        _patch_nav(cfg)

    log.info("Blog generation complete.")


@cli.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to zensical.toml or mkdocs.yml. Auto-detected when omitted.",
)
def clean(config_path: Path | None) -> None:
    """Remove all generated artifacts under docs/.bloggen/."""
    try:
        cfg = load_config(config_path=config_path)
    except FileNotFoundError as exc:
        click.echo(f"ERROR: {exc}", err=True)
        sys.exit(1)

    generated_root = cfg.generated_root

    # Safety: generated_root must be inside docs_dir
    try:
        generated_root.relative_to(cfg.docs_dir)
    except ValueError:
        click.echo(
            f"ERROR: generated_root {generated_root} is not inside"
            f" docs_dir {cfg.docs_dir}.",
            err=True,
        )
        sys.exit(1)

    if not generated_root.exists():
        log.info("Nothing to clean — %s does not exist.", generated_root)
        return

    shutil.rmtree(generated_root)
    log.info("Removed %s", generated_root)


def _patch_nav(cfg) -> None:  # type: ignore[no-untyped-def]
    """Patch ``mkdocs.yml`` nav to add the Blog entry as the first top-level item."""
    from ruamel.yaml import YAML

    mkdocs_yml = cfg.docs_dir.parent / "mkdocs.yml"
    if not mkdocs_yml.is_file():
        log.warning(
            "--apply-nav: mkdocs.yml not found at %s — skipping nav patch.", mkdocs_yml
        )
        return

    yaml = YAML()
    yaml.preserve_quotes = True
    with open(mkdocs_yml, encoding="utf-8") as fh:
        data = yaml.load(fh) or {}

    nav = data.get("nav") or []

    # Check if entry already present
    for entry in nav:
        if isinstance(entry, dict):
            for label, path in entry.items():
                if label == cfg.nav_label and path == cfg.nav_path:
                    log.info("--apply-nav: Nav entry already present — no change.")
                    return

    # Insert as first entry
    nav.insert(0, {cfg.nav_label: cfg.nav_path})
    data["nav"] = nav

    with open(mkdocs_yml, "w", encoding="utf-8") as fh:
        yaml.dump(data, fh)

    log.info(
        "--apply-nav: Added %r: %r to mkdocs.yml nav.", cfg.nav_label, cfg.nav_path
    )
