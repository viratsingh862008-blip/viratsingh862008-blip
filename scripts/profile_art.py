#!/usr/bin/env python3
"""Generate self-hosted animated SVG artwork for Aryan's GitHub profile.
Refreshes on the daily workflow schedule."""
from __future__ import annotations
import json
import os
from datetime import date, datetime
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
USERNAME = os.getenv("GITHUB_USERNAME", "viratsingh862008-blip")

class ContributionParser(HTMLParser):
    """Read contribution-day cells from GitHub's public calendar HTML."""
    def __init__(self):
        super().__init__()
        self.days = []

    def handle_starttag(self, tag, attrs):
        if tag != "td":
            return
        attrs = dict(attrs)
        if "ContributionCalendar-day" not in attrs.get("class", ""):
            return
        day, level = attrs.get("data-date"), attrs.get("data-level")
        if day and level is not None:
            try:
                self.days.append({"date": day, "level": max(0, min(4, int(level)))})
            except ValueError:
                pass


def fetch_contributions(username=USERNAME):
    url = f"https://github.com/users/{username}/contributions"
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 AryanProfileArt/1.0"})
    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="replace")
    parser = ContributionParser()
    parser.feed(html)
    if not parser.days:
        raise RuntimeError("GitHub returned no public contribution calendar cells")
    days = parser.days[-371:]
    counts = [0] * 5
    for item in days:
        counts[item["level"]] += 1
    return {
        "username": username,
        "updated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "days": days,
        "active_days": sum(1 for item in days if item["level"]),
        "level_counts": counts,
    }


def svg_heatmap(data):
    days = data.get("days", [])
    palette = ["#17211E", "#214D3B", "#327A51", "#8EBB56", "#D5F76B"]
    cells = []
    if days:
        offset = (date.fromisoformat(days[0]["date"]).weekday() + 1) % 7
        for index, item in enumerate(days):
            col, row = divmod(index + offset, 7)
            x, y = 112 + col * 13, 50 + row * 13
            delay = col * 0.025 + row * 0.018
            color = palette[item["level"]]
            cells.append(
                f'<rect x="{x}" y="{y}" width="9" height="9" rx="2" fill="{color}" opacity="0">'
                f'<title>{escape(item["date"])} · level {item["level"]}</title>'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur=".28s" fill="freeze"/>'
                f'</rect>'
            )
    status = "LIVE CALENDAR" if days else "WAITING FOR FIRST LIVE REFRESH"
    updated = escape(data.get("updated_at", ""))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="850" height="190" viewBox="0 0 850 190" role="img" aria-labelledby="title desc">
