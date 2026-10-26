"""Day 2, 1:30 block: CQL, CDS Hooks, SMART App Launch and OMOP, then show and tell prep.

Author: John Grimes
"""

from kit import (
    AMBER,
    BLUE,
    GREY,
    INK,
    LAVENDER,
    MINT,
    MUTED,
    PEACH,
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
    path,
    pill,
    pill_width,
    rect,
    screenshot,
    section,
    svg,
    table,
    text,
    title_slide,
)

from decks._shared import EVENT, LINKS, PRESENTER, standards_map

# Validated with the cql-to-elm translator at signature level Overloads (no errors
# or warnings). The statin value set URL is illustrative.
CQL = [
    "library StatinAfterMI version '1.0.0'",
    "using FHIR version '4.0.1'",
    "include FHIRHelpers version '4.0.1'",
    "valueset \"MI\": 'http://snomed.info/sct?fhir_vs=ecl/<< 22298006'",
    "valueset \"Statins\": 'https://example.org/ValueSet/statins'",
    "context Patient",
    "",
    'define "Recent MI":',
    '  [Condition: "MI"] C',
    "    where C.onset as dateTime",
    "      during Interval[Now() - 1 year, Now()]",
    "",
    'define "Statin since MI":',
    '  [MedicationRequest: "Statins"] M',
    '    with "Recent MI" C',
    "      such that M.authoredOn on or after C.onset as dateTime",
    "",
    'define "Statin gap":',
    '  exists "Recent MI" and not exists "Statin since MI"',
]

CARD = [
    "{",
    '  "cards": [{',
    '    "summary": "No statin since recent MI",',
    '    "indicator": "warning",',
    '    "source": { "label": "Post-MI care service" },',
    '    "links": [{',
    '      "label": "Review cardiac medicines",',
    '      "url": "https://meds.example.org",',
    '      "type": "smart"',
    "    }]",
    "  }]",
    "}",
]


def lifeline(x, rows, fill, top=0, bottom=300, w=150):
    """A sequence diagram participant: a header box and a dashed lifeline."""
    return box(x - w / 2, top, w, 44, fill, rows, 14, 700) + line(
        x, top + 44, x, bottom, "#B0B0B0", 1.4, "5 4", None
    )


def msg(x1, x2, y, label, fs=14, below=None, dash=None):
    """A sequence diagram message with its label above the arrow."""
    mx = (x1 + x2) / 2
    lw = len(label) * fs * 0.56 + 10
    out = [
        line(x1, y, x2, y, GREY, 1.8, dash),
        f'<rect x="{mx - lw / 2}" y="{y - fs - 9}" width="{lw}" height="{fs + 6}" fill="#fff"/>',
        text(mx, y - 7, label, fs),
    ]
    if below:
        out.append(text(mx, y + 18, below, 13, fill=MUTED))
    return "".join(out)


def cql_anatomy():
    """The CQL example with the parts of a library labelled."""
    cx, fs, lh = 395, 12.5, 1.24

    def base(i):
        return 30 + 8 + fs + i * fs * lh

    b = [code(cx, 0, 545, CQL, "StatinAfterMI.cql", fs, lh)]
    notes = [
        (0, 0, ["A versioned, shareable library"]),
        (1, 2, ["Data model: FHIR R4"]),
        (3, 4, ["Terminology: two value sets"]),
        (5, 5, ["Evaluated once per patient"]),
        (
            7,
            10,
            ["An MI in the last year, including", "STEMI and NSTEMI (descendants)"],
        ),
        (12, 15, ["Statins on or after the MI:", "with relates two queries"]),
        (17, 18, ["True or false: the gap that", "a CDS service acts on"]),
    ]
    for first, last, rows in notes:
        y1, y2 = base(first) - fs + 2, base(last) + 4
        b.append(
            path(f"M{cx - 8},{y1} H{cx - 14} V{y2} H{cx - 8}", TEAL, 2, arrow=None)
        )
        b.append(lines(cx - 22, (y1 + y2) / 2, rows, 14, anchor="end", lh=1.2))
    return svg(940, 342, b)


