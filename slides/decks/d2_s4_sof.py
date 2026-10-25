"""Day 2, 9:30 block: SQL on FHIR views, Pathling and terminology, with the prostate cancer exercise.

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
            "code.coding.where(system = 'http://snomed.info/sct').code",
            "Filter a collection",
        ),
        (
            "exists()",
            "code.coding.exists(system = 'http://loinc.org' and code = '2093-3')",
            "True if any item matches",
        ),
        (
            "ofType()",
            "value.ofType(Quantity).where(code = 'mg/dL').value > 240",
            "Pick one type of a value[x]",
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
            "All examples except first() come from the prostate cancer views in the repo",
            14,
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 345, b)


def keys_join():
    """Two views joined in SQL on the keys they emit."""
    b = [text(0, 16, "patient_demographics_view", 15, "start", 700, MUTED)]
    b.append(
        table(
            0,
            26,
            [("id", 210), ("birth_date", 110)],
            [
                ("Patient/6a793f8f-…", "1958-05-05"),
                ("Patient/2220fdc9-…", "1919-02-25"),
            ],
            LAVENDER,
            13,
            30,
            mono_cols=(0,),
        )
    )
    b.append(text(0, 148, "bmi_view", 15, "start", 700, MUTED))
    b.append(
        table(
            0,
            158,
            [("patient_id", 210), ("date", 120), ("value", 70)],
            [
                ("Patient/6a793f8f-…", "2019-12-16", "30.47"),
                ("Patient/2220fdc9-…", "2001-02-06", "30.06"),
                ("Patient/2220fdc9-…", "2000-05-09", "30.06"),
                ("Patient/2220fdc9-…", "1999-06-15", "30.05"),
            ],
            MINT,
            13,
            30,
            mono_cols=(0,),
        )
    )
    # Key labels.
    b.append(pill(222, 0, "getResourceKey()", BLUE, 12))
    b.append(pill(222, 132, "subject.getReferenceKey()", BLUE, 12))
    b.append(path_join())
    sql = [
        "SELECT p.id, p.birth_date,",
        "       b.date, b.value",
        "FROM patient_demographics_view p",
        "LEFT JOIN bmi_view b",
        "  ON p.id = b.patient_id",
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


def four_views():
    """The four Pathling views feeding the combine SQL."""
    views = [
        (
            LAVENDER,
            "patient_demographics_view",
            "Patient: id, birth_date, postal_code, deceased",
        ),
        (YELLOW, "hyperlipidemia_view", "Observation: LOINC 2093-3, > 240 mg/dL"),
        (YELLOW, "bmi_view", "Observation: LOINC 39156-5, > 30 kg/m2"),
        (PINK, "prostate_cancer_diagnosis_view", "Condition: SNOMED CT 126906006"),
    ]
    b = []
    for i, (fill, name, desc) in enumerate(views):
        y = 4 + i * 82
        b.append(rect(0, y, 430, 68, fill, rx=8))
        b.append(text(16, y + 28, name, 15, "start", 700))
        b.append(text(16, y + 52, desc, 14, "start"))
        b.append(hcurve(432, y + 34, 516, 168, stroke=GREY))
    b.append(rect(518, 108, 190, 120, "#F7F7F7", rx=10))
    b.append(
        lines(
            613,
            168,
            ["combine_prostate_", "cancer_views.sql", "", "joins + temporal", "logic"],
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
                "prostate_cancer_",
                "risk_factors",
                "",
                "800 rows,",
                "one per patient",
                "6 with prostate",
                "cancer",
            ],
            14,
        )
    )
    b.append(text(613, 290, "Views: create_prostate_cancer_views", 14, fill=MUTED))
    b.append(text(613, 312, "notebook (Pathling, Python)", 14, fill=MUTED))
    return svg(940, 335, b)


CHOLESTEROL = [
    "cholesterol = data.view(",
    '    "Observation",',
    "    select=[{",
    '        "column": [',
    '            {"path": "getResourceKey()", "name": "id"},',
    '            {"path": "subject.getReferenceKey()", "name": "patient_id"},',
    '            {"path": "effective.ofType(dateTime)", "name": "date"},',
    "        ],",
    '        "select": [',
    '            {"forEach": "code.coding", ...},',
    '            {"forEach": "value.ofType(Quantity)",',
    '             "column": [{"path": "unit", "name": "unit"},',
    '                        {"path": "value", "name": "value"}]},',
    "        ],",
    "    }],",
    '    where=[{"path":',
    "        \"where(code.coding.exists(system = 'http://loinc.org'\"",
    "        \" and code = '2093-3'))\"",
    "        \".value.ofType(Quantity).where(code = 'mg/dL').value > 240\"}],",
    ")",
]


def cholesterol_card():
    """The cholesterol view from the notebook, abridged, with callouts."""
    fs, lh = 12, 1.32
    b = [code(0, 2, 600, CHOLESTEROL, fs=fs, lh=lh)]
    marks = [
        (4, 5, "Keys for joining", "getResourceKey() and getReferenceKey()"),
        (10, 12, "Unnest with forEach", "One row per Quantity value"),
        (16, 18, "Filter with where", "LOINC 2093-3 above 240 mg/dL"),
    ]
    for n, (r0, r1, title, desc) in enumerate(marks, 1):
        y0 = code_baseline(2, r0, fs, lh) - 13
        y1 = code_baseline(2, r1, fs, lh) + 5
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
            "cholesterol.write.saveAsTable(",
            12,
            "start",
            family="JetBrains Mono",
        )
    )
    b.append(
        text(
            650, 52, '  "...hyperlipidemia_view")', 12, "start", family="JetBrains Mono"
        )
    )
    return svg(940, 340, b)


def timeline():
    """Latest observation before diagnosis, on two real patients."""
    b = []
    x0, x1 = 120, 920
    y0, y1 = 1990, 2024

    def tx(year):
        return x0 + (year - y0) / (y1 - y0) * (x1 - x0)

    for yr in range(1990, 2025, 5):
        b.append(text(tx(yr), 150, str(yr), 12, fill=MUTED))
    pts = [
        ("Patient 6a79…", 50, 2022.03, [(2019.96, "30.47", True)]),
        (
            "Patient 2220…",
            112,
            1993.57,
            [(1999.45, "", False), (2000.35, "", False), (2001.1, "30.06", False)],
        ),
    ]
    for label, y, onset, obs in pts:
        b.append(text(0, y + 5, label, 14, "start", 700))
        b.append(line(x0, y, x1, y, "#C8C8C8", 2, arrow=None))
        b.append(line(tx(onset), y - 26, tx(onset), y + 18, RED, 2.5, arrow=None))
        for when, val, kept in obs:
            b.append(
                circle(
                    tx(when), y, 8, MINT if kept else "#fff", TEAL if kept else GREY, 2
                )
            )
            if val:
                b.append(
                    text(
                        tx(when) + (-16 if kept else 16),
                        y - 14,
                        f"BMI {val}"
                        if kept
                        else "3 readings with BMI > 30, all after diagnosis",
                        12,
                        "end" if kept else "start",
                        700 if kept else 400,
                        INK if kept else MUTED,
                    )
                )
    b.append(text(tx(2022.03) + 6, 22, "diagnosis", 12, "start", 700, RED))
    b.append(text(tx(1993.57) + 6, 84, "diagnosis", 12, "start", 700, RED))
    sql = [
        "ROW_NUMBER() OVER (",
        "  PARTITION BY h.patient_id",
        "  ORDER BY h.date DESC) AS rn",
        "...",
        "WHERE pd.prostate_cancer_onset IS NULL",
        "   OR h.date < pd.prostate_cancer_onset",
    ]
    b.append(code(0, 168, 420, sql, "Rank observations before diagnosis", 13, 1.35))
    steps = [
        (BLUE, "Rank: newest first, before onset"),
        (BLUE, "Keep rn = 1 per patient"),
        (MINT, "LEFT JOIN onto 800 patients"),
    ]
    for i, (fill, s) in enumerate(steps):
        y = 172 + i * 54
        b.append(box(470, y, 260, 40, fill, [s], 14))
        if i < 2:
            b.append(line(600, y + 41, 600, y + 52, sw=1.6))
    b.append(rect(760, 172, 175, 148, "#fff", TEAL, 2, 10))
    b.append(
        lines(
            847,
            246,
            [
                "6 patients with",
                "prostate cancer:",
                "1 has a high BMI",
                "before diagnosis,",
                "0 high cholesterol",
            ],
            14,
        )
    )
    return svg(940, 335, b)


TX_FHIRPATH = [
    'where=[{"path": "code.memberOf(',
    "  'http://snomed.info/sct?fhir_vs=ecl/<< 126906006')\"}]",
]

TX_PYTHON = [
    "from pathling import member_of, to_snomed_coding, \\",
    "    to_ecl_value_set",
    "dx.where(member_of(to_snomed_coding(dx.sct_id),",
    '                   to_ecl_value_set("<< 126906006")))',
]


def terminology():
    """From one hard-coded code to a value set, in FHIRPath or Python."""
    b = [text(0, 18, "<< 126906006 (self and descendants)", 15, "start", 700, MUTED)]
    b.append(box(0, 30, 330, 46, PINK, ["126906006 Neoplasm of prostate"], 14, 700))
    kids = [
        ("399068003 Malignant neoplasm of prostate", "#fff"),
        ("92691004 Carcinoma in situ of prostate", "#fff"),
        ("... 45 concepts in total", "#fff"),
    ]
    for i, (s, fill) in enumerate(kids):
        y = 96 + i * 52
        b.append(path_elbow(20, 76, y + 20))
        b.append(box(40, y, 290, 40, fill, [s], 13))
    b.append(rect(0, 254, 330, 80, "#fff", TEAL, 2, 10))
    b.append(
        lines(
            165,
            294,
            [
                "In Synthea AU: 126906006 and 92691004,",
                "6 patients each (the same 6). Not:",
                "315268008 Suspected prostate cancer",
            ],
            13,
        )
    )
    b.append(code(370, 2, 565, TX_FHIRPATH, "FHIRPath, inside the view", 13))
    b.append(code(370, 112, 565, TX_PYTHON, "Python, on a view's output column", 13))
    b.append(rect(370, 268, 565, 66, CYAN, rx=10))
    b.append(
        lines(
            652,
            301,
            [
                "Pathling asks a FHIR terminology server (default tx.ontoserver.csiro.au)",
                "or a local terminology store. Terminology fundamentals: James's sessions.",
            ],
            13,
        )
    )
    return svg(940, 340, b)


def path_elbow(x, y_top, y):
    """An elbow connector from a parent's trunk to a child box."""
    return line(x, y_top, x, y, GREY, 1.6, arrow=None) + line(x, y, 38, y, GREY, 1.6)


