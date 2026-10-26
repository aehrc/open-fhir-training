"""Day 1, 3:30 Track 3 slab: getting data out with Bulk Data and Pathling.

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
    lines,
    path,
    pill,
    pill_width,
    rect,
    screenshot,
    section,
    svg,
    text,
    title_slide,
)

from decks._shared import EVENT, PATHLING_URL, PRESENTER, REPO_URL

BULK_URL = "https://hl7.org/fhir/uv/bulkdata/"


def person(x, y, fill=TEAL, s=1.0):
    """A small person glyph centred on (x, y)."""
    return circle(x, y - 9 * s, 6 * s, fill, "#fff", 1.2) + path(
        f"M{x - 10 * s},{y + 12 * s} Q{x - 10 * s},{y} {x},{y} Q{x + 10 * s},{y} "
        f"{x + 10 * s},{y + 12 * s} z",
        stroke="#fff",
        sw=1.2,
        arrow=None,
        fill=fill,
    )


def step(n, x, y, title, detail=None, fs=15):
    """A numbered teal marker with a bold title and an optional muted line below."""
    out = callout(n, x + 14, y, 13) + text(x + 36, y + 5, title, fs, "start", 700)
    if detail:
        out += text(x + 36, y + 26, detail, 14, "start", 400, MUTED)
    return out


def one_vs_many():
    """REST read/search for one patient beside bulk export for a population."""
    b = [rect(10, 8, 450, 325, YELLOW, rx=12), rect(480, 8, 450, 325, BLUE, rx=12)]
    b.append(text(30, 42, "One patient", 19, "start", 700))
    b.append(text(30, 64, "REST read and search", 15, "start", 400, MUTED))
    b.append(person(400, 50, INK, 1.3))
    b.append(
        code(
            30,
            84,
            410,
            [
                "GET [base]/Patient/123",
                "GET [base]/Condition?patient=123",
                "GET [base]/Observation?patient=123",
            ],
            fs=14,
            fill="#fff",
        )
    )
    b.append(line(235, 166, 235, 192))
    b.append(
        box(
            30,
            196,
            410,
            120,
            "#fff",
            [
                "Synchronous: answer in seconds",
                "One resource, or a Bundle of results",
                "Paged, one request per question",
                "Suits apps working on one record",
            ],
            15,
        )
    )
    b.append(text(500, 42, "A population", 19, "start", 700))
    b.append(text(500, 64, "Bulk Data $export", 15, "start", 400, MUTED))
    for i in range(7):
        for j in range(2):
            b.append(person(752 + i * 25, 36 + j * 28, INK, 0.75))
    b.append(
        code(
            500,
            84,
            410,
            [
                "GET [base]/Patient/$export",
                "Accept: application/fhir+json",
                "Prefer: respond-async",
            ],
            fs=14,
            fill="#fff",
        )
    )
    b.append(line(705, 166, 705, 192))
    b.append(rect(500, 196, 410, 120, "#fff"))
    files = ["Patient", "Encounter", "Condition", "Observation"]
    for i, f in enumerate(files):
        b.append(box(512 + i * 98, 208, 90, 40, CYAN, [f], 13))
    b.append(
        lines(
            705,
            284,
            [
                "Asynchronous: poll until ready",
                "NDJSON files, one set per resource type",
            ],
            15,
        )
    )
    return svg(940, 340, b)


def export_flow():
    """The $export async request pattern as a sequence diagram, with a manifest."""
    cx, sx = 80, 500
    b = [
        box(cx - 65, 4, 130, 36, YELLOW, ["Client"], 15, 700),
        box(sx - 75, 4, 150, 36, BLUE, ["FHIR server"], 15, 700),
        line(cx, 40, cx, 336, "#BBBBBB", 1.4, "4 4", None),
        line(sx, 40, sx, 336, "#BBBBBB", 1.4, "4 4", None),
    ]
    mid = (cx + sx) / 2

    def msg(y, top, bottom=None, back=False, teal=False):
        x1, x2 = (sx, cx) if back else (cx, sx)
        col = TEAL if teal else GREY
        out = line(
            x1 + (-3 if back else 3),
            y,
            x2 + (3 if back else -3),
            y,
            col,
            1.8,
            "6 4" if back else None,
            "at" if teal else "ag",
        )
        out += text(mid, y - 7, top, 13.5, weight=700, family="JetBrains Mono")
        if bottom:
            out += text(mid, y + 17, bottom, 13, fill=MUTED)
        return out

    b.append(
        msg(
            70,
            "GET [base]/Patient/$export",
            "Accept: application/fhir+json · Prefer: respond-async",
        )
    )
    b.append(msg(122, "202 Accepted", "Content-Location: [status URL]", back=True))
    b.append(rect(28, 146, 524, 104, "none", TEAL, 1.4, 8, "5 4"))
    b.append(pill(36, 152, "poll, backing off", AMBER, 12))
    b.append(msg(186, "GET [status URL]"))
    b.append(
        msg(
            222,
            "202 Accepted",
            "X-Progress: 50% complete · Retry-After: 120",
            back=True,
        )
    )
    b.append(msg(282, "200 OK + manifest (JSON)", back=True, teal=True))
    b.append(msg(326, "GET each output url -> NDJSON"))
    b.append(
        code(
            600,
            64,
            332,
            [
                "{",
                '  "transactionTime":',
                '      "2021-01-01T00:00:00Z",',
                '  "requiresAccessToken": true,',
                '  "output": [',
                '    {"type": "Patient",',
                '     "url": ".../patient_1.ndjson"},',
                '    {"type": "Observation", ...}',
                "  ],",
                '  "error": []',
                "}",
            ],
            "Manifest (abridged)",
            12.5,
            1.4,
            title_fill=CYAN,
        )
    )
    b.append(path(f"M{sx + 4},282 H570 V160 H598", TEAL, 1.6, "5 4", "at"))
    return svg(940, 340, b)


def levels():
    """Export levels as nested scopes, with example requests using the parameters."""
    b = [
        rect(10, 10, 360, 320, LAVENDER, rx=14),
        text(30, 42, "System", 18, "start", 700),
        text(30, 64, "[base]/$export", 14, "start", 400, INK, "JetBrains Mono"),
        text(30, 86, "every resource on the server", 14, "start", 400, MUTED),
        rect(30, 104, 320, 210, BLUE, rx=12),
        text(48, 134, "Patient", 18, "start", 700),
        text(
            48, 156, "[base]/Patient/$export", 14, "start", 400, INK, "JetBrains Mono"
        ),
        text(48, 178, "data about all patients", 14, "start", 400, MUTED),
        rect(50, 196, 280, 102, MINT, rx=10),
        text(68, 226, "Group", 18, "start", 700),
        text(
            68,
            248,
            "[base]/Group/[id]/$export",
            14,
            "start",
            400,
            INK,
            "JetBrains Mono",
        ),
        text(68, 270, "patients in one cohort", 14, "start", 400, MUTED),
    ]
    params = [
        (
            "_type",
            "Only these resource types",
            ["[base]/Patient/$export", "  ?_type=Patient,Condition,Observation"],
        ),
        (
            "_since",
            "Only resources changed after this instant",
            ["[base]/Group/[id]/$export", "  ?_since=2026-10-01T00:00:00Z"],
        ),
        (
            "_typeFilter",
            "A search query per type (experimental, URL-encoded)",
            [
                "[base]/Patient/$export?_type=Observation",
                "  &_typeFilter=Observation?category=laboratory",
            ],
        ),
    ]
    for i, (name, desc, req) in enumerate(params):
        y = 10 + i * 110
        b.append(rect(392, y, 538, 100, "#fff", rx=10))
        b.append(pill(408, y + 12, name, PEACH, 14))
        b.append(
            text(408 + pill_width(name, 14) + 12, y + 30, desc, 14, "start", 400, MUTED)
        )
        for j, r in enumerate(req):
            b.append(
                text(
                    408,
                    y + 62 + j * 22,
                    r,
                    13.5,
                    "start",
                    400,
                    "#222",
                    "JetBrains Mono",
                )
            )
    return svg(940, 340, b)


def ndjson():
    """One resource per line, one file set per type, read by Pathling by name."""
    b = [rect(10, 10, 560, 200, "#F7F7F7")]
    b.append(rect(10, 10, 560, 34, LAVENDER))
    b.append(
        text(26, 33, "Patient.00000.ndjson", 15, "start", 700, family="JetBrains Mono")
    )
    rows = [
        '{"resourceType":"Patient","id":"9f8e2002-...","gender":"male",...}',
        '{"resourceType":"Patient","id":"ed7e40af-...","gender":"male",...}',
        '{"resourceType":"Patient","id":"5b01a645-...","gender":"female",...}',
        "...",
    ]
    for i, r in enumerate(rows):
        b.append(text(48, 74 + i * 34, r, 12.5, "start", 400, "#222", "JetBrains Mono"))
        if i < 3:
            b.append(
                text(
                    28,
                    74 + i * 34,
                    str(i + 1),
                    12.5,
                    "middle",
                    700,
                    TEAL,
                    "JetBrains Mono",
                )
            )
    b.append(
        text(
            290,
            200,
            "one complete JSON resource per line - no Bundle wrapper",
            13,
            fill=MUTED,
            italic=True,
        )
    )
    b.append(rect(600, 10, 330, 200, "#fff", rx=10))
    b.append(
        text(616, 36, "synthea/au/fhir/", 15, "start", 700, family="JetBrains Mono")
    )
    files = [
        "Patient.00000.ndjson",
        "Encounter.00000.ndjson",
        "Condition.00000.ndjson",
        "Observation.00000.ndjson",
        "...  15 resource types",
    ]
    for i, f in enumerate(files):
        b.append(
            text(
                636,
                66 + i * 30,
                f,
                14,
                "start",
                400,
                MUTED if i == 4 else "#222",
                "JetBrains Mono",
            )
        )
    b.append(line(290, 214, 290, 240))
    b.append(line(765, 214, 765, 240))
    b.append(rect(10, 244, 920, 86, MINT, rx=12))
    b.append(
        lines(
            470,
            287,
            [
                "Easy to stream, split and process in parallel: each line parses on its own",
                "Pathling takes the resource type from the file name: Patient.00000.ndjson -> Patient",
            ],
            16,
        )
    )
    return svg(940, 340, b)


def backend_services():
    """SMART Backend Services: register a key, sign a JWT, get a token, call $export."""
    b = [
        box(10, 18, 200, 56, YELLOW, ["Backend client", "holds a private key"], 14),
        box(370, 18, 200, 56, LAVENDER, ["Authorisation server", "token endpoint"], 14),
        box(730, 18, 200, 56, BLUE, ["FHIR server", "$export"], 14),
        line(213, 34, 366, 34),
        text(290, 27, "0 key · 2 signed JWT", 12, fill=MUTED),
        line(367, 58, 214, 58, dash="5 4"),
        text(290, 72, "3 access token", 12, fill=MUTED),
        path("M110,76 V98 H830 V78", TEAL, 2, arrow="at"),
        text(650, 92, "4 $export with the token", 12, fill=TEAL, weight=700),
    ]
    cards = [
        (
            "0  Register (once)",
            YELLOW,
            [
                "client_id issued",
                "public key as a JWKS",
                "  (or a JWKS URL)",
                "private key never",
                "  leaves the client",
                "",
            ],
        ),
        (
            "1  Sign a JWT",
            PEACH,
            [
                "alg: RS384 or ES384",
                "iss = sub = client_id",
                "aud = token endpoint",
                "exp: <= 5 min ahead",
                "jti: unique nonce",
                "",
            ],
        ),
        (
            "2  POST for a token",
            LAVENDER,
            [
                "grant_type=",
                "  client_credentials",
                "client_assertion_type=",
                "  ...:jwt-bearer",
                "client_assertion=<JWT>",
                "scope=system/*.rs",
            ],
        ),
        (
            "3-4  Token, then $export",
            MINT,
            [
                "access_token: ...",
                "token_type: bearer",
                "expires_in: 300",
                "GET [base]/Patient/",
                "  $export  Authorization:",
                "  Bearer <access_token>",
            ],
        ),
    ]
    for i, (title, fill, rows) in enumerate(cards):
        b.append(code(10 + i * 233, 114, 222, rows, title, 12, 1.4, title_fill=fill))
    b.append(rect(10, 278, 921, 54, "#fff", TEAL, 2, 10))
    b.append(
        lines(
            470,
            305,
            [
                "Tokens are short-lived (expires_in SHOULD NOT exceed 300 s) and refresh tokens SHOULD NOT be",
                "issued: the client signs a new JWT whenever it needs a new token",
            ],
            14,
        )
    )
    return svg(940, 340, b)


def pathling_arch():
    """Pathling's libraries, modules and where it runs."""
    b = [rect(10, 10, 920, 78, YELLOW, rx=12)]
    b.append(text(30, 44, "Use it from", 17, "start", 700))
    b.append(text(30, 68, "your code or a service", 14, "start", 400, MUTED))
    for i, lang in enumerate(["Python", "R", "Java", "Scala"]):
        b.append(box(200 + i * 112, 26, 100, 46, "#fff", [lang], 15, 700))
    b.append(box(660, 26, 252, 46, PEACH, ["Pathling server (FHIR API)"], 15, 700))
    b.append(line(470, 90, 470, 106))
    b.append(rect(10, 108, 920, 120, LAVENDER, rx=12))
    b.append(text(30, 136, "Pathling", 17, "start", 700))
    mods = [
        (["FHIR encoders", "FHIR -> data frames"]),
        (["SQL on FHIR views", "ViewDefinitions"]),
        (["FHIRPath engine", "expressions over FHIR"]),
        (["Terminology functions", "member_of, translate, ..."]),
    ]
    for i, rows in enumerate(mods):
        b.append(box(30 + i * 224, 150, 208, 64, "#fff", rows, 14.5))
    b.append(line(470, 230, 470, 246))
    b.append(rect(10, 248, 600, 84, BLUE, rx=12))
    b.append(text(30, 276, "Apache Spark, anywhere", 17, "start", 700))
    for i, where in enumerate(["Laptop (pip)", "Databricks", "Any Spark cluster"]):
        b.append(box(30 + i * 190, 288, 176, 34, "#fff", [where], 14))
    b.append(rect(630, 248, 300, 84, MINT, rx=12))
    b.append(text(650, 276, "Stores and reads", 17, "start", 700))
    b.append(text(650, 304, "Delta · Parquet · NDJSON · Bundles", 14, "start"))
    b.append(
        text(650, 324, "terminology server or local store", 13, "start", 400, MUTED)
    )
    return svg(940, 340, b)


