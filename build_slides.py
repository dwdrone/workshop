#!/usr/bin/env python3
"""
build_slides.py — Convert .md course files to Dark Wolf HTML.

Two output styles, chosen automatically per file:
    * Presentations / activities  ->  Reveal.js slide deck (denser layout,
      more content fits on each slide).
    * Labs                        ->  a single scrollable "lab guide" page
      with a sticky phase sidebar and a reading-progress bar, so students can
      work through the steps at their own pace instead of clicking slides.

No API required. Run whenever you finish editing your markdown.

Requirements:
    pip install markdown

Usage:
    python build_slides.py                         # rebuild everything
    python build_slides.py day1/01-uas.md          # rebuild one file
    python build_slides.py --list                  # show the file map
"""

import re
import sys
from pathlib import Path

try:
    import markdown as md_lib
    from markdown.extensions.tables import TableExtension
    from markdown.extensions.fenced_code import FencedCodeExtension
except ImportError:
    print("[ERROR] markdown library not installed.")
    print("        Run:  pip install markdown")
    sys.exit(1)

# ---------------------------------------------------------------------------
# File map
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent

FILE_MAP = {
    "day1/00-lab-kali-setup.md":            "slides/00-lab-kali-setup.html",
    "day1/01-uas-cybersecurity.md":         "slides/01-uas-cybersecurity.html",
    "day1/02-attack-surface-activity.md":   "slides/02-attack-surface.html",
    "day1/03-uav-hardware-software.md":     "slides/03-uav-hardware-software.html",
    "day1/04-lab-firmware-analysis.md":     "slides/04-lab-firmware-analysis.html",
    "day1/05-uav-flight-controllers.md":    "slides/05-uav-flight-controllers.html",
    "day1/06-lab-qgroundcontrol.md":        "slides/06-lab-qgroundcontrol.html",
    "day1/07-android-cybersecurity.md":     "slides/07-android-cybersecurity.html",
    "day1/08-lab-android-gcs.md":           "slides/08-lab-android-gcs.html",
    "day1/09-gcs-hardware-software.md":     "slides/09-gcs-hardware-software.html",
    "day1/10-lab-gcs-exploitation.md":      "slides/10-lab-gcs-exploitation.html",
    "day2/11-rf-communications.md":         "slides/11-rf-communications.html",
    "day2/12-lab-cracking-wireless.md":     "slides/12-lab-cracking-wireless.html",
    "day2/13-droneid-remoteid.md":          "slides/13-droneid-remoteid.html",
    "day2/14-lab-remoteid.md":              "slides/14-lab-remoteid.html",
    "day2/15-sik-telemetry-radios.md":      "slides/15-sik-telemetry-radios.html",
    "day2/16-lab-sik-hacks.md":             "slides/16-lab-sik-hacks.html",
    "day2/17-mavlink.md":                   "slides/17-mavlink.html",
    "day2/18-lab-mavlink-sniffing.md":      "slides/18-lab-mavlink-sniffing.html",
    "day2/19-uav-cameras.md":               "slides/19-uav-cameras.html",
    "day2/20-lab-analog-video.md":          "slides/20-lab-analog-video.html",
    "day1/21-uas-logging.md":               "slides/21-uas-logging.html",
    "day1/22-lab-forensics.md":             "slides/22-lab-forensics.html",
    "day2/23-cybersecurity-review.md":      "slides/23-cybersecurity-review.html",
    "day2/99-lab-chanbw.md":      "slides/99-lab-chanbw.html",
}

# ---------------------------------------------------------------------------
# Shared Dark Wolf palette + reusable component styles
# ---------------------------------------------------------------------------

DW_VARS = """\
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    :root {
        --dw-bg: #080808; --dw-panel: #111111; --dw-border: #1a1a1a;
        --dw-green: #68E01A; --dw-green-glow: rgba(104,224,26,0.1); --dw-green-border: rgba(104,224,26,0.3);
        --dw-white: #f0f0f0; --dw-gray: #7a8290;
    }"""