def steps_panel(steps, x, y, w, fs=15, gap=50, fill=YELLOW):
    """Numbered step boxes stacked vertically."""
    out = []
    for i, rows in enumerate(steps):
        yy = y + i * gap
        out.append(rect(x, yy, w, gap - 10, fill, rx=8))
        out.append(callout(i + 1, x + 22, yy + (gap - 10) / 2, 13))
        out.append(lines(x + 46, yy + (gap - 10) / 2, rows, fs, anchor="start"))
    return "".join(out)


def demo():
    """What I show live."""
    steps = [
        ["Open notebooks/synthea/create_prostate_cancer_views"],
        ["Attach to Open FHIR Training Cluster (not Serverless)"],
        ["Walk through the cholesterol view: keys, forEach, where"],
        ["Run it and cholesterol.show(10, truncate=False)"],
        ["Open sql/synthea/combine_prostate_cancer_views.sql"],
        ["SQL editor: run the SELECT on prostate_cancer_risk_factors"],
    ]
    b = [steps_panel(steps, 0, 4, 600, 15, 54)]
    b.append(rect(630, 4, 305, 314, "#F7F7F7", rx=10))
    b.append(text(648, 34, "What to look for", 16, "start", 700))
    look = [
        ["The view returns a Spark data frame"],
        ["id and patient_id hold keys like", "Observation/... and Patient/..."],
        ["334 rows above 240 mg/dL in", "hyperlipidemia_view (106 patients)"],
        ["Final table: 800 rows, 6 with", "prostate cancer"],
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
        ["File > Clone create_prostate_cancer_views to your home folder"],
        ["Write a new view, e.g. HbA1c (LOINC 4548-4) above 6.5 %"],
        ['saveAsTable("jane_citizen.hba1c_view") in your own schema'],
        ["Add a latest_hba1c CTE to a copy of the risk factor query"],
    ]
    b = [steps_panel(steps, 0, 4, 560, 14, 56)]
    hint = [
        "where(code.coding.exists(",
        "  system = 'http://loinc.org'",
        "  and code = '4548-4'))",
        ".value.ofType(Quantity)",
        ".where(code = '%').value > 6.5",
    ]
    b.append(code(590, 4, 345, hint, "Hint: the where path", 13, 1.4))
    b.append(
        text(
            590, 190, "253 readings, 22 patients in Synthea AU", 13, "start", fill=MUTED
        )
    )
    b.append(rect(0, 238, 935, 92, PEACH, rx=10))
    b.append(text(18, 266, "Stretch", 16, "start", 700))
    b.append(
        text(
            18,
            292,
            "Replace code = '126906006' with code.memberOf('http://snomed.info/sct?fhir_vs=ecl/<< 126906006')",
            13,
            "start",
            family="JetBrains Mono",
        )
    )
    b.append(
        text(
            18,
            316,
            "Or try systolic blood pressure (LOINC 8480-6) > 140 mm[Hg]: it sits in Observation.component",
            14,
            "start",
        )
    )
    return svg(940, 335, b)


