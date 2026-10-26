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

from decks._shared import EVENT, FORM_URL, LINKS, PRESENTER, show_and_tell, strands

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


def analytics_path():
    """The analytics path: two ways into FHIR tables, then the stages that use them."""
    b = [
        text(305, 30, "Get the data", 17, weight=700, fill=TEAL),
        text(795, 30, "Then use it", 17, weight=700, fill=TEAL),
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
    stages = [
        (LAVENDER, ["Shape: SQL on FHIR views", "FHIRPath · terminology"]),
        (MINT, ["Analyse: SQL · Python", "a real-world study"]),
        (PEACH, ["Act: CQL · CDS Hooks", "SMART apps · OMOP"]),
    ]
    for i, (fill, rows) in enumerate(stages):
        y = 60 + i * 80
        b.append(box(660, y, 270, 64, fill, rows, 15))
        if i < len(stages) - 1:
            b.append(line(795, y + 64, 795, y + 78))
    b.append(
        text(
            470,
            322,
            "Two ways in, one set of FHIR tables - everything after reuses them",
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
    """Friday in Track 3 on a timeline, with the recap highlighted."""
    blocks = [
        ("9:00", 220, "Recap", ["Track leads", "summarise Day 1"], "Main room", YELLOW),
        (
            "From 9:30",
            440,
            "Hands-on",
            [
                "Carry on through the analytics topics",
                "from wherever your group has got to",
            ],
            "Track 3 room",
            LAVENDER,
        ),
        (
            "3:30",
            220,
            "Show and tell",
            ["A few minutes", "per group"],
            "Main room",
            BLUE,
        ),
    ]
    b = [line(20, 60, 920, 60, GREY, 2, arrow=None)]
    x = 10
    for i, (when, w, title, rows, where, fill) in enumerate(blocks):
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
        x += w + 20
    b.append(text(120, 312, "You are here", 15, weight=700, fill=TEAL))
    b.append(
        text(
            600,
            312,
            "Each topic: some context and a demo, then hands-on",
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
            "Across the track",
            "Four strands, one set of shared data and questions",
            "strands",
            strands(),
            "Track 3 runs as four strands. In the analytics strand we're working through six topics "
            "at the pace of the room, starting with the kick-off, where we set up the Databricks "
            "environment and walked through the standards map. Alongside that, James Grant leads "
            "terminology, Dion McMurtrie leads the work on turning text into structured, coded "
            "data, and Duncan Pullen brings the Queensland Health perspective. James and Dion can "
            "tell you more about their strands.",
        ),
        diagram(
            "The analytics path",
            "Two ways into FHIR tables, then shaping, analysing and acting on them",
            "analytics-path",
            analytics_path(),
            "This is the analytics path. It starts with getting the data, and there are two ways "
            "in. One is mapping a legacy extract, the Synthea CSV tables, into FHIR resources with "
            "Spark. The other is the route a FHIR server gives you: a Bulk Data export, which "
            "produces NDJSON files per resource type. Either way, Pathling encodes the resources "
            "and writes one Delta table per resource type. Everything after that reuses those "
            "tables: shaping them with SQL on FHIR views, analysing them, and putting results back "
            "into the workflow.",
        ),
        diagram(
            "Progress so far",
            "Where the analytics groups had got to by the end of Thursday",
            "progress",
            progress_table(PROGRESS),
            "Here is a snapshot of where the groups had got to at the end of yesterday: the team, "
            "the question each group picked up, and how far they got. I'll read through these "
            "briefly. If your group isn't here, or I've got it wrong, come and tell me and I'll "
            "update it before show and tell. This isn't meant as a comparison between groups. Several of these "
            "questions will carry on today, and some of you may want to join another group whose "
            "question interests you.",
        ),
        diagram(
            "Friday in Track 3",
            "Hands-on in the Track 3 room, then show and tell here",
            "friday",
            friday(),
            "Here's today. From 9:30 the Track 3 room is open, and we carry on through the "
            "analytics topics from wherever your group has got to: SQL on FHIR and terminology, the "
            "septic shock study on the MIMIC-IV intensive care demo data, and closing the loop with "
            "CQL, CDS Hooks, SMART apps and OMOP. Each topic starts with some context and a demo "
            "from me, then the rest is hands-on time. At 3:30 we all come back here for show and "
            "tell.",
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
            "That's the recap from Track 3. The Track 3 room opens at 9:30. If you're new today, "
            "scan the form on the "
            "left now, so your invitation is waiting when you sit down. The code on the right takes "
            "you to the exercises on GitHub, which stay public after the event. "
            "The track leads will be in the Track 3 room, so come and find us with your "
            "questions. See you there.",
            LINKS[:2],
        ),
    ],
}