# Small, reusable pieces shared by both the slide and lab stylesheets.
DW_COMPONENTS = """\
    .tag { display: inline-block; padding: 3px 12px; border-radius: 20px; font-size: 0.6em; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-right: 6px; }
    .tag-presentation { border: 1px solid var(--dw-green); color: var(--dw-green); background: var(--dw-green-glow); }
    .tag-lab { border: 1px solid #60a5fa; color: #93c5fd; background: rgba(96,165,250,0.1); }
    .tag-activity { border: 1px solid #a78bfa; color: #c4b5fd; background: rgba(167,139,250,0.1); }
    .objective-box { background: var(--dw-green-glow); border-left: 3px solid var(--dw-green); padding: 10px 16px; border-radius: 0 6px 6px 0; margin: 8px 0; }
    .warning-box { background: rgba(239,68,68,0.08); border-left: 3px solid #ef4444; padding: 10px 16px; border-radius: 0 6px 6px 0; margin: 10px 0; }
    .phase-box { background: var(--dw-green-glow); border-left: 3px solid var(--dw-green); padding: 10px 16px; border-radius: 0 6px 6px 0; margin: 8px 0; font-weight: 600; color: var(--dw-green); }
    .highlight-green { color: var(--dw-green); font-weight: 600; }
    .highlight-red { color: #f87171; font-weight: 600; }
    .highlight-yellow { color: #fbbf24; font-weight: 600; }
    .highlight-blue { color: #60a5fa; font-weight: 600; }"""

# ---------------------------------------------------------------------------
# Presentation (Reveal.js) CSS — tuned for DENSITY so more fits per slide
# ---------------------------------------------------------------------------

DW_CSS = DW_VARS + """
    :root {
        --r-background-color: #080808; --r-main-color: #f0f0f0; --r-heading-color: #ffffff;
        --r-link-color: #68E01A; --r-main-font: 'Inter', system-ui, sans-serif;
        --r-heading-font: 'Inter', system-ui, sans-serif; --r-code-font: 'JetBrains Mono','Courier New',monospace;
        --r-main-font-size: 23px;
    }
    .reveal-viewport { background: var(--dw-bg); }
    .reveal .slides { text-align: left; }
    .reveal .slides section { top: 0 !important; }
    .reveal h1, .reveal h2, .reveal h3 { text-transform: none; font-weight: 700; }
    .reveal h1 { color: var(--dw-green); font-size: 1.8em; letter-spacing: -1px; }
    .reveal h2 { color: var(--dw-white); border-bottom: 2px solid var(--dw-green); padding-bottom: 6px; margin-bottom: 14px; font-size: 1.05em; }
    .reveal h3 { color: var(--dw-green); font-size: 0.82em; text-transform: uppercase; letter-spacing: 1.5px; margin: 14px 0 8px; }
    .reveal a { color: var(--dw-green); }
    .reveal p { line-height: 1.4; margin: 0 0 8px; }
    .reveal ul, .reveal ol { margin: 0 0 8px; }
    .reveal li { line-height: 1.38; }
    .reveal ul li { margin-bottom: 4px; }
    .reveal ul li::marker { color: var(--dw-green); }
    .reveal .progress span { background: var(--dw-green); }
    .reveal .controls { color: var(--dw-green); }
    .reveal .slide-number { color: var(--dw-green); background: rgba(0,0,0,0.7); font-family: var(--r-code-font); font-size: 0.52em; padding: 4px 10px; border-radius: 4px; }
    .reveal .slides > section { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='97' viewBox='0 0 56 97'%3E%3Cpath fill='none' stroke='%23161616' stroke-width='1' d='M28 0l28 16.3v32.7L28 65.3 0 49V16.3zM28 32l28 16.3v32.7L28 97 0 80.7V48z'/%3E%3C/svg%3E"); background-size: 56px 97px; }
""" + DW_COMPONENTS + """
    .terminal { background: #050505; border: 1px solid var(--dw-border); border-top: 2px solid var(--dw-green); border-radius: 0 0 8px 8px; padding: 12px; font-family: var(--r-code-font); font-size: 0.82em; line-height: 1.55; color: var(--dw-green); white-space: pre; overflow-x: auto; }
    .terminal::before { content: '\\25CF \\25CF \\25CF'; display: block; color: #252525; margin-bottom: 8px; letter-spacing: 5px; font-size: 0.9em; }
    .reveal pre { margin: 0 0 8px; box-shadow: none; width: 100%; }
    .reveal pre code { background: #050505 !important; color: var(--dw-green) !important; border: 1px solid var(--dw-border); border-radius: 6px; padding: 10px 12px; font-size: 0.78em; line-height: 1.45; max-height: none; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; align-items: start; }
    .reveal table { border-collapse: collapse; width: 100%; font-size: 0.68em; margin: 4px 0 8px; }
    .reveal table th { background: var(--dw-green-glow); color: var(--dw-green); border: 1px solid var(--dw-green-border); padding: 5px 9px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.82em; }
    .reveal table td { border: 1px solid var(--dw-border); padding: 5px 9px; color: var(--dw-white); vertical-align: top; }
    .reveal table tr:nth-child(even) td { background: rgba(255,255,255,0.02); }
    .reveal img { max-height: 62vh; width: auto; border-radius: 6px; }
    .reveal strong, .reveal b { color: var(--dw-green); }
    .reveal :not(pre) > code { color: var(--dw-green); font-size: 0.9em; }
    .dw-back { position: fixed; top: 14px; left: 16px; z-index: 60; color: var(--dw-gray); text-decoration: none;
        font-family: var(--r-main-font); font-size: 14px; font-weight: 600; padding: 6px 12px;
        background: rgba(8,8,8,0.72); border: 1px solid var(--dw-border); border-radius: 6px;
        backdrop-filter: blur(4px); transition: color .15s, border-color .15s; }
    .dw-back:hover { color: var(--dw-green); border-color: var(--dw-green-border); }
    @media print { .dw-back { display: none; } }"""

