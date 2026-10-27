"""Day 1, 11:30 Track 3 kick-off: the analytics environment and the standards map. Author: John Grimes"""

from kit import (
    AMBER,
    BLUE,
    CYAN,
    INK,
    LAVENDER,
    MINT,
    MONO,
    MUTED,
    PEACH,
    PINK,
    RED,
    TEAL,
    YELLOW,
    box,
    callout,
    circle,
    closing,
    code,
    diagram,
    highlight,
    line,
    qr,
    rect,
    screenshot,
    section,
    svg,
    table,
    text,
    title_slide,
)

from decks._shared import (
    EVENT,
    FORM_URL,
    LINKS,
    PRESENTER,
    WORKSPACE_URL,
    topics,
    standards_map,
)


def mark(pt, px, py, pw, ph):
    """A highlight around a screenshot region given in screenshot pixels."""
    x1, y1 = pt(px, py)
    x2, y2 = pt(px + pw, py + ph)
    return highlight(x1, y1, x2 - x1, y2 - y1)


def legend(y, items, fs=15):
    """A row of numbered callouts with labels, spread evenly across 940 px."""
    widths = [36 + len(s) * fs * 0.55 for s in items]
    gap = (940 - sum(widths)) / (len(items) + 1)
    out, x = [], gap
    for i, (s, w) in enumerate(zip(items, widths), 1):
        out.append(callout(i, x + 13, y, 13))
        out.append(text(x + 34, y + fs * 0.36, s, fs, "start"))
        x += w + gap
    return "".join(out)


def cross(x, y, r=11):
    """A red circled cross, for marking the option not to pick."""
    return (
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{RED}" stroke="#fff" stroke-width="2.5"/>'
        + line(
            x - r * 0.4, y - r * 0.4, x + r * 0.4, y + r * 0.4, "#fff", 2.6, arrow=None
        )
        + line(
            x - r * 0.4, y + r * 0.4, x + r * 0.4, y - r * 0.4, "#fff", 2.6, arrow=None
        )
    )


