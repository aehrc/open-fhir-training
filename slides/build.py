# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py==0.5.0", "segno==1.6.6"]
# ///
"""Build the Track 3 decks with DeckCraft.

Usage: uv run build.py [deck ...]  (default: every module in decks/)

Each deck module in decks/ defines DECK (see kit.py). For every deck, this
script renders the deck's diagrams from SVG to PNG with resvg, using only the
fonts in fonts/, then drives `deckcraft-cli run` over template.pptx to add the
slides, and saves out/<file>.pptx. It also renders every slide of the result to
build/preview/<file>/ for review.

template.pptx holds the AEHRC title and closing slides, and the AEHRC slide
masters, taken from the Pathling pitch deck (pathling-no-recording.pptx) with
the Pathling logos removed.

Requires uv and deckcraft-cli (https://deckcraft.run) on the PATH.

Author: John Grimes
"""

import importlib
import json
import pathlib
import shutil
import subprocess
import sys

import resvg_py

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

import kit  # noqa: E402

TEMPLATE = HERE / "template.pptx"
FONTS = [str(p) for p in sorted((HERE / "fonts").glob("*.ttf"))]
BUILD = HERE / "build"
OUT = HERE / "out"
ZOOM = 3  # PNG pixels per diagram pixel: a full-width diagram is 2,820 px wide.
PT_PER_PX = 0.72  # Diagrams are drawn at 100 px per inch; slides are 72 pt per inch.

# Slide geometry, in points on the 720 x 405 slide.
LEFT = 21.6
CONTENT_TOP = 108.0
CONTENT_W = 676.8
SUBTITLE = [20.16, 70.56, 680.4, 28.8]
TITLE_SLIDE_TITLE = [19.8, 222.0, 680.0, 110.0]


def render(svg_text, stem):
    """Write the SVG and its PNG rendering to the build directory; return the PNG path."""
    stem.parent.mkdir(parents=True, exist_ok=True)
    svg_path = stem.with_suffix(".svg")
    png_path = stem.with_suffix(".png")
    svg_path.write_text(svg_text)
    png = resvg_py.svg_to_bytes(
        svg_string=svg_text,
        zoom=ZOOM,
        skip_system_fonts=True,
        font_files=FONTS,
        font_family=kit.SANS,
        sans_serif_family=kit.SANS,
        monospace_family=kit.MONO,
    )
    png_path.write_bytes(bytes(png))
    return png_path


def place(png, left=LEFT, width=CONTENT_W, top=CONTENT_TOP):
    """Return the slide rect for a diagram PNG, at its drawn scale, centred in the given band.

    Raises ValueError for a diagram taller than kit.HEIGHT, which would cover the footer.
    """
    pw, ph = kit.png_size(png)
    if ph / ZOOM > kit.HEIGHT + 0.5:
        raise ValueError(
            f"{png.name}: {ph / ZOOM:.0f} px tall; the limit is {kit.HEIGHT} px"
        )
    w, h = pw / ZOOM * PT_PER_PX, ph / ZOOM * PT_PER_PX
    if w > width:  # Only ever shrink a diagram drawn wider than the band.
        h, w = h * width / w, width
    return [round(left + (width - w) / 2, 2), top, round(w, 2), round(h, 2)]


def cmd(name, params=None):
    """Format one DeckCraft command for `deckcraft-cli run --cmd`."""
    return (
        name if params is None else f"{name}={json.dumps(params, ensure_ascii=False)}"
    )


def textbox(rect, s, size, color=None, bold=False):
    """Commands that add a text box with no margins, formatted as a whole."""
    out = [
        cmd("insert.textBox", {"rect": rect, "text": s}),
        cmd("format.margins", {"left": 0, "top": 0, "right": 0, "bottom": 0}),
        cmd("format.size", {"size": size}),
    ]
    if color:
        out.append(cmd("format.color", {"color": color}))
    if bold:
        out.append(cmd("format.bold", {"on": True}))
    return out


def picture(png, rect, alt):
    """Commands that insert a picture and give it alt text."""
    return [
        cmd("insert.picture", {"path": str(png), "rect": rect}),
        cmd("shape.altText", {"text": alt}),
    ]


def bullet_items(items):
    """Split bullet items into paragraph texts and their list levels."""
    texts, levels = [], []
    for item in items:
        s, level = (item, 0) if isinstance(item, str) else item
        texts.append(s)
        levels.append(level)
    return texts, levels


