"""Day 1, 2:00 Track 3 slab: tactical FHIR amid legacy and proprietary systems.

Author: John Grimes
"""

from kit import (
    AMBER,
    BLUE,
    CYAN,
    GREY,
    INK,
    LAVENDER,
    LBLUE,
    MINT,
    MUTED,
    PEACH,
    PINK,
    TEAL,
    YELLOW,
    bullets,
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


def chip(x, y, s, fill="#fff", fs=12):
    """A small rounded format label; returns (svg, width)."""
    w = len(s) * fs * 0.58 + 18
    return (
        rect(x, y, w, fs + 10, fill, sw=1.1, rx=(fs + 10) / 2)
        + text(x + w / 2, y + fs + 2.5, s, fs, "middle", 400)
    ), w


def step(x, y, n, rows, fs=15):
    """A numbered step: a teal number disc and one or more lines of text."""
    b = [callout(n, x + 14, y, 13)]
    for i, r in enumerate(rows):
        b.append(text(x + 38, y + 5 + i * fs * 1.3, r, fs, "start"))
    return "".join(b)


# --- Diagrams -------------------------------------------------------------------


def reality():
    """Archetype sources in a hospital and the formats they actually emit."""
    sources = [
        (
            BLUE,
            "EMR / EHR",
            "proprietary vendor database",
            ["SQL and report extracts", "HL7 v2 messages", "vendor API, some FHIR"],
        ),
        (
            LAVENDER,
            "Pathology LIS",
            "laboratory information system",
            ["HL7 v2 ORU results", "local test codes"],
        ),
        (
            LBLUE,
            "Radiology",
            "RIS and PACS",
            ["HL7 v2 orders and results", "DICOM images", "free-text reports"],
        ),
        (
            CYAN,
            "Patient admin system",
            "admissions and transfers",
            ["HL7 v2 ADT", "flat extracts"],
        ),
        (
            PEACH,
            "Departmental systems",
            "niche and local tools",
            ["CSV and spreadsheets", "local databases"],
        ),
        (
            AMBER,
            "Integration engine",
            "routes feeds between systems",
            ["HL7 v2 feeds", "message archives"],
        ),
        (
            MINT,
            "Data warehouse",
            "nightly loads",
            ["flat extracts (CSV)", "star schemas"],
        ),
        (
            PINK,
            "Documents and text",
            "letters, notes, scans",
            ["PDF and scanned images", "free text"],
        ),
    ]
    b = []
    for i, (fill, title, sub, formats) in enumerate(sources):
        col, row = i % 4, i // 4
        x, y = 4 + col * 234, 6 + row * 167
        b.append(rect(x, y, 214, 155, fill, rx=10))
        b.append(text(x + 14, y + 28, title, 16, "start", 700))
        b.append(text(x + 14, y + 49, sub, 13, "start", 400, MUTED))
        for j, f in enumerate(formats):
            s, _ = chip(x + 14, y + 64 + j * 29, f)
            b.append(s)
    return svg(940, 336, b)


def edge():
    """Many sources, mapped once into FHIR at the edge of the analytics platform."""
    b = [
        rect(222, 34, 714, 272, "#F6F8FA", "#C8C8C8", 1.2, 12),
        text(
            579,
            326,
            "Analytics platform: FHIR is the interchange model at its edge",
            14,
            fill=MUTED,
            italic=True,
        ),
        line(222, 20, 222, 318, TEAL, 2, "6 4", None),
    ]
    heads = [
        (95, "Many sources"),
        (305, "Map once"),
        (475, "One model"),
        (645, "Shared views"),
        (855, "Many consumers"),
    ]
    for x, s in heads:
        b.append(text(x, 22, s, 15, weight=700, fill=INK))
    srcs = [
        "EMR extract",
        "LIS feed",
        "PAS extract",
        "Departmental CSV",
        "Documents (NLP)",
    ]
    for i, s in enumerate(srcs):
        y = 48 + i * 52
        b.append(box(10, y, 170, 40, "#fff", [s], 14))
        b.append(hcurve(182, y + 20, 246, 170, lead=6, tail=10))
    b.append(box(250, 120, 110, 100, YELLOW, ["Map to", "FHIR", "resources"], 15, 700))
    b.append(line(362, 170, 398, 170, sw=2))
    b.append(box(402, 112, 146, 116, CYAN, ["FHIR", "NDJSON", "Delta tables"], 15))
    b.append(line(550, 170, 576, 170, sw=2))
    b.append(
        box(580, 112, 130, 116, LAVENDER, ["SQL on FHIR", "views", "+ terminology"], 15)
    )
    cons = [
        "Dashboards",
        "Research cohorts",
        "Quality reports",
        "ML features",
        "Decision support",
    ]
    for i, s in enumerate(cons):
        y = 48 + i * 52
        b.append(hcurve(712, 170, 776, y + 20, lead=6, tail=10))
        b.append(box(780, y, 150, 40, MINT, [s], 14))
    return svg(940, 336, b)


def patterns():
    """Five patterns for getting FHIR out of systems that don't speak it."""
    cols = [(10, "Pattern"), (300, "Input"), (490, "Effort"), (610, "When to use it")]
    b = [rect(0, 0, 940, 30, LAVENDER, rx=6)]
    for x, s in cols:
        b.append(text(x + 6, 20, s, 14, "start", 700))
    rows = [
        (
            YELLOW,
            "Extract and map",
            "CSV or SQL extract -> NDJSON · today",
            "CSV, SQL extracts",
            2,
            ["You can get extracts now;", "batch analytics and research"],
        ),
        (
            AMBER,
            "HL7 v2 to FHIR",
            "integration engine · Track 2, 2B",
            "ADT, ORU messages",
            2,
            [
                "Feeds already flow through the engine;",
                "you need data close to real time",
            ],
        ),
        (
            CYAN,
            "FHIR facade",
            "over an existing database",
            "the source database",
            3,
            ["Data must stay in the source;", "live queries rather than copies"],
        ),
        (
            BLUE,
            "Bulk Data $export",
            "where the vendor supports it",
            "vendor FHIR server",
            1,
            ["The vendor exposes $export;", "population-level extracts"],
        ),
        (
            PINK,
            "Text to FHIR with NLP",
            "Dion's strand",
            "notes, letters, reports",
            3,
            ["The facts exist only in free text;", "pair NLP with terminology"],
        ),
    ]
    for i, (fill, title, note, inp, effort, when) in enumerate(rows):
        y = 38 + i * 60
        b.append(rect(0, y, 940, 54, "#fff", rx=8))
        b.append(circle(30, y + 27, 13, fill))
        b.append(text(30, y + 32, str(i + 1), 14, weight=700))
        b.append(text(52, y + 23, title, 15, "start", 700))
        b.append(text(52, y + 42, note, 12, "start", 400, MUTED))
        b.append(text(306, y + 32, inp, 14, "start"))
        for d in range(3):
            b.append(
                circle(
                    506 + d * 20, y + 21, 6.5, TEAL if d < effort else "#fff", TEAL, 1.5
                )
            )
        b.append(
            text(
                496,
                y + 45,
                ["low", "medium", "high"][effort - 1],
                12,
                "start",
                400,
                MUTED,
            )
        )
        b.append(lines(616, y + 27, when, 13, anchor="start", lh=1.35))
    return svg(940, 338, b)


def contract():
    """The same Patient view over FHIR from two different sources, then four benefits."""
    b = [
        box(
            0,
            14,
            236,
            78,
            CYAN,
            ["synthea.patient", "Synthea AU, generated as FHIR"],
            14,
        ),
        box(
            0,
            110,
            236,
            78,
            PEACH,
            ["synthea_encoded.patient", "mapped from the CSV extract"],
            14,
        ),
        hcurve(238, 53, 272, 101, lead=4, tail=8),
        hcurve(238, 149, 272, 101, lead=4, tail=8),
        code(
            276,
            18,
            342,
            [
                'data.view("Patient", select=[{"column": [',
                '  {"path": "getResourceKey()", "name": "id"},',
                '  {"path": "gender", "name": "gender"},',
                '  {"path": "birthDate", "name": "birth_date"},',
                "]}])",
            ],
            "One view definition",
            fs=11.5,
            lh=1.45,
        ),
        line(620, 101, 648, 101, sw=2),
        text(796, 22, "Patients by gender", 14, weight=700),
        table(
            652,
            34,
            [("Source", 140), ("male", 70), ("female", 78)],
            [
                ("synthea", "389", "411"),
                ("synthea_encoded", "554", "589"),
            ],
            MINT,
            fs=13,
            rh=30,
        ),
        text(796, 146, "Same columns, either source", 13, fill=MUTED, italic=True),
    ]
    cards = [
        (
            LAVENDER,
            "Meaning from terminology",
            ["SNOMED CT-AU, LOINC and AMT", "bindings make codes comparable"],
        ),
        (
            YELLOW,
            "Incremental adoption",
            ["one source and one resource", "type at a time"],
        ),
        (BLUE, "Portable", ["views and queries move", "across sites and vendors"]),
        (MINT, "Reuse", ["AU Core profiles, validators,", "Pathling, community tools"]),
    ]
    for i, (fill, title, rows) in enumerate(cards):
        x = i * 237
        b.append(rect(x, 214, 229, 112, fill, rx=10))
        b.append(text(x + 14, 242, title, 15, "start", 700))
        b.append(lines(x + 14, 285, rows, 13, anchor="start", lh=1.4))
    return svg(940, 330, b)


def tactics():
    """Three tactics in miniature: scope, code binding, storage."""
    b = [text(0, 16, "Scope from the question", 14, "start", 700, TEAL)]
    for i, s in enumerate(["Question", "Resources", "Elements"]):
        x = i * 165
        b.append(box(x, 28, 136, 40, YELLOW, [s], 14))
        if i < 2:
            b.append(line(x + 138, 48, x + 162, 48))
    b.append(text(0, 108, "Bind local codes with a ConceptMap", 14, "start", 700, TEAL))
    b.append(box(0, 120, 136, 58, PEACH, ["GLU-F", "local lab code"], 13))
    b.append(line(138, 149, 162, 149))
    b.append(box(165, 120, 120, 58, LAVENDER, ["ConceptMap", "$translate"], 13))
    b.append(line(287, 149, 311, 149))
    b.append(box(314, 120, 176, 58, MINT, ["LOINC 1558-6", "Fasting glucose, S/P"], 13))
    b.append(text(0, 222, "Store it twice", 14, "start", 700, TEAL))
    b.append(box(0, 234, 236, 62, CYAN, ["NDJSON", "exchange · archive · reload"], 13))
    b.append(
        box(254, 234, 236, 62, BLUE, ["Delta / Parquet", "query · views · SQL"], 13)
    )
    b.append(
        text(
            0,
            324,
            "GLU-F is an invented example of a local code",
            12,
            "start",
            400,
            MUTED,
            italic=True,
        )
    )
    return svg(490, 330, b)


def flat_to_nested():
    """A row of synthea_csv.patients mapped column by column to a FHIR Patient."""
    shot, dw, dh, pt = screenshot(
        "csv-patients-sample", 0, 44, 440, crop=(590, 196, 783, 279)
    )
    b = [text(0, 14, "synthea_csv.patients (flat)", 14, "start", 700), shot]
    hx, hy = pt(592, 300)
    b.append(highlight(hx, hy, dw, 25 * dh / 279))
    for n, px in enumerate([625, 915, 1060, 1190], 1):
        x, _ = pt(px, 210)
        b.append(callout(n, x, 31, 10))
    b.append(callout(5, 10, 224, 10))
    b.append(
        text(26, 229, "GENDER, further right in the extract", 13, "start", 400, MUTED)
    )
    b.append(
        table(
            0,
            240,
            [("GENDER", 90), ("rows", 70)],
            [("F", "589"), ("M", "554")],
            PEACH,
            fs=13,
            rh=26,
        )
    )
    b.append(text(180, 276, "Row 4 (highlighted) is the", 13, "start", 400, MUTED))
    b.append(text(180, 294, "Patient on the right", 13, "start", 400, MUTED))
    json_rows = [
        '{ "resourceType": "Patient",',
        '  "id": "04cded97-719a-...-aee36812ec43",',
        '  "identifier": [',
        '    { "system": ".../sid/us-ssn",',
        '      "value": "999-93-8972" },',
        '    { "system": "urn:oid:...Massachusetts",',
        '      "value": "S99940284" }, ... ],',
        '  "gender": "male",',
        '  "birthDate": "1996-11-19" }',
    ]
    cx, cy, fs, lh = 625, 26, 11, 1.55
    b.append(
        code(
            cx,
            cy,
            315,
            json_rows,
            "FHIR Patient (abridged)",
            fs=fs,
            lh=lh,
            title_fill=CYAN,
        )
    )

    def row_y(i):
        return cy + 30 + 8 + fs + i * fs * lh - 4

    chips = [
        (1, "Id", "id", 1),
        (4, "SSN · DRIVERS", "identifier[]", 4.5),
        (5, "GENDER M/F", "male/female", 7),
        (2, "BIRTHDATE", "birthDate", 8),
    ]
    for k, (n, src, dst, i) in enumerate(chips):
        y = 40 + k * 46
        b.append(rect(455, y, 150, 36, "#fff", rx=18))
        b.append(callout(n, 471, y + 18, 10))
        b.append(text(487, y + 23, src, 13, "start", 700))
        b.append(hcurve(607, y + 18, cx - 2, row_y(i), lead=4, tail=8))
    b.append(rect(455, 228, 150, 36, "#F6F8FA", GREY, 1.2, 18, "4 3"))
    b.append(callout(3, 471, 246, 10))
    b.append(text(487, 251, "DEATHDATE", 13, "start", 700, MUTED))
    b.append(text(455, 284, "-> deceasedDateTime,", 12, "start", 400, MUTED))
    b.append(text(455, 300, "omitted when null", 12, "start", 400, MUTED))
    b.append(
        text(
            625,
            276,
            "One flat row becomes nested structs and",
            13,
            "start",
            400,
            MUTED,
            italic=True,
        )
    )
    b.append(
        text(
            625,
            294,
            "arrays; three optional columns become",
            13,
            "start",
            400,
            MUTED,
            italic=True,
        )
    )
    b.append(
        text(625, 312, "one identifier array", 13, "start", 400, MUTED, italic=True)
    )
    return svg(940, 320, b)


def pipeline():
    """The transform_csv_to_fhir notebook as a pipeline."""
    b = []
    top = [
        (PEACH, ["synthea_csv", "patients · encounters", "immunizations"]),
        (YELLOW, ["Spark mapping", "struct · array · when"]),
        (LAVENDER, ['to_json(struct("*"))', "one JSON string per row"]),
        (CYAN, ["NDJSON files", "Patient.ndjson ..."]),
    ]
    for i, (fill, rows) in enumerate(top):
        x = i * 240
        b.append(box(x, 8, 210, 80, fill, rows, 14))
        b.append(callout(i + 1, x + 18, 8, 11))
        if i < 3:
            b.append(line(x + 212, 48, x + 236, 48, sw=2))
    b.append(path_down())
    bottom = [
        (0, MINT, ["Validate", "line counts · JSON parse"]),
        (240, MINT, ["Referential integrity", "left_anti joins: orphans"]),
    ]
    for k, (x, fill, rows) in enumerate(bottom):
        b.append(box(x, 186, 210, 80, fill, rows, 14))
        b.append(callout(k + 5, x + 18, 186, 11))
    b.append(line(212, 226, 236, 226, sw=2))
    b.append(hcurve(452, 226, 478, 182, lead=4, tail=8))
    b.append(hcurve(452, 226, 478, 288, lead=4, tail=8))
    b.append(
        box(
            480,
            152,
            210,
            60,
            BLUE,
            ["synthea_transformed", "Delta · JSON text column"],
            14,
        )
    )
    b.append(callout(7, 498, 152, 11))
    b.append(box(480, 258, 210, 60, BLUE, ["pc.encode(text_df,", '"Patient")'], 14))
    b.append(callout(8, 498, 258, 11))
    b.append(line(692, 288, 716, 288, sw=2))
    b.append(
        box(
            720, 258, 210, 60, BLUE, ["synthea_encoded", "nested FHIR columns"], 14, 700
        )
    )
    b.append(callout(9, 738, 258, 11))
    b.append(
        text(
            720,
            222,
            "data.write.tables(",
            12,
            "start",
            family="JetBrains Mono",
            fill=MUTED,
        )
    )
    b.append(
        text(
            720,
            240,
            '    "synthea_encoded")',
            12,
            "start",
            family="JetBrains Mono",
            fill=MUTED,
        )
    )
    b.append(
        text(
            710,
            187,
            "-> query JSON strings with SQL",
            13,
            "start",
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 330, b)


def path_down():
    """The connector from the NDJSON box down to the validation row."""
    return vcurve(825, 90, 105, 182, lead=10, tail=10, sw=2)


def mapping_code():
    """The Patient mapping and the Pathling encode step, abridged from the notebook."""
    left = [
        "patient_fhir_df = patients_df.select(",
        '    col("Id").alias("id"),',
        '    lit("Patient").alias("resourceType"),',
        "    array(",
        '        when(col("SSN").isNotNull() & (col("SSN") != ""),',
        '             struct(struct(...).alias("type"),',
        '                    lit("http://hl7.org/fhir/sid/us-ssn")',
        '                        .alias("system"),',
        '                    col("SSN").alias("value"))),',
        "        ...  # DRIVERS, PASSPORT",
        '    ).alias("identifier"),',
        '    when(col("GENDER") == "M", lit("male"))',
        '    .when(col("GENDER") == "F", lit("female"))',
        '    .otherwise(lit("unknown")).alias("gender"),',
        '    col("BIRTHDATE").alias("birthDate"),',
        "    ...)",
    ]
    right = [
        "pc = PathlingContext.create()",
        "patient_text_df = spark.read.text(",
        "    patient_output)",
        "patient_pathling_df = pc.encode(",
        '    patient_text_df, "Patient")',
        "...",
        "data = pc.read.datasets({",
        '    "Patient": patient_pathling_df,',
        '    "Encounter": encounter_pathling_df,',
        '    "Immunization": immunization_pathling_df,',
        "})",
        'data.write.tables("synthea_encoded")',
    ]
    fs, lh = 11.5, 1.45
    b = [
        code(
            0,
            4,
            500,
            left,
            "Map: transform_csv_to_fhir, Patient cell",
            fs=fs,
            lh=lh,
            title_fill=YELLOW,
        ),
        code(530, 4, 410, right, "Encode with Pathling", fs=fs, lh=lh, title_fill=BLUE),
    ]

    def y(i):
        return 4 + 30 + 8 + fs + i * fs * lh - 4

    b.append(callout(1, 484, y(3), 11))
    b.append(callout(2, 484, y(11), 11))
    b.append(callout(3, 924, y(3), 11))
    notes = [
        (1, "Three optional columns -> one identifier array"),
        (2, "A value set mapping, with a default"),
        (3, "Encoders turn JSON into typed, nested columns"),
    ]
    for k, (n, s) in enumerate(notes):
        yy = 268 + k * 22
        b.append(callout(n, 544, yy, 10))
        b.append(text(562, yy + 5, s, 13, "start"))
    return svg(940, 330, b)


def pitfalls():
    """Six pitfalls, each with evidence from the exercise data."""
    cards = [
        (
            PINK,
            "Ids longer than 64 characters",
            13,
            [
                "Immunization id = patient UUID +",
                "encounter UUID + CVX code.",
                "All 16,501 ids are 76-77 characters.",
                "Known issue: hash or shorten them.",
            ],
        ),
        (
            YELLOW,
            "Dates and time zones",
            13,
            [
                "BIRTHDATE 2012-09-11 has no zone;",
                "first Observation 2012-09-10T23:57:37Z",
                "is UTC. Brisbane is UTC+10 - compare",
                "instants, not truncated dates.",
            ],
        ),
        (
            LAVENDER,
            "Value set mapping",
            13,
            [
                "GENDER M/F -> male/female, else",
                "unknown. Encounter class 'home' (348)",
                "and 'snf' (195) fall through to",
                "the AMB default.",
            ],
        ),
        (
            PEACH,
            "Local and foreign codes",
            12.5,
            [
                "Vaccines carry US CVX codes, not AMT.",
                "Driver's licence system",
                "urn:oid:...4.3.Massachusetts",
                "is not a valid OID.",
            ],
        ),
        (
            MINT,
            "Orphan references",
            13,
            [
                "Every Patient/ and Encounter/",
                "reference must resolve. The notebook",
                "counts orphans with left_anti joins",
                "before anything is loaded.",
            ],
        ),
        (
            CYAN,
            "Shape errors fail silently",
            13,
            [
                "identifier.type built as a Coding:",
                "0 of 1,143 encoded Patients keep it.",
                "248 have null identifier entries",
                "from array(when(...)).",
            ],
        ),
    ]
    b = []
    for i, (fill, title, fs, rows) in enumerate(cards):
        col, row = i % 3, i // 3
        x, y = col * 318, 4 + row * 166
        b.append(rect(x, y, 302, 156, fill, rx=10))
        b.append(text(x + 16, y + 30, title, 15.5, "start", 700))
        for j, r in enumerate(rows):
            b.append(text(x + 16, y + 60 + j * 22, r, fs, "start"))
    return svg(940, 330, b)


def demo():
    """What I show live, with thumbnails of the flat and nested tables."""
    steps = [
        [
            "Workspace > Repos > John.Grimes@csiro.au > open-fhir-training",
            "> notebooks > csv_to_fhir > transform_csv_to_fhir",
        ],
        ["Attach to Open FHIR Training Cluster (not Serverless)"],
        ["The Patient select: identifiers, gender, address"],
        ["Encounter class mapping and the Immunization id"],
        ["The referential integrity cell: left_anti joins"],
        ["Catalog: synthea_csv.patients vs synthea.patient"],
    ]
    b = []
    y = 14
    for i, rows in enumerate(steps):
        b.append(step(0, y, i + 1, rows, 14.5))
        y += 24 + 18 * len(rows)
    b.append(rect(0, 284, 520, 36, YELLOW, rx=8))
    b.append(
        text(
            14,
            307,
            "I won't run the cells that write NDJSON or tables",
            14,
            "start",
            700,
        )
    )
    s1, _, h1, _ = screenshot(
        "csv-patients-sample", 560, 22, 380, crop=(538, 196, 882, 250)
    )
    s2, _, h2, _ = screenshot(
        "patient-schema", 560, 22 + h1 + 30, 380, crop=(538, 295, 882, 250)
    )
    b += [
        text(560, 14, "Flat: synthea_csv.patients", 13, "start", 700),
        s1,
        text(560, 22 + h1 + 22, "Nested: synthea.patient", 13, "start", 700),
        s2,
    ]
    return svg(940, 336, b)


def your_turn():
    """What attendees do next, with a starter mapping for Condition."""
    steps = [
        ["File > Clone the notebook to your", "home folder"],
        [
            "CREATE SCHEMA IF NOT EXISTS jane_citizen;",
            "point output_path and tables at it",
        ],
        [
            "Map synthea_csv.conditions to Condition",
            "(SNOMED CT) or observations to",
            "Observation (LOINC)",
        ],
        ["pc.encode it, then query it with a view"],
    ]
    b = []
    y = 16
    for i, rows in enumerate(steps):
        b.append(step(0, y, i + 1, rows, 14))
        y += 24 + 18.5 * len(rows)
    b.append(rect(0, 246, 410, 84, YELLOW, rx=10))
    b.append(text(14, 268, "Stretch", 15, "start", 700, TEAL))
    b.append(
        lines(
            14,
            299,
            [
                "Compare your Patient with AU Core Patient:",
                "identifier, name, gender, birthDate. What",
                "would an Australian extract need (IHI)?",
            ],
            13,
            anchor="start",
            lh=1.35,
        )
    )
    rows = [
        'conditions_df = spark.table("synthea_csv.conditions")',
        "condition_fhir_df = conditions_df.select(",
        '    sha2(concat_ws("|", "PATIENT", "ENCOUNTER",',
        '                   "CODE", "START"), 256).alias("id"),',
        '    lit("Condition").alias("resourceType"),',
        "    struct(array(struct(",
        '        lit("http://snomed.info/sct").alias("system"),',
        '        col("CODE").alias("code"),',
        '        col("DESCRIPTION").alias("display"),',
        '    )).alias("coding")).alias("code"),',
        '    struct(concat_ws("", lit("Patient/"), col("PATIENT"))',
        '           .alias("reference")).alias("subject"),',
        '    col("START").alias("onsetDateTime"),',
        ")",
    ]
    b.append(
        code(
            430,
            4,
            510,
            rows,
            "A starting point (add sha2 to the imports)",
            fs=11,
            lh=1.42,
            title_fill=MINT,
        )
    )
    b.append(
        text(
            430,
            300,
            "conditions: START, STOP, PATIENT, ENCOUNTER, CODE,",
            12.5,
            "start",
            400,
            MUTED,
        )
    )
    b.append(
        text(
            430,
            318,
            "DESCRIPTION · 37,438 rows · SHA-256 ids are 64 characters",
            12.5,
            "start",
            400,
            MUTED,
        )
    )
    return svg(940, 332, b)


def backup_notebook():
    """The CSV to FHIR notebook, annotated."""
    shot, dw, dh, pt = screenshot(
        "csv-notebook", 0, 2, 620, 330, crop=(243, 50, 920, 550)
    )
    b = [shot]
    marks = [(1090, 67), (1050, 172), (903, 172), (700, 393)]
    for n, (px, py) in enumerate(marks, 1):
        x, y = pt(px, py)
        b.append(callout(n, x, y, 12))
    tx, ty = pt(850, 55)
    tx2, ty2 = pt(1030, 80)
    b.append(highlight(tx, ty, tx2 - tx, ty2 - ty))
    notes = [
        ["transform_csv_to_fhir, opened from", "the open-fhir-training Git folder"],
        ["Compute: Open FHIR Training Cluster", "(Pathling is not on Serverless)"],
        ["Not Run all: later cells write", "NDJSON and shared tables"],
        ["Three resources: Patient, Encounter,", "Immunization"],
    ]
    yy = 30
    for i, rows in enumerate(notes):
        b.append(step(dw + 24, yy, i + 1, rows, 14))
        yy += 34 + 18 * len(rows)
    return svg(940, 334, b)


def backup_compare():
    """Flat CSV sample beside the nested FHIR schema."""
    s1, w1, h1, p1 = screenshot(
        "csv-patients-sample", 0, 26, 455, crop=(538, 196, 882, 470)
    )
    s2, w2, h2, p2 = screenshot(
        "patient-schema", 485, 26, 455, crop=(538, 300, 882, 470)
    )
    b = [
        text(0, 16, "synthea_csv.patients · Sample Data", 14, "start", 700),
        text(485, 16, "synthea.patient · Overview", 14, "start", 700),
        s1,
        s2,
    ]
    x, y = p1(540, 198)
    x2, y2 = p1(1418, 224)
    b.append(highlight(x, y, x2 - x, y2 - y))
    b.append(callout(1, x2 - 14, y2 + 16, 12))
    x, y = p2(540, 626)
    x2, y2 = p2(1100, 698)
    b.append(highlight(x, y, x2 - x, y2 - y))
    b.append(callout(2, x2 + 18, (y + y2) / 2, 12))
    b.append(step(0, 296, 1, ["One string column per CSV field"], 14))
    b.append(step(485, 296, 2, ["Structs and arrays: meta.profile is an array"], 14))
    return svg(940, 320, b)


def backup_clone():
    """The File menu with Clone, annotated."""
    shot, dw, dh, pt = screenshot(
        "file-menu-clone", 0, 2, 620, 330, crop=(243, 80, 420, 480)
    )
    b = [shot]
    x, y = pt(256, 418)
    x2, y2 = pt(536, 442)
    b.append(highlight(x, y, x2 - x, y2 - y))
    fx, fy = pt(258, 127)
    fx2, fy2 = pt(288, 151)
    b.append(highlight(fx, fy, fx2 - fx, fy2 - fy))
    b.append(callout(1, fx2 + 16, fy - 12, 12))
    b.append(callout(2, x2 + 18, (y + y2) / 2, 12))
    notes = [
        ["Open the File menu in the", "notebook toolbar"],
        ["Clone... and choose your", "home folder"],
        ["In the clone, set output_path", "and table names to your schema"],
        ["Attach the clone to Open FHIR", "Training Cluster and run it"],
    ]
    yy = 30
    for i, rows in enumerate(notes):
        b.append(step(dw + 60, yy, i + 1, rows, 15))
        yy += 34 + 18 * len(rows)
    return svg(940, 334, b)


DECK = {
    "file": "track-3-d1-2-fhir-amid-legacy",
    "slides": [
        title_slide(
            "FHIR amid legacy and proprietary systems",
            f"Track 3 · Thursday 2:00 · {EVENT}",
            "This session is about the data you actually have. Most clinical systems in a hospital "
            "were not built to speak FHIR, and many won't for years. I want to show that you can "
            "still use FHIR for analytics today, by treating it as the model you map into at the "
            "edge of your analytics platform. We'll look at the patterns for getting there, some "
            "tactics, and then a hands-on exercise that turns a flat CSV extract into FHIR "
            "resources, including the problems that exercise runs into.",
        ),
        diagram(
            "The reality: data arrives in many shapes",
            "Typical hospital system archetypes and the formats they actually emit",
            "reality",
            reality(),
            "Here is a generic picture of where clinical data lives. An EMR on a proprietary "
            "database, a laboratory system, radiology, patient administration, a long tail of "
            "departmental and niche systems, an integration engine carrying HL7 version 2 feeds "
            "between them, a data warehouse with nightly extracts, and a great deal of documents "
            "and free text. Look at the chips: SQL extracts, HL7 v2 messages, CSV, DICOM, PDF. Only "
            "occasionally FHIR. Most of this will not arrive as FHIR any time soon. The point of "
            "this session is that you don't have to wait for it to.",
        ),
        diagram(
            "Don't wait for a FHIR server",
            "Use FHIR as the analytic interchange model at the edge of your analytics platform",
            "edge",
            edge(),
            "The idea is simple. Leave the source systems alone. At the edge of your analytics "
            "platform, map each source into FHIR resources once. Store them as NDJSON and as "
            "tables, here Delta tables in Databricks. Then everything downstream - SQL on FHIR "
            "views, terminology, dashboards, research cohorts, machine learning features - is "
            "written against one model rather than against each source. Adding a new source means "
            "writing one more mapping, not rewriting every report. You don't need a FHIR server "
            "for any of this; FHIR is the data model, not the transport.",
        ),
        diagram(
            "Five ways in",
            "Patterns for getting FHIR from systems that don't produce it",
            "patterns",
            patterns(),
            "There are five common patterns. One: extract and map - take a CSV or SQL extract and "
            "transform it into FHIR. That's today's exercise. Two: convert HL7 version 2 messages "
            "to FHIR in the integration engine; Track 2 stream 2B is working on exactly this. "
            "Three: put a FHIR facade over an existing database, when data has to stay where it "
            "is. Four: Bulk Data export, where a vendor supports it - that's the next session. "
            "Five: turn free text into coded FHIR with NLP, which is Dion's strand. The effort "
            "dots are my rough judgement, not a measurement. Most organisations end up using "
            "several of these at once.",
        ),
        diagram(
            "Why bother: one analytic contract",
            "The same view runs over FHIR from any source, so analysis outlives any one system",
            "contract",
            contract(),
            "Why go to the trouble of mapping? Because the analysis becomes independent of the "
            "source. Our workspace has two Patient tables: one Synthea generated directly as FHIR, "
            "and one we mapped from the CSV extract. The same view definition - id, gender, birth "
            "date - runs over either of them and gives the same columns. Terminology bindings to "
            "SNOMED CT-AU, LOINC and AMT make the codes mean the same thing across sources. You can "
            "adopt this one resource type at a time, your queries travel to other sites and "
            "vendors, and you inherit AU Core and the community tooling.",
        ),
        bullets(
            "Tactics that work",
            "Practical rules for mapping legacy data into FHIR for analytics",
            [
                "Start from one question",
                "Map only what you need",
                "Keep source ids and provenance",
                "Bind local codes via ConceptMaps",
                "Validate against AU Core",
                "Check referential integrity",
                "Store NDJSON and Delta/Parquet",
            ],
            "Some tactics. Start from one question, and let it decide which resources and which "
            "elements you map - you don't need the whole of FHIR on day one. Keep the source "
            "identifiers and record where each resource came from, so you can trace a number back. "
            "Bind local codes to SNOMED CT-AU, LOINC or AMT with ConceptMaps, so the mapping is "
            "data rather than code; GLU-F here is an invented local code. Validate against AU Core "
            "where you can, check that references resolve, and keep NDJSON for exchange next to "
            "Delta or Parquet for querying.",
            name="tactics",
            drawing=tactics(),
            split=0.46,
        ),
        section(
            "Exercise: CSV to FHIR",
            "Now let's make this concrete. The exercise takes the Synthea CSV export, which stands "
            "in for a legacy flat extract, and turns three of its tables into FHIR resources. It's "
            "deliberately simple code, written with plain Spark functions, so you can see every "
            "decision the mapping makes - including some decisions that turn out to be wrong. "
            "That's the useful part.",
        ),
        diagram(
            "From flat to nested",
            "A row of synthea_csv.patients and the Patient resource the notebook makes from it",
            "flat-to-nested",
            flat_to_nested(),
            "On the left is the CSV patients table: one string column per field, 1,143 rows. Row "
            "four is highlighted. On the right is the Patient the notebook makes from that row. Id "
            "becomes the resource id. SSN, driver's licence and passport - three separate columns - "
            "become entries in one identifier array, each with a system. GENDER is M or F, which "
            "maps to the FHIR codes male and female. BIRTHDATE becomes birthDate, and DEATHDATE "
            "becomes deceasedDateTime, but only when it has a value. Note this extract is US "
            "data: social security numbers, a Massachusetts address.",
        ),
        diagram(
            "The notebook as a pipeline",
            "transform_csv_to_fhir: map, serialise, check, store, then encode with Pathling",
            "pipeline",
            pipeline(),
            "Here is the whole notebook. It reads three synthea_csv tables. It maps each one with "
            "Spark struct, array and when functions, then serialises each row with to_json, giving "
            "one FHIR resource per line - NDJSON. It validates by counting lines and parsing "
            "sample resources, and it checks referential integrity with left anti joins, looking "
            "for encounters without patients and immunisations without encounters. It saves the "
            "JSON text to synthea_transformed. Finally Pathling's encoder reads the NDJSON into "
            "typed, nested columns, and writes synthea_encoded. That last schema is the one you "
            "can query with views.",
        ),
        diagram(
            "The mapping in code",
            "Abridged from the Patient cell and the Pathling cells of transform_csv_to_fhir",
            "mapping-code",
            mapping_code(),
            "This is the real code, trimmed. The identifier array has one when clause per source "
            "column, so a patient without a driver's licence gets a null in that position - we'll "
            "come back to that. Gender is a chained when with an otherwise, which is a value set "
            "mapping with a default. On the right, the Pathling part is short: create a context, "
            "read the NDJSON as text, encode it as Patient, gather the three resource types into "
            "one dataset, and write it as tables. The encoder does the hard work of turning JSON "
            "into the full FHIR structure.",
        ),
        diagram(
            "Pitfalls the exercise exposes",
            "Each one is visible in the data the notebook produced",
            "pitfalls",
            pitfalls(),
            "Every one of these shows up in our workspace. Immunisation ids join two UUIDs and a "
            "code, giving 76 or 77 characters - FHIR ids allow 64. That's a known issue to fix. "
            "Dates: birth dates have no time zone, while observations are UTC, so a naive date "
            "comparison puts this baby's first measurement the day before birth. Unmapped "
            "encounter classes like home and snf fall through to ambulatory. Vaccines use US CVX "
            "codes, not AMT. And shape errors are silent: identifier type was built as a Coding, "
            "not a CodeableConcept, so the encoder dropped it for every patient.",
        ),
        diagram(
            "Demo",
            "What I'll show in the workspace",
            "demo",
            demo(),
            "Live, in Databricks. One: Workspace, Repos, John.Grimes, open-fhir-training, "
            "notebooks, csv_to_fhir, and open transform_csv_to_fhir. Two: check the compute "
            "dropdown says Open FHIR Training Cluster, not Serverless. Three: scroll to the Patient "
            "select and walk through identifier, gender and address. Four: the Encounter cell - "
            "the class mapping and its otherwise - and the Immunization id. Five: the referential "
            "integrity cell. I won't run anything that writes. Six: open Catalog, show "
            "synthea_csv.patients Sample Data, then synthea.patient Overview, to compare flat and "
            "nested.",
        ),
        diagram(
            "Your turn",
            "Map one more CSV table into FHIR, in your own copy and your own schema",
            "your-turn",
            your_turn(),
            "For the rest of the block, clone the notebook into your home folder - never edit the "
            "shared one. Create a personal schema and change the output path and table names to "
            "point at it. Then map one more table: conditions to Condition with SNOMED CT codes, or "
            "observations to Observation with LOINC. The code on the right is a starting point for "
            "conditions; it hashes four columns into a 64-character id, which avoids the id length "
            "problem. Encode the result with Pathling and query it. If you finish, compare your "
            "Patient with AU Core Patient.",
        ),
        section(
            "Demo walkthrough (backup)",
            "If the live demo doesn't cooperate, here are the same steps as screenshots, so you "
            "can follow along on your own laptop. The first shows the notebook and where to attach "
            "it, the second compares the flat extract with the FHIR table in Catalog Explorer, and "
            "the third shows how to clone the notebook so you can change it safely.",
        ),
        diagram(
            "The CSV to FHIR notebook",
            "notebooks > csv_to_fhir > transform_csv_to_fhir, attached to the training cluster",
            "backup-notebook",
            backup_notebook(),
            "This is the notebook as you'll find it. One: the tab shows transform_csv_to_fhir, "
            "opened from the open-fhir-training Git folder - the banner says so. Two: the compute "
            "selector shows Open FHIR Training Cluster; Pathling is installed there, not on "
            "Serverless. Three: please don't press Run all in the shared copy, because later cells "
            "write NDJSON files and shared tables. Four: the introduction lists the three resource "
            "types the notebook creates. Read down from here cell by cell.",
        ),
        diagram(
            "Flat versus nested",
            "The same patients in the CSV extract and as FHIR, in Catalog Explorer",
            "backup-compare",
            backup_compare(),
            "In Catalog Explorer, open hive_metastore, synthea_csv, patients, and the Sample Data "
            "tab. One: every field is its own string column - Id, BIRTHDATE, SSN and so on. Then "
            "open synthea, patient, and the Overview tab. Two: here the columns follow the FHIR "
            "structure - meta is a struct, meta.profile is an array of strings. That is the shape "
            "your mapping has to produce, and the shape the Pathling encoder writes into "
            "synthea_encoded.",
        ),
        diagram(
            "Cloning the notebook",
            "Work in your own copy, writing to your own schema",
            "backup-clone",
            backup_clone(),
            "To make your own copy: one, open the File menu in the notebook toolbar. Two, choose "
            "Clone, and save it in your home folder. Three, in the clone, change output_path and "
            "every schema and table name to your personal schema - for example jane_citizen - so "
            "you never overwrite synthea_transformed or synthea_encoded. Four, attach the clone to "
            "Open FHIR Training Cluster. Then you can run it, change it and extend it freely.",
        ),
        closing(
            "Questions?",
            PRESENTER,
            "That's the legacy session. The short version: you don't need to wait for FHIR - map "
            "what you have into it at the edge of your platform, and check your mapping as "
            "carefully as your analysis. The exercises are in the repository. Next block, we look "
            "at getting data out of systems that do speak FHIR, with Bulk Data and Pathling.",
            [
                (REPO_URL, "Exercises"),
                (SOF_URL, "sql-on-fhir.org"),
                (PATHLING_URL, "pathling.csiro.au"),
            ],
        ),
    ],
}
