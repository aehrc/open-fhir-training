"""Day 2, 11:00 block: reproducing a pulse oximetry bias study on MIMIC-IV FHIR data.

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
    PINK,
    RED,
    ROSE,
    TEAL,
    YELLOW,
    box,
    circle,
    closing,
    code,
    callout,
    diagram,
    highlight,
    line,
    lines,
    path,
    rect,
    screenshot,
    section,
    svg,
    table,
    text,
    title_slide,
)

from decks._shared import EVENT, PATHLING_URL, PRESENTER, REPO_URL, SOF_URL

CITATION = (
    "Sjoding MW, Dickson RP, Iwashyna TJ, Gay SE, Valley TS. Racial bias in pulse "
    "oximetry measurement. N Engl J Med 2020;383:2477-8."
)


def mark(x, y, w, h, fill=ROSE):
    """A translucent band behind lines of code, to show what changed."""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{fill}" '
        f'fill-opacity="0.35"/>'
    )


def code_row_y(y, i, title=True, fs=14, lh=1.45):
    """The top of row i in a kit.code() card at y, for marking rows."""
    head = 30 if title else 0
    return y + head + 8 + i * fs * lh + fs * 0.15


def clinical_question():
    """A pulse oximeter on a finger beside an arterial blood gas, and what goes wrong."""
    b = []
    # Pulse oximeter.
    b.append(rect(10, 10, 440, 205, BLUE, rx=12))
    b.append(text(30, 42, "Pulse oximeter: SpO2", 19, "start", 700))
    b.append(
        text(
            30,
            66,
            "Light through the fingertip; continuous, non-invasive",
            14,
            "start",
            400,
            MUTED,
        )
    )
    b.append(rect(40, 120, 190, 44, PEACH, rx=22))  # Finger.
    b.append(rect(160, 106, 80, 72, "#fff", rx=10))  # Probe clip.
    b.append(circle(200, 116, 5, RED, RED, 0))  # Light source.
    b.append(line(200, 122, 200, 166, ROSE, 2, dash="3 3", arrow=None))
    b.append(text(200, 98, "probe", 13, "middle", 400, MUTED))
    b.append(line(240, 142, 290, 142, arrow=None))
    b.append(rect(290, 100, 140, 84, "#fff", rx=8))
    b.append(text(360, 132, "SpO2", 15, "middle", 400, MUTED))
    b.append(text(360, 166, "95%", 28, "middle", 700, INK))
    b.append(
        text(
            30,
            202,
            "Monitor reading, charted every few minutes",
            14,
            "start",
            400,
            MUTED,
        )
    )
    # Arterial blood gas.
    b.append(rect(490, 10, 440, 205, PINK, rx=12))
    b.append(text(510, 42, "Arterial blood gas: SaO2", 19, "start", 700))
    b.append(
        text(
            510,
            66,
            "Co-oximetry on an arterial sample; the reference",
            14,
            "start",
            400,
            MUTED,
        )
    )
    b.append(rect(520, 128, 130, 28, "#fff", rx=4))  # Syringe barrel.
    b.append(rect(530, 132, 70, 20, ROSE, sw=0, rx=2))  # Blood.
    b.append(line(650, 142, 675, 142, INK, arrow=None))  # Plunger.
    b.append(line(675, 128, 675, 156, INK, 3, arrow=None))
    b.append(line(495, 142, 520, 142, INK, arrow=None))  # Needle.
    b.append(line(690, 142, 760, 142, arrow="ag"))
    b.append(rect(770, 100, 140, 84, "#fff", rx=8))
    b.append(text(840, 132, "SaO2", 15, "middle", 400, MUTED))
    b.append(text(840, 166, "87%", 28, "middle", 700, RED))
    b.append(
        text(
            510,
            202,
            "Laboratory result, a few times a day at most",
            14,
            "start",
            400,
            MUTED,
        )
    )
    # Pairing and the risk.
    b.append(line(450, 142, 490, 142, TEAL, 2.5, arrow=None))
    b.append(rect(10, 235, 920, 100, YELLOW, rx=12))
    b.append(
        text(
            30,
            266,
            "Occult hypoxaemia: SaO2 < 88% despite SpO2 of 92-96%",
            18,
            "start",
            700,
        )
    )
    b.append(
        text(
            30,
            293,
            "Pairs measured within 10 minutes: 11.7% of measurements in Black patients vs 3.6% in White patients",
            15,
            "start",
        )
    )
    b.append(text(30, 320, CITATION, 13, "start", 400, MUTED, italic=True))
    return svg(940, 340, b)


def the_data():
    """From the PhysioNet release to tables in the workspace."""
    b = []
    steps = [
        (
            10,
            BLUE,
            ["MIMIC-IV Clinical", "Database Demo", "on FHIR 2.1.0"],
            "PhysioNet",
        ),
        (
            250,
            LAVENDER,
            ["NDJSON files", "MimicPatient.ndjson,", "MimicObservation..."],
            "one file per profile",
        ),
        (
            490,
            MINT,
            ["Pathling import", "file_name_mapper ->", "resource type"],
            "import_mimic_iv_demo.py",
        ),
        (
            730,
            AMBER,
            ["hive_metastore.", "mimic_iv_demo", "13 tables"],
            "one per resource type",
        ),
    ]
    for i, (x, fill, rows, cap) in enumerate(steps):
        b.append(box(x, 10, 200, 100, fill, rows, 15, rx=10))
        b.append(text(x + 100, 132, cap, 14, "middle", 400, MUTED))
        if i:
            b.append(line(x - 38, 60, x - 4, 60))
    stats = [
        ("100", ["de-identified", "ICU patients"]),
        ("813,540", ["Observations"]),
        ("13", ["resource types"]),
    ]
    for i, (n, label) in enumerate(stats):
        x = 10 + i * 150
        b.append(rect(x, 160, 135, 100, "#fff", rx=10))
        b.append(text(x + 67, 198, n, 24, "middle", 700, INK))
        b.append(lines(x + 67, 232, label, 14, 400, MUTED, lh=1.2))
    b.append(
        code(
            470,
            155,
            460,
            [
                '"code": { "coding": [ {',
                '  "system": "http://mimic.mit.edu/fhir/',
                "             mimic/CodeSystem/",
                '             mimic-chartevents-d-items",',
                '  "code": "220277",',
                '  "display": "O2 saturation pulseoxymetry"',
                "} ] }",
            ],
            "Observation.code: a local item id, not LOINC",
            fs=13,
            lh=1.3,
        )
    )
    return svg(940, 340, b)


def study_design():
    """A timeline of one ICU stay: the index period and the readings in it."""
    b = []
    x0, ip, x1 = 170, 330, 660
    y = 190
    b.append(line(x0 - 20, y, x1, y, GREY, 1.6))
    b.append(rect(x0, y - 26, ip, 52, MINT, rx=8))
    b.append(text(x0 + ip / 2, y + 6, "Index period (>= 12 hours)", 15, "middle", 700))
    b.append(line(x0, 60, x0, y + 50, INK, 2, arrow=None))
    b.append(text(x0, 50, "ICU admission", 14, "middle", 700))
    b.append(line(x0 + ip, 70, x0 + ip, y + 50, INK, 2, dash="5 4", arrow=None))
    b.append(
        lines(
            x0 + ip,
            30,
            [
                "Ends at the first of: discharge,",
                "first ventilation beyond",
                "supplemental O2, or day 5",
            ],
            14,
            400,
            INK,
            lh=1.2,
        )
    )
    # Readings.
    rows = [
        (BLUE, "SpO2", 262, 15),
        (PINK, "Arterial SaO2", 292, 3),
        (AMBER, "O2 flow", 322, 5),
    ]
    for fill, label, ry, n in rows:
        for k in range(n):
            cx = x0 + 14 + k * ((ip - 28) / (n - 1))
            b.append(circle(cx, ry, 6, fill, INK, 1.2))
        for k in range(3):
            b.append(circle(x0 + ip + 40 + k * 40, ry, 6, "#EEE", "#BBB", 1.2))
        b.append(text(x0 - 22, ry + 5, label, 14, "end"))
    b.append(
        text(x0 + ip + 80, y + 46, "later readings excluded", 13, "middle", 400, MUTED)
    )
    # Criteria.
    for by, bh, fill, head, rows_ in [
        (
            10,
            150,
            BLUE,
            "Subjects",
            ["first ICU stay", "race recorded", "index period >= 12 h"],
        ),
        (
            180,
            155,
            YELLOW,
            "Cohort",
            [
                "subjects with at least",
                "one SpO2, one arterial",
                "SaO2 and one O2 flow",
                "in the index period",
            ],
        ),
    ]:
        b.append(rect(700, by, 235, bh, fill, rx=10))
        b.append(text(720, by + 32, head, 17, "start", 700))
        for j, r in enumerate(rows_):
            b.append(text(720, by + 62 + j * 23, r, 15, "start"))
    return svg(940, 340, b)


def layered_views():
    """Four layers of tables, from FHIR to cohort, with row counts."""
    b = []
    cols = [
        (0, 130, AMBER, "FHIR tables", "Pathling encoders", [("mimic_iv_demo", "")]),
        (
            156,
            270,
            LAVENDER,
            "rv_* raw views",
            "SQL on FHIR, Pathling",
            [
                ("rv_patient", "100"),
                ("rv_icu_encounter", "140"),
                ("rv_obs_vitalsigns", "42,697"),
                ("rv_obs_o2_flow", "1,248"),
                ("rv_o2_delivery_device", "3,145"),
                ("rv_obs_bg", "2,145"),
            ],
        ),
        (
            452,
            230,
            BLUE,
            "st_* study views",
            "Spark SQL",
            [
                ("st_ventilation", "1,369"),
                ("st_subject", "87"),
                ("st_reading_spo2", "6,165"),
                ("st_reading_so2", "75"),
                ("st_reading_o2_flow", "567"),
            ],
        ),
        (
            708,
            230,
            MINT,
            "coh_* cohort",
            "Spark SQL",
            [
                ("coh_subject", "19"),
                ("coh_reading_spo2", "1,438"),
                ("coh_reading_so2", "60"),
                ("coh_reading_o2_flow", "241"),
            ],
        ),
    ]
    top = 70
    for i, (x, w, fill, title, how, rows) in enumerate(cols):
        b.append(text(x + w / 2, 22, title, 16, "middle", 700))
        b.append(text(x + w / 2, 46, how, 14, "middle", 400, MUTED))
        h = 270
        b.append(rect(x, top, w, h, fill, rx=10))
        for j, (name, n) in enumerate(rows):
            ry = top + 18 + j * 41
            b.append(rect(x + 8, ry, w - 16, 32, "#fff", sw=1.2, rx=5))
            if not n:  # The source schema: centred, no count.
                b.append(
                    text(
                        x + w / 2,
                        ry + 21,
                        name,
                        13,
                        "middle",
                        400,
                        "#222",
                        "JetBrains Mono",
                    )
                )
                continue
            b.append(
                text(x + 18, ry + 21, name, 14, "start", 400, "#222", "JetBrains Mono")
            )
            b.append(text(x + w - 18, ry + 21, n, 14, "end", 700, INK))
        if i:
            b.append(line(x - 24, top + h / 2, x - 3, top + h / 2))
    b.append(
        lines(
            65,
            230,
            ["Patient", "Encounter", "Observation", "...", "13 types"],
            14,
            400,
            MUTED,
        )
    )
    return svg(940, 345, b)


def extensions():
    """The race column of rv_patient, beside the extension it reads."""
    b = []
    b.append(
        code(
            0,
            0,
            450,
            [
                "{",
                '  "url": "http://hl7.org/fhir/us/core/',
                '          StructureDefinition/us-core-race",',
                '  "extension": [ {',
                '    "url": "ombCategory",',
                '    "valueCoding": {',
                '      "system": "urn:oid:2.16.840.1.113883.6.238",',
                '      "code": "2106-3",',
                '      "display": "White" }',
                "  }, ... ]",
                "}",
            ],
            "Patient.extension (US Core race)",
            fs=13,
            lh=1.3,
        )
    )
    b.append(
        code(
            480,
            0,
            455,
            [
                "rv_patient = datasource.view(",
                '  resource="Patient",',
                '  select=[{"column": [',
                '    {"name": "subject_id",',
                '     "path": "getResourceKey()"},',
                '    {"name": "race_code",',
                '     "path": "extension(\'http://hl7.org/',
                "       fhir/us/core/StructureDefinition/",
                "       us-core-race').extension(",
                "       'ombCategory').value.ofType(",
                '       Coding).code"}, ...',
            ],
            "create_spo2_views.py (abridged)",
            fs=13,
            lh=1.3,
        )
    )
    b.append(rect(0, 255, 935, 85, YELLOW, rx=10))
    b.append(
        text(
            20,
            288,
            "Extensions are only kept if you ask for them at import:",
            16,
            "start",
            700,
        )
    )
    b.append(
        text(
            20,
            320,
            "PathlingContext.create(enable_extensions=True)",
            15,
            "start",
            400,
            "#222",
            "JetBrains Mono",
        )
    )
    b.append(
        text(445, 320, "in import_mimic_iv_demo.py; the default is False", 15, "start")
    )
    return svg(940, 345, b)


def local_codes():
    """The MIMIC item ids used by the raw views, labelled as in the notebook."""
    cols = [
        ("Item id", 90),
        ("Notebook label", 310),
        ("MIMIC display", 250),
        ("View", 230),
    ]
    rows = [
        ("220045", "Heart rate", "Heart Rate", "rv_obs_vitalsigns"),
        (
            "220277",
            "Oxygen saturation",
            "O2 saturation pulseoxymetry",
            "rv_obs_vitalsigns",
        ),
        ("220210", "Respiratory rate", "Respiratory Rate", "rv_obs_vitalsigns"),
        ("224690", "Respiratory rate", "Respiratory Rate (Total)", "rv_obs_vitalsigns"),
        (
            "226732",
            "Oxygen delivery device observations",
            "O2 Delivery Device(s)",
            "rv_o2_delivery_device",
        ),
        ("223834", "Regular oxygen flow", "O2 Flow", "rv_obs_o2_flow"),
        ("227582", "BiPAP oxygen flow", "BiPap O2 Flow", "rv_obs_o2_flow"),
        (
            "227287",
            "Additional oxygen flow",
            "O2 Flow (additional cannula)",
            "rv_obs_o2_flow",
        ),
        (
            "50817",
            "Oxygen saturation from blood samples",
            "Oxygen Saturation",
            "rv_obs_bg",
        ),
        ("50818", "Carbon dioxide levels", "pCO2", "rv_obs_bg"),
        ("52033", "Specimen information", "Specimen Type", "rv_obs_bg"),
    ]
    b = [table(25, 2, cols, rows, LAVENDER, 14, 28, mono_cols=(0, 3))]
    return svg(940, 340, b)


def ventilation():
    """st_ventilation's CASE: device strings to a ventilation status, in order."""
    b = []
    groups = [
        (PINK, ["'Tracheostomy tube', 'Trach mask'"], "Tracheostomy", "0"),
        (PINK, ["'Endotracheal tube'"], "InvasiveVent", "16"),
        (PEACH, ["'Bipap mask', 'CPAP mask'"], "NonInvasiveVent", "27"),
        (AMBER, ["'High flow nasal cannula'"], "HFNC", "46"),
        (
            MINT,
            [
                "'Nasal cannula', 'Face mask', 'Aerosol-cool', 'Venti mask',",
                "'Medium conc mask', 'Partial rebreath mask', 'High flow neb',",
                "'Non-rebreather'; 'None' with O2 flow > 0; anything else",
            ],
            "SupplementalOxygen",
            "1,277",
        ),
        ("#F0F0F0", ["'None' or no device"], "None", "3"),
    ]
    y = 0
    for i, (fill, rows, status, n) in enumerate(groups):
        h = 34 if len(rows) == 1 else 66
        b.append(text(14, y + h / 2 + 5, str(i + 1), 15, "middle", 700, MUTED))
        b.append(rect(34, y, 560, h, "#fff", rx=6))
        b.append(
            lines(48, y + h / 2, rows, 14, 400, "#222", "JetBrains Mono", "start", 1.3)
        )
        b.append(line(598, y + h / 2, 652, y + h / 2))
        b.append(rect(656, y, 200, h, fill, rx=6))
        b.append(text(670, y + h / 2 + 5, status, 15, "start", 700))
        b.append(text(925, y + h / 2 + 5, n, 15, "end", 400, MUTED))
        y += h + 7
    b.append(text(925, y + 12, "rows in st_ventilation", 13, "end", 400, MUTED))
    b.append(
        text(
            34,
            y + 12,
            "st_subject ends the index period at the first status above SupplementalOxygen",
            13,
            "start",
            400,
            MUTED,
        )
    )
    b.append(rect(34, y + 24, 891, 36, YELLOW, rx=8))
    b.append(
        text(
            50,
            y + 47,
            "Found and fixed: some device values had a trailing space ('Bipap mask '), so the input is now TRIMmed",
            14,
            "start",
        )
    )
    return svg(940, 345, b)