def encoders():
    """NDJSON to nested data frame to tables, beside the patient schema screenshot."""
    b = [
        code(
            10,
            8,
            470,
            [
                '{"resourceType": "Patient",',
                ' "meta": {"profile": [".../au-core-patient",',
                '                      ".../au-erequesting-patient"]},',
                ' "gender": "male",',
                ' "name": [{"family": "Lakin515", ...}], ...}',
            ],
            "NDJSON or Bundles",
            12,
            1.4,
            title_fill=CYAN,
        )
    ]
    b.append(line(40, 140, 40, 164))
    b.append(
        text(
            54,
            157,
            'pc.read.ndjson(...)  ·  pc.encode(df, "Patient")',
            12.5,
            "start",
            400,
            MUTED,
            "JetBrains Mono",
        )
    )
    b.append(rect(10, 168, 470, 98, LAVENDER, rx=10))
    b.append(
        text(26, 192, "Spark data frame: one column per element", 15, "start", 700)
    )
    cols = [
        ("id", "string"),
        ("meta", "struct"),
        ("gender", "string"),
        ("name", "array<struct>"),
    ]
    x = 26
    for c, t in cols:
        w = 70 if c != "name" else 140
        w = max(w, len(t) * 7.5 + 16)
        b.append(box(x, 204, w, 50, "#fff", [c, t], 13))
        x += w + 8
    b.append(line(40, 268, 40, 290))
    b.append(
        text(
            54,
            284,
            "write.tables()  ·  write.delta(...)",
            12.5,
            "start",
            400,
            MUTED,
            "JetBrains Mono",
        )
    )
    b.append(
        box(
            10,
            294,
            470,
            40,
            MINT,
            ["Delta / Parquet tables - lossless, round-trips to FHIR"],
            14.5,
        )
    )
    crop = (540, 295, 520, 480)
    shot, w, h, pt = screenshot("patient-schema", 560, 8, 370, 326, crop)
    b.append(shot)
    for n, py in enumerate([420, 642, 753], 1):
        hx, hy = pt(542, py - 17)
        b.append(highlight(hx, hy, w - 4, 34 * w / crop[2]))
        b.append(callout(n, 560 + w + 16, pt(0, py)[1], 12))
    return svg(940, 340, b)


