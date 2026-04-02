"""Integration tests for the CLI clean command."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from zensical_blog.cli import cli


def _scaffold(tmp_path: Path) -> Path:
    """Create a minimal project scaffold and return the project root."""
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
    return tmp_path


class TestCleanCommand:
    def test_clean_removes_generated_root(self, tmp_path: Path) -> None:
        root = _scaffold(tmp_path)
        toml = root / "zensical.toml"

        # Create some files in generated_root
        gen_root = root / "docs" / ".bloggen"
        gen_root.mkdir(parents=True)
        (gen_root / "something.md").write_text("generated", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["clean", "--config", str(toml)])
        assert result.exit_code == 0
        assert not gen_root.exists()

    def test_clean_idempotent_when_nothing_to_clean(self, tmp_path: Path) -> None:
        root = _scaffold(tmp_path)
        toml = root / "zensical.toml"

        runner = CliRunner()
        result = runner.invoke(cli, ["clean", "--config", str(toml)])
        assert result.exit_code == 0  # No error even when nothing to clean

    def test_clean_does_not_touch_outside_generated_root(self, tmp_path: Path) -> None:
        root = _scaffold(tmp_path)
        toml = root / "zensical.toml"

        # Create a legitimate docs file
        user_file = root / "docs" / "index.md"
        user_file.write_text("# Home", encoding="utf-8")

        # Create generated root with a file
        gen_root = root / "docs" / ".bloggen"
        gen_root.mkdir(parents=True)
        (gen_root / "gen.md").write_text("generated", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["clean", "--config", str(toml)])
        assert result.exit_code == 0

        assert user_file.exists()  # User file untouched
        assert not gen_root.exists()  # Generated root removed


class TestBuildCommand:
    def test_build_exit_code_0_on_success(self, tmp_path: Path) -> None:
        root = _scaffold(tmp_path)
        toml = root / "zensical.toml"
        posts_dir = root / "docs" / "blog" / "posts"
        (posts_dir / "post.md").write_text(
            "---\ntitle: Test\ndate: 2026-01-01\n---\nBody.\n",
            encoding="utf-8",
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["build", "--config", str(toml)])
        assert result.exit_code == 0
        assert (root / "docs" / "blog" / "index.md").exists()

    def test_build_fail_on_warnings(self, tmp_path: Path) -> None:
        root = _scaffold(tmp_path)
        # Remove .gitignore to trigger MISSING_GITIGNORE warning
        (root / ".gitignore").unlink()
        toml = root / "zensical.toml"
        posts_dir = root / "docs" / "blog" / "posts"
        (posts_dir / "post.md").write_text(
            "---\ntitle: T\ndate: 2026-01-01\n---\nBody.\n",
            encoding="utf-8",
        )

        runner = CliRunner()
        result = runner.invoke(
            cli, ["build", "--config", str(toml), "--fail-on-warnings"]
        )
        assert result.exit_code == 1
