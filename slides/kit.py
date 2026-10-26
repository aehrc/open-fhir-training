"""Drawing primitives and slide constructors shared by the Track 3 decks.

Diagrams are SVG strings drawn in pixels at 100 px per slide inch, so 940 px is
the full width of the content area (676.8 pt) and 345 px its full height (below
that is the footer logo; build.py rejects taller diagrams). They are placed on
the slide at that scale and never stretched, so a 15 px label is the same size
on every slide (10.8 pt). Keep labels at 14 px or larger so they read from the
back of a room. Beside bullets, a diagram gets the rest of the width (about
500 px at the default split).

Styling follows the Pathling booth deck: Open Sans, pastel fills, dark teal
outlines and grey connectors, with JetBrains Mono for code.

A deck module (decks/*.py) defines ``DECK``, a dict with ``file`` (output name
without extension) and ``slides`` (a list built with the slide constructors
below). The first slide must be ``title_slide`` and the last ``closing``. The
closing heading must fit on one line of about 20 characters.

Author: John Grimes
"""

import base64
import functools
import pathlib
import struct
from html import escape

import segno
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = pathlib.Path(__file__).parent
SCREENSHOTS = HERE / "screenshots"
FONT_FILES = {"Open Sans": "OpenSans.ttf", "JetBrains Mono": "JetBrainsMono.ttf"}

# Palette, from the booth deck.
INK = "#012B36"
GREY = "#686868"
RULE = "#9A9A9A"
TEXT = "#111111"
MUTED = "#555555"
YELLOW = "#FFF6D8"
PINK = "#FFDEEE"
BLUE = "#C9E9FF"
PEACH = "#F2CDBD"
PURPLE = "#DCC6FF"
LBLUE = "#BFD5FF"
ROSE = "#FF98B1"
CYAN = "#BDF6FF"
MINT = "#BDFFEB"
LAVENDER = "#D7D3FF"
AMBER = "#FFDC9D"
ORANGE = "#FFB773"
TEAL = "#00A9CE"  # CSIRO teal, for emphasis and callouts.
NAVY = "#001D34"
RED = "#D0312D"
SANS = "Open Sans"
MONO = "JetBrains Mono"

HEIGHT = 345  # Full content height, px; anything lower overlaps the footer logo.


# --- Drawing primitives --------------------------------------------------------


def data_uri(path):
    """Return a file as a data URI, for embedding images in a diagram."""
    p = pathlib.Path(path)
    mime = {
        "png": "image/png",
        "svg": "image/svg+xml",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
    }[p.suffix[1:].lower()]
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def png_size(path):
    """Return the (width, height) of a PNG file, read from its header."""
    with open(path, "rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24])


def svg(w, h, body):
    """Wrap diagram elements in an SVG document of w x h px."""
    defs = (
        "<defs>"
        f'<marker id="ag" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{GREY}"/></marker>'
        f'<marker id="at" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{TEAL}"/></marker>'
        "</defs>"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">{defs}{"".join(body)}</svg>'
    )


def text(
    x, y, s, fs=15, anchor="middle", weight=400, fill=TEXT, family=SANS, italic=False
):
    """One line of text with its baseline at y.

    Monospaced text gets an explicit x for every character: resvg ignores
    font-feature-settings, and JetBrains Mono's ligatures would otherwise turn
    code such as != and :// into single glyphs.
    """
    style = ' font-style="italic"' if italic else ""
    if family == MONO and s:
        advance = 0.6 * fs  # JetBrains Mono advance width is 600 units per em.
        start = x - {"start": 0, "middle": 0.5, "end": 1}[anchor] * advance * len(s)
        xs = " ".join(f"{start + i * advance:.2f}" for i in range(len(s)))
        x, anchor = xs, "start"
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{fs}" font-weight="{weight}" '
        f'fill="{fill}" text-anchor="{anchor}" xml:space="preserve"{style}>{escape(s)}</text>'
    )


def lines(
    cx, cy, rows, fs=15, weight=400, fill=TEXT, family=SANS, anchor="middle", lh=1.3
):
    """A block of text lines vertically centred on (cx, cy)."""
    top = cy - (len(rows) - 1) * fs * lh / 2 + fs * 0.35
    return "".join(
        text(cx, top + i * fs * lh, r, fs, anchor, weight, fill, family)
        for i, r in enumerate(rows)
    )


def rect(x, y, w, h, fill="#fff", stroke=INK, sw=1.6, rx=6, dash=None):
    """A rounded rectangle."""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{sw}"{d}/>'
    )


def box(x, y, w, h, fill, rows, fs=15, weight=400, tfill=TEXT, **kw):
    """A rounded rectangle with centred lines of text."""
    return rect(x, y, w, h, fill, **kw) + lines(
        x + w / 2, y + h / 2, rows, fs, weight, tfill
    )