def import_code():
    """The two import notebooks as code cards, with numbered annotations."""
    b = [
        code(
            10,
            6,
            560,
            [
                "pc = PathlingContext.create()                     (1)",
                'pc.spark.sql("CREATE SCHEMA IF NOT EXISTS synthea")',
                'pc.spark.catalog.setCurrentDatabase("synthea")',
                "source = pc.read.ndjson(                          (2)",
                '    "s3://open-fhir-training-data/synthea/au/fhir")',
                "source.resource_types()                           (3)",
                "source.write.tables()                             (4)",
            ],
            "notebooks/synthea/import_synthea.py",
            12.5,
            1.4,
        )
    ]
    b.append(
        code(
            10,
            196,
            560,
            [
                "pc = PathlingContext.create(enable_extensions=True)  (5)",
                "source = pc.read.ndjson(",
                '    "s3://.../mimic-iv-clinical-database-demo-on-fhir-2.1.0/fhir",',
                "    file_name_mapper=lambda file_name: re.findall(   (6)",
                '        r"Mimic(\\w+?)(?:ED|ICU|...|VitalSignsED)?$", file_name))',
            ],
            "notebooks/mimic_iv/import_mimic_iv_demo.py",
            11.5,
            1.4,
            title_fill=PINK,
        )
    )
    notes = [
        ("Start Spark with Pathling", "encoders, FHIRPath, terminology"),
        ("Point at a directory", "of NDJSON files"),
        ("List what was found", "15 resource types for Synthea"),
        ("One Delta table per type", "in the current schema"),
        ("Keep FHIR extensions", "e.g. US Core race in MIMIC"),
        ("Map file names to types", "MimicObservationLabevents -> Observation"),
    ]
    for i, (t, d) in enumerate(notes):
        y = 26 + i * 54
        b.append(callout(i + 1, 604, y, 13))
        b.append(text(626, y + 5, t, 14.5, "start", 700))
        b.append(text(626, y + 25, d, 13, "start", 400, MUTED))
    return svg(940, 340, b)


