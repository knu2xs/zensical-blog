"""Front matter parsing and excerpt extraction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import frontmatter


@dataclass
class RawPost:
    """Intermediate value from parsing a single source ``.md`` file.

    Not persisted; passed directly to the model-building step in ``builder.py``.
    """

    source_path: Path
    raw_metadata: dict[str, Any]
    raw_content: str


def parse_post(path: Path) -> RawPost:
    """Parse *path* and return a :class:`RawPost`.

    Uses ``python-frontmatter`` to handle YAML/TOML/JSON front matter.
    Files with no front matter delimiter are treated as having empty metadata.
    """
    post = frontmatter.load(str(path))
    return RawPost(
        source_path=path,
        raw_metadata=dict(post.metadata),
        raw_content=post.content,
    )


def extract_excerpt(
    raw_content: str,
    marker: str = "<!-- more -->",
    fallback: Literal["first_paragraph"] = "first_paragraph",
) -> str:
    """Extract an excerpt from *raw_content*.

    Strategy (in priority order):

    1. If *marker* appears in *raw_content*, return everything before it
       (stripped).
    2. If *fallback* is ``"first_paragraph"``, return text up to the first
       blank line (stripped).
    3. If the body has no blank line, return the first 200 characters
       (stripped).
    """
    if marker and marker in raw_content:
        return raw_content.split(marker, 1)[0].strip()

    lines = raw_content.splitlines()
    excerpt_lines: list[str] = []
    for line in lines:
        if line.strip() == "":
            break
        excerpt_lines.append(line)

    if excerpt_lines:
        return "\n".join(excerpt_lines).strip()

    return raw_content[:200].strip()
