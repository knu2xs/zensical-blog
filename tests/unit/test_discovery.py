"""Unit tests for discover_posts."""

from __future__ import annotations

from pathlib import Path

from zensical_blog.discovery import discover_posts


class TestDiscoverPosts:
    def test_empty_dir(self, tmp_path: Path) -> None:
        posts_dir = tmp_path / "posts"
        posts_dir.mkdir()
        assert discover_posts(posts_dir) == []

    def test_nonexistent_dir_returns_empty(self, tmp_path: Path) -> None:
        assert discover_posts(tmp_path / "nonexistent") == []

    def test_single_post(self, tmp_path: Path) -> None:
        posts_dir = tmp_path / "posts"
        posts_dir.mkdir()
        (posts_dir / "post.md").write_text("# Hi", encoding="utf-8")
        result = discover_posts(posts_dir)
        assert len(result) == 1
        assert result[0].name == "post.md"

    def test_non_md_files_ignored(self, tmp_path: Path) -> None:
        posts_dir = tmp_path / "posts"
        posts_dir.mkdir()
        (posts_dir / "post.md").write_text("", encoding="utf-8")
        (posts_dir / "image.png").write_text("", encoding="utf-8")
        (posts_dir / "notes.txt").write_text("", encoding="utf-8")
        result = discover_posts(posts_dir)
        assert all(p.suffix == ".md" for p in result)
        assert len(result) == 1

    def test_nested_posts_found(self, tmp_path: Path) -> None:
        posts_dir = tmp_path / "posts"
        sub = posts_dir / "2026"
        sub.mkdir(parents=True)
        (posts_dir / "top.md").write_text("", encoding="utf-8")
        (sub / "nested.md").write_text("", encoding="utf-8")
        result = discover_posts(posts_dir)
        assert len(result) == 2

    def test_deterministic_order(self, tmp_path: Path) -> None:
        posts_dir = tmp_path / "posts"
        posts_dir.mkdir()
        for name in ("zzz.md", "aaa.md", "mmm.md"):
            (posts_dir / name).write_text("", encoding="utf-8")
        result = discover_posts(posts_dir)
        names = [p.name for p in result]
        assert names == sorted(names)
