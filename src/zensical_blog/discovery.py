"""Post file discovery — finds all Markdown source files under posts_dir."""

from __future__ import annotations

from pathlib import Path


def discover_posts(posts_dir: Path) -> list[Path]:
    """Return all ``.md`` files under *posts_dir*, sorted by path for determinism.

    Returns an empty list (not an error) when *posts_dir* does not exist.
    """
    if not posts_dir.is_dir():
        return []
    return sorted(posts_dir.rglob("*.md"))
