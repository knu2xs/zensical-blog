"""Deterministic slug algorithm and collision-aware SlugRegistry."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from zensical_blog.models import BuildWarning

_MAX_SLUG_LEN = 80


def slugify(label: str) -> str:
    """Convert *label* to a lowercase URL-safe slug.

    Algorithm (R-05):
    1. Strip whitespace.
    2. NFKD normalise.
    3. Remove combining marks (Unicode category "Mn").
    4. Casefold.
    5. Replace runs of non-``[a-z0-9]`` with ``"-"``.
    6. Strip leading/trailing ``"-"``.
    7. Truncate to 80 chars, stripping any trailing ``"-"``.
    8. Fall back to ``"x"`` when the result is empty.
    """
    label = label.strip()
    label = unicodedata.normalize("NFKD", label)
    label = "".join(c for c in label if unicodedata.category(c) != "Mn")
    label = label.casefold()
    label = re.sub(r"[^a-z0-9]+", "-", label)
    label = label.strip("-")
    label = label[:_MAX_SLUG_LEN].rstrip("-")
    return label or "x"


@dataclass
class SlugRegistry:
    """Centralised registry assigning canonical slugs with collision resolution.

    Instantiate one registry per "namespace" (post slugs, tag slugs, category
    slugs are each tracked separately in the builder).
    """

    _assignments: dict[str, str] = field(default_factory=dict, init=False, repr=False)
    _base_to_labels: dict[str, list[str]] = field(
        default_factory=dict, init=False, repr=False
    )
    warnings: list[BuildWarning] = field(default_factory=list, init=False)

    def register_label(
        self,
        label: str,
        explicit_map: dict[str, str] | None = None,
    ) -> str:
        """Register *label* and return its canonical slug.

        If *explicit_map* contains *label*, that slug is used verbatim
        (bypasses the algorithm entirely, no collision check).

        If the label was already registered in this registry, the previously
        assigned slug is returned unchanged.

        On a collision (two different labels produce the same base slug):
        all colliding labels are re-sorted by Unicode code-point order and
        assigned ``base``, ``base-2``, ``base-3``, …  A ``BuildWarning``
        (code ``"SLUG_COLLISION"``) is appended to :attr:`warnings`.

        .. note::
            Re-sorting on collision can change slugs that were previously
            returned.  Always use :meth:`get_slug` (or ``registry[label]``)
            *after* registering **all** labels to obtain final slugs.
        """
        if explicit_map and label in explicit_map:
            slug = explicit_map[label]
            self._assignments[label] = slug
            return slug

        # Already registered — return current assignment
        if label in self._assignments:
            return self._assignments[label]

        base_slug = slugify(label)

        if base_slug not in self._base_to_labels:
            # No collision
            self._base_to_labels[base_slug] = [label]
            self._assignments[label] = base_slug
            return base_slug

        # Collision detected — re-sort the whole group and reassign
        group = self._base_to_labels[base_slug]
        group.append(label)
        sorted_group = sorted(group)  # sort by Unicode code points

        for i, lbl in enumerate(sorted_group):
            new_slug = base_slug if i == 0 else f"{base_slug}-{i + 1}"
            self._assignments[lbl] = new_slug

        assigned = [self._assignments[lbl] for lbl in sorted_group]
        self.warnings.append(
            BuildWarning(
                code="SLUG_COLLISION",
                message=(
                    f"Labels {sorted_group!r} all produce base slug {base_slug!r}. "
                    f"Assigned slugs: {assigned!r}."
                ),
            )
        )
        return self._assignments[label]

    def get_slug(self, label: str) -> str | None:
        """Return the current slug for *label*, or ``None`` if not registered."""
        return self._assignments.get(label)
