# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py==0.2.6"]
# ///
"""Build the Track 3 analytics slides from the figures in slides/figures.

Every diagram and code example is an SVG drawn in slide units: the 16:9 slide
is 960 x 540 (96 per inch), and each SVG's viewBox is the region of the slide
it covers. Figures are rendered with resvg from the fonts in slides/fonts
alone (Carlito, metric-compatible with Calibri, and DejaVu Sans Mono), so the
pictures look the same on every machine.

A figure that builds up over clicks is split into layers: top-level
<g data-layer="name"> groups, bottom first. Each layer is rendered alone to a
full-size, transparent PNG, and the slide stacks one picture per layer at the
same position. The slide definitions in deck.py say which layers appear on
which click.

The deck is assembled with DeckCraft's command line tool (deckcraft-cli) on
top of template.pptx, which carries the AEHRC slide master and layouts.

Usage:

    uv run slides/build.py figures [NAME...]   # render figures and previews
    uv run slides/build.py deck                # figures, then the .pptx
    uv run slides/build.py preview             # the .pptx as PNGs

Author: John Grimes
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import resvg_py

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import deck

FIGURES_DIR = HERE / "figures"
ASSETS_DIR = HERE / "assets"
FONTS_DIR = HERE / "fonts"
BUILD_DIR = HERE / "build"
PNG_DIR = BUILD_DIR / "figures"
PREVIEW_DIR = BUILD_DIR / "preview"
TEMPLATE = HERE / "template.pptx"
OUTPUT = HERE / "track-3-analytics.pptx"
DECKCRAFT = os.environ.get("DECKCRAFT_CLI", "deckcraft-cli")

FAMILIES = ("Carlito", "DejaVu Sans Mono")
ZOOM = 4
# Slide units (960 x 540) to points on the 720 x 405 pt slide.
PT_PER_UNIT = 0.75
FONT_FAMILY = re.compile(
    r"""font-family\s*(?:=\s*"([^"]*)"|=\s*'([^']*)'|:\s*([^;}"]*))"""
)
SVG_NS = "{http://www.w3.org/2000/svg}"
NOT_DRAWN = {"style", "defs", "title", "desc", "metadata"}

# Section header geometry, from the AEHRC deck the template was taken from.
SECTION_BODY_BOX = {"x": 19.8, "y": 85.42, "w": 555.65, "h": 215.46}
SECTION_NAME_RECT = [19.8, 319.09, 555.65, 32.77]
SECTION_GRAPHIC_RECT = [512.19, -7.08, 256.87, 256.87]
SECTION_NAME_COLOUR = {"scheme": "accent1", "lumMod": 20000, "lumOff": 80000}


class FigureError(ValueError):
    """A figure cannot be rendered faithfully."""


def check_fonts(svg: str) -> None:
    """Check that every font family an SVG asks for first is bundled.

    :param svg: SVG markup
    :raises FigureError: if a font family is not one of the bundled families
    """
    for match in FONT_FAMILY.finditer(svg):
        value = next(group for group in match.groups() if group is not None)
        first = value.split(",")[0].strip().strip("'\"")
        if first not in FAMILIES:
            raise FigureError(
                f"font family {first!r} is not one of {', '.join(FAMILIES)}"
            )


def parse(svg: str) -> tuple[list[str], list[float], str]:
    """Read the layers, viewBox and title of a figure.

    :param svg: SVG markup
    :returns: the data-layer names in z-order (empty if not layered), the
        viewBox as [x, y, w, h] in slide units, and the <title> text
    :raises FigureError: if a layered SVG draws outside its layers, or the
        figure has no viewBox or title
    """
    root = ET.fromstring(svg.encode("utf-8"))
    names, outside = [], []
    for child in root:
        tag = child.tag.removeprefix(SVG_NS)
        if tag == "g" and child.get("data-layer"):
            names.append(child.get("data-layer"))
        elif tag not in NOT_DRAWN:
            outside.append(tag)
    if names and outside:
        raise FigureError(
            f"layered figure draws {', '.join(outside)} outside its layers"
        )
    view_box = root.get("viewBox")
    if not view_box:
        raise FigureError("figure has no viewBox")
    title = root.find(f"{SVG_NS}title")
    if title is None or not (title.text or "").strip():
        raise FigureError("figure has no <title> to use as alt text")
    return names, [float(v) for v in view_box.split()], " ".join(title.text.split())


def render_svg(svg: str, resources_dir: Path, style_sheet: str | None = None) -> bytes:
    """Render SVG markup to PNG bytes with the bundled fonts only.

    :param svg: SVG markup
    :param resources_dir: directory that relative image references resolve against
    :param style_sheet: extra CSS applied to the SVG
    :returns: PNG bytes
    """
    return bytes(
        resvg_py.svg_to_bytes(
            svg_string=svg,
            zoom=ZOOM,
            style_sheet=style_sheet,
            resources_dir=str(resources_dir),
            skip_system_fonts=True,
            font_dirs=[str(FONTS_DIR)],
            font_family=FAMILIES[0],
            monospace_family=FAMILIES[1],
        )
    )


def render_figure(svg_path: Path) -> dict:
    """Render a figure's layers to PNG, and a preview of the whole figure.

    :param svg_path: the SVG file
    :returns: {"layers": [(name, png path)], "rect": [x, y, w, h] in points,
        "title": alt text}
    :raises FigureError: if the figure is invalid
    """
    svg = svg_path.read_text(encoding="utf-8")
    check_fonts(svg)
    names, view_box, title = parse(svg)
    jobs = [
        (
            name,
            PNG_DIR / f"{svg_path.stem}-{name}.png",
            f'[data-layer] {{ display: none; }} [data-layer="{name}"] {{ display: inline; }}',
        )
        for name in names
    ] or [(svg_path.stem, PNG_DIR / f"{svg_path.stem}.png", None)]
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    layers = []
    for name, path, style in jobs:
        path.write_bytes(render_svg(svg, svg_path.parent, style))
        layers.append((name, path))
    # The preview is the whole figure on white, to check its layout.
    (PNG_DIR / "previews").mkdir(exist_ok=True)
    (PNG_DIR / "previews" / f"{svg_path.stem}.png").write_bytes(
        render_svg(svg, svg_path.parent, "svg { background-color: #ffffff; }")
    )
    rect = [round(v * PT_PER_UNIT, 2) for v in view_box]
    return {"layers": layers, "rect": rect, "title": title}


def render_figures(names: list[str] | None = None) -> dict[str, dict]:
    """Render every figure, or the named ones.

    :param names: figure stems to render; all when empty
    :returns: rendered figures by stem
    """
    paths = sorted(FIGURES_DIR.glob("*.svg"))
    if names:
        paths = [p for p in paths if p.stem in names]
        missing = set(names) - {p.stem for p in paths}
        if missing:
            raise FigureError(f"no such figure: {', '.join(sorted(missing))}")
    return {path.stem: render_figure(path) for path in paths}


def cmd(command: str, params: dict | None = None) -> list[str]:
    """Format one deckcraft-cli command argument.

    :param command: command id
    :param params: command parameters
    :returns: the --cmd argument pair
    """
    if params is None:
        return ["--cmd", command]
    return ["--cmd", f"{command}={json.dumps(params, ensure_ascii=False)}"]


def figure_commands(slide: dict, figures: dict[str, dict]) -> list[str]:
    """Commands that add a title-only slide with a layered figure.

    The layers named in the slide's builds appear on click, one step per
    entry; the rest are on the slide from the start.

    :param slide: a deck.slide() definition
    :param figures: rendered figures by stem
    :returns: deckcraft-cli arguments
    :raises FigureError: if the slide names a missing figure or layer
    """
    figure = figures.get(slide["figure"])
    if figure is None:
        raise FigureError(f"slide {slide['title']!r} needs figure {slide['figure']!r}")
    names = [name for name, _ in figure["layers"]]
    built = [layer for step in slide["builds"] for layer in step]
    unknown = set(built) - set(names)
    if unknown:
        raise FigureError(
            f"figure {slide['figure']!r} has no layer {', '.join(sorted(unknown))}"
        )
    args = cmd("slide.new", {"layout": "Title Only", "title": slide["title"]})
    for index, (name, path) in enumerate(figure["layers"]):
        picture_name = (
            f"{slide['figure']}-{name}" if len(names) > 1 else slide["figure"]
        )
        args += cmd("insert.picture", {"path": str(path), "rect": figure["rect"]})
        args += cmd("shape.rename", {"name": picture_name})
        if index == 0:
            args += cmd("shape.altText", {"text": figure["title"]})
        else:
            args += cmd("shape.altText", {"text": "", "decorative": True})
    args += cmd(
        "transition.set", {"kind": "fade", "option": "smoothly", "duration": 500}
    )
    return args


def build_deck(figures: dict[str, dict]) -> None:
    """Assemble the deck on the template and save it to OUTPUT.

    Section headers need a second pass: their name text box and graphic are
    added after the slides exist, and animations are added once every picture
    has its id. Both passes run on a working copy, so a failed build leaves
    any previous OUTPUT untouched.

    :param figures: rendered figures by stem
    :raises subprocess.CalledProcessError: if deckcraft-cli fails
    """
    BUILD_DIR.mkdir(exist_ok=True)
    work = BUILD_DIR / "work.pptx"
    shutil.copyfile(TEMPLATE, work)

    # Pass 1: slides, titles, pictures and notes.
    args = []
    for slide in deck.SLIDES:
        if slide["kind"] == "section":
            args += cmd(
                "slide.new", {"layout": "Section Header", "body": slide["title"]}
            )
        else:
            args += figure_commands(slide, figures)
        args += cmd("slide.notes", {"text": slide["notes"]})
    run(["run", "--in", str(work), *args, "--save", str(work)])

    # Pass 2: section header details and click builds, which need shape ids.
    args = []
    for index, slide in enumerate(deck.SLIDES):
        inspect = slide_shapes(work, index)
        args += cmd("slide.go", {"index": index})
        if slide["kind"] == "section":
            body = next(s for s in inspect if s.get("placeholder") == "body")
            args += cmd("shape.setBounds", {**SECTION_BODY_BOX, "ids": [body["id"]]})
            args += cmd(
                "insert.textBox", {"rect": SECTION_NAME_RECT, "text": slide["subtitle"]}
            )
            args += section_name_format()
            graphic = render_asset("sql-on-fhir-balloon.svg")
            args += cmd(
                "insert.picture", {"path": str(graphic), "rect": SECTION_GRAPHIC_RECT}
            )
            args += cmd("shape.rename", {"name": "SQL on FHIR balloon"})
            args += cmd("shape.altText", {"text": "", "decorative": True})
            continue
        ids = {s["name"]: s["id"] for s in inspect if s.get("kind") == "picture"}
        for step in slide["builds"]:
            for position, layer in enumerate(step):
                args += cmd(
                    "animation.add",
                    {
                        "effect": "fade",
                        "start": "onClick" if position == 0 else "withPrevious",
                        "duration": 400,
                        "ids": [ids[f"{slide['figure']}-{layer}"]],
                    },
                )
    run(["run", "--in", str(work), *args, "--save", str(OUTPUT)])
    print(OUTPUT.relative_to(HERE.parent))


def section_name_format() -> list[str]:
    """Commands that format the selected section header name text box.

    insert.textBox leaves the new box selected, so the format commands act on
    it.

    :returns: deckcraft-cli arguments
    """
    return (
        cmd("format.size", {"size": 28})
        + cmd("format.color", {"color": SECTION_NAME_COLOUR})
        + cmd("format.margins", {"left": 0, "top": 0, "right": 0, "bottom": 0})
    )


def render_asset(name: str) -> Path:
    """Render an SVG asset to PNG at the figure zoom.

    :param name: file name in slides/assets
    :returns: the PNG path
    """
    svg_path = ASSETS_DIR / name
    out = PNG_DIR / f"{svg_path.stem}.png"
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    out.write_bytes(render_svg(svg_path.read_text(encoding="utf-8"), ASSETS_DIR))
    return out


def slide_shapes(path: Path, index: int) -> list[dict]:
    """Inspect the shapes of one slide.

    :param path: the presentation
    :param index: slide index
    :returns: the slide's shapes as reported by slide.inspect
    """
    out = run(
        [
            "run",
            "--in",
            str(path),
            *cmd("slide.go", {"index": index}),
            *cmd("slide.inspect"),
            "--print",
        ],
        capture=True,
    )
    line = next(line for line in out.splitlines() if line.startswith("slide.inspect"))
    return json.loads(line.split("→", 1)[1])["shapes"]


def run(args: list[str], capture: bool = False) -> str:
    """Run deckcraft-cli.

    :param args: arguments after the executable
    :param capture: return standard output instead of passing it through
    :returns: standard output when captured, else an empty string
    :raises subprocess.CalledProcessError: if deckcraft-cli fails
    """
    result = subprocess.run(
        [DECKCRAFT, *args], check=True, text=True, capture_output=capture
    )
    return result.stdout if capture else ""


def preview() -> None:
    """Render every slide of OUTPUT to PNG in build/preview."""
    if PREVIEW_DIR.exists():
        shutil.rmtree(PREVIEW_DIR)
    run(["render", str(OUTPUT), "--all", "--scale", "2", str(PREVIEW_DIR)])


def main(argv: list[str] | None = None) -> None:
    """Command line entry point.

    :param argv: arguments; sys.argv when None
    """
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    figures = sub.add_parser("figures", help="render figures to build/figures")
    figures.add_argument("names", nargs="*", help="figure stems (default: all)")
    sub.add_parser("deck", help="render figures and build the .pptx")
    sub.add_parser("preview", help="render the .pptx slides to build/preview")
    args = parser.parse_args(argv)
    if args.command == "figures":
        for stem, figure in render_figures(args.names).items():
            print(stem, ", ".join(name for name, _ in figure["layers"]))
    elif args.command == "deck":
        build_deck(render_figures())
    else:
        preview()


if __name__ == "__main__":
    main()