def fhir_shape():
    """One arterial blood gas: three Observations that share a Specimen."""
    b = []
    b.append(box(20, 130, 200, 80, YELLOW, ["Specimen", "3d726715-..."], 15, rx=10))
    obs = [
        (20, PINK, "50817 Oxygen Saturation", "valueQuantity 98 %"),
        (130, LAVENDER, "52033 Specimen Type", "valueString 'ART.'"),
        (240, BLUE, "50818 pCO2", "valueQuantity 46 mm Hg"),
    ]
    for oy, fill, head, val in obs:
        b.append(rect(300, oy, 280, 80, fill, rx=10))
        b.append(text(316, oy + 26, "Observation", 13, "start", 400, MUTED))
        b.append(text(316, oy + 48, head, 15, "start", 700))
        b.append(text(316, oy + 70, val, 14, "start", 400, "#222", "JetBrains Mono"))
        b.append(path(f"M300,{oy + 40} C260,{oy + 40} 260,170 224,170"))
    b.append(
        text(120, 116, "Observation.specimen", 13, "middle", 400, MUTED, italic=True)
    )
    cols = [("itemid", 80), ("value", 90), ("valuenum", 110)]
    b.append(text(640, 22, "rv_obs_bg: one row per Observation", 15, "start", 700))
    b.append(
        table(
            640,
            36,
            cols,
            [
                ("50817", "null", "98.0"),
                ("52033", "ART.", "null"),
                ("50818", "null", "46.0"),
            ],
            LAVENDER,
            14,
            30,
            mono_cols=(0, 1, 2),
        )
    )
    b.append(highlight(640 + 80 + 2, 36 + 60 + 2, 86, 26))
    b.append(
        lines(
            640,
            220,
            [
                "Across all 223 rows for 50817,",
                "value is never populated:",
                "the specimen type lives on",
                "a different row (1,033 x 52033)",
            ],
            15,
            400,
            "#222",
            anchor="start",
        )
    )
    return svg(940, 340, b)