def backup_results():
    """The risk factor query and its six rows, annotated."""
    q, qw, qh, qp = screenshot(
        "sql-prostate-results", 0, 0, 680, crop=(243, 118, 700, 70)
    )
    r, rw, rh, rp = screenshot(
        "sql-prostate-results", 0, 92, 680, crop=(243, 578, 935, 272)
    )
    b = [q, r]
    (x0, y0), (x1, y1) = rp(822, 656), rp(956, 682)
    b.append(highlight(x0, y0, x1 - x0, y1 - y0))
    b.append(callout(2, x1 + 18, (y0 + y1) / 2))
    (x0, y0), (x1, y1) = rp(308, 822), rp(362, 848)
    b.append(highlight(x0, y0, x1 - x0, y1 - y0))
    b.append(callout(3, (x0 + x1) / 2, y0 - 16))
    b.append(callout(1, 20, 36))
    notes = [
        ("The query reads the", "combined view in the", "shared schema"),
        ("One patient has a BMI", "above 30 before", "diagnosis"),
        ("6 rows: the patients", "with prostate cancer", ""),
    ]
    for i, rows in enumerate(notes):
        ty = 20 + i * 100
        b.append(callout(i + 1, 718, ty + 10))
        for j, s in enumerate(rows):
            b.append(text(742, ty + 15 + j * 20, s, 14, "start"))
    return svg(940, 300, b)


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
        ["Write tables to your schema,", "e.g. jane_citizen.hba1c_view"],
    ]
    b.append(steps_panel(steps, 510, 4, 425, 15, 80, BLUE))
    return svg(940, 335, b)