# ---------------------------------------------------------------------------
# Lab (scrollable guide) CSS
# ---------------------------------------------------------------------------

LAB_CSS = DW_VARS + """
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
        margin: 0; background: var(--dw-bg); color: var(--dw-white);
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        font-size: 17px; line-height: 1.6;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='97' viewBox='0 0 56 97'%3E%3Cpath fill='none' stroke='%23111111' stroke-width='1' d='M28 0l28 16.3v32.7L28 65.3 0 49V16.3zM28 32l28 16.3v32.7L28 97 0 80.7V48z'/%3E%3C/svg%3E");
        background-size: 56px 97px; background-attachment: fixed;
    }
    a { color: var(--dw-green); }

    /* ── Reading-progress bar (fixed, very top) ── */
    .progress-track { position: fixed; top: 0; left: 0; right: 0; height: 3px; background: #141414; z-index: 60; }
    .progress-fill { height: 100%; width: 0; background: var(--dw-green); box-shadow: 0 0 10px rgba(104,224,26,0.6); transition: width 0.1s linear; }

    /* ── Top bar ── */
    .lab-topbar { position: fixed; top: 3px; left: 0; right: 0; height: 52px; z-index: 55;
        display: flex; align-items: center; gap: 14px; padding: 0 20px;
        background: rgba(8,8,8,0.92); backdrop-filter: blur(6px); border-bottom: 1px solid var(--dw-border); }
    .lab-topbar .back { color: var(--dw-gray); text-decoration: none; font-size: 0.85em; white-space: nowrap; }
    .lab-topbar .back:hover { color: var(--dw-green); }
    .lab-topbar .crumb { color: var(--dw-white); font-weight: 600; font-size: 0.9em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .lab-topbar .crumb .mod { color: var(--dw-green); font-family: 'JetBrains Mono', monospace; margin-right: 8px; font-size: 0.85em; }
    .lab-topbar .pct { margin-left: auto; color: var(--dw-gray); font-family: 'JetBrains Mono', monospace; font-size: 0.8em; }
    .nav-toggle { display: none; background: none; border: 1px solid var(--dw-border); color: var(--dw-green); border-radius: 6px; padding: 4px 10px; font-size: 1.1em; cursor: pointer; }

    /* ── Layout ── */
    .lab-layout { display: grid; grid-template-columns: 264px 1fr; max-width: 1320px; margin: 0 auto; padding-top: 55px; }

    /* ── Sidebar ── */
    .lab-nav { position: sticky; top: 55px; align-self: start; height: calc(100vh - 55px); overflow-y: auto;
        padding: 22px 12px 40px 20px; border-right: 1px solid var(--dw-border); }
    .lab-nav .nav-label { color: var(--dw-gray); font-size: 0.68em; letter-spacing: 2px; text-transform: uppercase; margin: 0 0 12px 8px; }
    .lab-nav a { display: block; text-decoration: none; color: var(--dw-gray); border-radius: 6px;
        padding: 6px 10px; font-size: 0.86em; line-height: 1.35; border-left: 2px solid transparent; transition: all 0.12s; }
    .lab-nav a.nav-top { color: #c9cdd4; font-weight: 600; margin-top: 3px; }
    .lab-nav a.nav-sub { font-size: 0.8em; padding: 4px 10px 4px 22px; color: var(--dw-gray); }
    .lab-nav a:hover { color: var(--dw-white); background: rgba(255,255,255,0.03); }
    .lab-nav a.active { color: var(--dw-green); border-left-color: var(--dw-green); background: var(--dw-green-glow); }

    /* ── Main content ── */
    .lab-main { padding: 8px 46px 120px; min-width: 0; }
    .lab-hero { padding: 26px 0 22px; border-bottom: 1px solid var(--dw-border); margin-bottom: 10px; }
    .lab-hero .meta { margin-bottom: 12px; }
    .lab-hero .meta .dur { color: var(--dw-gray); font-size: 0.82em; margin-left: 4px; }
    .lab-hero h1 { color: var(--dw-green); font-size: 2em; line-height: 1.15; letter-spacing: -0.5px; margin: 6px 0 8px; }
    .lab-hero .section-name { color: var(--dw-gray); font-size: 0.9em; }

    .lab-section { padding: 26px 0 8px; scroll-margin-top: 70px; border-top: 1px solid #121212; }
    .lab-section:first-of-type { border-top: none; }
    .lab-section h2 { color: var(--dw-white); font-size: 1.4em; margin: 0 0 14px; padding-bottom: 8px; border-bottom: 2px solid var(--dw-green); }
    .lab-section h3 { color: var(--dw-green); font-size: 0.82em; text-transform: uppercase; letter-spacing: 1.5px; margin: 22px 0 10px; scroll-margin-top: 70px; }
    .lab-section p { margin: 0 0 12px; }
    .lab-section ul, .lab-section ol { margin: 0 0 14px; padding-left: 24px; }
    .lab-section li { margin-bottom: 6px; }
    .lab-section li::marker { color: var(--dw-green); }
    .lab-section strong, .lab-section b { color: var(--dw-green); }
    .lab-section img { max-width: 100%; height: auto; border: 1px solid var(--dw-border); border-radius: 8px; margin: 10px 0; display: block; }
""" + DW_COMPONENTS + """
    .lab-section pre { margin: 0 0 16px; }
    .lab-section pre code { display: block; background: #050505; color: var(--dw-green); border: 1px solid var(--dw-border);
        border-top: 2px solid var(--dw-green); border-radius: 8px; padding: 14px 16px; font-family: 'JetBrains Mono','Courier New',monospace;
        font-size: 0.82em; line-height: 1.6; overflow-x: auto; }
    .lab-section :not(pre) > code { background: #050505; color: var(--dw-green); border: 1px solid var(--dw-border);
        border-radius: 4px; padding: 1px 6px; font-family: 'JetBrains Mono','Courier New',monospace; font-size: 0.85em; }
    .lab-section table { border-collapse: collapse; width: 100%; font-size: 0.86em; margin: 6px 0 18px; display: block; overflow-x: auto; }
    .lab-section table th { background: var(--dw-green-glow); color: var(--dw-green); border: 1px solid var(--dw-green-border);
        padding: 8px 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.9em; text-align: left; }
    .lab-section table td { border: 1px solid var(--dw-border); padding: 8px 12px; color: var(--dw-white); vertical-align: top; }
    .lab-section table tr:nth-child(even) td { background: rgba(255,255,255,0.02); }

    .lab-footer { border-top: 1px solid var(--dw-border); margin-top: 40px; padding: 22px 0; color: #3a3a3a; font-size: 0.8em; }

    /* ── Responsive ── */
    @media (max-width: 900px) {
        .lab-layout { grid-template-columns: 1fr; }
        .nav-toggle { display: inline-block; }
        .lab-nav { position: fixed; top: 55px; left: 0; bottom: 0; width: 280px; background: #0a0a0a; z-index: 50;
            transform: translateX(-102%); transition: transform 0.2s ease; border-right: 1px solid var(--dw-border); }
        body.nav-open .lab-nav { transform: translateX(0); }
        .lab-main { padding: 8px 20px 100px; }
    }"""