def line(x1, y1, x2, y2, stroke=GREY, sw=1.6, dash=None, arrow="ag"):
    """A straight line, with an arrowhead at the end unless arrow is None."""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{arrow})"' if arrow else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
        f'stroke-width="{sw}"{d}{m}/>'
    )


def path(d, stroke=GREY, sw=1.6, dash=None, arrow="ag", fill="none"):
    """An SVG path, with an arrowhead at the end unless arrow is None."""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{arrow})"' if arrow else ""
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}{m}/>'


def vcurve(x1, y1, x2, y2, lead=4, tail=12, **kw):
    """A vertical S-shaped arrow that ends in a straight segment."""
    a, b = y1 + lead, y2 - tail
    ym = (a + b) / 2
    return path(f"M{x1},{y1} V{a} C{x1},{ym} {x2},{ym} {x2},{b} V{y2}", **kw)


def hcurve(x1, y1, x2, y2, lead=4, tail=12, **kw):
    """A horizontal S-shaped arrow that ends in a straight segment."""
    d = 1 if x2 >= x1 else -1
    a, b = x1 + d * lead, x2 - d * tail
    xm = (a + b) / 2
    return path(f"M{x1},{y1} H{a} C{xm},{y1} {xm},{y2} {b},{y2} H{x2}", **kw)


def image(href, x, y, w, h):
    """An image scaled to fit the box, keeping its aspect ratio."""
    return (
        f'<image href="{href}" x="{x}" y="{y}" width="{w}" height="{h}" '
        f'preserveAspectRatio="xMidYMid meet"/>'
    )


def circle(cx, cy, r, fill, stroke=INK, sw=1.6):
    """A circle."""
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{sw}"/>'
    )


def table(x, y, cols, rows, header_fill, fs=14, rh=30, family=SANS, mono_cols=()):
    """A small table: cols is a list of (title, width) and rows a list of tuples."""
    w = sum(c[1] for c in cols)
    h = rh * (len(rows) + 1)
    out = [
        rect(x, y, w, h, "#fff"),
        f'<path d="M{x + 6},{y} H{x + w - 6} Q{x + w},{y} {x + w},{y + 6} V{y + rh} H{x} '
        f'V{y + 6} Q{x},{y} {x + 6},{y} z" fill="{header_fill}" stroke="{INK}" stroke-width="1.6"/>',
    ]
    cx = x
    for i, (title, cw) in enumerate(cols):
        out.append(text(cx + 10, y + rh / 2 + fs * 0.36, title, fs, "start", 700))
        for j, r in enumerate(rows):
            fam = MONO if i in mono_cols else family
            out.append(
                text(
                    cx + 10,
                    y + rh * (j + 1.5) + fs * 0.36,
                    r[i],
                    fs,
                    "start",
                    400,
                    TEXT,
                    fam,
                )
            )
        cx += cw
    for j in range(1, len(rows)):
        out.append(
            line(x, y + rh * (j + 1), x + w, y + rh * (j + 1), "#D0D0D0", 1, arrow=None)
        )
    return "".join(out)


@functools.cache
def _advances(family, weight):
    """Glyph advance widths (in em) by character, for a font at a given weight."""
    font = TTFont(HERE / "fonts" / FONT_FILES[family])
    axes = {a.axisTag: a.defaultValue for a in font["fvar"].axes}
    axes["wght"] = weight
    static = instantiateVariableFont(font, axes)
    upem = static["head"].unitsPerEm
    hmtx = static["hmtx"].metrics
    return {chr(cp): hmtx[name][0] / upem for cp, name in static.getBestCmap().items()}


def text_width(s, fs=15, weight=400, family=SANS):
    """The rendered width of one line of text in px, from the bundled font's metrics."""
    adv = _advances(family, weight)
    return sum(adv.get(c, 0.6) for c in s) * fs


def pill(x, y, s, fill=MINT, fs=13, weight=700):
    """A small rounded label sized to its text; returns the SVG.

    pill_width gives its width, for laying out a row of pills.
    """
    w = pill_width(s, fs, weight)
    return rect(x, y, w, fs + 10, fill, sw=1.2, rx=(fs + 10) / 2) + text(
        x + w / 2, y + fs + 3, s, fs, "middle", weight
    )


def pill_width(s, fs=13, weight=700):
    """The width of a pill: the text plus equal padding on each side."""
    return text_width(s, fs, weight) + 1.3 * fs


