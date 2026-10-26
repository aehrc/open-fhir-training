"""Day 2, 9:30 block: SQL on FHIR views, Pathling and terminology, with the MI secondary prevention exercise.

Author: John Grimes
"""

from kit import (
    AMBER,
    BLUE,
    CYAN,
    GREY,
    INK,
    LAVENDER,
    MINT,
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
    hcurve,
    highlight,
    line,
    lines,
    pill,
    rect,
    screenshot,
    section,
    svg,
    table,
    text,
    title_slide,
    vcurve,
)

from decks._shared import EVENT, PATHLING_URL, PRESENTER, REPO_URL, SOF_URL


def code_baseline(y, i, fs, lh, head=0):
    """The baseline of row i in a code() card drawn at y."""
    return y + head + 8 + fs + i * fs * lh


def tree_to_table():
    """A nested Patient resource on the left, flat tables on the right."""
    b = [text(150, 18, "FHIR resource (a tree)", 16, weight=700, fill=MUTED)]
    b.append(box(10, 34, 200, 40, LAVENDER, ["Patient p1"], 16, 700))
    nodes = [
        (BLUE, "birthDate", "1958-05-05"),
        (YELLOW, "name[0] official", "John Citizen"),
        (YELLOW, "name[1] usual", "Jack Citizen"),
        (MINT, "address[0] home", "Brisbane 4000"),
        (MINT, "address[1] old", "Townsville 4810"),
    ]
    for i, (fill, label, value) in enumerate(nodes):
        y = 90 + i * 50
        b.append(line(30, y + 20, 56, y + 20, arrow=None))
        b.append(rect(58, y, 232, 40, fill))
        b.append(text(70, y + 17, label, 13, "start", 700))
        b.append(text(70, y + 33, value, 13, "start"))
    b.append(line(30, 74, 30, 310, arrow=None))
    # The view runner in the middle.
    b.append(line(300, 180, 400, 180, TEAL, 2.5))
    b.append(lines(350, 154, ["View-", "Definition"], 14, 700, TEAL))
    # Flat tables on the right.
    b.append(text(420, 18, "patient (one row per patient)", 15, "start", 700, MUTED))
    b.append(
        table(
            420,
            30,
            [("id", 110), ("birth_date", 130), ("family", 130)],
            [("p1", "1958-05-05", "Citizen")],
            LAVENDER,
            14,
            32,
        )
    )
    b.append(
        text(420, 136, "patient_address (one row per address)", 15, "start", 700, MUTED)
    )
    b.append(
        table(
            420,
            148,
            [("id", 110), ("use", 90), ("city", 140), ("postcode", 110)],
            [("p1", "home", "Brisbane", "4000"), ("p1", "old", "Townsville", "4810")],
            MINT,
            14,
            32,
        )
    )
    b.append(rect(420, 268, 515, 66, "#fff", TEAL, 2, 10))
    b.append(
        lines(
            677,
            301,
            [
                "Flattening everything gives 2 names x 2 addresses = 4 rows.",
                "A view chooses the grain: one row per patient, or per address.",
            ],
            14,
        )
    )
    return svg(940, 340, b)


ANATOMY = [
    "{",
    '  "resourceType": "ViewDefinition",',
    '  "resource": "Patient",',
    '  "status": "active",',
    '  "constant": [{"name": "home", "valueCode": "home"}],',
    '  "select": [',
    '    {"column": [',
    '      {"name": "id", "path": "getResourceKey()"},',
    '      {"name": "birth_date", "path": "birthDate"}]},',
    '    {"forEachOrNull": "address.where(use = %home)",',
    '     "column": [{"name": "postcode", "path": "postalCode"}]}',
    "  ],",
    '  "where": [{"path": "gender = \'male\'"}]',
    "}",
]