<title id="title">Aryan Singh's animated GitHub contribution heatmap</title>
<desc id="desc">Contribution cells reveal diagonally and are refreshed daily from GitHub's public contribution page.</desc>
<rect width="850" height="190" rx="14" fill="#0A2B24" stroke="#1C5B49"/>
<text x="28" y="29" fill="#D5F76B" font-family="monospace" font-size="12">aryan@github ~ $ ./contributions.sh</text>
<text x="822" y="29" text-anchor="end" fill="#FF8465" font-family="monospace" font-size="10">{status}</text>
<g fill="#AAB8AF" font-family="monospace" font-size="10"><text x="28" y="67">Mon</text><text x="28" y="93">Wed</text><text x="28" y="119">Fri</text></g>
{''.join(cells)}
<g fill="#AAB8AF" font-family="monospace" font-size="10">
<text x="112" y="166">Less</text>
<rect x="143" y="157" width="9" height="9" rx="2" fill="#17211E"/><rect x="156" y="157" width="9" height="9" rx="2" fill="#214D3B"/><rect x="169" y="157" width="9" height="9" rx="2" fill="#327A51"/><rect x="182" y="157" width="9" height="9" rx="2" fill="#8EBB56"/><rect x="195" y="157" width="9" height="9" rx="2" fill="#D5F76B"/><text x="211" y="166">More</text>
<text x="822" y="166" text-anchor="end">Updated {updated}</text></g></svg>"""


def svg_ascii():
    # Original abstract terminal glyph portrait; replace with a photo-derived ASCII
    # render if Aryan supplies a portrait image.
    art = [
        "                 .:+*#%%%%#*+:.                 ",
        "             .-*%%%%%%%%%%%%%%%%*-.             ",
        "           :#%%%%%%%%%%%%%%%%%%%%%%#:           ",
        "         =%%%%%%%%%%%%%%%%%%%%%%%%%%%%=         ",
        "        #%%%%%%%%%####****####%%%%%%%%%#        ",
        "       #%%%%%%#*=-:.        .:-=*#%%%%%%#       ",
        "      #%%%%%*-.                  .-*%%%%%#      ",
        "      %%%%%+.      .-======-.      .+%%%%%      ",
        "      %%%%*.      :%%%%%%%%%%:      .*%%%%      ",
        "      %%%%+       #%%%%%%%%%%#       +%%%%      ",
        "      %%%%*.      :%%%%%%%%%%:      .*%%%%      ",
        "       %%%%#-.     '-======-'     .-#%%%%       ",
        "        #%%%%%*-.              .-*%%%%%#        ",
        "         =%%%%%%%#*=-:....:-=*#%%%%%%%=",
        "           :#%%%%%%%%%%%%%%%%%%%%%%#:           ",
        "             .-*%%%%%%%%%%%%%%%%*-.             ",
        "                 .:+*#%%%%#*+:.                 ",
        "       A R Y A N   /   S I N G H                  ",
    ]
    lines = []
    for i, line in enumerate(art):
        lines.append(
            f'<text x="18" y="{34+i*18}" opacity="0" fill="#D5F76B" '
            f'font-family="monospace" font-size="11" xml:space="preserve">{escape(line)}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{i*.12:.2f}s" dur=".32s" fill="freeze"/></text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="410" height="390" viewBox="0 0 410 390" role="img" aria-labelledby="title">
<title id="title">Aryan Singh's animated ASCII terminal portrait artwork</title>
<rect width="410" height="390" rx="14" fill="#0A2B24" stroke="#1C5B49"/>
<text x="18" y="20" fill="#FF8465" font-family="monospace" font-size="10">● ● ●  aryan@webtea:~</text>
{''.join(lines)}
<text x="18" y="372" fill="#81968A" font-family="monospace" font-size="9">[ ASCII IDENTITY // WEBTEA TERMINAL ]</text></svg>"""


def svg_info():
    rows = [
        ("NAME", "Aryan Singh"),
        ("ROLE", "Builder / Founder / Developer"),
        ("BASE", "Bettiah, Bihar, India"),
        ("FOCUS", "Products · AI workflows · Web"),
        ("STACK", "React · TypeScript · Python"),
        ("BUILDING", "WebTea HQ / 4Wingmen"),
        ("MINDSET", "Build useful things. Ship with intent."),
    ]
    items = []
    for i, (key, value) in enumerate(rows):
        y, start = 91 + i * 36, .5 + i * .22
        items.append(
            f'<text x="28" y="{y}" fill="#D5F76B" font-family="monospace" font-size="12" opacity="0">{key:<10}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{start:.2f}s" dur=".35s" fill="freeze"/></text>'
        )
        items.append(
            f'<text x="145" y="{y}" fill="#F5F3E9" font-family="monospace" font-size="12" opacity="0">{escape(value)}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{start+.08:.2f}s" dur=".35s" fill="freeze"/></text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="490" height="390" viewBox="0 0 490 390" role="img" aria-labelledby="title">
<title id="title">Aryan Singh's animated neofetch information card</title>
<rect width="490" height="390" rx="14" fill="#0A2B24" stroke="#1C5B49"/>
<text x="22" y="28" fill="#FF8465" font-family="monospace" font-size="11">● ● ●  neofetch --profile</text>
<text x="28" y="61" fill="#D5F76B" font-family="monospace" font-size="16" font-weight="bold">ARYAN@WEBTEA</text><path d="M28 72H462" stroke="#1C5B49"/>
{''.join(items)}
<text x="28" y="365" fill="#81968A" font-family="monospace" font-size="9">STATUS: BUILDING / LEARNING / ITERATING</text></svg>"""


def main():
    (ROOT / "ascii-portrait.svg").write_text(svg_ascii(), encoding="utf-8")
    (ROOT / "info-card.svg").write_text(svg_info(), encoding="utf-8")
    data_path = ROOT / "data" / "contributions.json"
    try:
        data = fetch_contributions()
        data_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        if not data_path.exists():
            raise
        data = json.loads(data_path.read_text(encoding="utf-8"))
    (ROOT / "contrib-heatmap.svg").write_text(svg_heatmap(data), encoding="utf-8")

if __name__ == "__main__":
    main()
