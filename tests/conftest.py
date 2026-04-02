"""Shared pytest fixtures for zensical-blog tests."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest


@pytest.fixture()
def blog_scaffold(tmp_path: Path) -> Path:
    """Create a minimal Zensical project scaffold in *tmp_path*.

    Layout::

        tmp_path/
        ├── zensical.toml
        └── docs/
            └── blog/
                └── posts/

    Returns the project root (``tmp_path``).
    """
    posts_dir = tmp_path / "docs" / "blog" / "posts"
    posts_dir.mkdir(parents=True)

    toml = tmp_path / "zensical.toml"
    toml.write_text(
        textwrap.dedent("""\
            [project]
            site_name = "Test Site"

            [project.extra.zensical_blog]
            blog_dir = "blog"
            posts_dir = "blog/posts"
            drafts = "hide"
        """),
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture()
def make_post(blog_scaffold: Path):
    """Return a factory that writes a Markdown post file.

    Usage::

        path = make_post("my-post.md", {"title": "Hi", "date": "2026-01-01"}, "Body")
    """

    def _factory(
        filename: str,
        front_matter: dict,
        body: str = "Post body.",
        subdir: str = "docs/blog/posts",
    ) -> Path:
        import yaml  # python-frontmatter brings in pyyaml

        fm_str = yaml.dump(front_matter, default_flow_style=False).strip()
        content = f"---\n{fm_str}\n---\n\n{body}\n"
        target = blog_scaffold / subdir / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    return _factory
