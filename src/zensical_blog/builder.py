"""Model layer: orchestrates post discovery, parsing, and model construction.

MODEL LAYER — no file writes allowed here.
All I/O is read-only (source post files, config files).
The only output is a :class:`~zensical_blog.models.BlogModel` value object.
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from zensical_blog.config import BlogConfig
from zensical_blog.discovery import discover_posts
from zensical_blog.models import (
    ArchivePeriod,
    BlogModel,
    BuildWarning,
    DraftPostError,
    Post,
    TaxonomyTerm,
)
from zensical_blog.parser import extract_excerpt, parse_post
from zensical_blog.slugifier import SlugRegistry, slugify

if TYPE_CHECKING:
    pass

log = logging.getLogger(__name__)

_DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-")
_VALID_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _derive_post_slug(source_path: Path, fm_slug: str | None) -> tuple[str, bool]:
    """Return ``(slug, from_front_matter)`` for a post.

    Priority:
    1. Front matter ``slug`` field (verbatim after validation).
    2. Source filename stem with leading ``YYYY-MM-DD-`` stripped.
    3. Apply :func:`~zensical_blog.slugifier.slugify` to the result of (2).
    """
    if fm_slug is not None:
        if _VALID_SLUG_RE.match(fm_slug):
            return fm_slug, True
        # Invalid front matter slug — fall through with a warning logged
        log.warning(
            "Post %s has invalid front-matter slug %r — using filename instead.",
            source_path.name,
            fm_slug,
        )

    stem = _DATE_PREFIX.sub("", source_path.stem)
    return slugify(stem), False


def _extract_title(raw_content: str, source_path: Path) -> str:
    """Extract title from content H1 heading, falling back to stem."""
    h1 = re.search(r"^#\s+(.+)$", raw_content, re.MULTILINE)
    if h1:
        return h1.group(1).strip()
    return source_path.stem


def _check_gitignore(project_root: Path) -> BuildWarning | None:
    """Return a warning if ``docs/.bloggen/`` is absent from ``.gitignore``."""
    gitignore = project_root / ".gitignore"
    if not gitignore.is_file():
        return BuildWarning(
            code="MISSING_GITIGNORE",
            message=(
                "No .gitignore found. Add `docs/.bloggen/` to prevent "
                "generated artifacts from being committed."
            ),
        )
    content = gitignore.read_text(encoding="utf-8")
    # Accept any line that contains the essential path fragment
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ".bloggen" in stripped:
            return None
    return BuildWarning(
        code="MISSING_GITIGNORE",
        message=(
            "docs/.bloggen/ is not in .gitignore. Add it to prevent "
            "generated artifacts from being committed."
        ),
    )


def build_blog_model(config: BlogConfig) -> BlogModel:
    """Build and return a :class:`~zensical_blog.models.BlogModel`.

    Steps:
    1. Discover post source files.
    2. Parse each file into a :class:`~zensical_blog.parser.RawPost`.
    3. Register post slugs (collision detection).
    4. Build :class:`~zensical_blog.models.Post` objects.
    5. Filter by ``config.drafts``.
    6. Sort visible posts by :attr:`~zensical_blog.models.Post.sort_key`.
    7. Register taxonomy labels (tags + categories).
    8. Build :class:`~zensical_blog.models.TaxonomyTerm` objects.
    9. Build :class:`~zensical_blog.models.ArchivePeriod` objects.
    10. Collect advisory warnings.
    11. Return the immutable :class:`~zensical_blog.models.BlogModel`.
    """
    warnings: list[BuildWarning] = []

    # --- 1. Discover --------------------------------------------------------
    posts_dir = config.docs_dir / config.posts_dir
    paths = discover_posts(posts_dir)

    # --- 2. Parse -----------------------------------------------------------
    raw_posts = []
    for path in paths:
        try:
            raw = parse_post(path)
            raw_posts.append(raw)
        except Exception as exc:  # noqa: BLE001
            warnings.append(
                BuildWarning(
                    code="PARSE_ERROR",
                    message=f"Could not parse {path.name}: {exc}",
                    source_path=path,
                )
            )

    # --- 3. Register post slugs (first pass) ---------------------------------
    post_registry = SlugRegistry()
    for raw in raw_posts:
        fm_slug = raw.raw_metadata.get("slug")
        slug, from_fm = _derive_post_slug(raw.source_path, fm_slug)
        if from_fm:
            # Explicit slug — register directly for collision detection
            post_registry.register_label(slug, explicit_map={slug: slug})
        else:
            # Register the derived (date-stripped) slug label for collision detection
            stripped_stem = _DATE_PREFIX.sub("", raw.source_path.stem)
            post_registry.register_label(stripped_stem, explicit_map={})

    # --- 4. Build Post objects -----------------------------------------------
    all_posts: list[Post] = []
    for raw in raw_posts:
        meta = raw.raw_metadata
        fm_slug = meta.get("slug")
        slug, from_fm = _derive_post_slug(raw.source_path, fm_slug)

        # Resolve final slug from registry (handles collisions)
        if from_fm:
            final_slug = slug
        else:
            stripped_stem = _DATE_PREFIX.sub("", raw.source_path.stem)
            final_slug = post_registry.get_slug(stripped_stem) or slug

        # Date (required)
        raw_date = meta.get("date")
        if raw_date is None:
            warnings.append(
                BuildWarning(
                    code="MISSING_DATE",
                    message=(
                        f"Post {raw.source_path.name} has no 'date' field"
                        " — skipped."
                    ),
                    source_path=raw.source_path,
                )
            )
            continue

        if isinstance(raw_date, str):
            try:
                post_date = date.fromisoformat(raw_date[:10])
            except ValueError:
                warnings.append(
                    BuildWarning(
                        code="INVALID_DATE",
                        message=(
                            f"Post {raw.source_path.name} has unparseable"
                            f" date {raw_date!r} — skipped."
                        ),
                        source_path=raw.source_path,
                    )
                )
                continue
        elif isinstance(raw_date, date):
            post_date = raw_date
        else:
            warnings.append(
                BuildWarning(
                    code="INVALID_DATE",
                    message=(
                        f"Post {raw.source_path.name} has invalid date type"
                        " — skipped."
                    ),
                    source_path=raw.source_path,
                )
            )
            continue

        # Title
        raw_title = meta.get("title")
        title = str(raw_title) if raw_title else _extract_title(
            raw.raw_content, raw.source_path
        )

        # Draft
        draft = bool(meta.get("draft", False))

        # Tags / categories
        tags = tuple(str(t).strip() for t in (meta.get("tags") or []))
        categories = tuple(str(c).strip() for c in (meta.get("categories") or []))

        # Authors
        authors = tuple(str(a).strip() for a in (meta.get("authors") or []))

        # Excerpt
        excerpt = extract_excerpt(
            raw.raw_content,
            marker=config.excerpt_marker,
            fallback=config.excerpt_fallback,
        )

        # URL path
        url_path = f"/{config.blog_dir}/{final_slug}/"

        all_posts.append(
            Post(
                source_path=raw.source_path,
                title=title,
                date=post_date,
                draft=draft,
                tags=tags,
                categories=categories,
                slug=final_slug,
                excerpt=excerpt,
                body=raw.raw_content,
                authors=authors,
                url_path=url_path,
            )
        )

    # Collect post_registry collision warnings
    for w in post_registry.warnings:
        warnings.append(w)

    # --- 5 & 6. Filter and sort -----------------------------------------------
    draft_posts = tuple(p for p in all_posts if p.draft)
    visible_posts: tuple[Post, ...]

    if config.drafts == "fail" and draft_posts:
        raise DraftPostError(
            f"{len(draft_posts)} draft post(s) found and drafts='fail'."
        )
    elif config.drafts == "hide":
        visible_posts = tuple(sorted(
            (p for p in all_posts if not p.draft), key=lambda p: p.sort_key
        ))
    else:  # "show"
        visible_posts = tuple(sorted(all_posts, key=lambda p: p.sort_key))

    # --- 7. Register taxonomy labels -----------------------------------------
    tag_registry = SlugRegistry()
    cat_registry = SlugRegistry()

    if config.enable_tags:
        all_tag_labels: set[str] = set()
        for p in visible_posts:
            all_tag_labels.update(p.tags)
        for label in sorted(all_tag_labels):
            tag_registry.register_label(label, explicit_map=config.tag_slug_map)
        warnings.extend(tag_registry.warnings)

    if config.enable_categories:
        all_cat_labels: set[str] = set()
        for p in visible_posts:
            all_cat_labels.update(p.categories)
        for label in sorted(all_cat_labels):
            cat_registry.register_label(label, explicit_map=config.category_slug_map)
        warnings.extend(cat_registry.warnings)

    # --- 8. Build TaxonomyTerm objects ----------------------------------------
    tags_list: list[TaxonomyTerm] = []
    if config.enable_tags:
        tag_to_posts: dict[str, list[Post]] = defaultdict(list)
        for p in visible_posts:
            for tag_label in p.tags:
                tag_to_posts[tag_label].append(p)
        for label in sorted(tag_to_posts.keys(), key=str.casefold):
            slug = tag_registry.get_slug(label) or slugify(label)
            tags_list.append(
                TaxonomyTerm(
                    kind="tag",
                    label=label,
                    slug=slug,
                    posts=tuple(tag_to_posts[label]),
                    url_path=f"/{config.blog_dir}/tag/{slug}/",
                )
            )

    cats_list: list[TaxonomyTerm] = []
    if config.enable_categories:
        cat_to_posts: dict[str, list[Post]] = defaultdict(list)
        for p in visible_posts:
            for cat_label in p.categories:
                cat_to_posts[cat_label].append(p)
        for label in sorted(cat_to_posts.keys(), key=str.casefold):
            slug = cat_registry.get_slug(label) or slugify(label)
            cats_list.append(
                TaxonomyTerm(
                    kind="category",
                    label=label,
                    slug=slug,
                    posts=tuple(cat_to_posts[label]),
                    url_path=f"/{config.blog_dir}/category/{slug}/",
                )
            )

    # --- 9. Build ArchivePeriod objects ----------------------------------------
    archives_list: list[ArchivePeriod] = []
    if config.enable_archive_landing:
        year_to_posts: dict[int, list[Post]] = defaultdict(list)
        for p in visible_posts:
            year_to_posts[p.date.year].append(p)
        for year in sorted(year_to_posts.keys(), reverse=True):
            archives_list.append(
                ArchivePeriod(
                    year=year,
                    posts=tuple(year_to_posts[year]),
                    url_path=f"/{config.blog_dir}/archive/{year}/",
                )
            )

    # --- 10. Advisory warnings ------------------------------------------------
    project_root = config.docs_dir.parent
    gi_warning = _check_gitignore(project_root)
    if gi_warning:
        warnings.append(gi_warning)

    return BlogModel(
        config=config,
        posts=visible_posts,
        draft_posts=draft_posts,
        archives=tuple(archives_list),
        tags=tuple(tags_list),
        categories=tuple(cats_list),
        warnings=tuple(warnings),
    )
