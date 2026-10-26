"""Day 2, 9:00 main room: a 10 minute recap of Track 3 and the plan for Friday.

Author: John Grimes

To fill in the "Progress so far" slide on Thursday night, add one (team, question,
progress) tuple of strings per group to PROGRESS below, then rebuild with
`uv run build.py d2_recap` from the slides directory. Each cell wraps to at most two
lines (longer text is cut short with an ellipsis); up to six rows fit on the slide.
Leave PROGRESS empty to show four blank ruled rows.
"""

from kit import (
    BLUE,
    CYAN,
    GREY,
    INK,
    LAVENDER,
    MINT,
    MUTED,
    PEACH,
    TEAL,
    YELLOW,
    box,
    closing,
    diagram,
    hcurve,
    line,
    qr,
    rect,
    svg,
    text,
    title_slide,
)

from decks._shared import EVENT, FORM_URL, LINKS, PRESENTER, show_and_tell

# One (team, question, progress) tuple per group, e.g.
#   ("Metro North", "Do beta-blockers help in septic shock?", "Cohort built; comparing mortality"),
# Fill in on Thursday night, then run `uv run build.py d2_recap` in slides/.
PROGRESS = []


def wrap(s, width, max_lines=2):
    """Word-wrap s to lines of at most width characters, cut to max_lines."""
    out, cur = [], ""
    for word in s.split():
        if cur and len(cur) + 1 + len(word) > width:
            out.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}" if cur else word
    if cur:
        out.append(cur)
    if len(out) > max_lines:
        last = out[max_lines - 1]
        out = out[: max_lines - 1] + [last[: width - 1].rstrip() + "…"]
    return [r if len(r) <= width else r[: width - 1] + "…" for r in out]


def strands():
    """What each Track 3 strand covered on Thursday."""
    b = [rect(10, 10, 450, 320, BLUE, rx=12)]
    b.append(text(30, 46, "Analytics", 20, "start", 700))
    b.append(text(30, 72, "John Grimes", 15, "start", 400, MUTED))
    slabs = [
        ("11:30", ["Kick-off: the environment", "and the standards map"]),
        ("2:00", ["FHIR amid legacy systems:", "mapping CSV to FHIR"]),
        ("3:30", ["Getting data out: Bulk Data", "and Pathling"]),
    ]
    for i, (when, rows) in enumerate(slabs):
        y = 96 + i * 76
        b.append(rect(30, y, 410, 64, "#fff", rx=8))
        b.append(text(48, y + 38, when, 16, "start", 700, TEAL))
        b.append(text(112, y + 27, rows[0], 15, "start"))
        b.append(text(112, y + 49, rows[1], 15, "start"))
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


