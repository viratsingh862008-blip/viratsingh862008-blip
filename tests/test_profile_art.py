import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from profile_art import ContributionParser, svg_heatmap, svg_ascii, svg_info

def test_parser_reads_contribution_day_cells():
    parser = ContributionParser()
    parser.feed('<td class="ContributionCalendar-day" data-date="2026-11-14" data-level="3"></td>')
    assert parser.days == [{"date": "2026-11-14", "level": 3}]

def test_heatmap_is_accessible_and_animated():
    svg = svg_heatmap({"days": [{"date": "2026-11-14", "level": 2}], "updated_at": "now"})
    assert "contribution heatmap" in svg.lower()
    assert "<animate" in svg
    assert "2026-11-14" in svg

def test_terminal_cards_include_animations():
    assert "<animate" in svg_ascii()
    assert "<animate" in svg_info()