def code(
    x, y, w, rows, title=None, fs=14, lh=1.45, fill="#F7F7F7", title_fill=LAVENDER
):
    """A code listing in a card, with an optional header strip; rows are strings."""
    head = 30 if title else 0
    h = head + 16 + len(rows) * fs * lh
    out = [rect(x, y, w, h, fill)]
    if title:
        out.append(
            f'<path d="M{x + 6},{y} H{x + w - 6} Q{x + w},{y} {x + w},{y + 6} V{y + head} '
            f'H{x} V{y + 6} Q{x},{y} {x + 6},{y} z" fill="{title_fill}" stroke="{INK}" '
            f'stroke-width="1.6"/>'
        )
        out.append(text(x + 12, y + 20, title, 14, "start", 700))
    for i, r in enumerate(rows):
        out.append(
            text(
                x + 14,
                y + head + 8 + fs + i * fs * lh,
                r,
                fs,
                "start",
                400,
                "#222",
                MONO,
            )
        )
    return "".join(out)


def qr(url, x, y, size=110, label=None, fs=12):
    """A QR code for url with an optional caption below it."""
    q = segno.make(url, error="m")
    n = q.symbol_size(border=2)[0]
    cell = size / n
    cells = []
    for r, row in enumerate(q.matrix_iter(border=2)):
        for c, on in enumerate(row):
            if on:
                cells.append(
                    f"M{x + c * cell:.2f},{y + r * cell:.2f}h{cell:.2f}v{cell:.2f}h-{cell:.2f}z"
                )
    out = [
        f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="#fff"/>',
        f'<path d="{"".join(cells)}" fill="#000" shape-rendering="crispEdges"/>',
    ]
    if label:
        out.append(text(x + size / 2, y + size + fs + 4, label, fs, fill=MUTED))
    return "".join(out)


def callout(n, x, y, r=14):
    """A numbered teal marker, for pointing at parts of a screenshot."""
    return (
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{TEAL}" stroke="#fff" stroke-width="2.5"/>'
        + text(x, y + r * 0.38, str(n), r * 1.15, "middle", 700, "#fff")
    )


def highlight(x, y, w, h):
    """A teal outline drawn around a region of a screenshot."""
    return rect(x, y, w, h, "none", TEAL, 3, 6)


def screenshot(name, x, y, w, h=None, crop=None):
    """A screenshot from screenshots/, fitted to width w (and height h if given).

    crop is an optional (cx, cy, cw, ch) region of the screenshot, in its own
    pixels, to show instead of the whole image. Returns (svg, drawn_w, drawn_h,
    point) where point(px, py) maps a screenshot pixel to diagram coordinates,
    for placing callouts and highlights.
    """
    path_ = SCREENSHOTS / f"{name}.png"
    iw, ih = png_size(path_)
    cx, cy, cw, ch = crop or (0, 0, iw, ih)
    scale = w / cw
    if h is not None and ch * scale > h:
        scale = h / ch
    dw, dh = cw * scale, ch * scale
    body = (
        f'<rect x="{x - 1}" y="{y - 1}" width="{dw + 2}" height="{dh + 2}" fill="#fff" '
        f'stroke="#C8C8C8" stroke-width="1.5"/>'
        f'<svg x="{x}" y="{y}" width="{dw}" height="{dh}" viewBox="{cx} {cy} {cw} {ch}">'
        f'<image href="{data_uri(path_)}" x="0" y="0" width="{iw}" height="{ih}"/></svg>'
    )

    def point(px, py):
        return x + (px - cx) * scale, y + (py - cy) * scale

    return body, dw, dh, point


# --- Slide constructors --------------------------------------------------------
# Each returns a plain dict that build.py turns into DeckCraft commands.


def title_slide(title, subtitle, notes):
    """The opening slide: the template's leaf photo with a title and subtitle."""
    return {"kind": "title", "title": title, "subtitle": subtitle, "notes": notes}


def section(heading, notes):
    """A dark section divider."""
    return {"kind": "section", "heading": heading, "notes": notes}


def diagram(title, subtitle, name, drawing, notes):
    """A titled slide with one diagram (an SVG string) below the subtitle."""
    return {
        "kind": "diagram",
        "title": title,
        "subtitle": subtitle,
        "name": name,
        "svg": drawing,
        "notes": notes,
    }


def bullets(title, subtitle, items, notes, name=None, drawing=None, split=0.45):
    """A titled slide with bullet points, optionally beside a diagram.

    items are strings, or (string, level) tuples for sub-points. With a
    drawing, the bullets take the left `split` fraction of the width.
    """
    return {
        "kind": "bullets",
        "title": title,
        "subtitle": subtitle,
        "items": items,
        "name": name,
        "svg": drawing,
        "split": split,
        "notes": notes,
    }


def closing(heading, presenter, notes, links=()):
    """The closing slide; links are (url, label) pairs shown as QR codes."""
    return {
        "kind": "closing",
        "heading": heading,
        "presenter": presenter,
        "links": list(links),
        "notes": notes,
    }