def where_cql_runs():
    """A CQL Library used by a Measure and by a PlanDefinition."""
    b = [box(10, 128, 150, 80, LAVENDER, ["Library", "(CQL)"], 16, 700)]
    lanes = [
        (
            40,
            "Quality measures",
            BLUE,
            "Measure",
            "$evaluate-measure",
            "MeasureReport",
            "population counts: numerator, denominator",
        ),
        (
            215,
            "Clinical decision support",
            PEACH,
            "PlanDefinition",
            "$apply",
            "CarePlan",
            "patient-specific actions and suggestions",
        ),
    ]
    for y, title, fill, res, op, out, note in lanes:
        b.append(text(220, y - 12, title, 16, "start", 700, INK))
        b.append(box(220, y, 190, 70, fill, [res], 16, 700))
        b.append(line(414, y + 35, 452, y + 35, sw=2))
        b.append(box(456, y, 210, 70, "#fff", [op], 15, 700, dash="6 4"))
        b.append(line(670, y + 35, 708, y + 35, sw=2))
        b.append(box(712, y, 190, 70, fill, [out], 16, 700))
        b.append(text(220, y + 94, note, 14, "start", fill=MUTED))
        b.append(hcurve(160, 168, 216, y + 35, sw=2))
    b.append(
        text(
            470,
            335,
            "One Library can serve both: count patients in a measure, or flag one patient in the workflow",
            14,
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 342, b)


def sof_vs_cql():
    """SQL on FHIR views for population tables versus CQL for patient-level logic."""
    b = []
    # Left panel: many resources become a table.
    b.append(rect(0, 0, 450, 285, BLUE, rx=12))
    b.append(text(20, 34, "SQL on FHIR views", 19, "start", 700))
    for r in range(3):
        for c in range(4):
            b.append(rect(22 + c * 24, 58 + r * 24, 18, 18, "#fff", sw=1.2, rx=3))
    b.append(line(126, 92, 176, 92, sw=2))
    b.append(rect(184, 56, 180, 72, "#fff", rx=4))
    for r in range(1, 4):
        b.append(line(184, 56 + r * 18, 364, 56 + r * 18, "#B0B0B0", 1, arrow=None))
    for c in (244, 304):
        b.append(line(c, 56, c, 128, "#B0B0B0", 1, arrow=None))
    b.append(text(374, 97, "rows", 14, "start", fill=MUTED))
    left = [
        "In: every patient's resources",
        "Out: tables, a row per patient or reading",
        "For: analysts, dashboards, research",
        "Runs: in batch, on Spark or a warehouse",
    ]
    for i, s in enumerate(left):
        b.append(text(20, 170 + i * 28, s, 15, "start"))
    # Right panel: one patient becomes a decision.
    b.append(rect(490, 0, 450, 285, PEACH, rx=12))
    b.append(text(510, 34, "CQL", 19, "start", 700))
    b.append(circle(545, 92, 24, "#fff"))
    b.append(text(545, 98, "1", 17, weight=700))
    b.append(text(545, 136, "patient", 13, fill=MUTED))
    b.append(line(574, 92, 630, 92, sw=2))
    b.append(box(636, 70, 140, 44, "#fff", ["true / false"], 15, 700))
    b.append(line(780, 92, 820, 92, sw=2))
    b.append(text(828, 97, "decision", 14, "start", fill=MUTED))
    right = [
        "In: one patient's record",
        "Out: a value per patient (true, a list)",
        "For: CDS services, measure engines",
        "Runs: at the point of care, or per patient",
        "    across a population for a measure",
    ]
    for i, s in enumerate(right):
        b.append(text(510, 170 + i * 26, s, 15, "start"))
    b.append(
        box(
            250,
            300,
            440,
            36,
            "#fff",
            ["Shared ground: FHIR data, path expressions, value sets"],
            15,
            700,
        )
    )
    return svg(940, 340, b)


def cds_hooks():
    """CDS Hooks sequence beside a minimal card response."""
    ehr, svc, app = 75, 270, 440
    b = [
        lifeline(ehr, ["EHR"], BLUE, bottom=255, w=130),
        lifeline(svc, ["CDS service"], PEACH, bottom=255, w=140),
        lifeline(app, ["SMART app"], YELLOW, bottom=255, w=120),
        msg(ehr, svc - 4, 82, "1  patient-view", below="patientId + prefetch"),
        box(svc - 62, 112, 124, 38, "#fff", ["evaluate CQL"], 14),
        msg(svc, ehr + 4, 186, "2  cards"),
        text((ehr + svc) / 2, 204, "info, suggestion, link", 13, fill=MUTED),
        msg(ehr, app - 4, 238, "3  clinician opens the app link", 14),
        text(10, 300, "Hooks include:", 14, "start", fill=MUTED),
    ]
    x = 124
    for h in ("patient-view", "order-select", "order-sign"):
        b.append(pill(x, 284, h, MINT, 13))
        x += pill_width(h, 13) + 10
    b.append(
        code(520, 0, 420, CARD, "Response from the service", 13, 1.4, title_fill=PEACH)
    )
    b.append(
        text(730, 290, "summary, indicator and source are required;", 14, fill=MUTED)
    )
    b.append(text(730, 310, 'type "smart" means launch with SMART', 14, fill=MUTED))
    return svg(940, 340, b)


def smart_launch():
    """SMART App Launch (EHR launch) sequence, with the Day 1 deployment."""
    ehr, app, auth, fhir = 70, 255, 440, 625
    bottom = 282
    b = [
        lifeline(ehr, ["EHR"], BLUE, bottom=bottom, w=120),
        lifeline(app, ["App"], YELLOW, bottom=bottom, w=120),
        lifeline(auth, ["Authorisation", "server"], LAVENDER, bottom=bottom, w=150),
        lifeline(fhir, ["FHIR server"], MINT, bottom=bottom, w=140),
    ]
    steps = [
        (ehr, app, "1  launch: iss + launch id"),
        (app, fhir, "2  GET .well-known/smart-configuration"),
        (app, auth, "3  authorize (scope, launch)"),
        (auth, app, "4  code (redirect)"),
        (app, auth, "5  POST token"),
        (auth, app, "6  access token + patient id"),
        (app, fhir, "7  GET Observation?patient=... (Bearer)"),
    ]
    for i, (a, z, label) in enumerate(steps):
        d = 4 if z > a else -4
        b.append(msg(a, z - d, 74 + i * 31, label, 13))
    b.append(
        pill(
            110, 302, "scope=launch openid fhirUser patient/Observation.rs", "#fff", 13
        )
    )
    b.append(rect(712, 0, 228, 236, AMBER, rx=12))
    b.append(text(728, 30, "Seen on Day 1", 16, "start", 700))
    day1 = [
        "Spot FHIRs: a SMART on",
        "FHIR test result review",
        "app at Queensland",
        "Children's Hospital - the",
        "first FHIR-based CDS",
        "deployment in a",
        "Queensland HHS",
    ]
    for i, s in enumerate(day1):
        b.append(text(728, 58 + i * 23, s, 14, "start"))
    b.append(rect(712, 250, 228, 82, "#fff", rx=12))
    b.append(text(728, 276, "Track 1 builds SMART apps", 14, "start", 700))
    b.append(text(728, 298, "FHIR for Users - Forms", 14, "start"))
    b.append(text(728, 318, "and Apps (main room)", 14, "start"))
    return svg(940, 340, b)


def omop_cdm():
    """Person-centric OMOP tables around standard vocabularies, beside FHIR."""
    b = []
    tables = [
        "visit_occurrence",
        "condition_occurrence",
        "drug_exposure",
        "procedure_occurrence",
        "measurement",
        "observation",
    ]
    cx, cy = 280, 135
    for i, t in enumerate(tables):
        x = 0 if i < 3 else 380
        y = 20 + (i % 3) * 95
        b.append(
            line(x + 180 if x == 0 else x, y + 21, cx, cy, "#B0B0B0", 1.4, arrow=None)
        )
        b.append(box(x, y, 180, 42, MINT, [t], 14))
    b.append(circle(cx, cy, 54, "#fff", TEAL, 2.5))
    b.append(lines(cx, cy, ["person"], 17, 700, INK))
    b.append(rect(0, 270, 560, 64, LAVENDER, rx=10))
    b.append(text(280, 296, "Standardised vocabularies", 16, weight=700))
    b.append(text(280, 320, "concept · concept_relationship · concept_ancestor", 14))
    b.append(box(600, 0, 340, 150, BLUE, [], rx=12))
    b.append(text(620, 32, "FHIR", 18, "start", 700))
    for i, s in enumerate(
        [
            "Exchange and operations",
            "REST APIs, profiles such as AU Core",
            "Rich local detail, as recorded",
        ]
    ):
        b.append(text(620, 62 + i * 26, s, 15, "start"))
    b.append(text(770, 172, "complementary", 14, fill=MUTED, italic=True))
    b.append(box(600, 184, 340, 150, MINT, [], rx=12))
    b.append(text(620, 216, "OMOP CDM v5.4 (OHDSI)", 18, "start", 700))
    for i, s in enumerate(
        [
            "Observational research networks",
            "Local codes mapped to",
            "    standard concepts",
            "Federated studies: ATLAS, HADES",
        ]
    ):
        b.append(text(620, 244 + i * 24, s, 15, "start"))
    return svg(940, 340, b)


def fhir_to_omop():
    """FHIR to OMOP ETL through SQL on FHIR views, with resource mappings."""
    b = []
    steps = [
        (BLUE, ["FHIR resources", "NDJSON, Delta"]),
        (LAVENDER, ["SQL on FHIR views", "ViewDefinitions"]),
        (MINT, ["OMOP tables", "CDM v5.4"]),
        (AMBER, ["Network studies", "across sites"]),
    ]
    for i, (fill, rows) in enumerate(steps):
        x = i * 240
        b.append(rect(x, 0, 210, 60, fill))
        b.append(text(x + 105, 25, rows[0], 15, weight=700))
        b.append(text(x + 105, 46, rows[1], 14, fill=MUTED))
        if i < 3:
            b.append(line(x + 213, 30, x + 237, 30, sw=2))
    b.append(
        text(
            470,
            92,
            "Mapping patterns: HL7 Vulcan FHIR to OMOP IG v1.0.0 (informative, targets CDM v5.4)",
            14,
            fill=MUTED,
            italic=True,
        )
    )
    rows = [
        ("Patient", "person", "gender concept, year of birth"),
        ("Encounter", "visit_occurrence", "visit type concept"),
        ("Condition", "condition_occurrence", "SNOMED CT is standard here"),
        ("Observation", "measurement or observation", "routed by the concept's domain"),
        ("MedicationRequest", "drug_exposure", "end date may need deriving"),
        ("Procedure", "procedure_occurrence", "procedure concept and date"),
    ]
    b.append(
        table(
            0,
            110,
            [("FHIR resource", 200), ("OMOP table", 270), ("Note", 466)],
            rows,
            LAVENDER,
            14,
            32,
            mono_cols=(1,),
        )
    )
    return svg(940, 340, b)


def scenario():
    """One statin gap finding carried through every standard in the track."""
    steps = [
        (
            BLUE,
            "Find",
            "SQL on FHIR",
            [
                "mi_secondary_",
                "prevention: 22 of",
                "274 patients, no",
                "statin in a year",
            ],
        ),
        (
            LAVENDER,
            "Express",
            "CQL",
            ['"Statin gap"', "in a shared,", "versioned Library"],
        ),
        (
            PEACH,
            "Deliver",
            "CDS Hooks",
            ["a warning card", "at patient-view", "in the EHR"],
        ),
        (
            YELLOW,
            "Detail",
            "SMART app",
            ["medication history,", "launched from", "the card"],
        ),
        (
            MINT,
            "Pool",
            "OMOP",
            ["drug_exposure rows", "from many sites,", "one network study"],
        ),
    ]
    b = []
    w, gap = 172, 20
    for i, (fill, verb, std, rows) in enumerate(steps):
        x = i * (w + gap)
        b.append(rect(x, 10, w, 236, fill, rx=12))
        b.append(circle(x + 26, 40, 15, "#fff", TEAL, 2))
        b.append(text(x + 26, 46, str(i + 1), 15, weight=700, fill=TEAL))
        b.append(text(x + 50, 47, verb, 18, "start", 700))
        for j, r in enumerate(rows):
            b.append(text(x + w / 2, 92 + j * 24, r, 14))
        b.append(box(x + 14, 196, w - 28, 36, "#fff", [std], 14, 700))
        if i < 4:
            b.append(line(x + w + 2, 128, x + w + gap - 2, 128, sw=2))
    b.append(path("M846,246 V290 H86 V252", TEAL, 2, arrow="at"))
    b.append(
        text(
            466,
            314,
            "Pooled results raise new questions and refine the logic",
            15,
            fill=INK,
            italic=True,
        )
    )
    return svg(940, 330, b)


def show_and_tell():
    """The five prompts for a show and tell slot, with tips."""
    b = [rect(0, 0, 580, 335, "#fff", rx=12)]
    b.append(text(24, 36, "Your group · 3 minutes", 19, "start", 700))
    prompts = [
        ("The question", "what did you want to know?"),
        ("The data", "which dataset, which resources?"),
        ("What you did", "which standards and tools?"),
        ("What you found", "one result, one picture"),
        ("What's next", "what would you try with more time?"),
    ]
    for i, (h, s) in enumerate(prompts):
        y = 62 + i * 54
        b.append(circle(44, y + 20, 16, BLUE))
        b.append(text(44, y + 26, str(i + 1), 15, weight=700))
        b.append(text(74, y + 26, h, 17, "start", 700))
        b.append(text(250, y + 26, s, 15, "start", fill=MUTED))
    b.append(rect(610, 0, 330, 335, YELLOW, rx=12))
    b.append(text(632, 36, "Tips", 19, "start", 700))
    tips = [
        ["One screenshot or chart", "beats a page of text"],
        ["Say what didn't work -", "it helps the next group"],
        ["Name the standards", "and tools you used"],
        ["Keep to time; questions", "can follow in the break"],
    ]
    for i, rows in enumerate(tips):
        y = 70 + i * 66
        b.append(text(632, y, "·", 20, "start", 700))
        b.append(text(650, y, rows[0], 15, "start"))
        b.append(text(650, y + 21, rows[1], 15, "start", fill=MUTED))
    return svg(940, 340, b)


def demo_steps():
    """The SQL editor, with the run button and visualisation tab marked."""
    w = 560
    top, _, th, tp = screenshot("sql-mimic-cohort", 0, 0, w, crop=(243, 88, 740, 180))
    bot, _, _, bp = screenshot(
        "sql-mimic-cohort", 0, th + 26, w, crop=(243, 540, 740, 150)
    )
    b = [top, bot]
    b.append(text(w / 2, th + 18, "...", 14, fill=MUTED))
    rx, ry = tp(305, 103)
    b.append(highlight(rx - 60, ry - 13, 120, 26))
    b.append(callout(2, rx + 76, ry))
    px, py = bp(352, 557)
    b.append(highlight(px - 15, py - 15, 30, 30))
    b.append(callout(3, px + 36, py))
    steps = [
        ["Open the SQL Editor; attach the", "Serverless Starter Warehouse"],
        ["Run the cohort query: mean SaO2", "by race category"],
        ["Click + next to Table, then", "Visualization"],
        ["Bar chart: X race_category,", "Y mean_sao2"],
        ["Save it, then screenshot the", "chart for your slide"],
    ]
    for i, rows in enumerate(steps):
        y = 22 + i * 64
        b.append(callout(i + 1, 612, y - 5, 13))
        b.append(text(636, y, rows[0], 16, "start"))
        b.append(text(636, y + 23, rows[1], 16, "start", fill=MUTED))
    return svg(940, 330, b)


def your_turn():
    """The rest of the afternoon, with a stretch task."""
    b = []
    slots = [
        (0, 150, BLUE, ["1:30", "this talk + demo"]),
        (160, 300, MINT, ["2:00-3:00", "finish your work"]),
        (470, 170, "#F0F0F0", ["3:00", "afternoon tea"]),
        (650, 290, AMBER, ["3:30 main room", "show and tell"]),
    ]
    for x, w, fill, rows in slots:
        b.append(box(x, 0, w, 60, fill, rows, 15, 400))
    b.append(rect(0, 84, 460, 250, "#fff", rx=12))
    b.append(text(20, 116, "Now", 18, "start", 700))
    todo = [
        ["Finish the exercise or question you started"],
        ["Pick one result and chart it"],
        [
            "Fill in the five prompts: question, data,",
            "what you did, what you found, what's next",
        ],
        ["Rehearse 3 minutes; choose a speaker"],
    ]
    y = 150
    for rows in todo:
        b.append(text(20, y, "·", 18, "start", 700))
        for r in rows:
            b.append(text(36, y, r, 15, "start"))
            y += 22
        y += 12
    b.append(rect(480, 84, 460, 250, PEACH, rx=12))
    b.append(text(500, 116, "Stretch", 18, "start", 700))
    b.append(text(500, 142, "Write the CQL define or the CDS Hooks", 15, "start"))
    b.append(text(500, 164, "card that would deliver your finding", 15, "start"))
    b.append(
        code(
            500,
            182,
            420,
            [
                '{ "summary": "Your finding, one line",',
                '  "indicator": "info",',
                '  "source": { "label": "Your group" } }',
            ],
            None,
            14,
            1.4,
        )
    )
    b.append(text(500, 290, "Start from the StatinAfterMI library", 15, "start"))
    b.append(
        text(
            500,
            312,
            "on the CQL slide; check against cql.hl7.org",
            15,
            "start",
            fill=MUTED,
        )
    )
    return svg(940, 340, b)


def backup_results():
    """The MI secondary prevention summary in the SQL editor, annotated."""
    w = 600
    top, _, th, tp = screenshot("sql-mi-results", 0, 0, w, crop=(243, 88, 700, 92))
    bot, _, _, bp = screenshot(
        "sql-mi-results", 0, th + 20, w, crop=(243, 540, 940, 310)
    )
    b = [top, bot]
    x, y = tp(317, 103)
    b.append(highlight(x - 60, y - 11, 120, 22))
    b.append(callout(1, x + 74, y))
    x, y = bp(352, 557)
    b.append(highlight(x - 13, y - 13, 26, 26))
    b.append(callout(2, x + 30, y))
    x, y = bp(829, 665)
    b.append(callout(3, x + 22, y))
    x, y = bp(268, 835)
    b.append(highlight(x - 14, y - 12, 50, 24))
    b.append(callout(4, x + 11, y - 30))
    notes = [
        (1, ["Run all on the Serverless", "Starter Warehouse"]),
        (2, ["+ next to Table adds a", "visualisation tab"]),
        (3, ["Results: one row per", "class, and all four"]),
        (4, ["Download the result if you", "would rather chart elsewhere"]),
    ]
    for i, (n, rows) in enumerate(notes):
        y = 30 + i * 78
        b.append(callout(n, 660, y))
        b.append(text(684, y + 5, rows[0], 15, "start"))
        b.append(text(684, y + 27, rows[1], 15, "start"))
    return svg(940, 340, b)


def backup_chart():
    """The cohort result beside a sketch of the bar chart it produces."""
    shot, sw, sh, p = screenshot(
        "sql-mimic-cohort", 0, 30, 500, crop=(243, 540, 640, 150)
    )
    b = [text(0, 16, "Result in the SQL editor", 15, "start", 700), shot]
    x, y = p(352, 557)
    b.append(highlight(x - 14, y - 14, 28, 28))
    b.append(callout(1, x + 34, y))
    for i, s in enumerate(
        [
            "1  + next to Table > Visualization",
            "2  Visualization type: Bar",
            "3  X column race_category, Y column mean_sao2",
            "4  Save, then screenshot the chart",
        ]
    ):
        b.append(text(0, 30 + sh + 40 + i * 32, s, 16, "start"))
    # Sketch of the bar chart, drawn from the same three rows.
    b.append(text(540, 16, "What the bar chart shows", 15, "start", 700))
    ox, oy, ph = 590, 258, 196
    b.append(line(ox, oy, ox, oy - ph - 6, INK, 1.4, arrow=None))
    b.append(line(ox, oy, 930, oy, INK, 1.4, arrow=None))
    lo, hi = 90, 100
    for v in (90, 95, 100):
        y = oy - (v - lo) / (hi - lo) * ph
        b.append(line(ox - 5, y, ox, y, INK, 1.2, arrow=None))
        b.append(text(ox - 10, y + 5, str(v), 13, "end", fill=MUTED))
    data = [
        ("2106-3", 96.7, ["White"]),
        ("2054-5", 94.6, ["Black or African", "American"]),
        ("UNK", 95.8, ["Unknown"]),
    ]
    for i, (code_, v, label) in enumerate(data):
        x = ox + 22 + i * 120
        h = (v - lo) / (hi - lo) * ph
        b.append(rect(x, oy - h, 70, h, BLUE, rx=2))
        b.append(text(x + 35, oy - h - 8, f"{v}", 14, weight=700))
        b.append(text(x + 35, oy + 20, code_, 13))
        for j, r in enumerate(label):
            b.append(text(x + 35, oy + 38 + j * 17, r, 13, fill=MUTED))
    b.append(text(ox - 40, oy - ph - 16, "mean SaO2 (%)", 13, "start", fill=MUTED))
    b.append(
        text(
            760,
            338,
            "y axis starts at 90 - say so on your slide",
            13,
            fill=MUTED,
            italic=True,
        )
    )
    return svg(940, 342, b)


DECK = {
    "file": "track-3-d2-6-closing-the-loop",
    "slides": [
        title_slide(
            "Closing the loop: CQL, CDS Hooks, SMART and OMOP",
            f"Day 2, 1:30 · {EVENT}",
            "This is the last block before show and tell. So far we've spent our time getting FHIR "
            "data, shaping it with SQL on FHIR, and analysing it in Databricks. This session is "
            "about what happens next: how an analytic finding becomes something a clinician sees "
            "at the right moment, and how it feeds research across many sites. I'll cover four "
            "standards briefly - CQL, CDS Hooks, SMART App Launch and OMOP - then we'll talk "
            "about how show and tell works, and I'll show you how to turn a query into a chart "
            "for your slide.",
        ),
        diagram(
            "From insight to action",
            "The last stage of the map: putting results back into the clinical workflow",
            "standards-map-act",
            standards_map(highlight="act"),
            "Here is the map we've used all track. We've worked mostly in the middle two stages. "
            "The fourth stage, act on it, is where analytics meets care. Three standards matter "
            "here. CQL lets you write clinical logic once, in a form that can be shared and "
            "executed. CDS Hooks delivers advice into the EHR at a workflow moment. SMART App "
            "Launch lets an app open inside the EHR with the patient already selected. And I'll "
            "come back to OMOP from the analyse box, because it is how findings get pooled across "
            "sites for research. None of these replace what you've built this week; they consume it.",
        ),
        diagram(
            "CQL: clinical logic you can share",
            "HL7 CQL v1.5: readable logic over a FHIR data model, shared as FHIR Library resources",
            "cql-anatomy",
            cql_anatomy(),
            "CQL is the Clinical Quality Language from HL7, now at version 1.5. It is designed to "
            "be read by clinicians and informaticians, not just programmers. This library carries "
            "a finding from this morning's exercise into the workflow: a myocardial infarction in "
            "the last year with no statin prescribed since. The using and include lines bind it "
            "to FHIR R4, with FHIRHelpers converting FHIR types to CQL types. The value sets are "
            "the terminology. The MI one is an ECL expression, 22298006 and its descendants, which "
            "takes in STEMI and NSTEMI; the statin one stands for the AMT products the ConceptMap "
            "relates to HMG-CoA reductase inhibitor. The context line says every expression is "
            "evaluated for one patient. The defines are named expressions you can reuse, and the "
            "with clause relates statin requests to the MI. I ran this through the reference CQL "
            "to ELM translator and it compiles cleanly. In practice the library is stored in a "
            "FHIR Library resource.",
        ),
        diagram(
            "Where CQL runs",
            "The same logic powers quality measures and decision support",
            "where-cql-runs",
            where_cql_runs(),
            "A CQL library rarely runs on its own. For quality measures, a Measure resource points "
            "to the library and names which expressions define the populations. Calling "
            "evaluate-measure gives you a MeasureReport with counts like numerator and "
            "denominator. For decision support, a PlanDefinition references the library and "
            "describes actions to take when conditions are true. Calling apply for a specific "
            "patient returns a CarePlan with the actions that apply to them. The point is that "
            "the same definition of a statin gap can drive a measure across a clinic and an "
            "alert for one patient, without being written twice.",
        ),
        diagram(
            "SQL on FHIR and CQL",
            "Population tables for analysts, patient-level logic for decisions",
            "sof-vs-cql",
            sof_vs_cql(),
            "People often ask whether CQL competes with SQL on FHIR. I think of them as different "
            "tools. SQL on FHIR views turn every patient's resources into tables, with a row per "
            "patient or per reading, for analysts, dashboards and research. They run in batch on "
            "Spark or a warehouse, as you've seen in Databricks. CQL works on one patient's "
            "record at a time and returns a value - true or false, or a list - which is what a "
            "decision support service needs. They share a lot: the same FHIR data, very similar "
            "path expressions, and value sets. A good workflow uses views to find a pattern, then "
            "CQL to act on it.",
        ),
        diagram(
            "CDS Hooks: advice at the right moment",
            "CDS Hooks v2.0: the EHR calls a service at a workflow event and shows the cards it returns",
            "cds-hooks",
            cds_hooks(),
            "CDS Hooks is how the logic reaches a clinician. The EHR discovers services at a "
            "well-known endpoint, then calls a service when something happens in the workflow - "
            "here, patient-view, when a chart is opened. The request carries context, such as the "
            "patient id, and prefetched FHIR data the service asked for up front, so it doesn't "
            "have to query back. The service evaluates its logic, perhaps our CQL, and returns "
            "cards: information, suggested actions, or links. On the right is a minimal card. "
            "Summary, indicator and source are required. A link of type smart tells the EHR to "
            "launch a SMART app.",
        ),
        diagram(
            "SMART App Launch: apps inside the EHR",
            "SMART App Launch v2.2: OAuth 2.0 with launch context, so the app opens on the right patient",
            "smart-launch",
            smart_launch(),
            "SMART App Launch is the other half. In an EHR launch the EHR opens the app with the "
            "FHIR server address and a launch id. The app reads the server's SMART configuration, "
            "then asks the authorisation server for access, with scopes such as read access to "
            "the patient's Observations. It exchanges a code for an access token, and the token "
            "response says which patient is in context. Then it calls the FHIR API. Yesterday's "
            "Spot FHIRs talk showed this in production: a SMART test result review app at "
            "Queensland Children's Hospital, the first FHIR-based decision support deployment in "
            "a Queensland HHS. Track 1 is building SMART apps this week.",
        ),
        diagram(
            "OMOP: a common model for research",
            "OHDSI OMOP CDM v5.4: person-centric tables and standardised vocabularies",
            "omop-cdm",
            omop_cdm(),
            "Now to research. OMOP is the Common Data Model from the OHDSI community, at version "
            "5.4. Everything hangs off a person: visits, conditions, drug exposures, procedures, "
            "measurements and observations. Every clinical code is mapped to a standard concept "
            "in the OHDSI vocabularies, so the same query means the same thing at every site. "
            "That is what makes federated network studies possible, with tools like ATLAS and "
            "HADES. I see FHIR and OMOP as complementary. FHIR is built for exchange and "
            "operations, with rich local detail. OMOP is built for comparing populations across "
            "sites, and gives up some detail to get there.",
        ),
        diagram(
            "From FHIR to OMOP",
            "SQL on FHIR views make a natural first step of a FHIR to OMOP pipeline",
            "fhir-to-omop",
            fhir_to_omop(),
            "If your data is already FHIR, the views you've written this week are a good first "
            "step towards OMOP. You flatten resources into tables with SQL on FHIR, then map "
            "codes and load OMOP tables. HL7's Vulcan accelerator has published a FHIR to OMOP "
            "implementation guide, version 1.0.0, informative, targeting CDM 5.4, with mapping "
            "patterns. Patient becomes person, Encounter becomes visit occurrence, Condition "
            "becomes condition occurrence. Observation is the interesting one: it goes to "
            "measurement or observation depending on the domain of the mapped concept. And some "
            "fields OMOP requires, like a drug exposure end date, may have to be derived.",
        ),
        diagram(
            "One finding, end to end",
            "A statin gap after MI, from this morning's exercise, carried through every standard",
            "scenario",
            scenario(),
            "Let me put it together with a finding from this morning's exercise. In Databricks, 22 "
            "of the 274 synthetic patients with an MI had no statin prescribed within a year. That "
            "definition becomes a CQL expression in a shared library. A CDS service evaluates it "
            "when a chart is opened and returns a warning card. The clinician opens a SMART app "
            "from the card to see the medication history. Meanwhile, the same data, mapped to "
            "OMOP condition occurrence and drug exposure rows, is pooled with other sites in a "
            "network study. Those results raise new questions and refine the logic. That's the "
            "loop.",
        ),
        section(
            "Show and tell",
            "Now for the last part of the connectathon: show and tell. Every group across the "
            "three tracks gets a chance to share what they did, in the main room after afternoon "
            "tea. It doesn't need to be polished. The most useful presentations are honest about "
            "what you tried, what worked and what didn't. So let's talk about how to make the most "
            "of a few minutes, and then I'll show you a quick way to get a chart out of the "
            "workspace for your slide.",
        ),
        diagram(
            "Show and tell",
            "Main room, 3:30-4:30: a few minutes per group, across all three tracks",
            "show-and-tell",
            show_and_tell(),
            "Show and tell is in the main room at 3:30, after afternoon tea. Each group gets a "
            "few minutes; plan on about three. A simple structure works well: the question you "
            "asked, the data you used, what you did - which standards and tools - what you found, "
            "and what you'd do next. One screenshot or chart is worth more than a page of text. "
            "Please say what didn't work. That is often the most useful thing for the room, and "
            "for us as organisers. Name the standards and tools, and keep to time.",
        ),
        diagram(
            "Demo",
            "From a query result to a chart for your show and tell slide",
            "demo",
            demo_steps(),
            "Live demo. One: open the SQL Editor from the left navigation and attach the "
            "Serverless Starter Warehouse. Two: paste the cohort query from the pulse oximetry "
            "exercise, which counts subjects and averages SaO2 by race category, and click Run "
            "all. Three rows appear, one per race category. Three: click the plus next to the "
            "Table tab and choose Visualization. Four: pick a bar chart, put race category on the "
            "X axis and mean SaO2 on the Y axis. Five: save it, and take a screenshot for your "
            "slide. I'll point out that there are only 19 subjects, so this is a picture, not a result.",
        ),
        diagram(
            "Your turn",
            "Finish, chart one result, and prepare 3 minutes for show and tell",
            "your-turn",
            your_turn(),
            "The rest of this block is yours, until afternoon tea at 3. Finish the exercise or "
            "the question you've been working on. Pick one result and chart it the way I just "
            "showed. Then fill in the five prompts and decide who will speak. If you finish "
            "early, here's a stretch task: write the CQL define or the CDS Hooks card that would "
            "deliver your finding to a clinician. The card on the right is valid and has only the "
            "required fields. James, Dion, Duncan and I will be around the room to help.",
        ),
        section(
            "Demo walkthrough (backup)",
            "These slides walk through the demo with screenshots, in case the live environment "
            "isn't cooperating, or for anyone who wants to repeat the steps later. They show the "
            "same SQL editor and the same two queries from this week's exercises: the MI secondary "
            "prevention summary and the pulse oximetry cohort summary. Everything here works on "
            "the Serverless Starter Warehouse, so you don't need the notebook cluster to make a "
            "chart.",
        ),
        diagram(
            "Results in the SQL editor",
            "The MI secondary prevention summary, with the controls you need",
            "backup-results",
            backup_results(),
            "This is the SQL editor after running the summary query from the MI secondary "
            "prevention exercise, with follow_up_days set to 365. One: Run all executes on the "
            "Serverless Starter Warehouse. Two: the plus next to the Table tab is how you add a "
            "visualisation; it opens a new tab beside the table. Three: the result, one row per "
            "drug class and one for all four - a bar chart of percent_treated by drug_class works "
            "well. Four: the download button lets you take the result elsewhere if you'd rather "
            "chart it in another tool.",
        ),
        diagram(
            "From result to chart",
            "The pulse oximetry cohort as a bar chart",
            "backup-chart",
            backup_chart(),
            "On the left is the aggregated cohort result: three race categories with subject "
            "counts and mean SaO2. Click the plus, choose Visualization, then a bar chart with "
            "race category on the X axis and mean SaO2 on the Y axis. On the right is roughly "
            "what you'll get, drawn from those three rows: 96.7, 94.6 and 95.8. If the chart's "
            "axis doesn't start at zero, say so, because it exaggerates small differences. And "
            "with only 19 subjects, present it as a demonstration of the method, not a finding.",
        ),
        closing(
            "Thank you",
            PRESENTER,
            "Thank you. CQL, CDS Hooks, SMART App Launch and OMOP are where analytics turns into "
            "action and into research, and everything we've used this week is open, so you can "
            "keep going after today. The links are here: workspace access, the exercises "
            "repository, SQL on FHIR and Pathling. Workspace accounts are removed by 30 November. "
            "If you have questions later, use the connectathon Zulip chat or email "
            "fhir-training@csiro.au. I'll see you in the main room for show and tell at 3:30.",
            LINKS,
        ),
    ],
}
