"""Zensical Blog — sidecar blog generator for Zensical documentation sites."""

from __future__ import annotations

from zensical_blog.builder import build_blog_model
from zensical_blog.config import BlogConfig
from zensical_blog.emitter import emit_all
from zensical_blog.models import BlogModel
from zensical_blog.plugin import BlogPlugin

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "BlogConfig",
    "BlogModel",
    "BlogPlugin",
    "build_blog_model",
    "emit_all",
]