def backup_show():
    """What the cholesterol view looks like as a table."""
    b = [code(0, 4, 935, ["cholesterol.show(10, truncate=False)"], "Notebook cell", 14)]
    rows = [
        (
            "Observation/872ec130-…",
            "Patient/872ec130-…",
            "2026-10-13T13:24:35+10:00",
            "2093-3",
            "mg/dL",
            "246.2",
        ),
        (
            "Observation/15c308cf-…",
            "Patient/15c308cf-…",
            "2026-10-12T15:09:10+10:00",
            "2093-3",
            "mg/dL",
            "305.0",
        ),
        (
            "Observation/15c308cf-…",
            "Patient/15c308cf-…",
            "2026-10-12T15:09:10+10:00",
            "2093-3",
            "mg/dL",
            "299.3",
        ),
        (
            "Observation/0fe2d5e4-…",
            "Patient/0fe2d5e4-…",
            "2026-10-06T00:21:11+10:00",
            "2093-3",
            "mg/dL",
            "316.2",
        ),
    ]
    b.append(
        table(
            0,
            92,
            [
                ("id", 210),
                ("patient_id", 185),
                ("date", 250),
                ("code", 80),
                ("unit", 80),
                ("value", 130),
            ],
            rows,
            YELLOW,
            13,
            34,
            mono_cols=(0, 1, 2),
        )
    )
    b.append(
        text(
            0,
            300,
            "Rows from the saved hyperlipidemia_view (newest first); values rounded to 1 decimal place.",
            14,
            "start",
            fill=MUTED,
            italic=True,
        )
    )
    b.append(
        text(
            0,
            324,
            "334 rows for 106 patients. IDs truncated here.",
            14,
            "start",
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 335, b)


DECK = {
    "file": "track-3-d2-4-sql-on-fhir",
    "slides": [
        title_slide(
            "SQL on FHIR, Pathling views and terminology",
            f"Friday 9:30 · {EVENT}",
            "Good morning. This block is about the middle of the analytics pipeline: turning FHIR "
            "resources into tables you can analyse. I'll cover SQL on FHIR ViewDefinitions, the "
            "small amount of FHIRPath you need to write them, and how terminology can make a view "
            "smarter than a single hard-coded code. Then we'll work through the prostate cancer "
            "risk factor exercise in the workspace. I'll talk for about twenty minutes, show you "
            "the notebook and the SQL live, and then the rest of the block is yours.",
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
            "for example to the SNOMED CT coding of a condition. exists tests whether anything "
            "matches, which is how the exercise picks out total cholesterol by its LOINC code. "
            "ofType picks one type out of a choice element like value or effective. first takes "
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
            "each view emits keys. The patient view has getResourceKey as its id. The BMI view has "
            "subject dot getReferenceKey as its patient_id, which returns the same value for the "
            "same patient. Then plain SQL does the join. These are real rows from the workspace: "
            "one patient with one high BMI reading, another with three. Keeping views simple and "
            "pushing joins, ranking and aggregation into SQL is a deliberate design choice. It "
            "keeps views portable and lets each engine do what it is good at.",
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
            "declare a ValueSet or ConceptMap and join to it as a table. And there are standard "
            "operations to run and export. This is ballot content, so details may change.",
        ),
        section(
            "Exercise: prostate cancer risk factors",
            "Let's put this into practice. The exercise asks a simple question of the Synthea "
            "data: for patients with prostate cancer, what did we know about their cholesterol "
            "and body mass index before they were diagnosed? It isn't a serious epidemiological "
            "study - the data is synthetic - but it uses every idea we've just covered: views with "
            "keys, filters on LOINC and SNOMED CT codes, and SQL that joins and ranks the results. "
            "The notebook and SQL file are both in the repository folder in the workspace.",
        ),
        diagram(
            "Four views, one query",
            "Pathling views in a notebook, then one SQL file joins them",
            "four-views",
            four_views(),
            "The notebook defines four views with Pathling. A patient demographics view with "
            "birth date, postal codes and deceased date. Two Observation views: total cholesterol, "
            "LOINC 2093-3, above 240 milligrams per decilitre, and body mass index, LOINC 39156-5, "
            "above 30. And a Condition view for SNOMED CT 126906006, neoplasm of prostate. Each is "
            "saved as a table in the synthea_prostate_cancer_views schema. Then one SQL file "
            "combines them into a single table with one row per patient: 800 rows, 6 of them with "
            "prostate cancer.",
        ),
        diagram(
            "The cholesterol view in Pathling",
            "data.view() takes a ViewDefinition as Python and returns a Spark data frame",
            "cholesterol-code",
            cholesterol_card(),
            "Here is the cholesterol view from the notebook, with the descriptions removed so it "
            "fits. data.view takes the resource type, a select and a where - the same elements as "
            "the JSON, written as Python dictionaries. First, the keys: getResourceKey for the "
            "observation and getReferenceKey for the patient. Second, forEach over the Quantity "
            "value gives us unit and value columns. Third, the where: keep observations with a "
            "LOINC 2093-3 coding whose value in milligrams per decilitre is above 240. The result "
            "is a Spark data frame, so the last step is saveAsTable.",
        ),
        diagram(
            "Latest reading before diagnosis",
            "Temporal logic lives in SQL: rank, keep one row, join back to every patient",
            "temporal",
            timeline(),
            "The risk factor has to come before the diagnosis. These two patients are real rows "
            "from the workspace. The first had a BMI of 30.47 about two years before their "
            "diagnosis, so it counts. The second had three high BMI readings, all years after "
            "diagnosis, so none count. The SQL ranks each patient's readings newest first, keeping "
            "only those before onset, takes rank one, and left joins onto all 800 patients. Of the "
            "6 with prostate cancer, one has a high BMI beforehand, and none has high cholesterol "
            "beforehand.",
        ),
        diagram(
            "Terminology makes views smarter",
            "Match a value set of concepts, not one hard-coded code",
            "terminology",
            terminology(),
            "The condition view matches exactly one SNOMED CT code. But clinical data is coded at "
            "different levels of detail. The ECL expression double less-than 126906006 means "
            "neoplasm of prostate and all its descendants - 45 concepts today. In Synthea, the "
            "same 6 patients also have carcinoma in situ of prostate, which this would catch, and "
            "it correctly leaves out suspected prostate cancer. You can do this in FHIRPath with "
            "memberOf inside the view, or in Python with member_of on a column. I ran both on "
            "Pathling 10. James's sessions cover the terminology fundamentals.",
        ),
        diagram(
            "Demo",
            "Views in the notebook, then the combined table in the SQL editor",
            "demo",
            demo(),
            "Live demo. One: in Workspace, Repos, open-fhir-training, open notebooks, synthea, "
            "create_prostate_cancer_views. Two: check the compute dropdown shows Open FHIR "
            "Training Cluster, not Serverless. Three: scroll to the hyperlipidemia view and point "
            "out the keys, the forEach and the where. Four: run the setup cells and the cholesterol "
            "cell, then the show cell - don't run saveAsTable. Five: open "
            "sql/synthea/combine_prostate_cancer_views.sql and walk through the CTEs. Six: in the "
            "SQL editor on the Serverless Starter Warehouse, run the SELECT for rows where "
            "prostate_cancer_onset is not null - six rows.",
        ),
        diagram(
            "Your turn",
            "Add a risk factor of your own, in your own schema",
            "your-turn",
            your_turn(),
            "Now it's over to you. Clone the notebook into your home folder - you can't edit the "
            "shared copy. Write a new view: HbA1c, LOINC 4548-4, is a good first one because it "
            "has the same shape as the cholesterol view. The unit code is percent, and there are "
            "253 readings above 6.5 for 22 patients. Save it to your own schema, then copy the "
            "risk factor query and add a latest HbA1c before diagnosis. If you finish, swap the "
            "single SNOMED CT code for a memberOf filter, or try systolic blood pressure, which is "
            "a component of the blood pressure panel. We're all here to help.",
        ),
        section(
            "Demo walkthrough (backup)",
            "These slides are a fallback in case the live demo doesn't work - for example if the "
            "network or the cluster is slow. They show the same steps as screenshots and real "
            "output from the workspace, so you can follow along and still do the exercise "
            "afterwards. If the demo did work, I'll skip straight past them to questions, and you "
            "can come back to them later in the slides we share after the connectathon.",
        ),
        diagram(
            "The risk factor table",
            "SQL editor on the Serverless Starter Warehouse",
            "backup-results",
            backup_results(),
            "This is the final step of the demo. The query selects four columns from "
            "prostate_cancer_risk_factors in the shared schema, filtered to patients with a "
            "prostate cancer onset date. One, the query itself. Two, the BMI column: one patient "
            "has a BMI of 30.47 recorded before diagnosis, and the rest are null. The cholesterol "
            "column is null for all six, because none had a total cholesterol above 240 before "
            "diagnosis. Three, six rows - the six patients with prostate cancer in this dataset.",
        ),
        diagram(
            "Clone before you change",
            "The repository notebooks are read-only for attendees",
            "backup-clone",
            backup_clone(),
            "Before you change anything, clone the notebook. One, open it and click the File "
            "menu at the top left. Two, choose Clone and pick your home folder. Three, make sure "
            "your clone is attached to the Open FHIR Training Cluster, because Pathling isn't "
            "installed on Serverless. Four, when you save a view, use your own schema - create it "
            "first with CREATE SCHEMA IF NOT EXISTS and your name - rather than the shared "
            "synthea_prostate_cancer_views schema.",
        ),
        diagram(
            "What the cholesterol view returns",
            "One row per observation, with keys for joining",
            "backup-show",
            backup_show(),
            "If the cluster isn't cooperating, this is what the cholesterol view gives you. The "
            "rows come from the saved hyperlipidemia view table, newest first. The id column is "
            "the observation key and patient_id the patient key, both in the form type slash id. "
            "Every row has the LOINC code 2093-3, the unit mg/dL and a value above 240. Across "
            "the dataset there are 334 such observations for 106 patients. Notice that one "
            "patient has two readings at the same time - real data has these quirks too.",
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