def rhythm():
    """The shape of each topic: context, demo, then hands-on time."""
    cards = [
        (
            BLUE,
            "Context",
            ["A standard or a technique,", "and where it fits on the map"],
        ),
        (LAVENDER, "Demo", ["Live in the Databricks", "workspace, step by step"]),
        (
            MINT,
            "Hands-on",
            [
                "Exercises or your own question;",
                "John, James, Dion and Duncan",
                "are on hand to help",
            ],
        ),
    ]
    b = []
    for i, (fill, title, rows) in enumerate(cards):
        x = 10 + i * 316
        b.append(rect(x, 30, 288, 220, fill, rx=12))
        b.append(text(x + 26, 76, title, 20, "start", 700))
        for j, r in enumerate(rows):
            b.append(text(x + 26, 124 + j * 28, r, 15, "start"))
        if i < len(cards) - 1:
            b.append(line(x + 291, 140, x + 313, 140, sw=2))
    b.append(
        text(
            470,
            300,
            "Friday 3:30: show and tell in the main room - note what you try as you go",
            15,
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 335, b)


def get_set_up():
    """Form, invitation and sign-in, with the form QR code and workspace URL."""
    b = []
    steps = [
        (
            YELLOW,
            "Scan the code, give us your email",
            "The form explains how we use it; accounts go by 30 Nov",
        ),
        (
            YELLOW,
            "Accept the Databricks invitation",
            "Look for an email from Databricks (check junk mail)",
        ),
        (BLUE, "Sign in to the workspace", "Open FHIR Training Environment"),
    ]
    for i, (fill, head, sub) in enumerate(steps):
        y = 10 + i * 92
        b.append(rect(10, y, 600, 76, fill, rx=10))
        b.append(circle(46, y + 38, 20, "#fff", TEAL, 2.2))
        b.append(text(46, y + 44, str(i + 1), 17, weight=700, fill=TEAL))
        b.append(text(82, y + 33, head, 18, "start", 700))
        b.append(text(82, y + 58, sub, 14, "start", fill=MUTED))
        if i < len(steps) - 1:
            b.append(line(46, y + 78, 46, y + 92 - 2, sw=1.6))
    b.append(
        text(
            10, 312, WORKSPACE_URL.removeprefix("https://"), 15, "start", 400, INK, MONO
        )
    )
    b.append(
        text(
            10,
            334,
            "Synthetic and de-identified data only - nothing sensitive",
            14,
            "start",
            fill=MUTED,
        )
    )
    b.append(qr(FORM_URL, 680, 14, 210, "Workspace access form", 15))
    b.append(text(785, 270, "forms.cloud.microsoft/r/inJ0BxKvw7", 13, fill=MUTED))
    return svg(940, 345, b)


def find_notebooks():
    """The workspace browser at the training repo, with numbered callouts."""
    shot, w, h, pt = screenshot("workspace-repo", 0, 16, 920, crop=(0, 50, 940, 286))
    b = [shot]
    b.append(mark(pt, 12, 97, 178, 28))
    b.append(mark(pt, 564, 56, 292, 24))
    b.append(mark(pt, 564, 84, 186, 30))
    b.append(mark(pt, 596, 211, 330, 62))
    marks = [(198, 111), (675, 50), (782, 50), (540, 99), (948, 242)]
    for i, (px, py) in enumerate(marks, 1):
        x, y = pt(px, py)
        b.append(callout(i, min(x, 922), y))
    b.append(
        legend(
            h + 40,
            [
                "Workspace",
                "Repos",
                "John.Grimes@csiro.au",
                "open-fhir-training",
                "notebooks / sql",
            ],
        )
    )
    return svg(940, h + 58, b)


def attach_cluster():
    """The compute dropdown in a notebook: pick the cluster, not Serverless."""
    shot, w, h, pt = screenshot("attach-cluster", 0, 0, 560, crop=(560, 92, 600, 320))
    b = [shot]
    b.append(mark(pt, 950, 127, 202, 26))
    b.append(mark(pt, 708, 266, 440, 66))
    b.append(callout(1, *pt(1150, 127)))
    b.append(callout(2, *pt(1150, 266)))
    x, y = pt(716, 361)
    b.append(cross(x + 120, y))
    x0 = 600
    steps = [
        (TEAL, "1", "Open the compute menu", "top right of the notebook"),
        (
            TEAL,
            "2",
            "Pick Open FHIR Training Cluster",
            "Pathling 10.0.0 is installed here",
        ),
        (RED, "×", "Not Serverless", "Pathling is not available there"),
    ]
    for i, (col, n, head, sub) in enumerate(steps):
        y = 22 + i * 76
        b.append(
            f'<circle cx="{x0 + 14}" cy="{y + 12}" r="14" fill="{col}" stroke="#fff" stroke-width="2.5"/>'
        )
        b.append(text(x0 + 14, y + 18, n, 16, weight=700, fill="#fff"))
        b.append(text(x0 + 38, y + 18, head, 17, "start", 700))
        b.append(text(x0 + 38, y + 42, sub, 14, "start", fill=MUTED))
    b.append(rect(x0, 250, 330, 72, YELLOW, rx=10))
    b.append(text(x0 + 16, 278, "SQL editor queries run on", 15, "start"))
    b.append(text(x0 + 16, 304, "Serverless Starter Warehouse", 15, "start", 700))
    return svg(940, max(h, 325) + 4, b)


def ground_rules():
    """Four rules for the shared workspace, with the File > Clone menu."""
    b = []
    rules = [
        (
            PINK,
            "Synthetic and de-identified data only",
            "No sensitive, identifiable or real patient data",
        ),
        (
            AMBER,
            "The data is already loaded",
            "Don't run the write cells in the import notebooks",
        ),
        (
            BLUE,
            "Run notebooks in place",
            "To change one, File > Clone it to your home folder",
        ),
    ]
    for i, (fill, head, sub) in enumerate(rules):
        y = 4 + i * 72
        b.append(rect(10, y, 560, 62, fill, rx=10))
        b.append(text(28, y + 27, f"{i + 1}.  {head}", 17, "start", 700))
        b.append(text(51, y + 50, sub, 14, "start"))
    b.append(rect(10, 220, 560, 112, MINT, rx=10))
    b.append(text(28, 246, "4.  Write results to your own schema", 17, "start", 700))
    b.append(
        code(
            28,
            258,
            524,
            [
                "CREATE SCHEMA IF NOT EXISTS jane_citizen",
                'df.write.saveAsTable("jane_citizen.my_view")',
            ],
            fs=14,
            fill="#fff",
        )
    )
    shot, w, h, pt = screenshot(
        "file-menu-clone", 620, 4, 310, 336, crop=(250, 125, 300, 345)
    )
    b.append(shot)
    b.append(mark(pt, 256, 128, 36, 26))
    b.append(mark(pt, 256, 416, 280, 28))
    x, y = pt(256, 430)
    b.append(line(572, 180, x - 4, y, TEAL, 2, dash="5 4", arrow="at"))
    return svg(940, 345, b)


def fhir_as_data():
    """A Patient resource as JSON beside the same data as nested columns."""
    b = []
    rows = [
        "{",
        '  "resourceType": "Patient",',
        '  "id": "d286c559-67c1-77b7-...",',
        '  "meta": {',
        '    "profile": ["...au-core-patient", ...]',
        "  },",
        '  "gender": "male",',
        '  "birthDate": "2012-07-09",',
        '  "name": [{',
        '    "family": "Collins926",',
        '    "given": ["Brice635", "Rocco842"]',
        "  }]",
        "}",
    ]
    b.append(code(4, 0, 420, rows, "One Patient resource (JSON)", fs=13, lh=1.42))
    shot, w, h, pt = screenshot(
        "patient-schema", 480, 30, 456, 312, crop=(538, 300, 560, 400)
    )
    b.append(text(480, 20, "The patient table in Databricks", 14, "start", 700))
    b.append(shot)
    b.append(mark(pt, 542, 405, 552, 34))
    b.append(mark(pt, 542, 626, 552, 70))
    mx, my = pt(542, 422)
    b.append(line(426, 101, mx - 6, my, TEAL, 2, dash="5 4", arrow="at"))
    b.append(
        text(
            4,
            316,
            "Structs for objects, arrays for repeating elements:",
            14,
            "start",
            fill=MUTED,
        )
    )
    b.append(
        text(
            4,
            338,
            "a tree in a table. SQL on FHIR views flatten it.",
            14,
            "start",
            fill=MUTED,
        )
    )
    return svg(940, 345, b)


def six_standards():
    """The six standards: what each is and when to use it."""
    rows = [
        (
            LAVENDER,
            "SQL on FHIR",
            "ViewDefinitions: FHIR resources to tables",
            "Building analytic tables",
        ),
        (
            BLUE,
            "Bulk Data Access",
            "$export of a population as NDJSON files",
            "Getting data out of a server",
        ),
        (
            PEACH,
            "SMART App Launch",
            "OAuth 2.0 for apps; Backend Services",
            "Authorising apps, bulk export",
        ),
        (
            PEACH,
            "CDS Hooks",
            "EHR calls a service, gets cards back",
            "Advice in the clinical workflow",
        ),
        (
            PEACH,
            "CQL",
            "Readable language for clinical logic",
            "Measures and decision rules",
        ),
        (
            MINT,
            "OMOP CDM",
            "Research data model and vocabularies",
            "Joining research networks",
        ),
    ]
    cols = [("Standard", 216), ("What it is", 400), ("Use it for", 320)]
    x0, y0, rh = 2, 2, 46
    b = [rect(x0, y0, 936, rh * 7, "#fff", rx=8)]
    b.append(rect(x0, y0, 936, rh, "#F0F0F0", rx=8))
    x = x0
    for title, cw in cols:
        b.append(text(x + 14, y0 + 29, title, 15, "start", 700))
        x += cw
    for j, (fill, *cells) in enumerate(rows):
        y = y0 + rh * (j + 1)
        b.append(rect(x0 + 8, y + 7, cols[0][1] - 16, rh - 14, fill, sw=1.2, rx=8))
        b.append(line(x0, y, x0 + 936, y, "#D0D0D0", 1, arrow=None))
        x = x0
        for i, ((_, cw), s) in enumerate(zip(cols, cells)):
            b.append(
                text(
                    x + (cw / 2 if i == 0 else 14),
                    y + 29,
                    s,
                    15,
                    "middle" if i == 0 else "start",
                    700 if i == 0 else 400,
                    INK,
                )
            )
            x += cw
    return svg(940, 330, b)


def exercises_map():
    """The five exercises used in the track, the concepts each teaches, and its section."""
    rows = [
        (
            YELLOW,
            "CSV to FHIR",
            "map a legacy extract to Patient, Encounter, Immunization",
            "Legacy systems",
        ),
        (
            CYAN,
            "Synthea import",
            "NDJSON in bulk data style, Pathling encoders, tables",
            "Bulk Data",
        ),
        (
            CYAN,
            "MI secondary prevention",
            "SQL on FHIR views, a ConceptMap in SQL, time windows",
            "SQL on FHIR",
        ),
        (
            PINK,
            "MIMIC-IV import",
            "file name mapping, extensions, de-identified ICU data",
            "Bulk Data",
        ),
        (
            PINK,
            "Septic shock study",
            "beta-blocker cohort: eight views, timed criteria, SOFA in SQL",
            "Septic shock",
        ),
    ]
    b = [
        text(130, 16, "Exercise", 15, weight=700, fill=MUTED),
        text(530, 16, "What it teaches", 15, weight=700, fill=MUTED),
        text(862, 16, "Section", 15, weight=700, fill=MUTED),
    ]
    for i, (fill, name, concepts, part) in enumerate(rows):
        y = 30 + i * 60
        b.append(box(10, y, 240, 48, fill, [f"{i + 1}. {name}"], 15, 700))
        b.append(line(252, y + 24, 282, y + 24))
        b.append(rect(286, y, 488, 48, "#fff", rx=8))
        b.append(text(302, y + 29, concepts, 15, "start"))
        b.append(line(776, y + 24, 788, y + 24))
        b.append(
            box(792, y + 4, 140, 40, "#fff", [part], 14, 700, TEAL, stroke=TEAL, rx=20)
        )
    b.append(
        text(
            470,
            336,
            "Synthea AU (8,297 patients)   ·   MIMIC-IV demo (100 ICU patients)   ·   CSV extract",
            14,
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 345, b)


def demo_steps():
    """What John shows live: a tour of the workspace."""
    steps = [
        (
            "Find the notebooks",
            "Workspace > Repos > John.Grimes@csiro.au > open-fhir-training > notebooks",
        ),
        (
            "Attach a notebook",
            "synthea/import_synthea > compute menu > Open FHIR Training Cluster",
        ),
        (
            "Run up to resource_types()",
            "cells 2-4: create a PathlingContext, read the NDJSON, list the types",
        ),
        (
            "Browse the data",
            "Catalog > hive_metastore > synthea > patient > Overview and Sample Data",
        ),
        (
            "Open the README",
            "open-fhir-training > README.md: the exercises and learning path",
        ),
    ]
    b = []
    for i, (head, where) in enumerate(steps):
        y = 6 + i * 66
        b.append(rect(10, y, 920, 56, "#fff" if i % 2 else "#F6F8FA", rx=10))
        b.append(callout(i + 1, 40, y + 28, 16))
        b.append(text(72, y + 34, head, 17, "start", 700))
        b.append(text(320, y + 34, where, 14, "start", 400, INK))
    return svg(940, 340, b)


def your_turn():
    """What attendees do in the hands-on time, with the SQL to try."""
    steps = [
        ("Sign in", "from your invitation email"),
        ("Open README.md", "in open-fhir-training"),
        ("Run import_synthea cells 2-4", "attach the cluster first; skip cell 5"),
        ("Browse hive_metastore.synthea", "in Catalog Explorer"),
        ("Run the query on the right", "SQL Editor, Serverless Starter Warehouse"),
    ]
    b = []
    for i, (head, sub) in enumerate(steps):
        y = 6 + i * 64
        b.append(callout(i + 1, 24, y + 22, 15))
        b.append(text(50, y + 20, head, 17, "start", 700))
        b.append(text(50, y + 42, sub, 14, "start", fill=MUTED))
    b.append(
        code(
            470,
            4,
            460,
            [
                "SELECT gender, count(*)",
                "FROM hive_metastore.synthea.patient",
                "GROUP BY gender",
            ],
            "SQL Editor",
            fs=14,
        )
    )
    b.append(text(470, 160, "You should see", 14, "start", fill=MUTED))
    b.append(
        table(
            586,
            140,
            [("gender", 110), ("count(1)", 110)],
            [("female", "4103"), ("male", "4194")],
            CYAN,
            14,
            26,
        )
    )
    b.append(rect(470, 232, 460, 106, YELLOW, rx=10))
    b.append(text(488, 258, "Stretch", 16, "start", 700))
    b.append(
        text(488, 284, "Open synthea.patient > Sample Data and expand", 14, "start")
    )
    b.append(text(488, 305, "meta and name. How do the nested columns", 14, "start"))
    b.append(text(488, 326, "compare with the Patient JSON?", 14, "start"))
    return svg(940, 345, b)


def backup_catalog():
    """Catalog Explorer at hive_metastore > synthea."""
    shot, w, h, pt = screenshot(
        "catalog-synthea", 0, 0, 940, 298, crop=(0, 155, 940, 375)
    )
    b = [shot]
    b.append(mark(pt, 14, 159, 174, 26))
    b.append(mark(pt, 250, 335, 140, 24))
    b.append(mark(pt, 212, 502, 300, 26))
    b.append(mark(pt, 800, 175, 70, 24))
    for i, (px, py) in enumerate([(190, 172), (392, 347), (514, 515), (884, 187)], 1):
        b.append(callout(i, *pt(px, py)))
    b.append(
        legend(
            h + 26,
            [
                "Catalog",
                "hive_metastore",
                "synthea: one table per resource type",
                "15 tables",
            ],
        )
    )
    return svg(940, h + 46, b)


def backup_patient():
    """Sample data from synthea.patient: ids and a JSON-like struct."""
    shot, w, h, pt = screenshot(
        "patient-sample", 0, 0, 640, 330, crop=(530, 170, 900, 420)
    )
    b = [shot]
    b.append(mark(pt, 594, 198, 274, 24))
    b.append(mark(pt, 874, 198, 318, 24))
    b.append(mark(pt, 1198, 198, 222, 24))
    for i, (px, py) in enumerate([(850, 210), (1174, 210), (1400, 210)], 1):
        b.append(callout(i, *pt(px, py)))
    x0 = 672
    notes = [
        ("id", ["the resource's logical id"]),
        ("id_versioned", ["the id qualified by type,", "e.g. Patient/d286c559-..."]),
        ("meta", ["a struct: one row holds", "the whole nested object"]),
    ]
    y = 14
    for i, (head, rows) in enumerate(notes, 1):
        b.append(callout(i, x0 + 14, y + 12))
        b.append(text(x0 + 36, y + 18, head, 16, "start", 700, family=MONO))
        for j, r in enumerate(rows):
            b.append(text(x0 + 36, y + 42 + j * 21, r, 14, "start"))
        y += 52 + len(rows) * 21
    b.append(
        text(
            x0,
            320,
            "Every FHIR element has a column",
            14,
            "start",
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 335, b)


def backup_compute():
    """The shared all-purpose cluster in the Compute page."""
    shot, w, h, pt = screenshot("compute", 0, 0, 940, crop=(205, 60, 1035, 314))
    b = [shot]
    b.append(mark(pt, 294, 130, 146, 26))
    b.append(mark(pt, 284, 332, 230, 28))
    b.append(mark(pt, 716, 332, 244, 28))
    for i, (px, py) in enumerate([(366, 172), (530, 345), (976, 345)], 1):
        b.append(callout(i, *pt(px, py)))
    b.append(
        legend(
            h + 30,
            [
                "All-purpose compute",
                "Open FHIR Training Cluster (running)",
                "Runtime 17.3 · 32 GB · 8 cores",
            ],
        )
    )
    return svg(940, h + 52, b)


DECK = {
    "file": "track-3-d1-1-kickoff",
    "slides": [
        title_slide(
            "Kick-off: the environment and the standards map",
            f"Track 3 kick-off · {EVENT}",
            "Welcome to the Track 3 room. I'm John Grimes from CSIRO's Australian e-Health Research "
            "Centre, and I look after the analytics strand of this track. In this kick-off I'll "
            "get everyone into the Databricks workspace, show you where to find the notebooks and go "
            "through a few ground rules. Then I'll give an overview of the standards we'll keep "
            "coming back to over the two days, and the exercises that go with them.",
        ),
        diagram(
            "What the analytics strand covers",
            "Six topics, each tied to a stage of the standards map",
            "topics",
            topics(),
            "These are the six topics in the analytics strand. After this kick-off we look at using "
            "FHIR alongside legacy and proprietary systems, then at getting data out with Bulk Data "
            "and Pathling. Then SQL on FHIR and terminology, a real-world study of beta-blockers in "
            "septic shock, and the standards that close the loop: CQL, CDS Hooks, SMART and OMOP. "
            "There's no fixed time for each one. We'll go at the pace of the room, and you can pick "
            "up any exercise whenever you like. James, Dion and Duncan run their own strands in this "
            "room as well, so you can move between them.",
        ),
        diagram(
            "How each topic runs",
            "Some context and a demo, then the time is yours",
            "rhythm",
            rhythm(),
            "Each topic has the same shape. Some slides, taken slowly, then a live demonstration in "
            "the workspace. After that the time is yours: work through the exercises, or bring your "
            "own question. James, Dion, Duncan and I will be walking around, so put your hand up "
            "whenever you're stuck. On Friday afternoon there's a show and tell in the main room, so "
            "keep a note of what you try and what you learn.",
        ),
        diagram(
            "Get set up",
            "Scan the code now, then watch for an email from Databricks",
            "get-set-up",
            get_set_up(),
            "If you didn't scan this code in the main room, please do it now. The form asks only for "
            "your email address and explains how we use it: we send you a Databricks invitation, and "
            "we remove your account and delete the form responses by the end of November. Accept the "
            "invitation from the email, set up your sign-in, and you'll land in the Open FHIR "
            "Training Environment. Everything in there is synthetic or de-identified, and that's the "
            "only kind of data that should go in. If you'd rather not have an account, pair with "
            "someone.",
        ),
        diagram(
            "Finding the notebooks",
            "The exercises live in a Git folder that everyone can run but not edit",
            "find-notebooks",
            find_notebooks(),
            "Once you're signed in, this is where to go. Click Workspace in the left-hand menu. In the "
            "workspace browser, open Repos, then my folder, John.Grimes@csiro.au, then "
            "open-fhir-training. That's a Git folder linked to our public GitHub repository, on the "
            "main branch. Inside there are two folders: notebooks, with the Python notebooks, and sql, "
            "with the SQL scripts for the studies. There's also a README that describes each exercise. "
            "Everyone can run these notebooks, but nobody can edit them in place, which keeps them "
            "working for everyone else.",
        ),
        diagram(
            "Attach to the cluster",
            "Notebooks run on the shared cluster; the SQL editor uses a warehouse",
            "attach-cluster",
            attach_cluster(),
            "When you open a notebook, check what it's attached to. The compute menu is at the top "
            "right of the notebook. Pick Open FHIR Training Cluster - that's a single shared machine "
            "with Pathling 10.0.0 installed. Please don't pick Serverless, even though it looks "
            "tempting: Pathling isn't installed there, so the first cell will fail. The SQL editor is "
            "different: it runs on the Serverless Starter Warehouse, which everyone can use, and "
            "that's the right choice for plain SQL queries.",
        ),
        diagram(
            "Ground rules",
            "One shared workspace, many people: four rules keep it working",
            "ground-rules",
            ground_rules(),
            "Four ground rules. First, synthetic and de-identified data only: please don't bring "
            "anything sensitive or identifiable into this environment. Second, the data is already "
            "loaded, so don't run the cells in the import notebooks that write tables. Third, run "
            "notebooks in place, and if you want to change one, use File, then Clone, to copy it "
            "into your home folder. Fourth, write your results to your own schema - something like "
            "jane_citizen - never to the shared schemas. That way nobody overwrites anyone else's "
            "work, or the tables the exercises depend on.",
        ),
        section(
            "The standards map",
            "That's the practical part done. If your invitation hasn't arrived yet, don't worry - "
            "keep listening and we'll sort it out during the hands-on time. Now let's step back from "
            "the workspace and look at the standards that matter for analytics with FHIR data, and "
            "how they fit together. I'll keep this high level for now; each of the later topics "
            "goes into one part of the map in more depth, with an exercise to match.",
        ),
        diagram(
            "The standards map",
            "Four stages from data to decisions, and the standards in each",
            "standards-map",
            standards_map(),
            "I'll come back to this map throughout the track. On the left, getting the data: bulk export from a FHIR "
            "server, authorised with SMART Backend Services, or mapping the extracts you already "
            "have. Next, shaping it into tables you can analyse, with SQL on FHIR views, FHIRPath and "
            "terminology. Then analysis, with whatever tools you prefer, and OMOP if you're part of "
            "a research network. Finally, acting on it: CQL for clinical logic, CDS Hooks and SMART "
            "apps to put results in front of clinicians. Most of the hands-on time is in the middle "
            "two stages, which is where Pathling sits.",
        ),
        diagram(
            "FHIR as data",
            "A resource is a tree; analysis wants tables",
            "fhir-as-data",
            fhir_as_data(),
            "This is why we need a shaping stage. On the left is one Patient from our Synthea data, "
            "abridged. It's a tree: meta is an object, profile is a list inside it, name is a list of "
            "objects with its own list of given names. On the right is the same resource type as a "
            "table in Databricks. Pathling has encoded each element it keeps, so meta becomes a "
            "struct column and profile an array. By default it leaves out extensions and stops "
            "recursive elements at three levels of nesting. Either way, this isn't the shape an "
            "analyst wants. SQL on FHIR views are how we flatten it into plain rows and columns, "
            "which we'll cover in the SQL on FHIR section.",
        ),
        diagram(
            "Six standards at a glance",
            "What each one is and what you'd use it for",
            "six-standards",
            six_standards(),
            "Six standards come up across the track. SQL on FHIR defines views that turn resources "
            "into tables. Bulk Data Access exports a whole population as NDJSON files. SMART App "
            "Launch authorises apps, and its Backend Services profile authorises system-to-system "
            "access such as bulk export. CDS Hooks lets an EHR call a service at a moment in the "
            "workflow and show cards. CQL is a readable language for clinical logic in measures and "
            "decision support. OMOP is a research data model with its own vocabularies. The colours "
            "match the stages on the map.",
        ),
        diagram(
            "The exercises",
            "Five exercises for this track, each tied to a section",
            "exercises",
            exercises_map(),
            "These are the five exercises we'll use in the track. CSV to FHIR maps a flat legacy extract "
            "into FHIR resources, and goes with the section on legacy systems. The two import "
            "notebooks read NDJSON files with Pathling and store them as tables; you'll run part of "
            "the Synthea one shortly. The MI secondary prevention exercise builds SQL on FHIR "
            "views, classifies medicines with a ConceptMap and joins them in SQL, and goes with the "
            "SQL on FHIR section. The septic shock study selects the cohort of a published study of "
            "beta-blockers from de-identified intensive care data, and has a section of its own. "
            "The repository also has two earlier studies, on prostate cancer and pulse oximetry, "
            "and the notebook that builds the AMT terminology store. They aren't part of the "
            "sections, but you're welcome to look at them. You don't need to do the exercises in "
            "order.",
        ),
        diagram(
            "Demo",
            "A tour of the workspace",
            "demo",
            demo_steps(),
            "Live demo. One: click Workspace, then Repos, John.Grimes@csiro.au, open-fhir-training, "
            "and notebooks. Two: open synthea, then import_synthea; open the compute menu at the top "
            "right and choose Open FHIR Training Cluster, pointing out Serverless as the one to avoid. "
            "Three: run cells two to four - the import, PathlingContext.create, and read.ndjson with "
            "resource_types, which lists fifteen types. Say clearly not to run cell five. Four: click "
            "Catalog, expand hive_metastore and synthea, open patient, show Overview then Sample Data. "
            "Five: back to Workspace and open README.md.",
        ),
        diagram(
            "Your turn",
            "Get into the workspace and look around - we'll come to you",
            "your-turn",
            your_turn(),
            "Now it's your turn. Sign in with your invitation, open the README, then run the first "
            "few cells of the Synthea import notebook - up to resource_types, and not the cell that "
            "writes tables. Browse the synthea schema in Catalog Explorer. Then open the SQL Editor, "
            "check it's on the Serverless Starter Warehouse, and run this query: you should get "
            "4,103 female and 4,194 male patients. If you finish early, open the patient table's "
            "sample data and compare the nested columns with the JSON from earlier. Put your hand "
            "up if anything "
            "doesn't work.",
        ),
        section(
            "Demo walkthrough",
            "Backup slides, in case the live demo fails. They walk through the same tour with "
            "annotated screenshots: Catalog Explorer and the synthea schema, the patient table's "
            "sample data, and the shared cluster on the Compute page. They're also useful later if "
            "you get lost in the workspace and want to retrace the steps.",
        ),
        diagram(
            "The data in Catalog Explorer",
            "hive_metastore > synthea holds one table per FHIR resource type",
            "backup-catalog",
            backup_catalog(),
            "Backup slide. "
            "This is Catalog Explorer. Click Catalog in the left-hand menu, then expand "
            "hive_metastore under Legacy. You'll see a schema for each dataset: mimic_iv_demo for the "
            "intensive care data and mimic_iv_beta_blocker_views for the septic shock study's views, "
            "and synthea for the synthetic Queensland "
            "patients. Click synthea and the overview lists fifteen tables, one per FHIR resource "
            "type: allergy intolerances, conditions, encounters, observations and so on. These were "
            "written by the import notebook with Pathling, and they're shared, so treat them as "
            "read-only.",
        ),
        diagram(
            "Inside the patient table",
            "Sample Data shows the encoded resource, one row per Patient",
            "backup-patient",
            backup_patient(),
            "Backup slide. "
            "Click patient, then the Sample Data tab. Each row is one Patient resource. The id column "
            "is the resource's logical id. id_versioned is the same id prefixed with the resource "
            "type, the same shape you see in references. Then meta, which is a struct: Databricks shows "
            "it as JSON because a single cell holds the whole nested object. Scroll right and you'll "
            "find a column for every Patient element - name, gender, birthDate, address and the rest. "
            "That's the encoded form that SQL on FHIR views work from.",
        ),
        diagram(
            "The shared cluster",
            "One all-purpose cluster runs every notebook in the workspace",
            "backup-compute",
            backup_compute(),
            "Backup slide. "
            "If you want to see the cluster itself, click Compute in the left-hand menu and stay on "
            "the All-purpose compute tab. There's one cluster, Open FHIR Training Cluster, and the "
            "green dot means it's running. It's on Databricks Runtime 17.3, with 32 GB of memory and "
            "8 cores, and Pathling 10.0.0 is installed as a library. Everyone shares it, so please "
            "stop long-running jobs you no longer need. You don't need to start or configure it "
            "yourself.",
        ),
        closing(
            "Let's get started",
            PRESENTER,
            "That's the kick-off. Now get signed in, open the README, run the first few cells of "
            "the Synthea import, and try the query in the SQL editor. The access form and the "
            "exercise repository are linked here if you need them again. James, Dion, Duncan and I "
            "are around the room - put your hand up and we'll come to you.",
            LINKS[:2],
        ),
    ],
}