def before_after():
    """The original and fixed SO2 filters, with what each produced."""
    b = []
    before = [
        "FROM mimic_iv_views.st_subject AS sbj",
        "JOIN mimic_iv_views.rv_obs_bg AS bg",
        "    ON sbj.subject_id = bg.subject_id",
        "WHERE bg.charttime BETWEEN ...",
        "    AND bg.itemid = '50817'",
        "    AND bg.valuenum IS NOT NULL",
        "    AND bg.value = 'ART.'",
    ]
    after = [
        "JOIN mimic_iv_views.rv_obs_bg AS bg",
        "    ON sbj.subject_id = bg.subject_id",
        "JOIN mimic_iv_views.rv_obs_bg AS spec",
        "    ON bg.specimen_id = spec.specimen_id",
        "    AND spec.itemid = '52033'",
        "    AND spec.value = 'ART.'",
        "WHERE bg.charttime BETWEEN ...",
        "    AND bg.itemid = '50817'",
        "    AND bg.valuenum IS NOT NULL",
    ]
    fs, lh = 14, 1.4
    b.append(
        code(
            0,
            0,
            440,
            before,
            "Before: st_reading_so2.sql on main",
            fs,
            lh,
            title_fill=PINK,
        )
    )
    b.append(mark(6, code_row_y(0, 6, fs=fs, lh=lh), 428, fs * lh))
    b.append(
        code(
            475,
            0,
            460,
            after,
            "After: branch fix-exercise-docs",
            fs,
            lh,
            title_fill=MINT,
        )
    )
    b.append(mark(481, code_row_y(0, 2, fs=fs, lh=lh), 448, fs * lh * 4, MINT))
    res = [
        (
            0,
            440,
            PINK,
            "0 SaO2 readings -> 0 cohort subjects",
            "filters the SO2 row on the specimen type",
        ),
        (
            475,
            460,
            MINT,
            "75 SaO2 readings -> 19 cohort subjects",
            "joins the SO2 row to its specimen type row",
        ),
    ]
    for x, w, fill, head, sub in res:
        b.append(rect(x, 262, w, 76, fill, rx=10))
        b.append(text(x + w / 2, 292, head, 17, "middle", 700))
        b.append(text(x + w / 2, 320, sub, 14, "middle", 400, MUTED))
    return svg(940, 340, b)