def analytics_path():
    """The analytics path so far: two ways into FHIR tables on Thursday, then Friday's stages."""
    b = [
        text(305, 30, "Thursday: get the data", 17, weight=700, fill=TEAL),
        text(795, 30, "Friday: use it", 17, weight=700, fill=MUTED),
        box(10, 60, 180, 80, CYAN, ["Legacy extract", "synthea_csv"], 15),
        box(10, 190, 180, 80, BLUE, ["FHIR server", "Bulk Data $export"], 15),
        box(225, 60, 180, 80, "#fff", ["Map to FHIR", "Spark struct · to_json"], 14),
        box(225, 190, 180, 80, "#fff", ["NDJSON per type", "Patient.00000.ndjson"], 14),
        box(440, 60, 170, 80, LAVENDER, ["Pathling", "encode · read.ndjson"], 14),
        box(440, 190, 170, 80, MINT, ["Delta tables", "one per resource type"], 14),
        line(190, 100, 223, 100),
        line(190, 230, 223, 230),
        line(405, 100, 438, 100),
        hcurve(405, 230, 438, 112),
        line(525, 140, 525, 188),
        hcurve(610, 230, 658, 92),
    ]
    friday = [
        (LAVENDER, ["Shape: SQL on FHIR views", "FHIRPath · terminology"]),
        (MINT, ["Analyse: SQL · Python", "a real-world study"]),
        (PEACH, ["Act: CQL · CDS Hooks", "SMART apps · OMOP"]),
    ]
    g = []
    for i, (fill, rows) in enumerate(friday):
        y = 60 + i * 80
        g.append(box(660, y, 270, 64, fill, rows, 15))
        if i < len(friday) - 1:
            g.append(line(795, y + 64, 795, y + 78))
    b.append(f'<g opacity="0.45">{"".join(g)}</g>')
    b.append(
        text(
            470,
            322,
            "Two ways in, one set of FHIR tables - everything on Friday reuses them",
            15,
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 335, b)


def progress_table(entries):
    """Team / question / progress, two lines per cell at most; blank rows if empty."""
    cols = [("Team", 200), ("Question", 370), ("Progress so far", 370)]
    fs, lh, head = 15, 19, 38
    rows = entries or [("", "", "")] * 4
    rh = min(62, (334 - 10 - head) // len(rows))
    x0, y0 = 0, 10
    w = sum(c[1] for c in cols)
    h = head + rh * len(rows)
    b = [
        rect(x0 + 1, y0, w - 2, h, "#fff", rx=8),
        f'<path d="M{x0 + 9},{y0} H{w - 9} Q{w - 1},{y0} {w - 1},{y0 + 8} V{y0 + head} '
        f'H{x0 + 1} V{y0 + 8} Q{x0 + 1},{y0} {x0 + 9},{y0} z" fill="{YELLOW}" '
        f'stroke="{INK}" stroke-width="1.6"/>',
    ]
    for j in range(1, len(rows)):
        y = y0 + head + j * rh
        b.append(line(x0 + 1, y, w - 1, y, "#D0D0D0", 1, arrow=None))
    cx = x0
    for i, (title, cw) in enumerate(cols):
        if i:
            b.append(line(cx, y0, cx, y0 + h, "#D0D0D0", 1, arrow=None))
        b.append(text(cx + 14, y0 + head / 2 + fs * 0.36, title, fs + 1, "start", 700))
        width = int((cw - 28) / (0.55 * fs))
        for j, r in enumerate(rows):
            cell = wrap(r[i], width)
            mid = y0 + head + rh * j + rh / 2
            top = mid - (len(cell) - 1) * lh / 2 + fs * 0.36
            for k, s in enumerate(cell):
                b.append(
                    text(cx + 14, top + k * lh, s, fs, "start", 700 if i == 0 else 400)
                )
        cx += cw
    return svg(940, max(h + y0 + 4, 300), b)


def friday():
    """Friday's blocks on a timeline, with the recap highlighted."""
    blocks = [
        ("9:00", "Recap", ["Track leads", "summarise Day 1"], "Main room", YELLOW),
        (
            "9:30",
            "SQL on FHIR",
            ["Pathling views and", "terminology"],
            "Track 3 room",
            LAVENDER,
        ),
        (
            "11:00",
            "A real-world study",
            ["Beta-blockers in", "septic shock"],
            "Track 3 room",
            MINT,
        ),
        (
            "1:30",
            "Closing the loop",
            ["CQL, CDS Hooks,", "SMART, OMOP"],
            "Track 3 room",
            PEACH,
        ),
        ("3:30", "Show and tell", ["A few minutes", "per group"], "Main room", BLUE),
    ]
    b = [line(20, 60, 920, 60, GREY, 2, arrow=None)]
    w, gap = 172, 14
    for i, (when, title, rows, where, fill) in enumerate(blocks):
        x = 10 + i * (w + gap)
        cx = x + w / 2
        now = i == 0
        b.append(
            f'<circle cx="{cx}" cy="60" r="9" fill="{TEAL if now else "#fff"}" stroke="{INK}" stroke-width="1.6"/>'
        )
        b.append(text(cx, 36, when, 18, weight=700, fill=TEAL if now else INK))
        b.append(rect(x, 90, w, 190, fill, sw=2.4 if now else 1.6, rx=10))
        b.append(text(cx, 128, title, 16, weight=700))
        b.append(text(cx, 172, rows[0], 15))
        b.append(text(cx, 194, rows[1], 15))
        b.append(text(cx, 258, where, 14, fill=MUTED, italic=True))
    b.append(text(103, 312, "You are here", 15, weight=700, fill=TEAL))
    b.append(
        text(
            560,
            312,
            "Every Track 3 block: about 30 minutes of context and a demo, then hands-on",
            15,
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 330, b)


def reminders():
    """Housekeeping for the analytics workspace, with the access form QR code."""
    cards = [
        (
            YELLOW,
            "Synthetic data only",
            ["Synthetic and de-identified", "data - nothing sensitive"],
        ),
        (BLUE, "Your own schema", ["CREATE SCHEMA IF NOT", "EXISTS jane_citizen"]),
        (
            MINT,
            "Open FHIR Training Cluster",
            ["Not Serverless - Pathling", "is not installed there"],
        ),
        (
            LAVENDER,
            "Run in place, or clone",
            ["File > Clone to your home", "folder to change a notebook"],
        ),
    ]
    b = []
    for i, (fill, title, rows) in enumerate(cards):
        col, row = divmod(i, 2)
        x, y = 10 + col * 315, 10 + row * 165
        b.append(rect(x, y, 300, 150, fill, rx=12))
        b.append(text(x + 20, y + 40, title, 17, "start", 700))
        b.append(text(x + 20, y + 84, rows[0], 15, "start"))
        b.append(text(x + 20, y + 108, rows[1], 15, "start"))
    b.append(rect(650, 10, 280, 315, "#fff", rx=12))
    b.append(text(790, 44, "New today?", 18, weight=700))
    b.append(qr(FORM_URL, 690, 62, 200, "Scan for workspace access", 14))
    return svg(940, 335, b)


DECK = {
    "file": "track-3-day-2-recap",
    "slides": [
        title_slide(
            "Track 3: recap and Day 2 plan",
            f"Day 2 recap · {EVENT}",
            "Good morning. I'm John Grimes from CSIRO's Australian e-Health Research Centre, one of "
            "the leads for Track 3, FHIR for data: analytics and text. In the next ten minutes I'll "
            "go back over what the track covered yesterday, show where the analytics groups have got "
            "to, and walk through today's plan. That ends with show and tell in this room at 3:30, "
            "so I'll also say what we'd like each group to bring. If you're joining Track 3 for the "
            "first time today, there's a slide near the end on how to get into the workspace.",
        ),
        diagram(
            "Day 1 across the track",
            "Four strands, one set of shared data and questions",
            "strands",
            strands(),
            "Track 3 ran as four strands yesterday. In the analytics strand we had three blocks: the "
            "kick-off, where we set up the Databricks environment and walked through the standards "
            "map; then FHIR amid legacy and proprietary systems, where we mapped a flat CSV extract "
            "into FHIR; then getting data out with Bulk Data and Pathling. Alongside that, James "
            "Grant led terminology, Dion McMurtrie led the work on turning text into structured, "
            "coded data, and Duncan Pullen brought the Queensland Health perspective. James and Dion "
            "can tell you more about their strands.",
        ),
        diagram(
            "The analytics path so far",
            "Thursday was about getting data into FHIR tables; Friday is about using them",
            "analytics-path",
            analytics_path(),
            "This is where the analytics strand has got to. Yesterday was the left-hand side: getting "
            "the data. There were two ways in. One was mapping a legacy extract, the Synthea CSV "
            "tables, into FHIR resources with Spark. The other was the route a FHIR server gives "
            "you: a Bulk Data export, which produces NDJSON files per resource type. Either way, "
            "Pathling encodes the resources and writes one Delta table per resource type. Today is "
            "the right-hand side: shaping those tables with SQL on FHIR views, analysing them, and "
            "putting results back into the workflow.",
        ),
        diagram(
            "Progress so far",
            "Where the analytics groups had got to by the end of Thursday",
            "progress",
            progress_table(PROGRESS),
            "Here is a snapshot of where the groups had got to at the end of yesterday: the team, "
            "the question each group picked up, and how far they got. I'll read through these "
            "briefly. If your group isn't here, or I've got it wrong, come and tell me and I'll "
            "update it before show and tell. The point isn't to compare groups. Several of these "
            "questions will carry on today, and some of you may want to join another group whose "
            "question interests you.",
        ),
        diagram(
            "Friday in Track 3",
            "Three hands-on blocks in the Track 3 room, then show and tell here",
            "friday",
            friday(),
            "Here's today. At 9:30 we start in the Track 3 room with SQL on FHIR: Pathling views and "
            "terminology, on the synthetic Synthea data. At 11:00 we look at a "
            "real-world study, beta-blockers in septic shock, using the MIMIC-IV intensive care demo data. At "
            "1:30 we close the loop, with CQL, CDS Hooks, SMART apps and OMOP: how analytics results "
            "get back to clinicians and researchers. Each block starts with about 30 minutes of "
            "context and a demo from me, then the rest is hands-on time. At 3:30 we all come back "
            "here for show and tell.",
        ),
        diagram(
            "Show and tell",
            "What we'd like each group to bring at 3:30",
            "show-and-tell",
            show_and_tell(),
            "Show and tell is at 3:30 in this room, with a few minutes per group. You don't need "
            "polished slides. Tell us the question you started with, the data you used, what you "
            "did, what you found, and what you'd do next. A dead end is a perfectly good result if "
            "you can say why. A query, a chart or a screenshot from the workspace is enough. It "
            "helps to keep a few notes as you go through the day, so you're not reconstructing "
            "everything at 3:25.",
        ),
        diagram(
            "Reminders",
            "Housekeeping for the analytics workspace",
            "reminders",
            reminders(),
            "A few reminders. If you're new today and want an account, scan this code: the form "
            "asks only for your email, and I'll send you a Databricks invitation. Only use the "
            "synthetic and de-identified data we've loaded. Write anything you create into your own "
            "schema, never the shared ones. Attach notebooks to the Open FHIR Training Cluster, not "
            "Serverless, because Pathling isn't installed on serverless compute. And run notebooks "
            "in place; if you want to change one, use File, Clone to copy it into your home folder.",
        ),
        closing(
            "Over to you",
            PRESENTER,
            "That's the recap from Track 3. The Track 3 room opens at 9:30, and we start with SQL "
            "on FHIR, Pathling views and terminology. If you're new today, scan the form on the "
            "left now, so your invitation is waiting when you sit down. The code on the right takes "
            "you to the exercises on GitHub, which stay public after the event. "
            "The track leads will be in the Track 3 room, so come and find us with your "
            "questions. See you there.",
            LINKS[:2],
        ),
    ],
}