def server():
    """The Pathling server: one box with its capabilities around it."""
    b = [
        box(
            350,
            128,
            240,
            84,
            PEACH,
            ["Pathling server", "same engine, as a service"],
            16,
            700,
        )
    ]
    caps = [
        (10, 10, BLUE, ["FHIR REST API", "read, search, create, update"]),
        (350, 10, MINT, ["Bulk $import and $export", "NDJSON in and out"]),
        (690, 10, LAVENDER, ["SQL on FHIR", "$sql-run · $sql-export"]),
        (10, 250, YELLOW, ["SMART on FHIR auth", "for apps and backends"]),
        (350, 250, CYAN, ["Admin UI", "browse and manage"]),
        (690, 250, PINK, ["Docker image", "Helm chart"]),
    ]
    for x, y, fill, rows in caps:
        b.append(box(x, y, 240, 78, fill, rows, 14.5))
        tx = x + 120
        if tx < 350:
            b.append(
                line(
                    tx,
                    y + 78 if y < 100 else y,
                    352,
                    160 if y < 100 else 180,
                    GREY,
                    1.4,
                    None,
                    None,
                )
            )
        elif tx > 590:
            b.append(
                line(
                    tx,
                    y + 78 if y < 100 else y,
                    588,
                    160 if y < 100 else 180,
                    GREY,
                    1.4,
                    None,
                    None,
                )
            )
        else:
            b.append(
                line(
                    tx,
                    y + 78 if y < 100 else y,
                    tx,
                    128 if y < 100 else 212,
                    GREY,
                    1.4,
                    None,
                    None,
                )
            )
    b.append(text(130, 175, "Notebook: you run the job", 14, fill=MUTED, italic=True))
    b.append(text(810, 175, "Server: others call an API", 14, fill=MUTED, italic=True))
    return svg(940, 340, b)


