"""Integration tests for the full build pipeline."""

from __future__ import annotations

from pathlib import Path

import pytest

from zensical_blog.builder import build_blog_model
from zensical_blog.config import BlogConfig, load_config
from zensical_blog.emitter import emit_all
from zensical_blog.models import DraftPostError

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_post_file(
    posts_dir: Path,
    filename: str,
    title: str,
    post_date: str,
    body: str = "Post body.",
    draft: bool = False,
    tags: list[str] | None = None,
    categories: list[str] | None = None,
    slug: str | None = None,
) -> Path:
    fm_lines = [f"title: {title}", f"date: {post_date}"]
    if draft:
        fm_lines.append("draft: true")
    if tags:
        fm_lines.append(f"tags: {tags}")
    if categories:
        fm_lines.append(f"categories: {categories}")
    if slug:
        fm_lines.append(f"slug: {slug}")
    fm = "\n".join(fm_lines)
    content = f"---\n{fm}\n---\n\n{body}\n"
    path = posts_dir / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _scaffold(tmp_path: Path) -> BlogConfig:
    """Create a minimal zensical.toml scaffold and return a resolved BlogConfig."""
    posts_dir = tmp_path / "docs" / "blog" / "posts"
    posts_dir.mkdir(parents=True)
    toml = tmp_path / "zensical.toml"
    toml.write_text(
        "[project.extra.zensical_blog]\n"
        "blog_dir = \"blog\"\n"
        "posts_dir = \"blog/posts\"\n"
        "drafts = \"hide\"\n",
        encoding="utf-8",
    )
    (tmp_path / ".gitignore").write_text("docs/.bloggen/\n", encoding="utf-8")
    return load_config(config_path=toml)


# ---------------------------------------------------------------------------
# US1: Blog index generation
# ---------------------------------------------------------------------------


