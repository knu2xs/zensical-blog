"""Integration tests for canonical override file preservation (sentinel protocol)."""

from __future__ import annotations

from pathlib import Path

from zensical_blog.builder import build_blog_model
from zensical_blog.config import load_config
from zensical_blog.emitter import emit_all


def _scaffold(tmp_path: Path):
    posts_dir = tmp_path / "docs" / "blog" / "posts"
    posts_dir.mkdir(parents=True)
    toml = tmp_path / "zensical.toml"
    toml.write_text(
        "[project.extra.zensical_blog]\n"
        "blog_dir = \"blog\"\n"
        "posts_dir = \"blog/posts\"\n",
        encoding="utf-8",
    )
    (tmp_path / ".gitignore").write_text("docs/.bloggen/\n", encoding="utf-8")
    return load_config(config_path=toml)


def _make_post(posts_dir: Path, filename: str, title: str, post_date: str) -> None:
    content = f"---\ntitle: {title}\ndate: {post_date}\n---\n\nBody.\n"
    (posts_dir / filename).write_text(content, encoding="utf-8")


class TestSentinelProtocol:
    def test_user_preamble_preserved(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post(posts_dir, "post.md", "Post", "2026-01-01")

        # Pre-create canonical file with user preamble
        index = tmp_path / "docs" / "blog" / "index.md"
        index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text("# My Blog\n\nWelcome text.\n", encoding="utf-8")

        model = build_blog_model(cfg)
        emit_all(model)

        content = index.read_text(encoding="utf-8")
        assert "# My Blog" in content
        assert "Welcome text." in content
        assert "Post" in content  # generated listing appended

    def test_second_build_preamble_preserved_no_duplication(
        self, tmp_path: Path
    ) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post(posts_dir, "post.md", "Post A", "2026-01-01")

        index = tmp_path / "docs" / "blog" / "index.md"
        index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text("# Custom Title\n\nMy intro.\n", encoding="utf-8")

        model = build_blog_model(cfg)
        emit_all(model)
        emit_all(model)  # Second build

        content = index.read_text(encoding="utf-8")
        assert "# Custom Title" in content
        assert content.count("# Custom Title") == 1
        assert content.count("<!-- zensical-blog:generated:start -->") == 1

    def test_generated_listing_updated_on_new_post(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post(posts_dir, "first.md", "First Post", "2026-01-01")

        model = build_blog_model(cfg)
        emit_all(model)

        # Add a second post
        _make_post(posts_dir, "second.md", "Second Post", "2026-02-01")
        model2 = build_blog_model(cfg)
        emit_all(model2)

        index = tmp_path / "docs" / "blog" / "index.md"
        content = index.read_text(encoding="utf-8")
        assert "First Post" in content
        assert "Second Post" in content
        # Only one sentinel block
        assert content.count("<!-- zensical-blog:generated:start -->") == 1

    def test_fresh_canonical_created_when_absent(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post(posts_dir, "post.md", "Post", "2026-01-01")

        # Ensure canonical does NOT pre-exist
        index = tmp_path / "docs" / "blog" / "index.md"
        assert not index.exists()

        model = build_blog_model(cfg)
        emit_all(model)

        assert index.exists()
        content = index.read_text(encoding="utf-8")
        assert "<!-- zensical-blog:generated:start -->" in content
        assert "Post" in content
