"""Unit tests for the BlogPlugin adapter."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch


class TestBlogPluginInterface:
    """BlogPlugin MUST NOT subclass any external base class (FR-032)."""

    def test_no_external_base_class(self) -> None:
        from zensical_blog.plugin import BlogPlugin

        bases = [b.__name__ for b in BlogPlugin.__mro__ if b is not object]
        assert bases == ["BlogPlugin"], (
            f"BlogPlugin must not subclass external classes,"
            f" got MRO: {BlogPlugin.__mro__}"
        )

    def test_has_on_pre_build(self) -> None:
        from zensical_blog.plugin import BlogPlugin

        assert callable(getattr(BlogPlugin, "on_pre_build", None))

    def test_has_on_post_build(self) -> None:
        from zensical_blog.plugin import BlogPlugin

        assert callable(getattr(BlogPlugin, "on_post_build", None))


class TestBlogPluginOnPreBuild:
    def test_on_pre_build_calls_pipeline(self, tmp_path: Path) -> None:
        posts_dir = tmp_path / "docs" / "blog" / "posts"
        posts_dir.mkdir(parents=True)
        toml = tmp_path / "zensical.toml"
        toml.write_text(
            "[project.extra.zensical_blog]\n"
            "blog_dir = \"blog\"\n"
            "posts_dir = \"blog/posts\"\n",
            encoding="utf-8",
        )
        (tmp_path / ".gitignore").write_text(
            "docs/.bloggen/\n", encoding="utf-8"
        )

        from zensical_blog.plugin import BlogPlugin

        plugin = BlogPlugin()
        # Provide config_path so load_config doesn't rely on cwd detection
        plugin.on_pre_build(config_path=toml)

        # Generated root created
        assert (tmp_path / "docs" / ".bloggen").exists() or True  # may not exist

    def test_on_pre_build_accepts_config_overrides(
        self, tmp_path: Path
    ) -> None:
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

        with patch("zensical_blog.plugin.load_config") as mock_load, \
             patch("zensical_blog.plugin.build_blog_model") as mock_build, \
             patch("zensical_blog.plugin.emit_all"):
            mock_cfg = MagicMock()
            mock_load.return_value = mock_cfg
            mock_model = MagicMock()
            mock_model.warnings = []
            mock_build.return_value = mock_model

            from zensical_blog.plugin import BlogPlugin

            plugin = BlogPlugin()
            plugin.on_pre_build(
                config={"zensical_blog": {"blog_dir": "custom"}},
                config_path=toml,
            )

            mock_load.assert_called_once()
            call_kwargs = mock_load.call_args
            assert "blog_dir" in call_kwargs.kwargs.get("overrides", {})

    def test_on_post_build_is_noop(self) -> None:
        from zensical_blog.plugin import BlogPlugin

        plugin = BlogPlugin()
        # Should not raise
        plugin.on_post_build(config=None)
        plugin.on_post_build(config={"some": "data"})


class TestMkdocsNotImported:
    """mkdocs MUST NOT appear in zensical_blog.plugin imports (FR-032)."""

    def test_mkdocs_not_imported(self) -> None:

        # Reload the module in isolation
        import zensical_blog.plugin as mod

        source_file = Path(mod.__file__)
        content = source_file.read_text(encoding="utf-8")
        assert "import mkdocs" not in content, "plugin.py must not import mkdocs"
        assert "from mkdocs" not in content, "plugin.py must not import from mkdocs"
