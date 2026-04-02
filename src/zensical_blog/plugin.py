"""Zensical plugin adapter.

Registered under the ``zensical.plugins`` entry point. In bridge mode (v1),
the plugin lifecycle methods delegate to the same ``builder`` + ``emitter``
pipeline used by the CLI.

**IMPORTANT**: This module MUST NOT import ``mkdocs`` at any level.
The class MUST NOT subclass any external base class (FR-032).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from zensical_blog.builder import build_blog_model
from zensical_blog.config import load_config
from zensical_blog.emitter import emit_all

log = logging.getLogger(__name__)


class BlogPlugin:
    """Thin Zensical plugin adapter for the blog generation pipeline.

    Registered as ``zensical_blog`` under the ``zensical.plugins`` entry
    point.  When Zensical's module registry is active, it calls
    :meth:`on_pre_build` before site file collection and :meth:`on_post_build`
    after the site is built.

    In bridge mode (Zensical module API not yet active), use the CLI instead::

        zensical-blog build

    Both paths call the same :func:`~zensical_blog.builder.build_blog_model`
    and :func:`~zensical_blog.emitter.emit_all` functions.
    """

    def on_pre_build(
        self,
        config: dict[str, Any] | None = None,
        config_path: Path | None = None,
    ) -> None:
        """Run blog generation before Zensical's file collection phase.

        Parameters
        ----------
        config:
            Optional config dict passed by Zensical's plugin host.  When
            provided, the ``zensical_blog`` key is used as raw config data.
        config_path:
            Optional explicit path to ``zensical.toml`` or ``mkdocs.yml``.
            Useful for testing.
        """
        overrides: dict[str, Any] = {}
        if config and "zensical_blog" in config:
            overrides = dict(config["zensical_blog"])

        cfg = load_config(config_path=config_path, overrides=overrides)
        model = build_blog_model(cfg)
        emit_all(model)

        for warning in model.warnings:
            log.warning(warning.message)

    def on_post_build(
        self,
        config: dict[str, Any] | None = None,
    ) -> None:
        """Post-build hook. Currently a no-op (reserved for future use)."""