# ---------------------------------------------------------------------------
# Markdown parser helpers
# ---------------------------------------------------------------------------

def _preprocess_md(text: str) -> str:
    """
    Insert blank lines before list items when the preceding non-empty line is
    not already blank, and drop bare '---' separators. Without the blank-line
    fix, lists that immediately follow bold headers (e.g. **Examples:**\n- item)
    are treated as plain paragraph text instead of <ul>/<ol>.
    """
    lines = text.splitlines()
    out: list[str] = []
    in_fence = False
    for line in lines:
        if line.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        if line.strip() == "---":
            continue

        is_list_item = bool(re.match(r"^[-*+]\s", line) or re.match(r"^\d+\.\s", line))
        prev_is_blank = not out or not out[-1].strip()

        if is_list_item and not prev_is_blank:
            out.append("")
        out.append(line)

    return "\n".join(out)


def _md_convert(text: str) -> str:
    """Convert a markdown fragment to HTML using the markdown library."""
    converter = md_lib.Markdown(
        extensions=["tables", "fenced_code"],
        output_format="html",
    )
    return converter.convert(_preprocess_md(text).strip())


def _post_process(html: str) -> str:
    """Apply Dark Wolf class transformations to converted HTML."""
    # blockquote -> warning-box
    html = re.sub(
        r"<blockquote>\s*<p>(.*?)</p>\s*</blockquote>",
        r'<div class="warning-box">\1</div>',
        html,
        flags=re.DOTALL,
    )
    return html