def anatomy():
    """An annotated ViewDefinition."""
    fs, lh, cy = 13, 1.45, 4
    b = [code(0, cy, 540, ANATOMY, fs=fs, lh=lh)]
    notes = [
        (2, BLUE, "resource", "One FHIR resource type per view"),
        (4, AMBER, "constant", "A value used in paths as %home"),
        (7, LAVENDER, "select / column", "name + FHIRPath path = one column"),
        (9, MINT, "forEach / forEachOrNull", "One row per item (inner / outer join)"),
        (12, PINK, "where", "Keep only resources where the path is true"),
    ]
    for k, (row, fill, title, desc) in enumerate(notes):
        ly = code_baseline(cy, row, fs, lh) - 4
        by = 4 + k * 66
        b.append(hcurve(542, ly, 588, by + 27, lead=4, tail=8, stroke=GREY))
        b.append(rect(590, by, 345, 54, fill, rx=8))
        b.append(text(604, by + 22, title, 15, "start", 700))
        b.append(text(604, by + 43, desc, 14, "start"))
    b.append(
        text(
            470,
            336,
            "Element names from the SQL on FHIR v2 ViewDefinition; paths are FHIRPath",
            14,
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 342, b)


def fhirpath_table():
    """The handful of FHIRPath functions the exercises use."""
    rows = [
        (
            "where()",
            "code.coding.where(system = 'http://snomed.info/sct')",
            "Filter a collection",
        ),
        ("exists()", "coding.where(code.exists())", "True if there is any item"),
        (
            "ofType()",
            "medication.ofType(CodeableConcept).coding",
            "Pick one type of a choice [x]",
        ),
        ("first()", "name.first().family", "Keep only the first item"),
        ("getResourceKey()", "getResourceKey()", "This row's key"),
        (
            "getReferenceKey()",
            "subject.getReferenceKey()",
            "The key a reference points to",
        ),
    ]
    b = [
        table(
            0,
            4,
            [("Function", 158), ("Example", 548), ("What it does", 234)],
            rows,
            LAVENDER,
            13,
            45,
            mono_cols=(0, 1),
        )
    ]
    b.append(
        text(
            470,
            338,
            "All examples except first() come from the MI secondary prevention views in the repo",
            14,
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 345, b)


def keys_join():
    """Two views joined in SQL on the keys they emit."""
    b = [text(0, 16, "patient_view", 15, "start", 700, MUTED)]
    b.append(
        table(
            0,
            26,
            [("id", 210), ("birth_date", 110)],
            [
                ("Patient/da17b438-…", "1955-03-13"),
                ("Patient/3ab94520-…", "1955-01-28"),
            ],
            LAVENDER,
            13,
            30,
            mono_cols=(0,),
        )
    )
    b.append(text(0, 148, "myocardial_infarction_view", 15, "start", 700, MUTED))
    b.append(
        table(
            0,
            158,
            [("patient_id", 210), ("onset", 110), ("code", 80)],
            [
                ("Patient/da17b438-…", "2025-11-30", "22298006"),
                ("Patient/da17b438-…", "2025-11-30", "401303003"),
                ("Patient/3ab94520-…", "2021-04-11", "22298006"),
            ],
            MINT,
            13,
            30,
            mono_cols=(0,),
        )
    )
    # Key labels.
    b.append(pill(240, 0, "getResourceKey()", BLUE, 12))
    b.append(pill(240, 132, "subject.getReferenceKey()", BLUE, 12))
    b.append(path_join())
    sql = [
        "SELECT p.id, p.birth_date,",
        "       m.onset, m.code",
        "FROM patient_view p",
        "JOIN myocardial_infarction_view m",
        "  ON p.id = m.patient_id",
    ]
    b.append(code(470, 26, 340, sql, "SQL, not the view, does the join", 14))
    b.append(rect(470, 200, 465, 112, "#fff", TEAL, 2, 10))
    b.append(
        lines(
            702,
            256,
            [
                "Each view stays simple: one resource type,",
                "one grain, and a key column. Joins, ranking",
                "and aggregation happen in your SQL engine.",
            ],
            15,
        )
    )
    return svg(940, 342, b)


def path_join():
    """Curved connectors from the two key columns to the SQL card."""
    return hcurve(322, 71, 466, 110, stroke=TEAL, sw=2) + hcurve(
        402, 203, 466, 130, stroke=TEAL, sw=2
    )


def layers():
    """The SQL on FHIR system layers, with this exercise traced through them."""
    cols = [
        (
            BLUE,
            "Data layer",
            ["NDJSON files", "FHIR server ($export)", "Delta / Parquet tables"],
        ),
        (
            LAVENDER,
            "View layer",
            [
                "ViewDefinitions",
                "run by a view runner",
                "Pathling, DuckDB, BigQuery, JS, ...",
            ],
        ),
        (MINT, "Analytics layer", ["SQL", "Python / R", "Dashboards, ML"]),
    ]
    b = []
    w, gap = 280, 50
    for i, (fill, title, items) in enumerate(cols):
        x = i * (w + gap)
        b.append(rect(x, 4, w, 222, fill, rx=10))
        b.append(text(x + w / 2, 38, title, 19, weight=700))
        for j, item in enumerate(items):
            b.append(box(x + 14, 58 + j * 54, w - 28, 44, "#fff", [item], 14))
        if i < 2:
            b.append(line(x + w + 4, 115, x + w + gap - 4, 115, sw=2.2))
    b.append(text(0, 262, "In this exercise", 16, "start", 700, TEAL))
    trace = ["synthea Delta tables", "data.view(...) in Pathling", "Databricks SQL"]
    for i, s in enumerate(trace):
        x = i * (w + gap)
        b.append(box(x, 276, w, 44, "#fff", [s], 15, stroke=TEAL, sw=2))
        if i < 2:
            b.append(line(x + w + 4, 298, x + w + gap - 4, 298, TEAL, 2))
    return svg(940, 335, b)


def whats_next():
    """SQL on FHIR 3.0.0-ballot: SQL as FHIR Library resources, terminology in SQL."""
    b = [text(0, 18, "v2 today", 15, "start", 700, MUTED)]
    for j, s in enumerate(["ViewDefinition", "ViewDefinition"]):
        b.append(box(0, 30 + j * 62, 190, 48, LAVENDER, [s], 15, 700))
    b.append(text(240, 18, "Added in 3.0.0-ballot", 15, "start", 700, MUTED))
    b.append(rect(240, 30, 330, 110, AMBER, rx=10))
    b.append(text(256, 56, "SQLView (Library)", 16, "start", 700))
    b.append(text(256, 82, "A reusable, named SQL query that other", 14, "start"))
    b.append(text(256, 102, "queries use as a virtual table", 14, "start"))
    b.append(rect(240, 162, 330, 130, PEACH, rx=10))
    b.append(text(256, 188, "SQLQuery (Library)", 16, "start", 700))
    b.append(text(256, 214, "Shareable, parameterised SQL over views,", 14, "start"))
    b.append(text(256, 234, "with dialect-specific variants and", 14, "start"))
    b.append(text(256, 254, "declared dependencies", 14, "start"))
    b.append(hcurve(192, 54, 238, 85, stroke=GREY))
    b.append(hcurve(192, 116, 238, 210, stroke=GREY))
    b.append(vcurve(405, 142, 405, 160, lead=2, tail=8))
    b.append(rect(620, 30, 315, 110, CYAN, rx=10))
    b.append(text(636, 56, "Terminology in SQL", 16, "start", 700))
    b.append(text(636, 82, "A query declares a ValueSet or ConceptMap;", 13, "start"))
    b.append(text(636, 102, "the runner exposes its members or", 13, "start"))
    b.append(text(636, 122, "mappings as a table to join to", 13, "start"))
    b.append(hcurve(618, 85, 572, 220, stroke=GREY))
    b.append(rect(620, 162, 315, 130, "#fff", rx=10))
    b.append(text(636, 188, "Operations", 16, "start", 700))
    b.append(text(636, 214, "$sql-run: run one view or query", 14, "start"))
    b.append(text(636, 236, "$sql-export: asynchronous export to", 14, "start"))
    b.append(text(636, 256, "CSV, NDJSON or Parquet", 14, "start"))
    b.append(
        text(
            470,
            326,
            "STU 3 ballot (2026): draft content that may change before publication",
            14,
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 335, b)


def views_and_map():
    """The three Pathling views and the ConceptMap table feeding the combine SQL."""
    inputs = [
        (LAVENDER, "patient_view", "Patient: id, gender, birth_date, deceased"),
        (
            PINK,
            "myocardial_infarction_view",
            "Condition: SNOMED CT 22298006, 401303003, 401314000",
        ),
        (
            YELLOW,
            "medication_request_view",
            "MedicationRequest: AMT code, authored_on, status",
        ),
        (CYAN, "product_to_class", "ConceptMap: AMT product to class, 925,540 rows"),
    ]
    b = []
    for i, (fill, name, desc) in enumerate(inputs):
        y = 4 + i * 82
        b.append(rect(0, y, 430, 68, fill, rx=8))
        b.append(text(16, y + 28, name, 15, "start", 700))
        b.append(text(16, y + 52, desc, 14, "start"))
        b.append(hcurve(432, y + 34, 516, 168, stroke=GREY))
    b.append(rect(518, 98, 190, 140, "#F7F7F7", rx=10))
    b.append(
        lines(
            613,
            168,
            [
                "combine_mi_secondary_",
                "prevention_views.sql",
                "",
                "map join, then days",
                "to first prescription",
            ],
            14,
        )
    )
    b.append(line(710, 168, 744, 168, sw=2))
    b.append(rect(746, 88, 190, 160, MINT, TEAL, 2, rx=10))
    b.append(
        lines(
            841,
            168,
            [
                "mi_secondary_",
                "prevention",
                "",
                "274 rows, one per",
                "patient with an MI",
            ],
            14,
        )
    )
    b.append(
        text(
            690,
            290,
            "Views and map: create_mi_secondary_prevention_views",
            14,
            fill=MUTED,
        )
    )
    b.append(text(690, 312, "notebook (Pathling, Python)", 14, fill=MUTED))
    return svg(940, 335, b)


MEDICATION = [
    "medication_requests = data.view(",
    '    "MedicationRequest",',
    "    select=[{",
    '        "column": [',
    '            {"path": "getResourceKey()", "name": "id"},',
    '            {"path": "subject.getReferenceKey()", "name": "patient_id"},',
    '            {"path": "authoredOn", "name": "authored_on"},',
    '            {"path": "status", "name": "status"},',
    "        ],",
    '        "select": [{',
    '            "forEach": "medication.ofType(CodeableConcept).coding"',
    "                \".where(system = 'http://snomed.info/sct'\"",
    '                " and code.exists())",',
    '            "column": [{"path": "code", "name": "code"},',
    '                       {"path": "display", "name": "display"}],',
    "        }],",
    "    }],",
    ")",
]


def medication_card():
    """The medication request view from the notebook, abridged, with callouts."""
    fs, lh = 12, 1.32
    b = [code(0, 2, 600, MEDICATION, fs=fs, lh=lh)]
    marks = [
        (4, 5, "Keys for joining", "getResourceKey() and getReferenceKey()"),
        (10, 12, "Unnest with forEach", "SNOMED CT codings that have a code"),
        (13, 14, "AMT code and display", "Joined to the ConceptMap in SQL"),
    ]
    for n, (r0, r1, title, desc) in enumerate(marks, 1):
        y0 = code_baseline(2, r0, fs, lh) - 12
        y1 = code_baseline(2, r1, fs, lh) + 3
        b.append(rect(6, y0, 588, y1 - y0, "none", TEAL, 2, 4))
        cy = (y0 + y1) / 2
        b.append(line(596, cy, 640, cy, TEAL, 2, arrow=None))
        b.append(callout(n, 656, cy))
        b.append(text(680, cy - 4, title, 15, "start", 700))
        b.append(text(680, cy + 16, desc, 13, "start", fill=MUTED))
    b.append(text(650, 16, "Last step, save it as a table:", 14, "start", 700))
    b.append(
        text(
            650,
            36,
            "medication_requests.write.saveAsTable(",
            12,
            "start",
            family="JetBrains Mono",
        )
    )
    b.append(
        text(
            650,
            52,
            '  "...medication_request_view")',
            12,
            "start",
            family="JetBrains Mono",
        )
    )
    return svg(940, 340, b)


def days_to_first():
    """Days from the first MI to the first prescription of each class, for one real patient."""
    b = []
    x0, x1 = 190, 920
    d0, d1 = -120, 400

    def tx(day):
        return x0 + (day - d0) / (d1 - d0) * (x1 - x0)

    b.append(text(x0 - 12, 168, "days:", 12, "end", fill=MUTED))
    for d in (-90, 0, 90, 180, 270, 360):
        b.append(text(tx(d), 168, str(d), 12, fill=MUTED))
    b.append(line(tx(0), 16, tx(0), 150, RED, 2.5, arrow=None))
    b.append(text(tx(0) - 6, 14, "first MI", 12, "end", 700, RED))
    for day, label in ((30, "30 days"), (365, "365 days")):
        b.append(line(tx(day), 16, tx(day), 150, TEAL, 1.6, "5 4", None))
        b.append(text(tx(day) + 6, 14, label, 12, "start", 700, TEAL))
    lanes = [
        ("Antiplatelet", [(0, True)]),
        ("Statin", [(0, True)]),
        ("Beta-blocker", [(0, True)]),
        ("ACE inhibitor or ARB", [(-84, False), (287, True)]),
    ]
    for i, (label, points) in enumerate(lanes):
        y = 36 + i * 32
        b.append(text(0, y + 5, label, 14, "start", 700))
        b.append(line(x0, y, x1, y, "#C8C8C8", 2, arrow=None))
        for day, kept in points:
            b.append(
                circle(
                    tx(day), y, 8, MINT if kept else "#fff", TEAL if kept else GREY, 2
                )
            )
            if kept:
                # Labels sit left of the dot on day 0, clear of the 30 day line.
                dx, anchor = (-14, "end") if day < 30 else (14, "start")
                b.append(text(tx(day) + dx, y - 8, f"day {day}", 12, anchor, 700, INK))
            else:
                b.append(text(tx(day), y - 12, "ignored", 12, fill=MUTED))
    sql = [
        "SELECT i.patient_id, c.drug_class,",
        "       MIN(DATEDIFF(c.authored_date,",
        "                    i.index_date)) AS days",
        "FROM index_mi i JOIN classified_request c",
        "  ON c.patient_id = i.patient_id",
        " AND c.authored_date >= i.index_date",
    ]
    b.append(code(0, 186, 440, sql, "First prescription on or after the MI", 12, 1.3))
    steps = [
        (BLUE, "Join requests to the map"),
        (BLUE, "Keep those on or after the MI"),
        (MINT, "Earliest per class, in days"),
    ]
    for i, (fill, s) in enumerate(steps):
        y = 186 + i * 48
        b.append(box(470, y, 260, 36, fill, [s], 14))
        if i < 2:
            b.append(line(600, y + 37, 600, y + 46, sw=1.6))
    b.append(rect(760, 186, 175, 130, "#fff", TEAL, 2, 10))
    b.append(
        lines(
            847,
            251,
            ["Within 30 days:", "3 of 4 classes", "", "Within 365 days:", "all 4"],
            14,
        )
    )
    return svg(940, 335, b)


def results_chart():
    """The notebook's comparison with Halvorsen et al. 2016, with the headline numbers."""
    shot, _, _, _ = screenshot("mi-treated-vs-halvorsen", 0, 2, 760, 338)
    b = [shot]
    b.append(
        lines(
            865,
            170,
            [
                "274 patients",
                "with an MI",
                "",
                "64 (23%) were",
                "prescribed",
                "all four",
                "",
                "Not like for like:",
                "365 days, not",
                "discharge",
            ],
            14,
        )
    )
    return svg(940, 342, b)


def concept_map():
    """AMT products related to drug classes by the ConceptMap, joined in SQL."""
    b = [text(0, 16, "product_to_class (selected rows)", 15, "start", 700, MUTED)]
    aspirin = "Aspirin 325 mg + codeine … tablet"
    b.append(
        table(
            0,
            26,
            [
                ("source_display", 290),
                ("target_code", 110),
                ("target_display", 270),
                ("relationship", 115),
            ],
            [
                ("Atenolol 100 mg tablet", "373254001", "Beta blocker", "related-to"),
                (
                    "Atenolol 100 mg tablet",
                    "372586001",
                    "Antihypertensive agent",
                    "related-to",
                ),
                (aspirin, "771452004", "Platelet aggregation inhibitor", "related-to"),
                (aspirin, "404642006", "Opioid receptor agonist", "related-to"),
            ],
            CYAN,
            13,
            28,
            mono_cols=(1,),
        )
    )
    b.append(highlight(2, 56, 781, 24))
    b.append(highlight(2, 112, 781, 24))
    b.append(rect(2, 140, 781, 24, "none", RED, 2.5, 6))
    b.append(
        lines(
            862,
            108,
            [
                "Also an opioid.",
                "Without these",
                "products,",
                "265 patients on",
                "an antiplatelet",
                "become 245",
            ],
            13,
        )
    )
    python = [
        "pc = PathlingContext.create(",
        '    terminology_mode="local",',
        "    terminology_storage_path=TERMINOLOGY_STORE)",
        "product_to_class = pc.concept_map(",
        "    PRODUCT_TO_CLASS, max_mappings=1_000_000)",
    ]
    b.append(code(0, 184, 440, python, "Python: the map as a data frame", 12.5, 1.4))
    sql = [
        "JOIN product_to_class m",
        "  ON m.source_code = r.code",
        " AND m.relationship = 'related-to'",
        "JOIN drug_class d",
        "  ON d.class_code = m.target_code",
    ]
    b.append(code(470, 184, 465, sql, "SQL: join to it like any table", 12.5, 1.4))
    b.append(
        text(
            470,
            340,
            "Read from a local terminology store on S3, built once by "
            "notebooks/terminology/import_amt_classification",
            13,
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 345, b)


def demo():
    """What I show live."""
    steps = [
        ["Open notebooks/synthea/create_mi_secondary_prevention_views"],
        ["Attach to Open FHIR Training Cluster (not Serverless)"],
        ["Walk through the medication view: keys, ofType, forEach"],
        ["Run the setup cells, then the medication view and show"],
        ["Show concept_map() and product_to_class.show(5)"],
        ["SQL editor: summary query with follow_up_days = 365"],
    ]
    b = [steps_panel(steps, 0, 4, 600, 15, 54)]
    b.append(rect(630, 4, 305, 314, "#F7F7F7", rx=10))
    b.append(text(648, 34, "What to look for", 16, "start", 700))
    look = [
        ["The view returns a Spark data frame"],
        ["id and patient_id hold keys like", "MedicationRequest/... and Patient/..."],
        ["229,058 coded requests;", "925,540 mappings in the map"],
        ["Summary: 274 patients, 64 of", "them on all four classes"],
    ]
    y = 72
    for rows in look:
        b.append(text(648, y, "· " + rows[0], 14, "start"))
        for extra in rows[1:]:
            y += 22
            b.append(text(660, y, extra, 14, "start"))
        y += 46
    return svg(940, 330, b)


def your_turn():
    """What attendees do for the rest of the block."""
    steps = [
        ["File > Clone the notebook to your home folder"],
        ["Set VIEWS_SCHEMA to your own schema, e.g. jane_citizen"],
        ["Write an LDL cholesterol view (LOINC 18262-6) and save it"],
        ["SQL editor: LDL before the MI vs after the first statin"],
    ]
    b = [steps_panel(steps, 0, 4, 560, 14, 56)]
    hint = [
        "code.coding.exists(",
        "  system = 'http://loinc.org'",
        "  and code = '18262-6')",
        "",
        "value.ofType(Quantity).value",
    ]
    b.append(code(590, 4, 345, hint, "Hint: the where and value paths", 13, 1.4))
    b.append(
        text(
            590,
            190,
            "25,302 readings in mg/dL, 4,215 patients",
            13,
            "start",
            fill=MUTED,
        )
    )
    b.append(rect(0, 238, 935, 92, PEACH, rx=10))
    b.append(text(18, 266, "Stretch", 16, "start", 700))
    b.append(
        text(
            18,
            292,
            "Set follow_up_days to 30: how do the figures compare with Halvorsen's at discharge?",
            14,
            "start",
        )
    )
    b.append(
        text(
            18,
            316,
            "Leave out products the map also relates to 404642006 |Opioid receptor agonist|: "
            "expect 245, not 265",
            14,
            "start",
        )
    )
    return svg(940, 335, b)


def backup_results():
    """The summary query, its parameter and its five rows, annotated."""
    q, _, qh, _ = screenshot("sql-mi-results", 0, 0, 600, crop=(243, 92, 760, 130))
    r, _, _, rp = screenshot(
        "sql-mi-results", 0, qh + 12, 600, crop=(243, 478, 700, 258)
    )
    b = [q, r]
    b.append(callout(1, 20, 36))
    (x0, y0), (x1, y1) = rp(270, 499), rp(435, 533)
    b.append(highlight(x0, y0, x1 - x0, y1 - y0))
    # Right of the Add parameter button, level with the box.
    b.append(callout(2, rp(600, 516)[0], (y0 + y1) / 2))
    (x0, y0), (x1, y1) = rp(548, 605), rp(662, 731)
    b.append(highlight(x0, y0, x1 - x0, y1 - y0))
    b.append(callout(3, x1 + 18, y0 + 12))
    notes = [
        ("The summary query from", "the SQL file, reading the", "shared schema"),
        ("follow_up_days: 365", "(left empty, every count", "is zero)"),
        ("Patients treated within", "the window; 64 had", "all four"),
    ]
    for i, rows in enumerate(notes):
        ty = 20 + i * 100
        b.append(callout(i + 1, 648, ty + 10))
        for j, s in enumerate(rows):
            b.append(text(672, ty + 15 + j * 20, s, 14, "start"))
    return svg(940, 340, b)


def steps_panel(steps, x, y, w, fs=15, gap=50, fill=YELLOW):
    """Numbered step boxes stacked vertically."""
    out = []
    for i, rows in enumerate(steps):
        yy = y + i * gap
        out.append(rect(x, yy, w, gap - 10, fill, rx=8))
        out.append(callout(i + 1, x + 22, yy + (gap - 10) / 2, 13))
        out.append(lines(x + 46, yy + (gap - 10) / 2, rows, fs, anchor="start"))
    return "".join(out)


def backup_clone():
    """Cloning a notebook before changing it."""
    s, w, h, p = screenshot("file-menu-clone", 0, 0, 480, 335, crop=(243, 95, 560, 500))
    b = [s]
    k = w / 560
    b.append(highlight(*p(254, 126), 46 * k, 28 * k))
    x, y = p(300, 112)
    b.append(callout(1, x + 8, y))
    b.append(highlight(*p(256, 416), 280 * k, 28 * k))
    x, y = p(536, 430)
    b.append(callout(2, x + 22, y))
    steps = [
        ["Open the notebook, then the File menu"],
        ["Clone... to your home folder"],
        ["Attach the clone to", "Open FHIR Training Cluster"],
        ["Set VIEWS_SCHEMA to your", "own schema, e.g. jane_citizen"],
    ]
    b.append(steps_panel(steps, 510, 4, 425, 15, 80, BLUE))
    return svg(940, 335, b)


def backup_show():
    """What the medication request view looks like as a table."""
    query = [
        "SELECT patient_id, authored_on, status, code, display",
        "FROM synthea_mi_secondary_prevention_views.medication_request_view",
        "WHERE patient_id = 'Patient/da17b438-…' AND authored_on >= '2025-11-30'",
    ]
    b = [code(0, 4, 935, query, "SQL editor", 13)]
    patient = "Patient/da17b438-…"
    rows = [
        (
            patient,
            "2025-11-30T01:52:00+10:00",
            "completed",
            "61930011000036108",
            "Aspirin 325 mg + codeine…",
        ),
        (
            patient,
            "2025-11-30T03:13:25+10:00",
            "completed",
            "32641000036100",
            "Ticagrelor 90 mg tablet",
        ),
        (
            patient,
            "2025-11-30T03:43:25+10:00",
            "active",
            "1031691000168105",
            "Atenolol 100 mg tablet",
        ),
        (
            patient,
            "2025-11-30T03:43:25+10:00",
            "active",
            "22783011000036107",
            "Atorvastatin 10 mg tablet",
        ),
        (
            patient,
            "2026-09-13T01:43:58+10:00",
            "active",
            "23488011000036103",
            "Lisinopril 10 mg tablet",
        ),
    ]
    b.append(
        table(
            0,
            114,
            [
                ("patient_id", 175),
                ("authored_on", 235),
                ("status", 100),
                ("code", 175),
                ("display", 250),
            ],
            rows,
            YELLOW,
            13,
            30,
            mono_cols=(0, 1, 3),
        )
    )
    b.append(
        text(
            0,
            316,
            "5 of the 12 rows returned: the patient from the timeline slide. IDs truncated here.",
            14,
            "start",
            fill=MUTED,
            italic=True,
        )
    )
    b.append(
        text(
            0,
            338,
            "229,058 rows in all: every MedicationRequest with an AMT code.",
            14,
            "start",
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 345, b)


DECK = {
    "file": "track-3-d2-4-sql-on-fhir",
    "slides": [
        title_slide(
            "SQL on FHIR, Pathling views and terminology",
            f"Friday 9:30 · {EVENT}",
            "Good morning. This block is about the middle of the analytics pipeline: turning FHIR "
            "resources into tables you can analyse. I'll cover SQL on FHIR ViewDefinitions, the "
            "small amount of FHIRPath you need to write them, and how terminology lets you "
            "classify the codes in a view without writing them all into a query. Then we'll work "
            "through the secondary prevention after myocardial infarction exercise in the "
            "workspace. I'll talk for about twenty minutes, show you the notebook and the SQL live, "
            "and then the rest of the block is yours.",
        ),
        diagram(
            "From trees to tables",
            "FHIR resources are nested and repeating; most analytic tools expect flat tables",
            "tree-to-table",
            tree_to_table(),
            "Here is the problem we're solving. A FHIR Patient is a tree: this patient has two "
            "names and two addresses, and each of those has its own structure. Analysts, "
            "statisticians and dashboard tools want flat tables with one value per cell. If you "
            "flatten everything naively you get two names times two addresses, so four rows for "
            "one patient, and every count you do afterwards is wrong. The answer is to decide the "
            "grain of each table up front: one row per patient here, one row per address there. "
            "That decision is exactly what a ViewDefinition records.",
        ),
        diagram(
            "Anatomy of a ViewDefinition",
            "A FHIR logical model: one resource type in, one table out",
            "anatomy",
            anatomy(),
            "This is a complete ViewDefinition. It names one resource type, Patient. The select "
            "holds columns, and every column is a name plus a FHIRPath expression. forEach and "
            "forEachOrNull unroll a repeating element into one row per item - forEach behaves "
            "like an inner join, forEachOrNull like a left outer join, so patients without a home "
            "address still get a row. A constant is a value you can reuse in paths as percent "
            "home. And where filters the resources that make it into the view at all - here, male "
            "patients only. Because it is JSON, you can version it, share it and run it on "
            "different engines.",
        ),
        diagram(
            "The FHIRPath you need",
            "A handful of functions covers most views",
            "fhirpath",
            fhirpath_table(),
            "You don't need all of FHIRPath to write useful views. where filters a collection, "
            "for example to the SNOMED CT codings of a condition. exists tests whether anything "
            "is there, which is how the medication view leaves out codings that have no code. "
            "ofType picks one type out of a choice element like medication or onset. first takes "
            "the first item when you only want one. And the two key functions, getResourceKey and "
            "getReferenceKey, come from the SQL on FHIR spec itself: they give you the keys you "
            "need to join views later. Every example here except first comes from the views we "
            "will run today.",
        ),
        diagram(
            "Views don't join - they emit keys",
            "Each view carries a key; SQL joins them on id = patient_id",
            "keys-join",
            keys_join(),
            "A ViewDefinition only ever looks at one resource type, so it can't join. Instead, "
            "each view emits keys. The patient view has getResourceKey as its id. The myocardial "
            "infarction view has subject dot getReferenceKey as its patient_id, which returns the "
            "same value for the same patient. Then plain SQL does the join. These are real rows "
            "from the workspace. One patient has a single MI. The other has two Conditions on the "
            "same day, a general MI and a STEMI recorded minutes apart, which is why the SQL later "
            "takes each patient's first. Keeping views simple and pushing joins, ranking and "
            "aggregation into SQL is a deliberate design choice. It keeps views portable and lets "
            "each engine do what it is good at.",
        ),
        diagram(
            "Three layers",
            "The SQL on FHIR spec separates data, views and analytics",
            "layers",
            layers(),
            "The spec describes three layers. At the bottom is the data, in whatever form you "
            "have it: NDJSON files from a bulk export, a FHIR server, or tables in a lakehouse. In "
            "the middle is the view layer: ViewDefinitions, executed by a view runner. Pathling is "
            "one runner, on Spark; there are others on DuckDB, BigQuery, JavaScript and more. On "
            "top is analytics, in whatever tool you prefer. The point is that the middle layer is "
            "portable. In today's exercise the data is Delta tables in Databricks, Pathling runs "
            "the views, and Databricks SQL does the analysis.",
        ),
        diagram(
            "What's next in the spec",
            "SQL on FHIR 3.0.0-ballot: SQL as FHIR resources, and terminology in SQL",
            "whats-next",
            whats_next(),
            "SQL on FHIR version 3 is out for ballot. Today a ViewDefinition gets you to tables, "
            "but the SQL that joins them lives in files like the one we'll use this morning. The "
            "ballot adds two profiles on the FHIR Library resource: SQLView, a named query other "
            "queries can use as a table, and SQLQuery, a shareable, parameterised query that "
            "declares the views it depends on. It also adds terminology in SQL: a query can "
            "declare a ValueSet or ConceptMap and join to it as a table. Pathling 10 already does "
            "this, and this morning's exercise uses it. And there are standard operations to run "
            "and export. This is ballot content, so details may change.",
        ),
        section(
            "Exercise: secondary prevention after myocardial infarction",
            "Let's put this into practice. After a heart attack, guidelines recommend four classes "
            "of medicine: an antiplatelet, a statin, a beta-blocker, and an ACE inhibitor or ARB. "
            "A Norwegian registry study by Halvorsen and colleagues found 91, 90, 82 and 60 per "
            "cent of patients discharged on each. The exercise asks the same question of the "
            "Synthea data. It isn't a serious study - the data is synthetic - but it uses every "
            "idea we've just covered: views with keys, SNOMED CT and AMT codes, terminology in SQL "
            "with a ConceptMap, and SQL that works across time. The notebook and SQL file are both "
            "in the repository folder in the workspace.",
        ),
        diagram(
            "Three views and a map, one query",
            "Pathling views and a ConceptMap table in a notebook, then one SQL file joins them",
            "views-and-map",
            views_and_map(),
            "The notebook defines three views with Pathling. Patients, with gender, birth date and "
            "date of death. Myocardial infarctions: a Condition view for three SNOMED CT codes - "
            "MI, STEMI and NSTEMI. And medication requests, with the AMT code of each medicine. "
            "The fourth input isn't a view: it's the AMT product to classification ConceptMap, "
            "which Pathling presents as a table of 925,540 mappings. Each is saved as a table in "
            "the synthea_mi_secondary_prevention_views schema. Then one SQL file joins them into a "
            "view with one row per patient who had an MI: 274 rows, with the number of days to "
            "the first prescription of each class.",
        ),
        diagram(
            "The medication request view in Pathling",
            "data.view() takes a ViewDefinition as Python and returns a Spark data frame",
            "medication-code",
            medication_card(),
            "Here is the medication request view from the notebook, with the descriptions removed "
            "so it fits. data.view takes the resource type and a select - the same elements as the "
            "JSON, written as Python dictionaries. First, the keys: getResourceKey for the request "
            "and getReferenceKey for the patient. Second, the forEach. medication is a choice "
            "element, so ofType picks the CodeableConcept, and the where keeps SNOMED CT codings "
            "that have a code - AMT uses the SNOMED CT system. Some requests in the data have a "
            "display but no code; they can't be classified, so they're left out. Third, the code "
            "and display columns, which the SQL joins to the ConceptMap. The result is a Spark "
            "data frame, so the last step is saveAsTable.",
        ),
        diagram(
            "Classify medicines with a ConceptMap",
            "Terminology in SQL: the map is a table you join to",
            "concept-map",
            concept_map(),
            "Here's the terminology part. The ConceptMap relates each AMT product to the classes "
            "of substance it contains, using SNOMED CT concepts as the classes. Atenolol 100 "
            "milligram is related to beta blocker, and to broader classes like antihypertensive "
            "agent. In Python, concept_map returns the map as a table with the columns that the "
            "SQL on FHIR specification defines. It's read from a local terminology store on S3, so "
            "no terminology server is involved. In SQL, it's a join like any other, to a short list "
            "of the class codes we care about. One thing to watch: aspirin with codeine is related "
            "to platelet aggregation inhibitor, because it contains aspirin, as well as to opioid "
            "receptor agonist. The exercise uses the map as it stands, so it counts as an "
            "antiplatelet. Leave out products the map also relates to opioids, and the number of "
            "patients on an antiplatelet within a year falls from 265 to 245. James's sessions "
            "cover the terminology fundamentals.",
        ),
        diagram(
            "Days to the first prescription",
            "Temporal logic lives in SQL: the window is applied afterwards, as a parameter",
            "days-to-first",
            days_to_first(),
            "Each patient's index date is their first MI. This is a real patient from the "
            "workspace. On the day of the MI they were prescribed an antiplatelet, a statin and a "
            "beta-blocker, so those are day zero. They'd had lisinopril, an ACE inhibitor, 84 days "
            "before the MI; that one doesn't count, because only prescriptions on or after the MI "
            "do. The next lisinopril was at day 287. So with a 30 day window this patient has "
            "three of the four classes, and with 365 days, all four. The view keeps the number of "
            "days rather than a yes or no, so the summary query can apply any window as a "
            "parameter.",
        ),
        diagram(
            "What the exercise finds",
            "Synthea AU within 365 days of the first MI, against Halvorsen et al. 2016 at discharge",
            "results",
            results_chart(),
            "This is the main chart from the notebook. The coloured bars are the share of our 274 "
            "synthetic patients prescribed each class within 365 days of their first MI; the grey "
            "bars are Halvorsen's figures at discharge. Antiplatelets, statins and beta-blockers "
            "are at or above the registry figures. ACE inhibitors and ARBs are well below, at 28 "
            "per cent. 64 patients, 23 per cent, had all four. It isn't a like for like "
            "comparison: a year of follow-up rather than discharge, and 16 of the patients died "
            "within the year. The notebook has more charts: time to treatment, combinations and "
            "age groups.",
        ),
        diagram(
            "Demo",
            "Views in the notebook, then the summary in the SQL editor",
            "demo",
            demo(),
            "Live demo. One: in Workspace, Repos, open-fhir-training, open notebooks, synthea, "
            "create_mi_secondary_prevention_views. Two: check the compute dropdown shows Open FHIR "
            "Training Cluster, not Serverless. Three: scroll to the medication request view and "
            "point out the keys, ofType and the forEach. Four: run the setup and read cells, then "
            "the medication view cell and its show cell - don't run saveAsTable. Five: run the "
            "concept_map cell and show the first rows of the map. Six: open "
            "sql/synthea/combine_mi_secondary_prevention_views.sql and walk through the CTEs, then "
            "in the SQL editor on the Serverless Starter Warehouse run the summary query with "
            "follow_up_days set to 365 - five rows.",
        ),
        diagram(
            "Your turn",
            "Add a view of your own, in your own schema",
            "your-turn",
            your_turn(),
            "Now it's over to you. Clone the notebook into your home folder - you can't edit the "
            "shared copy - and set VIEWS_SCHEMA to your own schema. Write a new view: LDL "
            "cholesterol, LOINC 18262-6, is a good one, because statins are meant to lower it. It "
            "has the same shape as any Observation with a Quantity value; there are 25,302 "
            "readings for 4,215 patients. Save it to your schema, then in the SQL editor join it to "
            "the shared mi_secondary_prevention view, and compare each patient's LDL before their "
            "MI with their LDL after their first statin. In the clone, run only the setup cells "
            "and your own: the Combine section reads the SQL file from the repository folder, so "
            "it won't find it from your home folder. If you finish, try the stretch tasks. We're "
            "all here to help.",
        ),
        section(
            "Demo walkthrough",
            "Backup slides, for when the live demo fails. "
            "These slides are a fallback in case the live demo doesn't work - for example if the "
            "network or the cluster is slow. They show the same steps as screenshots and real "
            "output from the workspace, so you can follow along and still do the exercise "
            "afterwards. If the demo did work, I'll skip straight past them to questions, and you "
            "can come back to them later in the slides we share after the connectathon.",
        ),
        diagram(
            "The summary query",
            "SQL editor on the Serverless Starter Warehouse",
            "backup-results",
            backup_results(),
            "This is the final step of the demo: the summary query from the SQL file, pasted into "
            "the SQL editor. One, the query reads the combined view in the shared schema. Its "
            "parameter, follow_up_days, appears as a box under the editor. Two, set it to 365 - if "
            "you leave it empty, every count is zero. Three, five rows: within a year, 265 "
            "patients had an antiplatelet, 252 a statin, 239 a beta-blocker and 78 an ACE "
            "inhibitor or ARB, and 64 had all four.",
        ),
        diagram(
            "Clone before you change",
            "The repository notebooks are read-only for attendees",
            "backup-clone",
            backup_clone(),
            "Before you change anything, clone the notebook. One, open it and click the File "
            "menu at the top left. Two, choose Clone and pick your home folder. Three, make sure "
            "your clone is attached to the Open FHIR Training Cluster, because Pathling isn't "
            "installed on Serverless. Four, set VIEWS_SCHEMA in the first code cell to your own "
            "schema, such as your name, rather than the shared synthea_mi_secondary_prevention_views "
            "schema. The setup cell creates it for you.",
        ),
        diagram(
            "What the medication request view returns",
            "One row per coded medication request, with keys for joining",
            "backup-show",
            backup_show(),
            "If the cluster isn't cooperating, this is what the medication request view gives you. "
            "These rows are for the patient on the timeline slide, from the saved table. "
            "patient_id is the patient key, in the form type slash id, ready to join. The code is "
            "the AMT code, which is what the SQL looks up in the ConceptMap. Notice the first row: "
            "aspirin with codeine, on the day of the MI. The status column shows that some "
            "requests were completed and others are still active. Across the dataset there are "
            "229,058 rows, one for every MedicationRequest with an AMT code.",
        ),
        closing(
            "Questions?",
            PRESENTER,
            "That's the context for this block. The SQL on FHIR spec and the Pathling "
            "documentation are linked here, along with the exercises repository, so scan whichever "
            "you need. I'm happy to take a couple of questions now, and the rest as we go. Ask me, "
            "James, Dion or Duncan if you get stuck - we'll be walking around the room. And keep "
            "notes on what you try, because this afternoon's show and tell is a good place to share it.",
            [
                (REPO_URL, "Exercises"),
                (SOF_URL, "sql-on-fhir.org"),
                (PATHLING_URL, "pathling.csiro.au"),
            ],
        ),
    ],
}