def slide_commands(deck_dir, index, slide):
    """Return the commands for one slide."""
    kind = slide["kind"]
    out = []
    stem = deck_dir / f"{index:02d}-{slide.get('name') or kind}"
    if kind == "title":
        out += [
            cmd("slide.go", {"index": 0}),
            cmd("text.set", {"id": 3, "text": slide["subtitle"]}),
        ]
        out += textbox(TITLE_SLIDE_TITLE, slide["title"], 32, "#3F3F3F")
        out.append(cmd("format.anchor", {"anchor": "bottom"}))
    elif kind == "section":
        out.append(
            cmd("slide.new", {"layout": "Section Header", "body": slide["heading"]})
        )
    elif kind in ("diagram", "bullets"):
        out.append(cmd("slide.new", {"layout": "Title Only", "title": slide["title"]}))
        if slide["subtitle"]:
            out += textbox(SUBTITLE, slide["subtitle"], 16)
        if kind == "diagram":
            png = render(slide["svg"], stem)
            out += picture(png, place(png), f"Diagram: {slide['title']}")
        else:
            split = slide["split"] if slide["svg"] else 1.0
            width = CONTENT_W * split
            texts, levels = bullet_items(slide["items"])
            out += textbox([LEFT, CONTENT_TOP + 4, width, 255], "\n".join(texts), 18)
            out += [
                cmd("format.bullets", {"on": True}),
                cmd("format.paragraph", {"spaceAfter": 8}),
            ]
            for p, level in enumerate(levels):
                if level:
                    out += [cmd("text.edit", {"at": [p, 0]})]
                    out += [cmd("format.indent")] * level
                    out += [cmd("format.size", {"size": 16}), cmd("text.exit")]
            if slide["svg"]:
                png = render(slide["svg"], stem)
                gap = 14.4
                out += picture(
                    png,
                    place(png, LEFT + width + gap, CONTENT_W - width - gap),
                    f"Diagram: {slide['title']}",
                )
    elif kind == "closing":
        out += [
            cmd("slide.go", {"index": index}),
            cmd("text.set", {"id": 5, "text": slide["heading"]}),
            cmd("text.set", {"id": 4, "text": slide["presenter"]}),
        ]
        links = slide["links"]
        if links:
            size, gap = 100, 30
            w = len(links) * size + (len(links) - 1) * gap
            body = [
                kit.qr(url, i * (size + gap), 0, size, label)
                for i, (url, label) in enumerate(links)
            ]
            png = render(kit.svg(w, size + 22, body), stem)
            _, _, pw, ph = place(png)
            out += picture(png, [700 - pw, 222.0, pw, ph], "QR codes for links")
    else:
        raise ValueError(f"unknown slide kind {kind!r}")
    out.append(cmd("slide.notes", {"text": slide["notes"]}))
    return out


def build(module_name):
    """Build one deck module to out/<file>.pptx and render its preview."""
    deck = importlib.import_module(f"decks.{module_name}").DECK
    slides = deck["slides"]
    if slides[0]["kind"] != "title" or slides[-1]["kind"] != "closing":
        raise ValueError(
            f"{module_name}: decks start with title_slide and end with closing"
        )
    deck_dir = BUILD / deck["file"]
    shutil.rmtree(deck_dir, ignore_errors=True)
    commands = []
    for i, slide in enumerate(slides):
        commands += slide_commands(deck_dir, i, slide)
    OUT.mkdir(exist_ok=True)
    out = OUT / f"{deck['file']}.pptx"
    args = ["deckcraft-cli", "run", "--in", str(TEMPLATE)]
    for c in commands:
        args += ["--cmd", c]
    args += ["--save", str(out)]
    subprocess.run(args, check=True)
    preview = BUILD / "preview" / deck["file"]
    shutil.rmtree(preview, ignore_errors=True)
    preview.mkdir(parents=True)
    subprocess.run(
        ["deckcraft-cli", "render", str(out), "--all", f"{preview}/"],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    print(f"{out.relative_to(HERE)}: {len(slides)} slides")


def main():
    names = sys.argv[1:] or sorted(
        p.stem for p in (HERE / "decks").glob("*.py") if not p.stem.startswith("_")
    )
    for name in names:
        build(name)


if __name__ == "__main__":
    main()