def _extract_objectives(body: str) -> list[str]:
    """Pull the top-level bullet points from an Objectives section."""
    items = []
    for line in body.splitlines():
        m = re.match(r"^[-*]\s+(.*)", line)
        if m:
            items.append(m.group(1).strip())
    return items


def _slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "section"


def _unique_slug(text: str, seen: set) -> str:
    base = _slugify(text)
    slug = base
    i = 2
    while slug in seen:
        slug = f"{base}-{i}"
        i += 1
    seen.add(slug)
    return slug

# ---------------------------------------------------------------------------
# Document parsing
# ---------------------------------------------------------------------------

def parse_document(text: str) -> tuple[dict, list[tuple[str, str]]]:
    """
    Returns:
        metadata  — dict with keys: Title, Type, Duration, Section
        sections  — list of (heading, body_markdown) pairs
    """
    lines = text.splitlines()
    meta: dict = {}
    sections: list[tuple[str, str]] = []

    for line in lines:
        if line.startswith("# ") and not line.startswith("## "):
            meta["Title"] = line[2:].strip()
            break

    for line in lines:
        m = re.match(r"\*\*(\w[\w\s]*):\*\*\s*(.*)", line)
        if m:
            meta[m.group(1).strip()] = m.group(2).strip()

    current_heading: str | None = None
    current_body: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if current_heading is not None:
                sections.append((current_heading, "\n".join(current_body).strip()))
            current_heading = line[3:].strip()
            current_body = []
        else:
            if current_heading is not None:
                current_body.append(line)

    if current_heading is not None:
        sections.append((current_heading, "\n".join(current_body).strip()))

    cleaned = []
    for heading, body in sections:
        body = re.sub(r"\n---\s*$", "", body.rstrip())
        cleaned.append((heading, body.strip()))

    return meta, cleaned


