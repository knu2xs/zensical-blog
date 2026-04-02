"""Unit tests for slugify and SlugRegistry."""

from __future__ import annotations

from zensical_blog.slugifier import SlugRegistry, slugify


class TestSlugify:
    def test_ascii_lowercase(self) -> None:
        assert slugify("hello world") == "hello-world"

    def test_ascii_uppercase(self) -> None:
        assert slugify("Hello World") == "hello-world"

    def test_accented_chars(self) -> None:
        assert slugify("café") == "cafe"

    def test_hash_symbol(self) -> None:
        assert slugify("C#") == "c"

    def test_numbers_preserved(self) -> None:
        assert slugify("Python 3.11") == "python-3-11"

    def test_multiple_separators_collapsed(self) -> None:
        assert slugify("a  --  b") == "a-b"

    def test_leading_trailing_stripped(self) -> None:
        assert slugify("  hello-world  ") == "hello-world"

    def test_empty_returns_x(self) -> None:
        assert slugify("") == "x"
        assert slugify("###") == "x"

    def test_truncated_to_80_chars(self) -> None:
        long_label = "a" * 90
        result = slugify(long_label)
        assert len(result) <= 80

    def test_truncation_strips_trailing_dash(self) -> None:
        # Construct a label that produces a slug with a dash at position 80
        label = "a" * 79 + "-" + "b"
        result = slugify(label)
        assert not result.endswith("-")

    def test_unicode_combining_marks_stripped(self) -> None:
        # ñ decomposes to n + combining tilde; tilde should be stripped
        assert slugify("niño") == "nino"

    def test_c_sharp_to_c(self) -> None:
        assert slugify("C#") == "c"

    def test_c_sharp_language(self) -> None:
        assert slugify("C sharp") == "c-sharp"


class TestSlugRegistry:
    def test_no_collision(self) -> None:
        reg = SlugRegistry()
        s = reg.register_label("hello")
        assert s == "hello"
        assert not reg.warnings

    def test_same_label_twice_returns_same(self) -> None:
        reg = SlugRegistry()
        s1 = reg.register_label("hello")
        s2 = reg.register_label("hello")
        assert s1 == s2
        assert not reg.warnings

    def test_collision_two_labels(self) -> None:
        # "C#" and "C sharp" both slugify to "c" ... wait, "C sharp" → "c-sharp"
        # Let's use labels that actually collide
        # "C#" → "c", "C " → "c" (special case)
        reg = SlugRegistry()
        # Both "abc!" and "abc?" slugify to "abc"
        s1 = reg.register_label("abc!")
        s2 = reg.register_label("abc?")
        # After collision, re-sorted: ["abc!", "abc?"] (code point order)
        # "abc!" has "!" (0x21), "abc?" has "?" (0x3F), so "abc!" < "abc?"
        assert s1 == reg.get_slug("abc!")
        assert s2 == reg.get_slug("abc?")
        assert reg.get_slug("abc!") == "abc"
        assert reg.get_slug("abc?") == "abc-2"
        assert len(reg.warnings) == 1
        assert reg.warnings[0].code == "SLUG_COLLISION"

    def test_explicit_map_bypass(self) -> None:
        reg = SlugRegistry()
        s = reg.register_label("C#", explicit_map={"C#": "csharp"})
        assert s == "csharp"
        assert not reg.warnings

    def test_c_sharp_collision(self) -> None:
        """'C#' and 'C ' both produce base slug 'c'."""
        reg = SlugRegistry()
        # "C#" → "c", "C " → "c" via slugify
        reg.register_label("C#")
        reg.register_label("C ")
        # After collision: sorted ["C ", "C#"] by code point ("C " < "C#")
        # "C " gets "c", "C#" gets "c-2"
        assert reg.get_slug("C ") == "c"
        assert reg.get_slug("C#") == "c-2"
        assert len(reg.warnings) == 1

    def test_three_way_collision(self) -> None:
        reg = SlugRegistry()
        reg.register_label("abc!")
        reg.register_label("abc?")
        reg.register_label("abc.")
        # sorted by unicode: "abc!" (0x21) < "abc." (0x2E) < "abc?" (0x3F)
        assert reg.get_slug("abc!") == "abc"
        assert reg.get_slug("abc.") == "abc-2"
        assert reg.get_slug("abc?") == "abc-3"

    def test_get_slug_unknown_returns_none(self) -> None:
        reg = SlugRegistry()
        assert reg.get_slug("nope") is None

    def test_post_slug_date_prefix_strip(self) -> None:
        """Filename date prefix YYYY-MM-DD- is stripped before slugifying."""
        import re

        def derive_post_slug(filename_stem: str) -> str:
            stem = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", filename_stem)
            return slugify(stem)

        assert derive_post_slug("2026-04-01-my-post") == "my-post"
        assert derive_post_slug("my-post") == "my-post"
