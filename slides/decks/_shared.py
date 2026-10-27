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
    circle,
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
            "Data flows left to right; Pathling's libraries work in the middle two stages, and its server does bulk export",
            15,
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 335, b)


# The analytics topics in the order they are presented, each with its stage on the
# standards map, a fill, a full title and a short title. They have no fixed times.
TOPICS = [
    (
        "Start here",
        YELLOW,
        "Kick-off: the environment and the standards map",
        "Kick-off: environment and standards",
    ),
    (
        "Get the data",
        BLUE,
        "FHIR amid legacy and proprietary systems",
        "FHIR amid legacy systems",
    ),
    (
        "Get the data",
        BLUE,
        "Getting data out: Bulk Data and Pathling",
        "Getting data out: Bulk Data",
    ),
    (
        "Shape it",
        LAVENDER,
        "SQL on FHIR, Pathling views and terminology",
        "SQL on FHIR and terminology",
    ),
    (
        "Analyse it",
        MINT,
        "A real-world study: beta-blockers in septic shock",
        "Beta-blockers in septic shock",
    ),
    (
        "Act on it",
        PEACH,
        "Closing the loop: CQL, CDS Hooks, SMART, OMOP",
        "Closing the loop: CQL to OMOP",
    ),
]


def topics():
    """The analytics topics, each with its stage on the standards map."""
    b = []
    for i, (stage, fill, title, _) in enumerate(TOPICS):
        col, row = divmod(i, 3)
        x, y = 10 + col * 470, 20 + row * 100
        b.append(rect(x, y, 450, 80, fill, rx=10))
        b.append(text(x + 18, y + 33, stage, 16, "start", 700, INK))
        b.append(text(x + 18, y + 60, title, 15, "start"))
    b.append(
        text(
            470,
            325,
            "Taken at the pace of the room · Show and tell: Friday 3:30, main room",
            16,
            weight=700,
            fill=MUTED,
        )
    )
    return svg(940, 340, b)


def strands():
    """The four Track 3 strands: the analytics topics beside the other three leads."""
    b = [rect(10, 10, 450, 320, BLUE, rx=12)]
    b.append(text(30, 46, "Analytics", 20, "start", 700))
    b.append(text(440, 46, "John Grimes", 14, "end", 400, MUTED))
    for i, (_, fill, _, short) in enumerate(TOPICS):
        y = 66 + i * 43
        b.append(rect(30, y, 410, 36, "#fff", rx=8))
        b.append(circle(52, y + 18, 8, fill, sw=1.2))
        b.append(text(72, y + 24, short, 15, "start"))
    others = [
        (LAVENDER, "Terminology", "James Grant", "SNOMED CT-AU, AMT, Ontoserver, ECL"),
        (
            MINT,
            "Text to structured data",
            "Dion McMurtrie",
            "Clinical notes to coded FHIR data",
        ),
        (
            PEACH,
            "Queensland Health context",
            "Duncan Pullen",
            "The Queensland Health perspective",
        ),
    ]
    for i, (fill, title, lead, item) in enumerate(others):
        y = 10 + i * 110
        b.append(rect(480, y, 450, 100, fill, rx=12))
        b.append(text(500, y + 32, title, 18, "start", 700))
        b.append(text(910, y + 32, lead, 14, "end", 400, MUTED))
        b.append(text(500, y + 70, item, 15, "start"))
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
        (CYAN, ["synthea", "8,297 patients · AU Core"]),
        (CYAN, ["synthea_csv", "flat CSV extract"]),
        (MINT, ["synthea_mi_secondary_", "prevention_views"]),
        (PINK, ["mimic_iv_demo", "100 ICU patients"]),
        (PINK, ["mimic_iv_beta_", "blocker_views"]),
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


def show_and_tell():
    """What each group brings to the 3:30 show and tell."""
    items = [
        ("1", "The question", ["What did you", "want to know?"]),
        ("2", "The data", ["Which tables,", "resources, codes?"]),
        ("3", "What you did", ["Views, queries,", "mappings, notebooks"]),
        ("4", "What you found", ["A result, a number,", "or a dead end"]),
        ("5", "What's next", ["What would you", "do with more time?"]),
    ]
    b = []
    w, gap = 168, 20
    for i, (n, title, rows) in enumerate(items):
        x = 10 + i * (w + gap)
        cx = x + w / 2
        b.append(rect(x, 10, w, 200, YELLOW if i % 2 == 0 else BLUE, rx=12))
        b.append(f'<circle cx="{cx}" cy="52" r="22" fill="{TEAL}"/>')
        b.append(text(cx, 60, n, 20, weight=700, fill="#fff"))
        b.append(text(cx, 112, title, 17, weight=700))
        b.append(text(cx, 152, rows[0], 15))
        b.append(text(cx, 174, rows[1], 15))
        if i < len(items) - 1:
            b.append(line(x + w + 2, 110, x + w + gap - 2, 110, sw=2))
    b.append(rect(10, 238, 920, 84, "#fff", TEAL, 2, 12))
    b.append(
        text(
            470, 272, "3:30-4:30 · main room · a few minutes per group", 18, weight=700
        )
    )
    b.append(
        text(
            470,
            302,
            "A query, a chart or a screenshot from the workspace is enough",
            15,
            fill=MUTED,
        )
    )
    return svg(940, 335, b)
