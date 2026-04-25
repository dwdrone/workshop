#!/usr/bin/env python3
"""
build_slides.py — Convert .md course files to Dark Wolf Reveal.js HTML slides.
No API required. Run whenever you finish editing your markdown.

Requirements:
    pip install markdown

Usage:
    python build_slides.py                         # rebuild all 23 slides
    python build_slides.py day1/01-uas.md          # rebuild one slide
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
}

# ---------------------------------------------------------------------------
# Dark Wolf CSS (identical to the existing slides)
# ---------------------------------------------------------------------------

DW_CSS = """\
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    :root {
        --dw-bg: #080808; --dw-panel: #111111; --dw-border: #1a1a1a;
        --dw-green: #68E01A; --dw-green-glow: rgba(104,224,26,0.1); --dw-green-border: rgba(104,224,26,0.3);
        --dw-white: #f0f0f0; --dw-gray: #7a8290;
        --r-background-color: #080808; --r-main-color: #f0f0f0; --r-heading-color: #ffffff;
        --r-link-color: #68E01A; --r-main-font: 'Inter', system-ui, sans-serif;
        --r-heading-font: 'Inter', system-ui, sans-serif; --r-code-font: 'JetBrains Mono','Courier New',monospace;
        --r-main-font-size: 26px;
    }
    .reveal-viewport { background: var(--dw-bg); }
    .reveal .slides { text-align: left; }
    .reveal h1, .reveal h2, .reveal h3 { text-transform: none; font-weight: 700; }
    .reveal h1 { color: var(--dw-green); font-size: 1.9em; letter-spacing: -1px; }
    .reveal h2 { color: var(--dw-white); border-bottom: 2px solid var(--dw-green); padding-bottom: 10px; margin-bottom: 22px; font-size: 1.15em; }
    .reveal h3 { color: var(--dw-green); font-size: 0.9em; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 12px; }
    .reveal a { color: var(--dw-green); }
    .reveal p, .reveal li { line-height: 1.55; }
    .reveal ul li { margin-bottom: 8px; }
    .reveal ul li::marker { color: var(--dw-green); }
    .reveal .progress span { background: var(--dw-green); }
    .reveal .controls { color: var(--dw-green); }
    .reveal .slide-number { color: var(--dw-green); background: rgba(0,0,0,0.7); font-family: var(--r-code-font); font-size: 0.52em; padding: 4px 10px; border-radius: 4px; }
    .reveal .slides > section { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='97' viewBox='0 0 56 97'%3E%3Cpath fill='none' stroke='%23161616' stroke-width='1' d='M28 0l28 16.3v32.7L28 65.3 0 49V16.3zM28 32l28 16.3v32.7L28 97 0 80.7V48z'/%3E%3C/svg%3E"); background-size: 56px 97px; }
    .tag { display: inline-block; padding: 3px 12px; border-radius: 20px; font-size: 0.6em; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-right: 6px; }
    .tag-presentation { border: 1px solid var(--dw-green); color: var(--dw-green); background: var(--dw-green-glow); }
    .tag-lab { border: 1px solid #60a5fa; color: #93c5fd; background: rgba(96,165,250,0.1); }
    .tag-activity { border: 1px solid #a78bfa; color: #c4b5fd; background: rgba(167,139,250,0.1); }
    .objective-box { background: var(--dw-green-glow); border-left: 3px solid var(--dw-green); padding: 12px 18px; border-radius: 0 6px 6px 0; margin: 8px 0; }
    .warning-box { background: rgba(239,68,68,0.08); border-left: 3px solid #ef4444; padding: 12px 18px; border-radius: 0 6px 6px 0; margin: 8px 0; }
    .phase-box { background: var(--dw-green-glow); border-left: 3px solid var(--dw-green); padding: 10px 16px; border-radius: 0 6px 6px 0; margin: 8px 0; font-weight: 600; color: var(--dw-green); }
    .terminal { background: #050505; border: 1px solid var(--dw-border); border-top: 2px solid var(--dw-green); border-radius: 0 0 8px 8px; padding: 16px; font-family: var(--r-code-font); font-size: 0.94em; line-height: 1.7; color: var(--dw-green); white-space: pre; overflow-x: auto; }
    .terminal::before { content: '\\25CF \\25CF \\25CF'; display: block; color: #252525; margin-bottom: 10px; letter-spacing: 5px; font-size: 0.9em; }
    .reveal pre { margin: 0; box-shadow: none; }
    .reveal pre code { background: #050505 !important; color: var(--dw-green) !important; border: 1px solid var(--dw-border); border-radius: 6px; padding: 14px; font-size: 0.94em; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; align-items: start; }
    .reveal table { border-collapse: collapse; width: 100%; font-size: 0.72em; }
    .reveal table th { background: var(--dw-green-glow); color: var(--dw-green); border: 1px solid var(--dw-green-border); padding: 8px 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.82em; }
    .reveal table td { border: 1px solid var(--dw-border); padding: 8px 12px; color: var(--dw-white); vertical-align: top; }
    .reveal table tr:nth-child(even) td { background: rgba(255,255,255,0.02); }
    .highlight-green { color: var(--dw-green); font-weight: 600; }
    .highlight-red { color: #f87171; font-weight: 600; }
    .highlight-yellow { color: #fbbf24; font-weight: 600; }
    .highlight-blue { color: #60a5fa; font-weight: 600; }
    .reveal strong, .reveal b { color: var(--dw-green); }
    .reveal :not(pre) > code { color: var(--dw-green); }"""

# ---------------------------------------------------------------------------
# Markdown parser
# ---------------------------------------------------------------------------

def _preprocess_md(text: str) -> str:
    """
    Insert blank lines before list items when the preceding non-empty line is
    not already blank. Without this the markdown library treats lists that
    immediately follow bold headers (e.g. **Examples:**\n- item) as plain
    paragraph text instead of converting them to <ul>/<ol>.
    Also strip standalone '---' separator lines that would produce <hr> tags.
    """
    lines = text.splitlines()
    out: list[str] = []
    in_fence = False
    for line in lines:
        # Track fenced code blocks — don't touch content inside them
        if line.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        # Drop bare '---' separator lines (they become stray <hr> tags)
        if line.strip() == "---":
            continue

        is_list_item = bool(re.match(r"^[-*+]\s", line) or re.match(r"^\d+\.\s", line))
        prev_is_blank = not out or not out[-1].strip()

        if is_list_item and not prev_is_blank:
            out.append("")  # ensure blank line before list
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
    # blockquote → warning-box
    html = re.sub(
        r"<blockquote>\s*<p>(.*?)</p>\s*</blockquote>",
        r'<div class="warning-box">\1</div>',
        html,
        flags=re.DOTALL,
    )
    # fenced_code adds <code class="language-X"> — keep that, just remove extra div wrapping
    return html


def _extract_objectives(body: str) -> list[str]:
    """Pull the top-level bullet points from an Objectives section."""
    items = []
    for line in body.splitlines():
        m = re.match(r"^[-*]\s+(.*)", line)
        if m:
            items.append(m.group(1).strip())
    return items

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

    # Extract H1 title
    for line in lines:
        if line.startswith("# ") and not line.startswith("## "):
            meta["Title"] = line[2:].strip()
            break

    # Extract **Key:** Value metadata lines
    for line in lines:
        m = re.match(r"\*\*(\w[\w\s]*):\*\*\s*(.*)", line)
        if m:
            meta[m.group(1).strip()] = m.group(2).strip()

    # Split into sections on ## headings
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

    # Strip any trailing '---' separators left in section bodies
    cleaned = []
    for heading, body in sections:
        body = re.sub(r"\n---\s*$", "", body.rstrip())
        cleaned.append((heading, body.strip()))

    return meta, cleaned

# ---------------------------------------------------------------------------
# Slide renderers
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
        # Fall back to regular markdown conversion
        return render_content_slide("Objectives", body)
    boxes = "\n    ".join(
        f'<div class="objective-box">{_md_convert(item)}</div>' for item in items
    )
    # _md_convert wraps in <p>; strip it for single-line items
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
    Split a section body into multiple slides if it would be too long.
    Splitting strategy: break on ### sub-headings if there are more than 2,
    or on blank lines if the bullet count exceeds 10.
    """
    # Count top-level bullets
    bullet_count = len(re.findall(r"^[-*]\s", body, re.MULTILINE))

    # Count ### sub-sections
    sub_headings = list(re.finditer(r"^### ", body, re.MULTILINE))

    if bullet_count <= 10 and len(sub_headings) <= 3:
        return [body]  # Fits on one slide

    # Split on ### headings if there are many
    if len(sub_headings) >= 3:
        parts = re.split(r"(?=^### )", body, flags=re.MULTILINE)
        # Pair up consecutive parts so we don't have too many tiny slides
        chunks = []
        i = 0
        while i < len(parts):
            if i + 1 < len(parts):
                combined = parts[i] + "\n" + parts[i + 1]
                # Count bullets in combined chunk
                if len(re.findall(r"^[-*]\s", combined, re.MULTILINE)) <= 12:
                    chunks.append(combined.strip())
                    i += 2
                    continue
            chunks.append(parts[i].strip())
            i += 1
        return [c for c in chunks if c]

    # Otherwise split on blank lines at roughly the midpoint
    lines = body.splitlines()
    mid = len(lines) // 2
    # Find nearest blank line to midpoint
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

# ---------------------------------------------------------------------------
# Full document builder
# ---------------------------------------------------------------------------

def build_html(module_num: str, title: str, slides_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Module {module_num} \u2013 {title}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/reset.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/reveal.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/theme/black.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/plugin/highlight/monokai.css">
    <style>
{DW_CSS}
    </style>
</head>
<body>
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
    transition: 'fade',
    transitionSpeed: 'fast',
    backgroundTransition: 'none',
    mouseWheel: true,
    plugins: [RevealHighlight, RevealNotes]
}});
</script>
</body>
</html>"""


def build_slide(md_path_rel: str) -> bool:
    """Convert one markdown file to its HTML slide output. Returns True on success."""
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

    # Module number from filename (e.g. "01" from "01-uas-cybersecurity.md")
    m = re.match(r"(\d+)", Path(md_path_rel).name)
    module_num = m.group(1) if m else "??"
    title = meta.get("Title", Path(md_path_rel).stem)

    # Build slides
    all_slides = [render_title_slide(module_num, meta)]

    for heading, body in sections:
        if not body.strip():
            continue
        if heading.lower() == "objectives":
            all_slides.append(render_objectives_slide(body))
        else:
            all_slides.append(render_content_slide(heading, body))

    html = build_html(module_num, title, "\n".join(all_slides))

    out_path = BASE_DIR / html_rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    print(f"  [OK] {html_rel}  ({len(html):,} chars)")
    return True


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Rebuild Dark Wolf Reveal.js slides from Markdown sources.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python build_slides.py                      # rebuild all 23 slides\n"
            "  python build_slides.py day1/01-uas.md       # rebuild one\n"
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

    # Rebuild all
    total = len(FILE_MAP)
    ok_count = 0
    print(f"Rebuilding {total} slides ...\n")
    for i, rel in enumerate(FILE_MAP, 1):
        print(f"[{i:02d}/{total}] {rel}")
        if build_slide(rel):
            ok_count += 1
    print(f"\nDone: {ok_count}/{total} rebuilt.")
    sys.exit(0 if ok_count == total else 1)


if __name__ == "__main__":
    main()
