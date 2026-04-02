"""Unit tests for BlogConfig and load_config."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from zensical_blog.config import BlogConfig, load_config


class TestBlogConfig:
    def test_defaults(self) -> None:
        cfg = BlogConfig(docs_dir=Path("/tmp/docs"))
        assert cfg.blog_dir == "blog"
        assert cfg.posts_dir == "blog/posts"
        assert cfg.drafts == "hide"
        assert cfg.enable_tags is True
        assert cfg.pagination == 10
        assert cfg.generated_root == Path("/tmp/docs/.bloggen")

    def test_generated_root_inside_docs_dir(self, tmp_path: Path) -> None:
        cfg = BlogConfig(docs_dir=tmp_path / "docs")
        assert cfg.generated_root == tmp_path / "docs" / ".bloggen"

    def test_invalid_drafts_raises(self) -> None:
        with pytest.raises(ValueError, match="drafts"):
            BlogConfig(docs_dir=Path("/tmp/docs"), drafts="maybe")  # type: ignore[arg-type]

    def test_invalid_pagination_raises(self) -> None:
        with pytest.raises(ValueError, match="pagination"):
            BlogConfig(docs_dir=Path("/tmp/docs"), pagination=0)

    def test_invalid_nav_path_raises(self) -> None:
        with pytest.raises(ValueError, match="nav_path"):
            BlogConfig(docs_dir=Path("/tmp/docs"), nav_path="blog/index.html")

    def test_docs_dir_coerced_to_path(self) -> None:
        cfg = BlogConfig(docs_dir="/some/path")  # type: ignore[arg-type]
        assert isinstance(cfg.docs_dir, Path)

    def test_all_drafts_values_valid(self) -> None:
        for val in ("hide", "show", "fail"):
            cfg = BlogConfig(docs_dir=Path("/d"), drafts=val)  # type: ignore[arg-type]
            assert cfg.drafts == val


class TestLoadConfig:
    def test_load_from_toml(self, tmp_path: Path) -> None:
        toml = tmp_path / "zensical.toml"
        toml.write_text(
            textwrap.dedent("""\
                [project]
                site_name = "Test"

                [project.extra.zensical_blog]
                blog_dir = "myblog"
                drafts = "show"
            """),
            encoding="utf-8",
        )
        cfg = load_config(config_path=toml)
        assert cfg.blog_dir == "myblog"
        assert cfg.drafts == "show"
        assert cfg.docs_dir == tmp_path / "docs"

    def test_load_from_yaml_compat(self, tmp_path: Path) -> None:
        yml = tmp_path / "mkdocs.yml"
        yml.write_text(
            textwrap.dedent("""\
                site_name: Test
                plugins:
                  - zensical_blog:
                      blog_dir: blogcompat
                      pagination: 5
            """),
            encoding="utf-8",
        )
        cfg = load_config(config_path=yml)
        assert cfg.blog_dir == "blogcompat"
        assert cfg.pagination == 5

    def test_missing_config_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_config(config_path=tmp_path / "nonexistent.toml")

    def test_cli_overrides_win(self, tmp_path: Path) -> None:
        toml = tmp_path / "zensical.toml"
        toml.write_text(
            "[project.extra.zensical_blog]\nblog_dir = \"blog\"\n",
            encoding="utf-8",
        )
        cfg = load_config(
            config_path=toml, overrides={"blog_dir": "overridden"}
        )
        assert cfg.blog_dir == "overridden"

    def test_no_config_uses_defaults(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Ensure no zensical.toml or mkdocs.yml found by changing cwd to tmp_path
        monkeypatch.chdir(tmp_path)
        cfg = load_config()
        assert cfg.blog_dir == "blog"
        assert cfg.drafts == "hide"

    def test_docs_dir_override(self, tmp_path: Path) -> None:
        toml = tmp_path / "zensical.toml"
        toml.write_text("[project.extra.zensical_blog]\n", encoding="utf-8")
        custom_docs = tmp_path / "custom_docs"
        cfg = load_config(config_path=toml, docs_dir=custom_docs)
        assert cfg.docs_dir == custom_docs

    def test_toml_slug_maps(self, tmp_path: Path) -> None:
        toml = tmp_path / "zensical.toml"
        toml.write_text(
            textwrap.dedent("""\
                [project.extra.zensical_blog]
                [project.extra.zensical_blog.tag_slug_map]
                "C#" = "csharp"
            """),
            encoding="utf-8",
        )
        cfg = load_config(config_path=toml)
        assert cfg.tag_slug_map == {"C#": "csharp"}