def cohort_results():
    """From 100 patients to 19 subjects, and mean SaO2 by race category."""
    b = []
    funnel = [
        (BLUE, "100", "patients"),
        (LAVENDER, "87", "study subjects"),
        (MINT, "19", "cohort subjects"),
    ]
    for i, (fill, n, label) in enumerate(funnel):
        w = 220 - i * 40
        x = 10 + (220 - w) / 2
        y = i * 78
        b.append(rect(x, y, w, 64, fill, rx=10))
        b.append(text(120, y + 30, n, 22, "middle", 700, INK))
        b.append(text(120, y + 52, label, 14, "middle", 400, MUTED))
    cols = [
        ("race_category", 140),
        ("OMB category", 250),
        ("Subjects", 95),
        ("SaO2 n", 85),
        ("Mean SaO2", 110),
    ]
    rows = [
        ("2106-3", "White", "14", "38", "96.7"),
        ("2054-5", "Black or African American", "3", "14", "94.6"),
        ("UNK", "Unknown", "2", "8", "95.8"),
    ]
    b.append(table(260, 0, cols, rows, BLUE, 15, 36, mono_cols=(0,)))
    b.append(rect(260, 170, 680, 160, YELLOW, rx=12))
    b.append(
        text(280, 202, "This demonstrates the method, not a finding", 18, "start", 700)
    )
    for i, s in enumerate(
        [
            "19 subjects and 60 SaO2 readings: far too few to compare groups",
            "Mean SaO2 alone says nothing about bias; pair it with SpO2",
            "Sjoding et al. analysed 10,789 + 37,308 paired readings",
        ]
    ):
        b.append(text(280, 236 + i * 30, "· " + s, 15, "start"))
    b.append(text(120, 256, "from the 100-patient", 14, "middle", 400, MUTED))
    b.append(text(120, 276, "demo of MIMIC-IV", 14, "middle", 400, MUTED))
    return svg(940, 340, b)


