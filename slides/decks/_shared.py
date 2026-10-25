"""Diagrams and constants shared by more than one Track 3 deck.

Author: John Grimes
"""

from kit import (
    BLUE,
    CYAN,
    INK,
    LAVENDER,
    MINT,
    MUTED,
    PEACH,
    PINK,
    TEAL,
    YELLOW,
    box,
    line,
    qr,
    rect,
    svg,
    text,
)

PRESENTER = "John Grimes\nHealth Data Engineer, Australian e-Health Research Centre"
TRACK = "Track 3: FHIR for Data - Analytics and Text"
EVENT = "FHIR in Queensland Health Connectathon · 29-30 October 2026"
FORM_URL = "https://forms.cloud.microsoft/r/inJ0BxKvw7"
WORKSPACE_URL = "https://dbc-2accf367-79ff.cloud.databricks.com"
REPO_URL = "https://github.com/aehrc/open-fhir-training"
SOF_URL = "https://sql-on-fhir.org"
PATHLING_URL = "https://pathling.csiro.au"

LINKS = [
    (FORM_URL, "Workspace access"),
    (REPO_URL, "Exercises"),
    (SOF_URL, "sql-on-fhir.org"),
    (PATHLING_URL, "pathling.csiro.au"),
]


def standards_map(highlight=None):
    """The four stages of FHIR analytics and the standards in each.

    highlight names a stage ("get", "shape", "analyse", "act") to emphasise;
    the others are drawn faded.
    """
    stages = [
        (
            "get",
            "Get the data",
            BLUE,
            ["Bulk Data Access", "SMART Backend Services", "Map legacy extracts"],
        ),
        (
            "shape",
            "Shape it",
            LAVENDER,
            ["SQL on FHIR views", "FHIRPath", "Terminology"],
        ),
        (
            "analyse",
            "Analyse it",
            MINT,
            ["SQL · Python · R", "Dashboards · ML", "OMOP for research"],
        ),
        ("act", "Act on it", PEACH, ["CQL", "CDS Hooks", "SMART App Launch"]),
    ]
    b = []
    w, gap, x0, y0 = 212, 28, 6, 20
    for i, (key, title, fill, items) in enumerate(stages):
        x = x0 + i * (w + gap)
        faded = highlight is not None and key != highlight
        op = ' opacity="0.35"' if faded else ""
        g = [rect(x, y0, w, 262, fill, rx=10, sw=2.2 if key == highlight else 1.6)]
        g.append(text(x + w / 2, y0 + 36, title, 19, weight=700))
        for j, item in enumerate(items):
            g.append(box(x + 12, y0 + 62 + j * 64, w - 24, 48, "#fff", [item], 15))
        b.append(f"<g{op}>{''.join(g)}</g>")
        if i < len(stages) - 1:
            b.append(line(x + w + 3, y0 + 131, x + w + gap - 3, y0 + 131, sw=2))
    b.append(
        text(
            470,
            320,
            "FHIR data flows left to right; Pathling covers the middle two stages",
            15,
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 335, b)


def schedule(now=None):
    """The Track 3 blocks over both days, with John's slab topics.

    now is the index (0-5) of the block to highlight.
    """
    blocks = [
        ("Thu 11:30", "Kick-off: environment and the standards map"),
        ("Thu 2:00", "FHIR amid legacy and proprietary systems"),
        ("Thu 3:30", "Getting data out: Bulk Data and Pathling"),
        ("Fri 9:30", "SQL on FHIR, Pathling views and terminology"),
        ("Fri 11:00", "A real-world study: pulse oximetry bias"),
        ("Fri 1:30", "Closing the loop: CQL, CDS Hooks, SMART, OMOP"),
    ]
    b = []
    for i, (when, topic) in enumerate(blocks):
        col, row = divmod(i, 3)
        x, y = 10 + col * 470, 20 + row * 100
        on = now == i
        fill = YELLOW if on else "#fff"
        b.append(rect(x, y, 450, 80, fill, sw=2.4 if on else 1.6, rx=10))
        b.append(text(x + 18, y + 33, when, 16, "start", 700, TEAL if on else INK))
        b.append(text(x + 18, y + 60, topic, 15, "start"))
    b.append(text(245, 325, "Thursday 29 October", 16, weight=700, fill=MUTED))
    b.append(
        text(
            715,
            325,
            "Friday 30 October · Show and tell 3:30",
            16,
            weight=700,
            fill=MUTED,
        )
    )
    return svg(940, 340, b)


def environment():
    """Where the exercises run: form, invitation, workspace, notebooks, compute, data."""
    b = []
    steps = [
        (YELLOW, ["1. Fill in the form", "email only"]),
        (YELLOW, ["2. Accept the", "Databricks invitation"]),
        (BLUE, ["3. Open the", "open-fhir-training notebooks"]),
        (BLUE, ["4. Attach to", "Open FHIR Training Cluster"]),
    ]
    for i, (fill, rows) in enumerate(steps):
        x = 10 + i * 232
        b.append(box(x, 10, 212, 70, fill, rows, 15))
        if i < len(steps) - 1:
            b.append(line(x + 214, 45, x + 230, 45))
    b.append(rect(10, 108, 920, 140, "#F6F8FA", rx=10))
    b.append(
        text(
            30,
            136,
            "hive_metastore (shared, read-only by convention)",
            16,
            "start",
            700,
        )
    )
    data = [
        (CYAN, ["synthea", "800 patients · AU Core"]),
        (CYAN, ["synthea_csv", "flat CSV extract"]),
        (MINT, ["synthea_prostate_", "cancer_views"]),
        (PINK, ["mimic_iv_demo", "100 ICU patients"]),
        (PINK, ["mimic_iv_views", "rv · st · coh"]),
    ]
    for i, (fill, rows) in enumerate(data):
        b.append(box(30 + i * 180, 154, 166, 76, fill, rows, 14))
    b.append(rect(10, 270, 920, 54, "#fff", TEAL, 2, 10))
    b.append(
        text(
            470,
            303,
            "Your own experiments go in your own schema: CREATE SCHEMA IF NOT EXISTS jane_citizen",
            15,
            fill=INK,
        )
    )
    return svg(940, 335, b)


def qr_strip(links=LINKS, size=120):
    """A row of QR codes with captions."""
    gap = (940 - len(links) * size) / (len(links) + 1)
    b = [
        qr(url, gap + i * (size + gap), 10, size, label, 14)
        for i, (url, label) in enumerate(links)
    ]
    return svg(940, size + 40, b)