class TestBlogIndexGeneration:
    def test_two_posts_newest_first(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"

        _make_post_file(posts_dir, "old.md", "Old Post", "2025-01-01")
        _make_post_file(posts_dir, "new.md", "New Post", "2026-04-01")

        model = build_blog_model(cfg)
        emit_all(model)

        index = tmp_path / "docs" / "blog" / "index.md"
        assert index.exists()
        content = index.read_text(encoding="utf-8")
        assert "New Post" in content
        assert "Old Post" in content
        assert content.index("New Post") < content.index("Old Post")

    def test_second_build_no_duplicate_sentinel(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post_file(posts_dir, "post.md", "My Post", "2026-01-01")

        model = build_blog_model(cfg)
        emit_all(model)
        emit_all(model)  # Second run — must not duplicate

        index = tmp_path / "docs" / "blog" / "index.md"
        content = index.read_text(encoding="utf-8")
        assert content.count("<!-- zensical-blog:generated:start -->") == 1
        assert content.count("<!-- zensical-blog:generated:end -->") == 1

    def test_no_posts_generates_placeholder(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        model = build_blog_model(cfg)
        emit_all(model)

        index = tmp_path / "docs" / "blog" / "index.md"
        assert index.exists()

    def test_generated_root_created(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post_file(posts_dir, "post.md", "P", "2026-01-01")

        model = build_blog_model(cfg)
        emit_all(model)

        assert (tmp_path / "docs" / ".bloggen").is_dir()


class TestDraftFiltering:
    def test_draft_hidden_by_default(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post_file(posts_dir, "pub.md", "Public", "2026-01-01")
        _make_post_file(posts_dir, "draft.md", "Draft Post", "2026-01-02", draft=True)

        model = build_blog_model(cfg)
        emit_all(model)

        index = tmp_path / "docs" / "blog" / "index.md"
        content = index.read_text(encoding="utf-8")
        assert "Public" in content
        assert "Draft Post" not in content

    def test_draft_shown_when_configured(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        cfg.drafts = "show"
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post_file(posts_dir, "draft.md", "Draft Post", "2026-01-01", draft=True)

        model = build_blog_model(cfg)
        assert len(model.posts) == 1
        assert model.posts[0].title == "Draft Post"

    def test_draft_fail_raises(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        cfg.drafts = "fail"
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post_file(posts_dir, "draft.md", "Draft Post", "2026-01-01", draft=True)

        with pytest.raises(DraftPostError):
            build_blog_model(cfg)


# ---------------------------------------------------------------------------
# US2: Archive pages
# ---------------------------------------------------------------------------


class TestArchivePages:
    def test_two_years_generate_separate_pages(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post_file(posts_dir, "p2025.md", "Post 2025", "2025-06-15")
        _make_post_file(posts_dir, "p2026.md", "Post 2026", "2026-03-01")

        model = build_blog_model(cfg)
        emit_all(model)

        archive_2025 = tmp_path / "docs" / "blog" / "archive" / "2025.md"
        archive_2026 = tmp_path / "docs" / "blog" / "archive" / "2026.md"
        assert archive_2025.exists()
        assert archive_2026.exists()

        assert "Post 2025" in archive_2025.read_text(encoding="utf-8")
        assert "Post 2026" not in archive_2025.read_text(encoding="utf-8")
        assert "Post 2026" in archive_2026.read_text(encoding="utf-8")

    def test_archive_landing_lists_years(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post_file(posts_dir, "p2025.md", "Post 2025", "2025-06-15")
        _make_post_file(posts_dir, "p2026.md", "Post 2026", "2026-03-01")

        model = build_blog_model(cfg)
        emit_all(model)

        landing = tmp_path / "docs" / "blog" / "archive" / "index.md"
        assert landing.exists()
        content = landing.read_text(encoding="utf-8")
        assert "2025" in content
        assert "2026" in content

    def test_user_authored_archive_preserved(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post_file(posts_dir, "p2026.md", "Post 2026", "2026-01-01")

        archive_2026 = tmp_path / "docs" / "blog" / "archive" / "2026.md"
        archive_2026.parent.mkdir(parents=True, exist_ok=True)
        archive_2026.write_text("# Custom Header\n\nUser preamble.\n", encoding="utf-8")

        model = build_blog_model(cfg)
        emit_all(model)

        content = archive_2026.read_text(encoding="utf-8")
        assert "Custom Header" in content
        assert "User preamble." in content
        assert "Post 2026" in content


# ---------------------------------------------------------------------------
# US3: Taxonomy pages
# ---------------------------------------------------------------------------


class TestTaxonomyPages:
    def test_tag_pages_generated(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post_file(posts_dir, "p1.md", "Post 1", "2026-01-01", tags=["python"])
        _make_post_file(
            posts_dir, "p2.md", "Post 2", "2026-02-01", tags=["python", "devops"]
        )

        model = build_blog_model(cfg)
        emit_all(model)

        tag_python = tmp_path / "docs" / "blog" / "tag" / "python.md"
        tag_devops = tmp_path / "docs" / "blog" / "tag" / "devops.md"
        assert tag_python.exists()
        assert tag_devops.exists()
        assert "Post 1" in tag_python.read_text(encoding="utf-8")
        assert "Post 2" in tag_python.read_text(encoding="utf-8")
        assert "Post 2" in tag_devops.read_text(encoding="utf-8")
        assert "Post 1" not in tag_devops.read_text(encoding="utf-8")

    def test_category_pages_generated(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post_file(
            posts_dir, "p1.md", "Tutorial Post", "2026-01-01", categories=["tutorials"]
        )

        model = build_blog_model(cfg)
        emit_all(model)

        cat_page = tmp_path / "docs" / "blog" / "category" / "tutorials.md"
        assert cat_page.exists()
        assert "Tutorial Post" in cat_page.read_text(encoding="utf-8")

    def test_enable_tags_false_suppresses(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        cfg.enable_tags = False
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post_file(posts_dir, "p1.md", "Post", "2026-01-01", tags=["python"])

        model = build_blog_model(cfg)
        emit_all(model)

        assert not (tmp_path / "docs" / "blog" / "tag").exists()

    def test_slug_collision_warning_emitted(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        # "abc!" and "abc?" both slugify to "abc"
        _make_post_file(posts_dir, "p1.md", "P1", "2026-01-01", tags=["abc!"])
        _make_post_file(posts_dir, "p2.md", "P2", "2026-02-01", tags=["abc?"])

        model = build_blog_model(cfg)
        collision_warnings = [w for w in model.warnings if w.code == "SLUG_COLLISION"]
        assert collision_warnings


# ---------------------------------------------------------------------------
# US4: Slug and excerpt control
# ---------------------------------------------------------------------------


class TestSlugControl:
    def test_front_matter_slug_used(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post_file(
            posts_dir, "2026-01-01-long-filename.md",
            "My Post", "2026-01-01", slug="my-custom-slug"
        )

        model = build_blog_model(cfg)
        assert len(model.posts) == 1
        assert model.posts[0].slug == "my-custom-slug"
        assert model.posts[0].url_path == "/blog/my-custom-slug/"

    def test_date_prefix_stripped_from_filename(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        _make_post_file(posts_dir, "2026-04-01-hello-world.md", "Hello", "2026-04-01")

        model = build_blog_model(cfg)
        assert model.posts[0].slug == "hello-world"

    def test_more_marker_excerpt(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        body = "Intro line.\n\n<!-- more -->\n\nRest of post."
        _make_post_file(posts_dir, "post.md", "Post", "2026-01-01", body=body)

        model = build_blog_model(cfg)
        assert model.posts[0].excerpt.strip() == "Intro line."

    def test_first_paragraph_excerpt_fallback(self, tmp_path: Path) -> None:
        cfg = _scaffold(tmp_path)
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        body = "First para.\nContinued.\n\nSecond para."
        _make_post_file(posts_dir, "post.md", "Post", "2026-01-01", body=body)

        model = build_blog_model(cfg)
        assert "First para." in model.posts[0].excerpt
        assert "Second para." not in model.posts[0].excerpt