def demo_steps():
    """Three steps of the live demo, left to right."""
    b = []
    steps = [
        (
            LAVENDER,
            "Notebook",
            "create_spo2_views",
            [
                ["notebooks/mimic_iv/"],
                ["Step 3: the rv_patient", "view definition"],
                ["The race_code FHIRPath", "expression"],
                ["Result: 100 rows"],
            ],
        ),
        (
            BLUE,
            "SQL file",
            "st_subject.sql",
            [
                ["sql/mimic_iv/"],
                ["First ICU stay", "per subject"],
                ["Index period end:", "GREATEST and LEAST"],
                ["Result: 87 subjects"],
            ],
        ),
        (
            MINT,
            "SQL editor",
            "cohort query",
            [
                ["Serverless Starter", "Warehouse"],
                ["coh_subject joined to", "coh_reading_so2"],
                ["Group by race_category"],
                ["Result: three rows"],
            ],
        ),
    ]
    for i, (fill, kind, name, items) in enumerate(steps):
        x = i * 320
        b.append(rect(x, 10, 295, 320, fill, rx=12))
        b.append(circle(x + 36, 48, 20, "#fff", TEAL, 2.5))
        b.append(text(x + 36, 55, str(i + 1), 18, "middle", 700, TEAL))
        b.append(text(x + 68, 44, kind, 14, "start", 400, MUTED))
        b.append(text(x + 68, 66, name, 17, "start", 700))
        b.append(line(x + 20, 88, x + 275, 88, "#FFFFFF", 2, arrow=None))
        ty = 122
        for j, item in enumerate(items):
            last = j == len(items) - 1
            if last:
                ty = 306
            for k, r in enumerate(item):
                b.append(
                    text(
                        x + 24,
                        ty + k * 22,
                        r,
                        16,
                        "start",
                        700 if last else 400,
                        INK if last else "#222",
                    )
                )
            ty += len(item) * 22 + 18
        if i < 2:
            b.append(line(x + 297, 172, x + 318, 172))
    return svg(940, 340, b)


PAIR_SQL = [
    "WITH pairs AS (",
    "  SELECT c.subject_id, c.race_category, a.so2 AS sao2, p.spo2,",
    "    ROW_NUMBER() OVER (PARTITION BY a.subject_id, a.chart_time",
    "                       ORDER BY p.chart_time DESC) AS rn",
    "  FROM mimic_iv_views.coh_reading_so2 AS a",
    "  JOIN mimic_iv_views.coh_subject AS c ON a.subject_id = c.subject_id",
    "  JOIN mimic_iv_views.coh_reading_spo2 AS p ON p.subject_id = a.subject_id",
    "    AND p.chart_time BETWEEN a.chart_time - INTERVAL 10 MINUTES",
    "                         AND a.chart_time",
    ")",
    "SELECT race_category, COUNT(DISTINCT subject_id) AS subjects,",
    "  COUNT(*) AS pairs, ROUND(AVG(spo2 - sao2), 1) AS mean_diff",
    "FROM pairs WHERE rn = 1",
    "GROUP BY race_category ORDER BY race_category",
]