def demo():
    """What I show live, beside a thumbnail of the notebook output."""
    steps = [
        (
            "Open notebooks/synthea/import_synthea",
            "Workspace > Repos > ... > open-fhir-training",
        ),
        (
            "Attach Open FHIR Training Cluster",
            "not Serverless - Pathling is not installed there",
        ),
        ("Run cells 2-4", "import, create the context, read the NDJSON"),
        ("resource_types() lists 15 types", "Patient, Observation, Condition, ..."),
        ("Explain write.tables() - don't run it", "the tables are already loaded"),
        ("Catalog > hive_metastore > synthea", "patient: Overview, then Sample Data"),
    ]
    b = []
    for i, (t, d) in enumerate(steps):
        b.append(step(i + 1, 0, 20 + i * 55, t, d))
    shot, w, h, pt = screenshot(
        "import-synthea-output", 530, 6, 405, 330, (310, 260, 620, 500)
    )
    b.append(shot)
    x, y = pt(318, 354)
    b.append(highlight(x, y, pt(700, 0)[0] - x, pt(0, 642)[1] - y))
    b.append(callout(4, *pt(720, 380), 12))
    return svg(940, 340, b)


def your_turn():
    """Three verified SQL queries and a stretch, as cards."""
    q1 = [
        "SELECT 'patient' AS type, count(*) AS n",
        "  FROM hive_metastore.synthea.patient",
        "UNION ALL SELECT 'observation', count(*)",
        "  FROM hive_metastore.synthea.observation",
    ]
    q2 = [
        "SELECT id, gender, birthDate,",
        "       name[0].family AS family",
        "  FROM hive_metastore.synthea.patient",
        "  LIMIT 10",
    ]
    q3 = [
        "SELECT code.coding[0].display AS condition,",
        "       count(*) AS n",
        "  FROM hive_metastore.synthea.condition",
        "  GROUP BY 1 ORDER BY 2 DESC LIMIT 10",
    ]
    q4 = [
        "SELECT id, explode(meta.profile) AS profile",
        "  FROM hive_metastore.synthea.patient",
        "  LIMIT 10",
        "-- one row per profile, 2 per patient",
    ]
    b = [
        code(5, 5, 460, q1, "1  Rows per resource type", 12.5, 1.4, title_fill=CYAN),
        code(
            475, 5, 460, q2, "2  Reach into nested elements", 12.5, 1.4, title_fill=CYAN
        ),
        code(
            5, 141, 460, q3, "3  Group by a coded element", 12.5, 1.4, title_fill=CYAN
        ),
        code(
            475,
            141,
            460,
            q4,
            "Stretch: explode() a repeating element",
            12.5,
            1.4,
            title_fill=AMBER,
        ),
        rect(5, 280, 930, 52, MINT, rx=10),
        text(
            470,
            302,
            "SQL Editor > Serverless Starter Warehouse · add the other 13 types to query 1",
            15,
        ),
        text(
            470,
            323,
            "Then pick a resource you care about and look at its columns in the Catalog",
            14,
            fill=MUTED,
        ),
    ]
    return svg(940, 340, b)


