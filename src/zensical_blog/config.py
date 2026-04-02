"""BlogConfig dataclass and config loading logic."""

from __future__ import annotations

import logging
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from ruamel.yaml import YAML

log = logging.getLogger(__name__)

_VALID_DRAFTS = frozenset(("hide", "show", "fail"))


@dataclass
class BlogConfig:
    """Resolved, typed configuration for one blog build run.

    Constructed once by :func:`load_config`; treated as immutable thereafter.
    The :attr:`generated_root` property is always ``docs_dir / ".bloggen"``.
    """

    blog_dir: str = "blog"
    posts_dir: str = "blog/posts"
    docs_dir: Path = field(default_factory=lambda: Path("docs"))
    archives: Literal["yearly"] = "yearly"
    pagination: int = 10
    excerpt_marker: str = "<!-- more -->"
    excerpt_fallback: Literal["first_paragraph"] = "first_paragraph"
    drafts: Literal["hide", "show", "fail"] = "hide"
    nav_label: str = "Blog"
    nav_path: str = "blog/index.md"
    enable_tags: bool = True
    enable_categories: bool = True
    enable_archive_landing: bool = True
    tag_slug_map: dict[str, str] = field(default_factory=dict)
    category_slug_map: dict[str, str] = field(default_factory=dict)
    fail_on_warnings: bool = False

    @property
    def generated_root(self) -> Path:
        return self.docs_dir / ".bloggen"

    def __post_init__(self) -> None:
        if not isinstance(self.docs_dir, Path):
            self.docs_dir = Path(self.docs_dir)
        self._validate()

    def _validate(self) -> None:
        if self.archives != "yearly":
            raise ValueError(f"archives must be 'yearly', got {self.archives!r}")
        if self.drafts not in _VALID_DRAFTS:
            raise ValueError(
                f"drafts must be one of {sorted(_VALID_DRAFTS)!r}, got {self.drafts!r}"
            )
        if self.excerpt_fallback != "first_paragraph":
            raise ValueError(
                f"excerpt_fallback must be 'first_paragraph',"
                f" got {self.excerpt_fallback!r}"
            )
        if self.pagination < 1:
            raise ValueError(f"pagination must be >= 1, got {self.pagination!r}")
        if not self.blog_dir:
            raise ValueError("blog_dir must be non-empty")
        if not self.posts_dir:
            raise ValueError("posts_dir must be non-empty")
        if not self.nav_label:
            raise ValueError("nav_label must be non-empty")
        if not self.nav_path or not self.nav_path.endswith(".md"):
            raise ValueError(
                f"nav_path must be non-empty and end with .md,"
                f" got {self.nav_path!r}"
            )


def _find_config_file(start: Path) -> tuple[Path, str] | None:
    """Walk *start* and its parents for ``zensical.toml`` then ``mkdocs.yml``."""
    current = start.resolve()
    while True:
        for name, kind in (("zensical.toml", "toml"), ("mkdocs.yml", "yaml")):
            candidate = current / name
            if candidate.is_file():
                return candidate, kind
        parent = current.parent
        if parent == current:
            return None
        current = parent


def _parse_toml_config(config_path: Path) -> dict[str, Any]:
    with open(config_path, "rb") as fh:
        data = tomllib.load(fh)
    return data.get("project", {}).get("extra", {}).get("zensical_blog", {})


def _parse_yaml_config(config_path: Path) -> dict[str, Any]:
    yaml = YAML()
    with open(config_path, encoding="utf-8") as fh:
        data = yaml.load(fh) or {}
    for entry in data.get("plugins", []) or []:
        if isinstance(entry, dict) and "zensical_blog" in entry:
            raw = entry["zensical_blog"] or {}
            return dict(raw)
    return {}


def load_config(
    config_path: Path | None = None,
    docs_dir: Path | None = None,
    overrides: dict[str, Any] | None = None,
) -> BlogConfig:
    """Return a fully resolved :class:`BlogConfig`.

    Resolution order (highest priority first):

    1. *overrides* (CLI flags)
    2. ``[project.extra.zensical_blog]`` in ``zensical.toml``
    3. ``plugins: - zensical_blog:`` block in ``mkdocs.yml`` (compat)
    4. Defaults in :class:`BlogConfig`

    When ``zensical.toml`` is present and contains ``[project.extra.zensical_blog]``,
    any ``mkdocs.yml`` plugin block is ignored entirely.
    """
    overrides = overrides or {}
    config_kind: str | None = None
    raw: dict[str, Any] = {}

    if config_path is not None:
        config_path = Path(config_path).resolve()
        if not config_path.is_file():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        config_kind = "toml" if config_path.name.endswith(".toml") else "yaml"
    else:
        result = _find_config_file(Path.cwd())
        if result is not None:
            config_path, config_kind = result

    if config_path is not None:
        if config_kind == "toml":
            raw = _parse_toml_config(config_path)
        else:
            raw = _parse_yaml_config(config_path)
            log.debug(
                "Reading blog config from mkdocs.yml (compat mode). "
                "Migrate to [project.extra.zensical_blog] in zensical.toml."
            )

    # Derive docs_dir from config file location when not given explicitly
    if docs_dir is not None:
        raw["docs_dir"] = Path(docs_dir)
    elif "docs_dir" not in raw and config_path is not None:
        raw["docs_dir"] = config_path.parent / "docs"

    # Coerce YAML compat types
    for bool_key in (
        "enable_tags",
        "enable_categories",
        "enable_archive_landing",
        "fail_on_warnings",
    ):
        if bool_key in raw and isinstance(raw[bool_key], str):
            raw[bool_key] = raw[bool_key].lower() in ("true", "1", "yes")

    if "pagination" in raw:
        raw["pagination"] = int(raw["pagination"])

    # Convert ruamel CommentedMap to plain dict for slug maps
    for map_key in ("tag_slug_map", "category_slug_map"):
        if map_key in raw and not isinstance(raw[map_key], dict):
            raw[map_key] = dict(raw[map_key])

    # CLI overrides win
    raw.update({k: v for k, v in overrides.items() if v is not None})

    if "docs_dir" in raw and not isinstance(raw["docs_dir"], Path):
        raw["docs_dir"] = Path(raw["docs_dir"])

    # Filter to only known BlogConfig fields
    known = BlogConfig.__dataclass_fields__
    filtered = {k: v for k, v in raw.items() if k in known}

    return BlogConfig(**filtered)