def your_turn():
    """The starting query, and what to do with it."""
    b = []
    b.append(
        code(
            0,
            0,
            610,
            PAIR_SQL,
            "Starting point (catalog hive_metastore)",
            fs=12.5,
            lh=1.38,
        )
    )
    b.append(rect(0, 300, 610, 40, LAVENDER, rx=8))
    b.append(
        text(
            16,
            326,
            "As written: 18 pairs from 12 subjects. Save any tables to your own schema.",
            14,
            "start",
        )
    )
    b.append(rect(630, 0, 305, 180, MINT, rx=12))
    b.append(text(648, 30, "Pair and compare", 17, "start", 700))
    for i, s in enumerate(
        [
            "1  Run it: closest SpO2 in the",
            "    10 minutes before each SaO2",
            "2  Change it to 5 minutes:",
            "    what happens to n?",
            "3  What does mean_diff > 0",
            "    tell you?",
        ]
    ):
        b.append(text(648, 58 + i * 21, s, 15, "start"))
    b.append(rect(630, 192, 305, 148, AMBER, rx=12))
    b.append(text(648, 220, "Stretch", 17, "start", 700))
    for i, s in enumerate(
        [
            "Count occult hypoxaemia: SaO2",
            "< 88 with SpO2 92-96, by race",
            "Or add ventilation status from",
            "st_ventilation as a covariate",
        ]
    ):
        b.append(text(648, 248 + i * 22, s, 14, "start"))
    return svg(940, 345, b)


def cohort_screenshot():
    """The cohort query and its result in the SQL editor, with callouts."""
    b = []
    s1, w1, h1, p1 = screenshot("sql-mimic-cohort", 0, 0, 600, crop=(243, 90, 760, 180))
    s2, w2, h2, p2 = screenshot(
        "sql-mimic-cohort", 0, h1 + 20, 600 * 640 / 760, crop=(243, 575, 640, 112)
    )
    b += [s1, s2]
    x, y = p1(258, 103)
    b.append(highlight(x - 4, y - 12, 140, 24))
    b.append(callout(1, x + 150, y))
    x, y = p1(314, 210)
    b.append(callout(2, *p1(980, 211)))
    x, y = p2(300, 578)
    b.append(
        highlight(
            *p2(296, 604),
            w2 - (p2(296, 0)[0] - p2(243, 0)[0]) - 4,
            h2 - (p2(0, 604)[1] - p2(0, 575)[1]) - 2,
        )
    )
    b.append(callout(3, *p2(880, 640)))
    notes = [
        (1, ["Warehouse attached;", "Run all"]),
        (2, ["Join coh_subject to", "coh_reading_so2,", "group by race_category"]),
        (3, ["Three rows: 14, 3 and", "2 subjects; mean SaO2", "96.7, 94.6, 95.8"]),
    ]
    for i, (n, rows) in enumerate(notes):
        ty = 30 + i * 105
        b.append(callout(n, 660, ty))
        b.append(
            lines(690, ty + (len(rows) - 1) * 9, rows, 15, 400, "#222", anchor="start")
        )
    return svg(940, 340, b)


def expected_outputs():
    """What each demo step should show, for when the live demo is not available."""
    b = []
    b.append(
        code(
            0,
            0,
            450,
            [
                "rv_patient: 100 rows",
                "  race_code 2106-3   72",
                "  race_code UNK      17",
                "  race_code 2054-5   10",
                "  race_code ASKU      1",
                "st_subject:   87 rows",
                "coh_subject:  19 rows",
            ],
            "Steps 1 and 2: row counts",
            fs=14,
            lh=1.45,
        )
    )
    b.append(
        code(
            480,
            0,
            455,
            [
                "race_category  subjects  pairs  mean_diff",
                "2054-5                1      1        2.0",
                "2106-3                9     15        1.0",
                "UNK                   2      2        0.0",
            ],
            "Your turn query, 10-minute window",
            fs=13,
            lh=1.45,
        )
    )
    b.append(
        code(
            480,
            160,
            455,
            [
                "race_category  subjects  pairs  mean_diff",
                "2106-3                7      9        0.9",
            ],
            "Same query, 5-minute window",
            fs=13,
            lh=1.45,
        )
    )
    b.append(rect(0, 250, 935, 88, YELLOW, rx=10))
    b.append(
        text(
            20,
            280,
            "18 pairs from 12 subjects at 10 minutes; 9 pairs from 7 subjects at 5 minutes",
            15,
            "start",
            700,
        )
    )
    b.append(
        text(
            20,
            308,
            "No pair meets the occult hypoxaemia definition in the demo cohort",
            15,
            "start",
        )
    )
    b.append(
        text(
            20,
            330,
            "Queried on the Serverless Starter Warehouse, 26 October 2026",
            13,
            "start",
            400,
            MUTED,
        )
    )
    return svg(940, 345, b)


