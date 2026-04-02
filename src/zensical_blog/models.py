"""Core data model classes for the blog pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from zensical_blog.config import BlogConfig


@dataclass(frozen=True)
class BuildWarning:
    """A structured warning emitted during model construction or emission."""

    code: str
    message: str
    source_path: Path | None = None


class DraftPostError(Exception):
    """Raised when ``drafts="fail"`` and at least one draft post exists."""


@dataclass(frozen=True)
class Post:
    """A single validated, resolved blog post."""

    source_path: Path
    title: str
    date: date
    draft: bool
    tags: tuple[str, ...]
    categories: tuple[str, ...]
    slug: str
    excerpt: str
    body: str
    authors: tuple[str, ...]
    url_path: str

    @property
    def sort_key(self) -> tuple[int, str]:
        """Two-key sort: descending date, ascending source path for ties."""
        return (-self.date.toordinal(), str(self.source_path))


@dataclass(frozen=True)
class TaxonomyTerm:
    """A single tag or category with its resolved slug and associated posts."""

    kind: Literal["tag", "category"]
    label: str
    slug: str
    posts: tuple[Post, ...]
    url_path: str


@dataclass(frozen=True)
class ArchivePeriod:
    """A single yearly grouping of posts."""

    year: int
    posts: tuple[Post, ...]
    url_path: str


@dataclass(frozen=True)
class BlogModel:
    """Root aggregate produced by ``builder.build_blog_model``.

    Passed wholesale to ``emitter.emit_all``. All fields are immutable tuples.
    """

    config: BlogConfig  # type annotation is a forward reference under PEP 563
    posts: tuple[Post, ...]
    draft_posts: tuple[Post, ...]
    archives: tuple[ArchivePeriod, ...]
    tags: tuple[TaxonomyTerm, ...]
    categories: tuple[TaxonomyTerm, ...]
    warnings: tuple[BuildWarning, ...]