def merge_repeated_sections(sections: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """
    Merge consecutive sections that share the same ## heading into one block.
    Lab files frequently repeat a phase heading (e.g. eight
    '## Phase 6: Root Authentication Bypass' blocks); merging keeps the
    sidebar clean while preserving every step under one entry.
    """
    merged: list[list] = []
    for heading, body in sections:
        if merged and merged[-1][0] == heading:
            if body.strip():
                merged[-1][1] = (merged[-1][1] + "\n\n" + body).strip()
        else:
            merged.append([heading, body])
    return [(h, b) for h, b in merged]

# ---------------------------------------------------------------------------
# Presentation (Reveal.js) renderers
# ---------------------------------------------------------------------------

def _tag_class(module_type: str) -> str:
    t = module_type.lower()
    if "lab" in t:
        return "tag-lab"
    if "activity" in t:
        return "tag-activity"
    return "tag-presentation"


def render_title_slide(module_num: str, meta: dict) -> str:
    title    = meta.get("Title", "Untitled")
    mtype    = meta.get("Type", "Presentation")
    duration = meta.get("Duration", "")
    section  = meta.get("Section", "")
    tag_cls  = _tag_class(mtype)
    dur_html = f'<span style="color:var(--dw-gray); font-size:0.7em;">{duration}</span>' if duration else ""

    return f"""
<section data-background-gradient="radial-gradient(circle at 20% 50%, #060606 0%, #080808 60%)">
    <div style="text-align:center; padding-top: 40px;">
        <p><span class="tag {tag_cls}">{mtype.upper()}</span>{dur_html}</p>
        <h1 style="font-size:2em; margin-top: 16px;">{title}</h1>
        <h3 style="color:var(--dw-gray); font-weight:300; margin-top: 8px;">Module {module_num}</h3>
        <hr style="border-color: var(--dw-green-border); margin: 24px auto; width: 60%;">
        <p style="color:var(--dw-green); font-size:0.9em;">{section}</p>
        <p style="color:var(--dw-gray); font-size:0.7em; margin-top: 40px;">Hack Our Drone Workshop &mdash; Dark Wolf Solutions</p>
    </div>
</section>"""


def render_objectives_slide(body: str) -> str:
    items = _extract_objectives(body)
    if not items:
        return render_content_slide("Objectives", body)
    boxes = "\n    ".join(
        f'<div class="objective-box">{_md_convert(item)}</div>' for item in items
    )
    boxes = re.sub(r"<div class=\"objective-box\"><p>(.*?)</p></div>",
                   r'<div class="objective-box">\1</div>', boxes, flags=re.DOTALL)
    return f"""
<section>
    <h2>Objectives</h2>
    {boxes}
</section>"""


def render_content_slide(heading: str, body: str) -> str:
    """Render a single content slide. Long sections are auto-split."""
    chunks = _split_body(body)
    if len(chunks) == 1:
        html_body = _post_process(_md_convert(chunks[0]))
        return f"""
<section>
    <h2>{heading}</h2>
    {html_body}
</section>"""

    slides = []
    total = len(chunks)
    for i, chunk in enumerate(chunks, 1):
        label = f"{heading} ({i}/{total})"
        html_body = _post_process(_md_convert(chunk))
        slides.append(f"""
<section>
    <h2>{label}</h2>
    {html_body}
</section>""")
    return "\n".join(slides)


def _split_body(body: str) -> list[str]:
    """
    Split a section body into multiple slides only if it would clearly
    overflow. Thresholds are generous so MORE content fits on each slide
    (the denser CSS gives the room); we split mainly on ### sub-headings.
    """
    bullet_count = len(re.findall(r"^[-*]\s", body, re.MULTILINE))
    sub_headings = list(re.finditer(r"^### ", body, re.MULTILINE))

    if bullet_count <= 16 and len(sub_headings) <= 4:
        return [body]  # Fits on one denser slide

    if len(sub_headings) >= 4:
        parts = re.split(r"(?=^### )", body, flags=re.MULTILINE)
        chunks = []
        i = 0
        while i < len(parts):
            if i + 1 < len(parts):
                combined = parts[i] + "\n" + parts[i + 1]
                if len(re.findall(r"^[-*]\s", combined, re.MULTILINE)) <= 18:
                    chunks.append(combined.strip())
                    i += 2
                    continue
            chunks.append(parts[i].strip())
            i += 1
        return [c for c in chunks if c]

    # Otherwise split on a blank line near the midpoint
    lines = body.splitlines()
    mid = len(lines) // 2
    split_at = mid
    for delta in range(0, mid):
        if mid - delta >= 0 and not lines[mid - delta].strip():
            split_at = mid - delta
            break
        if mid + delta < len(lines) and not lines[mid + delta].strip():
            split_at = mid + delta
            break
    return [
        "\n".join(lines[:split_at]).strip(),
        "\n".join(lines[split_at:]).strip(),
    ]


def build_slide_html(module_num: str, title: str, slides_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Module {module_num} – {title}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/reset.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/reveal.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/theme/black.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/plugin/highlight/monokai.css">
    <style>
{DW_CSS}
    </style>
</head>
<body>
<a class="dw-back" href="index.html">&#8592; All Modules</a>
<div class="reveal">
<div class="slides">
{slides_html}
</div>
</div>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/reveal.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/plugin/highlight/highlight.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/plugin/notes/notes.js"></script>
<script>
Reveal.initialize({{
    hash: true,
    slideNumber: 'c/t',
    width: 1180,
    height: 760,
    margin: 0.04,
    minScale: 0.2,
    maxScale: 1.5,
    transition: 'fade',
    transitionSpeed: 'fast',
    backgroundTransition: 'none',
    mouseWheel: true,
    plugins: [RevealHighlight, RevealNotes]
}});
</script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Lab (scrollable guide) renderer
# ---------------------------------------------------------------------------

def _render_lab_section_body(body: str, seen: set) -> tuple[str, list[tuple[str, str]]]:
    """
    Convert one lab section's markdown to HTML, tag each ### sub-heading with a
    unique id, and return (html, [(id, text), ...]) sub-item list for the nav.
    """
    html = _post_process(_md_convert(body))
    subitems: list[tuple[str, str]] = []

    def repl(m):
        inner = m.group(1)
        text = re.sub(r"<[^>]+>", "", inner).strip()
        sid = _unique_slug("sub-" + text, seen)
        subitems.append((sid, text))
        return f'<h3 id="{sid}">{inner}</h3>'

    html = re.sub(r"<h3>(.*?)</h3>", repl, html, flags=re.DOTALL)
    return html, subitems


def render_lab_document(module_num: str, meta: dict, sections: list[tuple[str, str]]) -> str:
    title    = meta.get("Title", "Lab")
    mtype    = meta.get("Type", "Lab")
    duration = meta.get("Duration", "")
    section  = meta.get("Section", "")

    sections = merge_repeated_sections(sections)

    seen_ids: set = set()
    nav_entries: list[str] = []
    content_blocks: list[str] = []

    for heading, body in sections:
        if not body.strip() and not heading.strip():
            continue
        sec_id = _unique_slug(heading, seen_ids)

        if heading.strip().lower() == "objectives":
            items = _extract_objectives(body)
            if items:
                boxes = "\n".join(
                    f'<div class="objective-box">{re.sub(r"^<p>|</p>$", "", _md_convert(it)).strip()}</div>'
                    for it in items
                )
                body_html = boxes
                subitems: list[tuple[str, str]] = []
            else:
                body_html, subitems = _render_lab_section_body(body, seen_ids)
        else:
            body_html, subitems = _render_lab_section_body(body, seen_ids)

        content_blocks.append(f"""
<section class="lab-section" id="{sec_id}">
    <h2>{heading}</h2>
    {body_html}
</section>""")

        nav_entries.append(
            f'<a class="nav-top" data-target="{sec_id}" href="#{sec_id}">{heading}</a>'
        )
        for sid, text in subitems:
            nav_entries.append(f'<a class="nav-sub" href="#{sid}">{text}</a>')

    nav_html = "\n            ".join(nav_entries)
    content_html = "\n".join(content_blocks)
    dur_html = f'<span class="dur">⏱ {duration}</span>' if duration else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lab {module_num} – {title}</title>
    <style>
{LAB_CSS}
    </style>
</head>
<body>
<div class="progress-track"><div class="progress-fill" id="progress-fill"></div></div>

<header class="lab-topbar">
    <button class="nav-toggle" id="nav-toggle" aria-label="Toggle phases">☰</button>
    <a class="back" href="index.html">← All Modules</a>
    <span class="crumb"><span class="mod">LAB {module_num}</span>{title}</span>
    <span class="pct" id="pct">0%</span>
</header>

<div class="lab-layout">
    <nav class="lab-nav" id="lab-nav">
        <p class="nav-label">On this page</p>
            {nav_html}
    </nav>

    <main class="lab-main">
        <div class="lab-hero">
            <div class="meta"><span class="tag tag-lab">{mtype.upper()}</span>{dur_html}</div>
            <h1>{title}</h1>
            <div class="section-name">{section}</div>
        </div>
{content_html}
        <footer class="lab-footer">
            Hack Our Drone &mdash; Dark Wolf Solutions &bull; For authorized training use only.
        </footer>
    </main>
</div>

<script>
(function () {{
    var fill = document.getElementById('progress-fill');
    var pct  = document.getElementById('pct');
    function onScroll() {{
        var h = document.documentElement;
        var max = h.scrollHeight - h.clientHeight;
        var p = max > 0 ? (h.scrollTop / max) : 0;
        var v = Math.max(0, Math.min(100, p * 100));
        fill.style.width = v.toFixed(1) + '%';
        pct.textContent = Math.round(v) + '%';
    }}
    document.addEventListener('scroll', onScroll, {{ passive: true }});
    window.addEventListener('resize', onScroll);
    onScroll();

    // Highlight the current section in the sidebar.
    var tops = Array.prototype.slice.call(document.querySelectorAll('.lab-nav a.nav-top'));
    var byId = {{}};
    tops.forEach(function (a) {{ byId[a.getAttribute('data-target')] = a; }});
    var obs = new IntersectionObserver(function (entries) {{
        entries.forEach(function (e) {{
            if (e.isIntersecting) {{
                tops.forEach(function (a) {{ a.classList.remove('active'); }});
                var a = byId[e.target.id];
                if (a) {{
                    a.classList.add('active');
                    a.scrollIntoView({{ block: 'nearest' }});
                }}
            }}
        }});
    }}, {{ rootMargin: '-15% 0px -75% 0px', threshold: 0 }});
    document.querySelectorAll('section.lab-section').forEach(function (s) {{ obs.observe(s); }});

    // Mobile sidebar toggle.
    var toggle = document.getElementById('nav-toggle');
    var nav = document.getElementById('lab-nav');
    toggle.addEventListener('click', function () {{ document.body.classList.toggle('nav-open'); }});
    nav.addEventListener('click', function (e) {{
        if (e.target.tagName === 'A') document.body.classList.remove('nav-open');
    }});
}})();
</script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Build dispatch
# ---------------------------------------------------------------------------

def _is_lab(meta: dict, md_path_rel: str) -> bool:
    if "lab" in meta.get("Type", "").lower():
        return True
    return "lab" in Path(md_path_rel).name.lower()


def build_slide(md_path_rel: str) -> bool:
    """Convert one markdown file to its HTML output. Returns True on success."""
    md_path = BASE_DIR / md_path_rel
    html_rel = FILE_MAP.get(md_path_rel.replace("\\", "/"))

    if html_rel is None:
        print(f"  [SKIP] Not in FILE_MAP: {md_path_rel}")
        return False

    if not md_path.exists():
        print(f"  [ERROR] Not found: {md_path}")
        return False

    text = md_path.read_text(encoding="utf-8")
    meta, sections = parse_document(text)

    m = re.match(r"(\d+)", Path(md_path_rel).name)
    module_num = m.group(1) if m else "??"
    title = meta.get("Title", Path(md_path_rel).stem)

    if _is_lab(meta, md_path_rel):
        html = render_lab_document(module_num, meta, sections)
        kind = "LAB "
    else:
        all_slides = [render_title_slide(module_num, meta)]
        for heading, body in sections:
            if not body.strip():
                continue
            if heading.lower() == "objectives":
                all_slides.append(render_objectives_slide(body))
            else:
                all_slides.append(render_content_slide(heading, body))
        html = build_slide_html(module_num, title, "\n".join(all_slides))
        kind = "SLIDE"

    out_path = BASE_DIR / html_rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    print(f"  [OK] {kind} {html_rel}  ({len(html):,} chars)")
    return True

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Rebuild Dark Wolf slides (presentations) and lab guides from Markdown.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python build_slides.py                      # rebuild everything\n"
            "  python build_slides.py day1/06-lab-qgroundcontrol.md   # rebuild one\n"
            "  python build_slides.py --list               # show file map\n"
        ),
    )
    parser.add_argument("source", nargs="?", help="Single .md file to rebuild")
    parser.add_argument("--list", action="store_true", help="Print the file map and exit")
    args = parser.parse_args()

    if args.list:
        for src, dst in FILE_MAP.items():
            print(f"  {src}  →  {dst}")
        return

    if args.source:
        rel = args.source.replace("\\", "/")
        if rel not in FILE_MAP:
            print(f"[ERROR] Unknown source: {rel}")
            print("Run  python build_slides.py --list  to see valid paths.")
            sys.exit(1)
        ok = build_slide(rel)
        sys.exit(0 if ok else 1)

    total = len(FILE_MAP)
    ok_count = 0
    print(f"Rebuilding {total} files ...\n")
    for i, rel in enumerate(FILE_MAP, 1):
        print(f"[{i:02d}/{total}] {rel}")
        if build_slide(rel):
            ok_count += 1
    print(f"\nDone: {ok_count}/{total} rebuilt.")
    sys.exit(0 if ok_count == total else 1)


if __name__ == "__main__":
    main()