DECK = {
    "file": "track-3-d2-5-pulse-oximetry-study",
    "slides": [
        title_slide(
            "A real-world study on FHIR: pulse oximetry bias",
            f"Day 2, 11:00 · {EVENT}",
            "This block is a worked example of a real research question, answered on FHIR data. "
            "We'll take a published study about pulse oximeters, rebuild its cohort from the "
            "MIMIC-IV demo data on FHIR, using SQL on FHIR views and Spark SQL, and look at what "
            "can go wrong along the way. About twenty minutes of slides, a short demo, and then "
            "the rest of the block is yours to extend the analysis.",
        ),
        diagram(
            "The clinical question",
            "Does SpO2 overestimate arterial SaO2 more for some racial groups?",
            "clinical-question",
            clinical_question(),
            "A pulse oximeter estimates oxygen saturation by shining light through the fingertip. "
            "It's cheap and continuous, and we titrate oxygen on it. The reference is an arterial "
            "blood gas, measured by co-oximetry. In 2020 Sjoding and colleagues paired the two, "
            "taken within ten minutes of each other, and looked for occult hypoxaemia: an "
            "arterial saturation below 88 percent while the oximeter read 92 to 96. In their "
            "University of Michigan cohort that happened in 11.7 percent of measurements in Black "
            "patients and 3.6 percent in White patients. The question for us is whether we can "
            "rebuild that kind of analysis on FHIR data.",
        ),
        diagram(
            "The data: MIMIC-IV demo on FHIR",
            "100 de-identified ICU patients from PhysioNet, already loaded into the workspace",
            "the-data",
            the_data(),
            "MIMIC-IV is a de-identified intensive care dataset used widely in research. "
            "PhysioNet publishes an open demo of 100 patients, converted to FHIR. We "
            "imported the NDJSON files with Pathling - there's one file per MIMIC profile, so the "
            "import maps file names to resource types - and wrote one table per resource type. "
            "That gives 813,540 Observations. Note the codes: MIMIC uses its own item ids, from "
            "code systems like mimic-chartevents-d-items, rather than LOINC. So 220277 means "
            "pulse oximetry, and you need the MIMIC dictionary to know that.",
        ),
        diagram(
            "Study design",
            "One index period per subject, and the readings that fall inside it",
            "study-design",
            study_design(),
            "The study follows the original design closely. Each patient contributes their first "
            "ICU stay. The index period starts at ICU admission and ends at whichever comes first: "
            "discharge, the first ventilation intervention beyond supplemental oxygen, or five "
            "days. Stays with an index period shorter than twelve hours, or with no race recorded, "
            "are dropped. Inside the index period we collect three kinds of reading: SpO2 from the "
            "monitor, arterial SaO2 from blood gases, and nasal cannula oxygen flow up to six "
            "litres a minute. The cohort is the subjects who have all three.",
        ),
        diagram(
            "Layered views",
            "SQL on FHIR flattens the resources once; plain SQL does the study logic",
            "layered-views",
            layered_views(),
            "The work is split into layers. The rv views are six SQL on FHIR ViewDefinitions, run "
            "by Pathling in the create_spo2_views notebook: they turn nested FHIR into flat tables "
            "with one row per patient, stay or Observation. The st views are ordinary Spark SQL "
            "in the sql/mimic_iv folder: ventilation status, subjects and their index periods, and "
            "the readings inside each index period. The coh views keep only subjects with all "
            "three readings. The counts are from the workspace today: 100 patients, 87 study "
            "subjects, and a final cohort of 19 with 1,438 SpO2, 60 SaO2 and 241 oxygen flow "
            "readings.",
        ),
        diagram(
            "Extensions in a view",
            "Race is a US Core extension; FHIRPath reaches into it like any other element",
            "extensions",
            extensions(),
            "Race isn't a core element of Patient. MIMIC records it with the US Core race "
            "extension, which is itself a set of nested extensions, and the OMB category is a "
            "Coding inside one of them. In the view, the FHIRPath expression selects the race "
            "extension by URL, then the ombCategory sub-extension, then takes the Coding's code. "
            "One catch: Pathling only keeps extensions if you enable them when you encode the data. "
            "The MIMIC import notebook does that with enable_extensions equals True; the library "
            "default is False. In this dataset the race codes are mostly 2106-3, White, then "
            "unknown, then 2054-5, Black or African American.",
        ),
        diagram(
            "Local codes",
            "The MIMIC item ids behind each raw view, labelled as in create_spo2_views",
            "local-codes",
            local_codes(),
            "These are all the codes the raw views filter on. The first eight come from the ICU "
            "charted events dictionary, the last three from the laboratory items dictionary. The "
            "notebook labels are in the second column and the MIMIC display text in the third. "
            "Two things to notice. Several items mean similar things, like the two respiratory "
            "rates and three oxygen flows, and the view has to list them all. And none of these "
            "are standard codes, so this study only runs on MIMIC. Mapping them to LOINC with a "
            "ConceptMap would make the views portable - that's a good conversation to have with "
            "James.",
        ),
        diagram(
            "From devices to ventilation status",
            "st_ventilation maps free-text device names to a status, first match wins",
            "ventilation",
            ventilation(),
            "To find the first ventilation intervention we need a ventilation status, and MIMIC "
            "only records the oxygen delivery device as text. st_ventilation, adapted from the "
            "ventilation concept in the mimic-code repository, is a CASE expression evaluated in this order. Anything "
            "above supplemental oxygen ends the index period. The counts on the right are rows "
            "in st_ventilation today. We found one real-data problem here: some device values "
            "carry a trailing space, like 'Bipap mask' with a space after it, and the data says "
            "'Non-rebreather', not the name in the original list. Those rows fell through to the "
            "default. The view now trims the value and uses the name in the data, which moved 27 "
            "rows to non-invasive ventilation.",
        ),
        diagram(
            "The shape of FHIR matters",
            "An arterial blood gas is several Observations that share one Specimen",
            "fhir-shape",
            fhir_shape(),
            "Here's the most useful lesson from this exercise. In MIMIC on FHIR, one blood gas "
            "becomes several Observations, all pointing at the same Specimen. The oxygen "
            "saturation is one Observation, with a quantity. Whether the sample was arterial is a "
            "different Observation, item 52033, with the string ART. In the flattened view each "
            "of those is its own row. So asking for a row where the item is 50817 and the value "
            "is ART. can never match: across all 223 saturation rows, value is never populated.",
        ),
        diagram(
            "Fixing the filter",
            "Join each SO2 row to its specimen type row through specimen_id",
            "before-after",
            before_after(),
            "On the left is the original st_reading_so2. It filters the saturation row on a "
            "specimen type it doesn't carry, so it returns no readings, and because the cohort "
            "needs all three readings, the cohort was empty - with no error. The fix on the right "
            "joins the blood gas view to itself on specimen_id, picks the specimen type row, and "
            "keeps arterial samples. That gives 75 SaO2 readings and a cohort of 19. The same "
            "branch also fixed st_subject so it really takes the first ICU stay. The lesson: "
            "check row counts at every layer.",
        ),
        diagram(
            "What the demo cohort shows",
            "Mean SaO2 by race category in the cohort - with a very small n",
            "cohort-results",
            cohort_results(),
            "Here is the cohort by race category: 14 subjects in the White category with a mean "
            "SaO2 of 96.7, three Black or African American subjects with 94.6, and two unknown. "
            "Please don't read anything into these numbers. Nineteen subjects is far too few, "
            "and a mean arterial saturation on its own says nothing about oximeter bias - you "
            "need paired readings. The original study had tens of thousands of pairs. What this "
            "shows is that the method works end to end on FHIR, and it would run unchanged on "
            "the full MIMIC-IV.",
        ),
        diagram(
            "Demo",
            "From a FHIR extension to a cohort result in three steps",
            "demo",
            demo_steps(),
            "Here's what I'll show. One: open notebooks/mimic_iv/create_spo2_views in the Git "
            "folder, attached to the Open FHIR Training Cluster. Scroll to step 3, show the "
            "rv_patient view and the race extension path, and show its rows. I won't rewrite the "
            "shared tables. Two: open sql/mimic_iv/st_subject.sql and walk through the CTEs, "
            "especially the GREATEST and LEAST that compute the end of the index period. Three: "
            "open the SQL editor on the Serverless Starter Warehouse, paste the cohort query "
            "joining coh_subject to coh_reading_so2, run it, and read out the three rows.",
        ),
        diagram(
            "Your turn",
            "Pair each SaO2 with the closest preceding SpO2 and compare by race category",
            "your-turn",
            your_turn(),
            "For the rest of the block, take this query as a starting point. It's on the slide "
            "deck and it runs as is in the SQL editor with the hive_metastore catalog. For each "
            "arterial reading it finds the closest SpO2 in the ten minutes before, then averages "
            "SpO2 minus SaO2 by race category. Run it, then try five minutes and watch the number "
            "of pairs fall. If you want more, count occult hypoxaemia using the paper's definition, "
            "or bring in ventilation status from st_ventilation. If you create tables, put them "
            "in your own schema.",
        ),
        section(
            "Demo walkthrough (backup)",
            "If the live demo doesn't cooperate, here's what you would have seen. The next two "
            "slides show the cohort query in the SQL editor, with its result, and then the "
            "outputs of each demo step and of the Your turn query. They're also a useful "
            "reference later in the block: if your own numbers differ from these, check that "
            "you're reading the shared mimic_iv_views tables and that your query filters the "
            "same way.",
        ),
        diagram(
            "The cohort query",
            "SQL editor on the Serverless Starter Warehouse, grouped by race category",
            "cohort-screenshot",
            cohort_screenshot(),
            "This is the SQL editor with the Serverless Starter Warehouse attached. One: the Run "
            "all button. Two: the query joins coh_subject to coh_reading_so2 on subject_id and "
            "groups by race category, counting subjects and readings and averaging SaO2. Three: "
            "the result - 14 subjects in 2106-3 with a mean of 96.7, three in 2054-5 with 94.6, "
            "and two unknown with 95.8. If you get an empty result, check which branch your SQL "
            "came from: the original st_reading_so2 returned nothing.",
        ),
        diagram(
            "Expected outputs",
            "Row counts and query results to check your work against",
            "expected-outputs",
            expected_outputs(),
            "On the left are the row counts you should see from the first two demo steps: 100 "
            "patients in rv_patient with the race codes shown, 87 study subjects and 19 in the "
            "cohort. On the right is the output of the Your turn query. With a ten-minute window "
            "there are 18 pairs from 12 subjects; with five minutes, only 9 pairs, all in one "
            "category. And no pair meets the occult hypoxaemia definition. That's the honest "
            "answer for a 100-patient demo: the pipeline works, but the question needs the full "
            "dataset.",
        ),
        closing(
            "Questions?",
            PRESENTER,
            "That's the pulse oximetry study. We took a published question, rebuilt the cohort "
            "from FHIR with SQL on FHIR views and plain SQL, and found that the shape of the "
            "data mattered more than the SQL. The notebooks and SQL are in the open-fhir-training "
            "repository, and the SQL on FHIR and Pathling sites have the specification and the "
            "documentation. Grab me or one of the other leads if you get stuck on the pairing "
            "query.",
            [
                (REPO_URL, "Exercises"),
                (SOF_URL, "sql-on-fhir.org"),
                (PATHLING_URL, "pathling.csiro.au"),
            ],
        ),
    ],
}
