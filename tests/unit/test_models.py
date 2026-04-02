"""Unit tests for model dataclasses."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from zensical_blog.config import BlogConfig
from zensical_blog.models import (
    ArchivePeriod,
    BlogModel,
    BuildWarning,
    DraftPostError,
    Post,
    TaxonomyTerm,
)


def _make_post(
    slug: str = "test-post",
    post_date: date = date(2026, 1, 1),
    draft: bool = False,
) -> Post:
    return Post(
        source_path=Path(f"/docs/blog/posts/{slug}.md"),
        title="Test Post",
        date=post_date,
        draft=draft,
        tags=(),
        categories=(),
        slug=slug,
        excerpt="Excerpt.",
        body="Body.",
        authors=(),
        url_path=f"/blog/{slug}/",
    )


class TestBuildWarning:
    def test_construction(self) -> None:
        w = BuildWarning(code="TEST", message="msg")
        assert w.code == "TEST"
        assert w.source_path is None

    def test_with_source_path(self) -> None:
        p = Path("/some/file.md")
        w = BuildWarning(code="C", message="m", source_path=p)
        assert w.source_path == p


class TestPost:
    def test_sort_key_descending_date(self) -> None:
        newer = _make_post("newer", date(2026, 4, 1))
        older = _make_post("older", date(2025, 1, 1))
        assert newer.sort_key < older.sort_key

    def test_sort_key_tie_broken_by_path(self) -> None:
        p1 = Post(
            source_path=Path("/docs/blog/posts/aaa.md"),
            title="A",
            date=date(2026, 1, 1),
            draft=False,
            tags=(),
            categories=(),
            slug="aaa",
            excerpt="",
            body="",
            authors=(),
            url_path="/blog/aaa/",
        )
        p2 = Post(
            source_path=Path("/docs/blog/posts/bbb.md"),
            title="B",
            date=date(2026, 1, 1),
            draft=False,
            tags=(),
            categories=(),
            slug="bbb",
            excerpt="",
            body="",
            authors=(),
            url_path="/blog/bbb/",
        )
        assert p1.sort_key < p2.sort_key  # "aaa" < "bbb" lexicographically

    def test_frozen(self) -> None:
        import dataclasses

        p = _make_post()
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.slug = "changed"  # type: ignore[misc]


class TestTaxonomyTerm:
    def test_construction(self) -> None:
        post = _make_post()
        term = TaxonomyTerm(
            kind="tag",
            label="Python",
            slug="python",
            posts=(post,),
            url_path="/blog/tag/python/",
        )
        assert term.kind == "tag"
        assert len(term.posts) == 1


class TestArchivePeriod:
    def test_construction(self) -> None:
        post = _make_post()
        period = ArchivePeriod(
            year=2026,
            posts=(post,),
            url_path="/blog/archive/2026/",
        )
        assert period.year == 2026


class TestBlogModel:
    def test_construction(self) -> None:
        cfg = BlogConfig(docs_dir=Path("/tmp/docs"))
        model = BlogModel(
            config=cfg,
            posts=(),
            draft_posts=(),
            archives=(),
            tags=(),
            categories=(),
            warnings=(),
        )
        assert model.posts == ()
        assert model.warnings == ()

    def test_draft_post_error(self) -> None:
        assert issubclass(DraftPostError, Exception)