def backup_shot(name, crop, marks, sw=600):
    """A screenshot on the left with numbered callouts and step text on the right."""
    shot, w, h, pt = screenshot(name, 5, 5, sw, 330, crop)
    b = [shot]
    for i, (px, py, _, _) in enumerate(marks):
        b.append(callout(i + 1, *pt(px, py), 13))
    tx = 5 + w + 30
    for i, (_, _, t, d) in enumerate(marks):
        y = 30 + i * 80
        b.append(callout(i + 1, tx + 14, y, 13))
        b.append(text(tx + 36, y + 5, t, 15, "start", 700))
        for j, dl in enumerate(d):
            b.append(text(tx + 36, y + 27 + j * 20, dl, 13.5, "start", 400, MUTED))
    return svg(940, 340, b)


DECK = {
    "file": "track-3-d1-3-getting-data-out",
    "slides": [
        title_slide(
            "Getting data out: Bulk Data and Pathling",
            f"Thursday 3:30 · {EVENT}",
            "This block is about the first step on the standards map: getting FHIR data out of the "
            "systems that hold it, and into a form we can analyse. I'll cover the FHIR Bulk Data "
            "Access specification, the SMART Backend Services authorisation that goes with it, and "
            "the NDJSON files it produces. Then I'll introduce Pathling, which is the tool we use "
            "in the workspace to turn those files into tables. After about 20 minutes of slides "
            "I'll show the Synthea import notebook live, and then it's over to you.",
        ),
        diagram(
            "One patient or a whole population",
            "The REST API answers questions about a record; Bulk Data exports everyone at once",
            "one-vs-many",
            one_vs_many(),
            "Most FHIR APIs are built for one record at a time. An app reads a patient, then "
            "searches for their conditions and observations, and gets answers back in seconds. "
            "That works well inside a clinical workflow. Analytics is different: we want every "
            "patient, or a large cohort, and we want all of their data. Paging through searches "
            "for thousands of patients is slow and puts load on the server. The Bulk Data Access "
            "specification adds an export operation for this case. The server prepares the data "
            "in the background and hands back files, one set per resource type.",
        ),
        diagram(
            "The $export flow",
            "Kick off, poll the status URL, then download the files listed in the manifest",
            "export-flow",
            export_flow(),
            "Here is the whole conversation. The client sends a GET to the export endpoint with "
            "two headers: Accept application/fhir+json, and Prefer respond-async. The server "
            "replies 202 Accepted, with a Content-Location header pointing at a status URL. The "
            "client polls that URL, backing off between requests. While the job runs, the server "
            "keeps saying 202, optionally with an X-Progress header and a Retry-After. When it's "
            "finished, it returns 200 with a JSON manifest: the transaction time, and an output "
            "array with a type and URL for each file. The client then downloads each file, which "
            "may live on a separate file server.",
        ),
        diagram(
            "Levels and parameters",
            "Choose the scope of the export, then narrow it by type, time and search",
            "levels",
            levels(),
            "There are three levels. System level exports everything on the server, which also "
            "suits things like backups. Patient level exports data about all patients. Group "
            "level exports data for the patients in one Group resource, which is how you would "
            "export a defined cohort. Then there are parameters. _type limits the resource types. "
            "_since returns only resources changed after an instant, so you can do incremental "
            "loads using the transaction time from your previous manifest. _typeFilter applies a "
            "search query per type; it is marked experimental, and in a real request the query is "
            "URL-encoded.",
        ),
        diagram(
            "NDJSON: newline-delimited JSON",
            "One resource per line, one file set per resource type",
            "ndjson",
            ndjson(),
            "The output format is NDJSON: newline-delimited JSON. Each line is one complete FHIR "
            "resource, with no Bundle around it. That makes the files easy to stream, split and "
            "process in parallel, because every line parses on its own. Each file holds one "
            "resource type, and large exports are split across several files. The Synthea data in "
            "our workspace uses the same bulk-style naming, for example Patient.00000.ndjson. "
            "Pathling takes the resource type from the start of the file name, so it reads a "
            "directory like this without any configuration.",
        ),
        diagram(
            "SMART Backend Services",
            "System-to-system authorisation for bulk export, with no user in the loop",
            "backend-services",
            backend_services(),
            "Bulk export usually runs with no user present, so it is authorised with SMART "
            "Backend Services, part of SMART App Launch 2.2. First, once, the client registers its "
            "public key with the authorisation server, as a JSON Web Key Set. Each time it needs "
            "access, it signs a short-lived JWT with its private key: issuer and subject are its "
            "client ID, audience is the token endpoint. It posts that to the token endpoint with "
            "the client credentials grant and system scopes, such as system/*.rs for read and "
            "search on everything. It gets back a bearer token, valid for about five minutes, and "
            "uses it to call $export.",
        ),
        section(
            "Pathling",
            "So now we have a directory of NDJSON files. The next question is how to analyse them. "
            "FHIR resources are deeply nested, with repeating elements, choice types and "
            "extensions, and most analytic tools expect flat tables. This is where Pathling comes "
            "in. Pathling is the set of open-source tools my team at CSIRO builds for FHIR "
            "analytics, and it is what all the notebooks in our workspace use. I'll explain what "
            "it is, how it encodes FHIR, and how the import notebooks use it.",
        ),
        diagram(
            "What Pathling is",
            "Open-source FHIR analytics on Apache Spark, as libraries and as a server",
            "pathling-arch",
            pathling_arch(),
            "Pathling is open source, under the Apache 2.0 licence. You can use it as a library "
            "from Python, R, Java or Scala, or run it as a FHIR server. Inside there are four main "
            "parts: the FHIR encoders, which turn FHIR into Spark data frames; SQL on FHIR views; "
            "a FHIRPath engine; and terminology functions such as member_of and translate, backed "
            "by a terminology server or a local store. It is built on Apache Spark, so the same "
            "code runs on a laptop after a pip install, on Databricks as we do here, or on any "
            "Spark cluster.",
        ),
        diagram(
            "FHIR encoders",
            "FHIR JSON becomes nested Spark columns, with nothing lost along the way",
            "encoders",
            encoders(),
            "The encoders are the foundation. They take FHIR JSON, from NDJSON files, Bundles or "
            "an existing data frame, and turn each resource type into a Spark data frame. Every "
            "element becomes a column, keeping the FHIR structure: complex types become structs "
            "and repeating elements become arrays. You can see that on the right, in the patient "
            "table in our catalog. One, meta is a struct. Two, meta.profile is an array of "
            "strings. Three, meta.security is an array of structs. Because nothing is dropped, you "
            "can write the tables out as Delta or Parquet and turn them back into FHIR later.",
        ),
        diagram(
            "The import code",
            "Four lines of Pathling load a whole bulk export; the MIMIC variant needs two options",
            "import-code",
            import_code(),
            "This is the real code from our two import notebooks. One, create a Pathling context, "
            "which sets up Spark with the encoders. Two, point read.ndjson at the directory. "
            "Three, resource_types lists what was found: 15 types for Synthea. Four, write.tables "
            "writes one Delta table per resource type into the current schema. The MIMIC demo "
            "needs two changes. Five, enable_extensions keeps FHIR extensions, which MIMIC uses "
            "for things like US Core race. Six, its file names don't follow the bulk convention, "
            "so a file name mapper pulls the resource type out of names like "
            "MimicObservationLabevents.",
        ),
        diagram(
            "The Pathling server",
            "When you want a service that others can call, rather than a notebook",
            "server",
            server(),
            "Everything so far runs in a notebook: you run the job. Sometimes you want a service "
            "instead, that other systems call. The Pathling server packages the same engine "
            "behind a FHIR API. It supports the REST API, bulk $import and $export, so it can "
            "receive and serve NDJSON, and the SQL on FHIR operations $sql-run and $sql-export, "
            "which run a view and return the result. It supports SMART on FHIR authorisation, has "
            "an admin UI, and ships as a Docker image with a Helm chart. We won't use the server "
            "in the workspace, but it's worth knowing it exists.",
        ),
        diagram(
            "Demo",
            "The Synthea import notebook and the tables it produced",
            "demo",
            demo(),
            "Now the live demo. One, in the Workspace I open Repos, John.Grimes, "
            "open-fhir-training, notebooks, synthea, import_synthea. Two, from the compute menu I "
            "attach Open FHIR Training Cluster. Not Serverless - Pathling isn't installed there. "
            "Three, I run cells two to four: the import, creating the context, and reading the "
            "NDJSON from S3. Four, resource_types shows the 15 types. Five, I point at write.tables "
            "but don't run it; the tables are already loaded and nobody needs to run it again. "
            "Six, I open Catalog, hive_metastore, synthea, patient, show the Overview with the "
            "nested columns, then the Sample Data tab.",
        ),
        diagram(
            "Your turn",
            "Explore the encoded tables in the SQL editor",
            "your-turn",
            your_turn(),
            "For the rest of the block, open the SQL editor and attach the Serverless Starter "
            "Warehouse. Please don't run the import notebooks; the data is already there. Start "
            "with the first query: rows per resource type. You should see 8,297 patients and "
            "2,472,497 observations; add the other types. The second shows how to reach into "
            "nested elements with dots and array indexes. The third groups conditions by the "
            "display of their first coding. For a stretch, use explode to turn a repeating "
            "element into rows; each patient carries two profiles. Then pick a resource that "
            "interests you and explore its columns.",
        ),
        section(
            "Demo walkthrough (backup)",
            "If the live demo doesn't work, I'll walk through these screenshots instead. They "
            "show the same steps: the import notebook, its output, the synthea schema in the "
            "catalog, and the sample data in the patient table. They were captured from the "
            "same workspace you are using, so what you see on your screen should match. If you "
            "are following along at your own pace later, these slides also work as a written "
            "guide to the notebook.",
        ),
        diagram(
            "Running the import notebook",
            "Cells 2 to 4 of import_synthea, attached to the training cluster",
            "backup-import",
            backup_shot(
                "import-synthea",
                (310, 430, 840, 400),
                [
                    (
                        980,
                        484,
                        "Import Pathling",
                        ["from pathling import", "PathlingContext"],
                    ),
                    (
                        980,
                        594,
                        "Create the context",
                        ["and select the synthea", "schema"],
                    ),
                    (
                        980,
                        744,
                        "Read the NDJSON",
                        ["one data source over", "the S3 directory"],
                    ),
                ],
                sw=620,
            ),
            "This is the import notebook attached to the training cluster. One, cell two imports "
            "PathlingContext. Two, cell three creates the context, which starts Spark with the "
            "Pathling encoders, and creates and selects the synthea schema. Three, cell four "
            "reads the directory of NDJSON files from S3 into a single data source. Each cell has "
            "a green tick, so they have run successfully. The data source covers every resource "
            "type in the directory; we haven't written anything yet.",
        ),
        diagram(
            "Resource types found",
            "resource_types() lists the 15 types; write.tables() is left unrun",
            "backup-output",
            backup_shot(
                "import-synthea-output",
                (310, 262, 840, 500),
                [
                    (
                        960,
                        314,
                        "read.ndjson",
                        ["file names give", "the resource types"],
                    ),
                    (620, 500, "15 resource types", ["Condition through", "Location"]),
                    (
                        620,
                        730,
                        "write.tables()",
                        ["not run here: the", "tables already exist"],
                    ),
                ],
                sw=620,
            ),
            "Here is the output. One, the read.ndjson call, pointing at the Synthea directory. "
            "Two, resource_types returns the 15 types Pathling found from the file names, from "
            "Condition through to Location. Three, cell five, write.tables, would write one Delta "
            "table per type into the synthea schema. It hasn't been run here, because the tables "
            "already exist, and that's the same for you: please don't run it. Next we'll look at "
            "the tables it produced.",
        ),
        diagram(
            "The synthea schema",
            "Catalog > hive_metastore > synthea: one table per resource type",
            "backup-catalog",
            backup_shot(
                "catalog-synthea",
                (530, 50, 420, 320),
                [
                    (725, 100, "synthea schema", ["in hive_metastore"]),
                    (890, 187, "15 tables", ["one per resource type"]),
                    (
                        680,
                        311,
                        "Lower-case names",
                        ["condition, encounter,", "observation, ..."],
                    ),
                ],
                sw=470,
            ),
            "In the Catalog, under hive_metastore, the synthea schema. One, the schema name. Two, "
            "it holds 15 tables, one per resource type, matching the list we saw in the notebook. "
            "Three, the table names are the resource type in lower case: allergyintolerance, "
            "condition, encounter and so on. These are the names you use in SQL, for example "
            "hive_metastore.synthea.condition. Click patient to see its columns and data.",
        ),
        diagram(
            "The patient table",
            "Sample Data shows id, id_versioned and meta as a nested JSON struct",
            "backup-patient",
            backup_shot(
                "patient-sample",
                (530, 55, 900, 520),
                [
                    (653, 172, "Sample Data tab", ["after Overview"]),
                    (700, 210, "id", ["the logical id"]),
                    (1300, 210, "meta", ["a struct, shown", "as nested JSON"]),
                ],
                sw=560,
            ),
            "This is the Sample Data tab for the patient table. One, the tab itself, next to the "
            "Overview we saw earlier with the column types. Two, the id column holds the "
            "resource's logical id; id_versioned beside it adds the type and version. Three, meta "
            "is a struct, which the catalog shows as nested JSON. Further to the right are gender, "
            "birthDate, name, address and the rest of the patient, all keeping their FHIR shape. "
            "That's what you'll query in the SQL editor.",
        ),
        closing(
            "Questions?",
            PRESENTER,
            "That's bulk data and Pathling. The exercises, the Bulk Data Access specification and "
            "the Pathling documentation are all linked here. To recap: bulk export gets a whole "
            "population out of a FHIR server as NDJSON, SMART Backend Services authorises it, and "
            "Pathling turns the files into tables you can query. Grab me or one of the other leads "
            "if you get stuck with the queries, and in the session tomorrow morning we'll build "
            "SQL on FHIR views on top of these tables.",
            [
                (REPO_URL, "Exercises"),
                (BULK_URL, "Bulk Data IG"),
                (PATHLING_URL, "pathling.csiro.au"),
            ],
        ),
    ],
}
