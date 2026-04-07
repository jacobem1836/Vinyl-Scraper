"""Tests for email rendering and plain-text fallback in app/services/notifier.py."""
import pytest
from jinja2 import Environment, FileSystemLoader

from app.services.notifier import _html_to_plaintext

# ---------------------------------------------------------------------------
# Sample data reused across template rendering tests
# ---------------------------------------------------------------------------
SAMPLE_DATA = {
    "item_name": "Test Album",
    "item_type": "album",
    "best_landed_price": "$32.50",
    "pct_below_typical": "24%",
    "has_typical_price": True,
    "listings": [
        {"title": "Test LP", "landed_price": "$32.50", "source": "Discogs", "ships_from": "Australia"},
        {"title": "Test LP 2", "landed_price": "$38.00", "source": "eBay", "ships_from": "US"},
    ],
    "item_url": "/item/42",
    "notify_below_pct": "20%",
}


def _render_template(data: dict | None = None) -> str:
    """Render deal_alert.html with the given data (defaults to SAMPLE_DATA)."""
    env = Environment(loader=FileSystemLoader("templates"), autoescape=True)
    template = env.get_template("deal_alert.html")
    return template.render(**(data or SAMPLE_DATA))


# ---------------------------------------------------------------------------
# Plain-text conversion tests
# ---------------------------------------------------------------------------


def test_html_to_plaintext_strips_tags():
    """Tags are removed; text content is preserved."""
    result = _html_to_plaintext("<h1>Title</h1><p>Body</p>")
    assert "Title" in result
    assert "Body" in result
    assert "<" not in result
    assert ">" not in result


def test_html_to_plaintext_table_rows():
    """Table rows produce line-separated output; cell content is preserved with separators."""
    result = _html_to_plaintext("<table><tr><td>A</td><td>B</td></tr><tr><td>C</td><td>D</td></tr></table>")
    assert "A" in result
    assert "B" in result
    assert "C" in result
    assert "D" in result
    # Two rows separated by a newline
    assert "\n" in result


# ---------------------------------------------------------------------------
# Template rendering tests
# ---------------------------------------------------------------------------


def test_template_renders_without_error():
    """Template renders without raising a Jinja2 exception."""
    result = _render_template()
    assert isinstance(result, str)
    assert len(result) > 0


def test_template_inline_css_colors():
    """Rendered HTML uses inline hex colors, not CSS custom properties."""
    result = _render_template()
    assert "#0a0a0a" in result
    assert "#111111" in result
    assert "#f5f5f5" in result
    assert "var(--" not in result


def test_template_data_in_output():
    """Item name, best landed price, and listing title appear in rendered output."""
    result = _render_template()
    assert "Test Album" in result
    assert "$32.50" in result
    assert "Test LP" in result


def test_template_mso_conditional():
    """MSO conditional comment is present for Outlook compatibility."""
    result = _render_template()
    assert "[if mso]" in result.lower() or "<!--[if mso]>" in result


def test_template_footer_link():
    """Footer contains 'View on CRATE' link pointing to item_url."""
    result = _render_template()
    assert "View on CRATE" in result
    assert "/item/42" in result
