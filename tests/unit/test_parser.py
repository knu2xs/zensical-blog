"""Unit tests for parse_post and extract_excerpt."""

from __future__ import annotations

from pathlib import Path

from zensical_blog.parser import RawPost, extract_excerpt, parse_post


class TestParsePost:
    def test_parse_with_front_matter(self, tmp_path: Path) -> None:
        md = tmp_path / "post.md"
        md.write_text(
            "---\ntitle: Hello\ndate: 2026-01-01\n---\n\nBody text.",
            encoding="utf-8",
        )
        raw = parse_post(md)
        assert isinstance(raw, RawPost)
        assert raw.source_path == md
        assert raw.raw_metadata["title"] == "Hello"
        assert "Body text." in raw.raw_content

    def test_parse_no_front_matter(self, tmp_path: Path) -> None:
        md = tmp_path / "post.md"
        md.write_text("Just a plain body.", encoding="utf-8")
        raw = parse_post(md)
        assert raw.raw_metadata == {}
        assert "plain body" in raw.raw_content

    def test_parse_draft_flag(self, tmp_path: Path) -> None:
        md = tmp_path / "draft.md"
        md.write_text(
            "---\ntitle: Draft\ndate: 2026-01-01\ndraft: true\n---\n\nContent.",
            encoding="utf-8",
        )
        raw = parse_post(md)
        assert raw.raw_metadata.get("draft") is True

    def test_parse_tags_and_categories(self, tmp_path: Path) -> None:
        md = tmp_path / "post.md"
        md.write_text(
            "---\ntitle: T\ndate: 2026-01-01\ntags:\n  - python\n"
            "  - open-source\n---\nBody.",
            encoding="utf-8",
        )
        raw = parse_post(md)
        assert raw.raw_metadata["tags"] == ["python", "open-source"]


class TestExtractExcerpt:
    def test_more_marker_splits(self) -> None:
        body = "First part.\n\n<!-- more -->\n\nSecond part."
        result = extract_excerpt(body)
        assert result == "First part."
        assert "Second part" not in result

    def test_more_marker_exact_content(self) -> None:
        body = "Intro line 1.\nIntro line 2.\n<!-- more -->\nRest."
        result = extract_excerpt(body)
        assert result == "Intro line 1.\nIntro line 2."

    def test_no_marker_first_paragraph(self) -> None:
        body = "Para one.\nStill para one.\n\nPara two."
        result = extract_excerpt(body, marker="<!-- more -->")
        assert result == "Para one.\nStill para one."

    def test_no_marker_no_blank_line_returns_full_paragraph(self) -> None:
        # Body is one long paragraph (no blank line) — returned in full.
        body = "x" * 300
        result = extract_excerpt(body, marker="<!-- more -->")
        assert result == body

    def test_body_starts_with_blank_line_fallback_200(self) -> None:
        # No first paragraph (body starts blank) — fall back to first 200 chars.
        body = "\n" + "y" * 300
        result = extract_excerpt(body, marker="<!-- more -->")
        assert len(result) <= 200

    def test_custom_marker(self) -> None:
        body = "Before.\n<!-- cut -->\nAfter."
        result = extract_excerpt(body, marker="<!-- cut -->")
        assert result == "Before."

    def test_empty_body_returns_empty(self) -> None:
        result = extract_excerpt("", marker="<!-- more -->")
        assert result == ""

    def test_marker_at_start_returns_empty(self) -> None:
        body = "<!-- more -->\nAfter."
        result = extract_excerpt(body)
        assert result == ""
