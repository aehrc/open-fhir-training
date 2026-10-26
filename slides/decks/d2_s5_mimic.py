"""Day 2, 11:00 block: reproducing a study of beta-blockers in septic shock on MIMIC-IV FHIR data.

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
    "Zhang L et al. Effectiveness of β-blockers in improving 28-day mortality in "
    "septic shock. Front Cardiovasc Med 2024;11:1438798."
)

# Each patient in the demo cohort, from the beta_blocker_septic_shock view: group,
# label, then days from the baseline (first vasopressor) to ICU admission, ICU
# discharge, onset of sepsis and death (None if not within 28 days), and the days of
# each beta-blocker dose from 3 days before to 28 days after the baseline.
TIMELINE = [
    (
        True,
        "74 F",
        -0.02,
        12.89,
        0.01,
        None,
        [-1.2, -0.7, 1.4, 1.5, 3.9, 4.3, 13.0, 13.2, 13.5, 13.8, 14.0, 14.3, 14.5]
        + [14.8, 15.0, 15.2, 15.5, 15.7, 16.0, 16.2, 16.5, 16.7, 17.0, 17.2, 17.5]
        + [17.7, 18.0, 18.2, 18.5, 18.7, 19.2, 19.5, 19.7, 20.0, 20.2, 20.5, 20.7]
        + [21.2, 21.5],
    ),
    (True, "60 M", -0.01, 4.87, 0.0, 4.19, [0.7]),
    (
        False,
        "66 M",
        -1.03,
        9.46,
        -0.96,
        11.19,
        [5.7, 5.9, 6.4, 6.7, 6.9, 7.2, 7.4, 7.7, 8.0, 8.2, 8.4, 8.7],
    ),
    (False, "43 M", -0.6, 15.09, -0.59, None, []),
    (False, "72 M", -0.03, 9.04, -0.18, None, [11.8, 12.1, 12.7, 13.0, 13.7]),
    (False, "79 M", 0.0, 13.9, -0.2, None, []),
    (
        False,
        "69 M",
        -0.02,
        20.51,
        0.32,
        19.49,
        [3.4, 3.5, 4.3, 4.4, 5.0, 5.2, 5.5, 5.7, 6.0, 6.3, 6.5, 6.7, 9.6, 11.8],
    ),
    (False, "60 F", -0.3, 2.22, -0.39, None, []),
    (
        False,
        "51 M",
        -1.02,
        7.34,
        -0.96,
        None,
        [2.9, 7.4, 7.9, 8.1, 8.3, 8.9, 9.1, 9.4, 9.9, 10.1, 10.4, 10.9, 11.1]
        + [11.4, 11.8, 12.1, 12.3, 12.8, 13.1, 13.4, 13.9, 14.1, 14.3, 15.2]
        + [15.4, 15.8],
    ),
    (False, "63 M", 0.0, 5.05, 0.35, 4.17, []),
]


def mark(x, y, w, h, fill=ROSE):
    """A translucent band behind lines of code, to show what matters."""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{fill}" '
        f'fill-opacity="0.35"/>'
    )


def code_row_y(y, i, title=True, fs=14, lh=1.45):
    """The top of row i in a kit.code() card at y, for marking rows."""
    head = 30 if title else 0
    return y + head + 8 + i * fs * lh + fs * 0.15


def clinical_question():
    """Septic shock, the case for and against beta-blockers, and the published result."""
    b = []
    # Septic shock.
    b.append(rect(10, 10, 440, 205, PINK, rx=12))
    b.append(text(30, 42, "Septic shock", 19, "start", 700))
    b.append(
        text(
            30,
            66,
            "Sepsis that needs vasopressors to hold blood pressure",
            14,
            "start",
            400,
            MUTED,
        )
    )
    for i, s in enumerate(
        [
            "Infection with organ dysfunction (SOFA >= 2)",
            "Norepinephrine or vasopressin infusion",
            "Often still tachycardic after fluids",
        ]
    ):
        b.append(text(30, 112 + i * 34, "· " + s, 16, "start"))
    # Beta-blockers.
    b.append(rect(490, 10, 440, 205, BLUE, rx=12))
    b.append(text(510, 42, "Add a beta-blocker?", 19, "start", 700))
    b.append(text(510, 66, "Esmolol, metoprolol or labetalol", 14, "start", 400, MUTED))
    for x, fill, head, rows in [
        (510, MINT, "For", ["Slows the heart", "Shields it from", "catecholamines"]),
        (
            720,
            PEACH,
            "Against",
            ["Lowers cardiac", "output when blood", "pressure is low"],
        ),
    ]:
        b.append(rect(x, 84, 195, 116, fill, rx=8))
        b.append(text(x + 14, 108, head, 15, "start", 700))
        for j, r in enumerate(rows):
            b.append(text(x + 14, 134 + j * 21, r, 15, "start"))
    # The published result.
    b.append(rect(10, 235, 920, 100, YELLOW, rx=12))
    b.append(
        text(
            30,
            266,
            "4,860 patients with septic shock in the full MIMIC-IV database",
            18,
            "start",
            700,
        )
    )
    b.append(
        text(
            30,
            293,
            "After matching (619 pairs), 28-day mortality was 21.5% with a beta-blocker "
            "and 27.1% without",
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
            ["NDJSON files", "MimicPatient.ndjson,", "MimicMedication..."],
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
        ("56,535", ["Medication-", "Administrations"]),
        ("813,540", ["Observations"]),
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
                '"medicationCodeableConcept": {',
                '  "coding": [ {',
                '    "system": "http://mimic.mit.edu/fhir/',
                "               mimic/CodeSystem/",
                '               mimic-medication-icu",',
                '    "code": "221906",',
                '    "display": "Norepinephrine" } ] }',
            ],
            "MedicationAdministration: a local item id",
            fs=13,
            lh=1.3,
        )
    )
    return svg(940, 340, b)


def study_design():
    """The timing of each criterion, relative to the suspected infection and the baseline."""
    b = []
    day2 = 100  # 48 hours, in px; the windows are drawn to this scale.
    onset, base = 270, 350
    rows = [
        ("Suspected infection", 52),
        ("Sepsis", 112),
        ("Septic shock", 172),
        ("Treatment group", 232),
        ("Outcome", 292),
    ]
    for label, y in rows:
        b.append(text(150, y + 5, label, 15, "end", 700))
    # Onset of the suspected infection, and the baseline.
    b.append(line(onset, 30, onset, 312, GREY, 1.6, dash="5 4", arrow=None))
    b.append(line(base, 22, base, 312, RED, 2, arrow=None))
    b.append(text(base + 6, 16, "baseline: first vasopressor", 14, "start", 700, RED))
    b.append(text(onset, 332, "onset", 14, "middle", 400, MUTED))
    # Suspected infection: an antibiotic and a culture close together.
    b.append(circle(onset, 52, 8, AMBER, INK, 1.4))
    b.append(text(onset - 14, 57, "antibiotic", 14, "end", 400))
    b.append(circle(onset + 40, 52, 8, LAVENDER, INK, 1.4))
    b.append(text(onset + 40, 82, "culture", 14, "middle", 400))
    b.append(
        text(
            base + 14,
            57,
            "culture <= 24 h after the antibiotic, or antibiotic <= 72 h after the culture",
            13,
            "start",
            400,
            MUTED,
        )
    )
    # Sepsis: SOFA from the worst values around the onset.
    b.append(rect(onset - day2, 97, day2 * 1.5, 30, MINT, rx=6))
    b.append(
        text(
            base + 14,
            117,
            "SOFA >= 2 from the worst values, 48 h before to 24 h after",
            14,
            "start",
        )
    )
    # Septic shock: a vasopressor within 48 hours of the onset of sepsis.
    b.append(rect(onset - day2, 157, day2 * 2, 30, PEACH, rx=6))
    b.append(circle(base, 172, 7, RED, INK, 1.2))
    b.append(
        text(
            onset + day2 + 12,
            177,
            "norepinephrine or vasopressin within 48 h of the onset",
            14,
            "start",
        )
    )
    # Treatment group: a beta-blocker in the 48 hours after the baseline.
    b.append(rect(base, 217, day2, 30, BLUE, rx=6))
    b.append(
        text(
            base + day2 + 12,
            237,
            "esmolol, metoprolol or labetalol in the next 48 h",
            14,
            "start",
        )
    )
    # Outcome.
    b.append(line(base, 292, 900, 292, INK, 2))
    b.append(text(625, 282, "death within 28 days of the baseline", 14, "middle", 700))
    b.append(
        text(
            930,
            332,
            "Also: first ICU stay, aged 18+, ICU stay >= 48 h, no contraindication",
            13,
            "end",
            400,
            MUTED,
        )
    )
    return svg(940, 340, b)


def views():
    """Eight views, one patient-level view and a summary, with row counts."""
    b = []
    top, h = 64, 278

    def column(x, w, fill, title, how):
        b.append(text(x + w / 2, 20, title, 16, "middle", 700))
        b.append(text(x + w / 2, 44, how, 14, "middle", 400, MUTED))
        b.append(rect(x, top, w, h, fill, rx=10))

    def row(x, w, ry, name, n, fs=13, family="JetBrains Mono"):
        b.append(rect(x + 8, ry, w - 16, 28, "#fff", sw=1.2, rx=5))
        b.append(text(x + 16, ry + 19, name, fs, "start", 400, "#222", family))
        if n:
            b.append(text(x + w - 16, ry + 19, n, 14, "end", 700, INK))

    column(0, 150, AMBER, "FHIR tables", "Pathling encoders")
    row(0, 150, top + 10, "mimic_iv_demo", "", 12.5)
    b.append(
        lines(
            75,
            top + 150,
            [
                "Patient",
                "Encounter",
                "Condition",
                "Specimen",
                "Observation",
                "Medication-",
                "Administration",
            ],
            14,
            400,
            MUTED,
        )
    )
    column(176, 330, LAVENDER, "8 views", "SQL on FHIR, Pathling")
    for j, (name, n) in enumerate(
        [
            ("patient_view", "100"),
            ("icu_stay_view", "140"),
            ("diagnosis_view", "5,051"),
            ("antibiotic_view", "2,193"),
            ("microbiology_specimen_view", "1,291"),
            ("sofa_observation_view", "28,134"),
            ("vasoactive_view", "1,110"),
            ("beta_blocker_view", "1,457"),
        ]
    ):
        row(176, 330, top + 10 + j * 33, name, n)
    column(532, 230, BLUE, "Patient-level view", "Spark SQL, one CTE per step")
    row(532, 230, top + 10, "beta_blocker_septic_shock", "", 12)
    b.append(
        lines(
            647,
            top + 120,
            ["100 rows: one per", "patient, one column", "per criterion"],
            15,
        )
    )
    b.append(text(647, top + 210, "in_cohort: 10", 16, "middle", 700, INK))
    column(788, 150, MINT, "Summary", "Spark SQL")
    row(788, 150, top + 10, "Beta-blocker", "2", 13, "Open Sans")
    row(788, 150, top + 43, "No beta-blocker", "8", 13, "Open Sans")
    b.append(lines(863, top + 150, ["28-day", "mortality", "by group"], 15))
    for x in (176, 532, 788):
        b.append(line(x - 24, top + h / 2, x - 3, top + h / 2))
    return svg(940, 345, b)


def fhirpath():
    """The antibiotic view: selecting by category, and a time from a choice type."""
    b = []
    fs, lh = 12.5, 1.32
    rows = [
        "antibiotics = data.view(",
        '  "MedicationAdministration",',
        '  select=[{"column": [',
        '    {"name": "patient_id",',
        '     "path": "subject.getReferenceKey()"},',
        '    {"name": "start_time",',
        '     "path": "effective.ofType(dateTime)',
        '            | effective.ofType(Period).start"},',
        '    {"name": "medicine",',
        '     "path": "medication.ofType(CodeableConcept)',
        '              .coding.display"}]}],',
        '  where=[{"path": "category.coding.where(',
        "    system = '.../mimic-medadmin-category-icu'",
        "    and (code = '08-Antibiotics (IV)'",
        "      or code = '09-Antibiotics (Non IV)'))",
        '    .exists()"}])',
    ]
    b.append(code(0, 0, 560, rows, "create_beta_blocker_septic_shock_views.py", fs, lh))
    b.append(mark(6, code_row_y(0, 4, fs=fs, lh=lh), 548, fs * lh, TEAL))
    b.append(mark(6, code_row_y(0, 6, fs=fs, lh=lh), 548, fs * lh * 2))
    b.append(mark(6, code_row_y(0, 11, fs=fs, lh=lh), 548, fs * lh * 5, MINT))
    for n, row_ in [(1, 4), (2, 6.5), (3, 13)]:
        b.append(callout(n, 548, code_row_y(0, row_, fs=fs, lh=lh) + fs * lh / 2))
    notes = [
        (
            1,
            [
                "getReferenceKey() matches",
                "the Patient's getResourceKey(),",
                "so views join",
            ],
        ),
        (
            2,
            [
                "An infusion has a Period, a",
                "bolus a dateTime: ofType()",
                "picks each, | takes either",
            ],
        ),
        (
            3,
            [
                "Select by the ICU's category,",
                "not a list of antibiotics;",
                "the categories do the work",
            ],
        ),
    ]
    for i, (n, rs) in enumerate(notes):
        y = 30 + i * 108
        b.append(callout(n, 600, y))
        for j, r in enumerate(rs):
            b.append(text(624, y + 5 + j * 22, r, 15, "start"))
    return svg(940, 345, b)


def two_records():
    """Beta-blockers in the ICU record and the eMAR, and the patients found in each."""
    b = []
    cards = [
        (
            0,
            BLUE,
            "ICU bedside record",
            "mimic-medication-icu",
            [
                "221429 Esmolol · 225974 Metoprolol · 225153 Labetalol",
                "Intravenous doses, charted at the bedside",
            ],
        ),
        (
            132,
            PEACH,
            "Hospital eMAR",
            "mimic-medication-formulary-drug-cd",
            [
                "METO25 · METO12.5HT · TOPR50 · LABE100 · ...",
                "or mimic-medication-name: 'Metoprolol Tartrate'",
                "Oral metoprolol is only recorded here",
            ],
        ),
    ]
    for y, fill, head, system, rows in cards:
        b.append(rect(0, y, 450, 120, fill, rx=10))
        b.append(text(16, y + 26, head, 16, "start", 700))
        b.append(text(16, y + 49, system, 13, "start", 400, "#222", "JetBrains Mono"))
        for j, r in enumerate(rows):
            b.append(
                text(
                    16,
                    y + 72 + j * 20,
                    r,
                    14,
                    "start",
                    400,
                    MUTED if j == len(rows) - 1 else "#222",
                )
            )
    # Patients with a beta-blocker in each record.
    b.append(
        text(480, 18, "Patients given a beta-blocker, by record", 15, "start", 700)
    )
    scale = 5.4
    for i, (label, doses, n, fill) in enumerate(
        [
            ("ICU record", "152 doses", 30, BLUE),
            ("eMAR", "1,305 doses", 39, PEACH),
            ("Either", "1,457 doses", 53, MINT),
        ]
    ):
        y = 44 + i * 62
        b.append(text(600, y + 18, label, 15, "end", 700))
        b.append(text(600, y + 36, doses, 13, "end", 400, MUTED))
        b.append(rect(612, y + 4, n * scale, 36, fill, rx=4))
        b.append(text(612 + n * scale + 8, y + 28, str(n), 16, "start", 700, INK))
    b.append(
        text(
            480,
            240,
            "The ICU record alone misses 23 of the 53",
            14,
            "start",
            400,
            MUTED,
        )
    )
    b.append(rect(0, 266, 935, 74, YELLOW, rx=10))
    b.append(
        text(
            20,
            296,
            "Codes, not prefixes: METO10 and METO10I look like metoprolol",
            16,
            "start",
            700,
        )
    )
    b.append(
        text(
            20,
            324,
            "The NDC codes they were dispensed under show metoclopramide, an anti-emetic",
            15,
            "start",
        )
    )
    return svg(940, 345, b)


def sofa():
    """The six SOFA components, the items behind them, and one CASE expression."""
    b = []
    cols = [
        ("Component", 160),
        ("Measurement", 230),
        ("MIMIC-IV item", 365),
        ("Patients measured", 180),
    ]
    rows = [
        ("Respiration", "PaO2 / FiO2", "220224, 223835", "63 of 100"),
        ("Coagulation", "Platelets", "227457", "95"),
        ("Liver", "Bilirubin", "225690", "47"),
        (
            "Cardiovascular",
            "MAP, vasopressor rates",
            "220052, 220181 + vasoactive_view",
            "100",
        ),
        ("Nervous system", "Glasgow Coma Scale", "220739, 223900, 223901", "100"),
        ("Renal", "Creatinine", "220615", "98"),
    ]
    b.append(table(0, 0, cols, rows, LAVENDER, 14, 29, mono_cols=(2,)))
    b.append(
        code(
            0,
            216,
            600,
            [
                "CASE WHEN dopamine > 15 OR epinephrine > 0.1",
                "          OR norepinephrine > 0.1 THEN 4",
                "     WHEN dopamine > 5 OR epinephrine > 0",
                "          OR norepinephrine > 0 THEN 3",
                "     WHEN dopamine > 0 OR dobutamine > 0 THEN 2",
                "     WHEN map < 70 THEN 1 ELSE 0 END",
            ],
            None,
            12.5,
            1.38,
        )
    )
    b.append(rect(620, 216, 315, 124, YELLOW, rx=10))
    for i, s in enumerate(
        [
            "Worst value from 48 h before",
            "to 24 h after the infection",
            "No measurement scores 0",
            "Every cohort patient scores 4",
            "here, from the vasopressors",
        ]
    ):
        b.append(text(636, 240 + i * 22, s, 14, "start", 700 if i in (0, 1) else 400))
    return svg(940, 345, b)


def attrition():
    """The criterion columns of the patient-level view, and who is left after each."""
    b = []
    fs, lh = 12, 1.38
    b.append(
        code(
            0,
            0,
            410,
            [
                "SELECT f.patient_id,",
                "  f.age >= 18 AS adult,",
                "  f.discharge_time >= f.admit_time",
                "    + INTERVAL 48 HOURS AS stay_48_hours,",
                "  si.first_onset",
                "    AS suspected_infection_time,",
                "  s.onset AS sepsis_time,",
                "  k.baseline_time,",
                "  c.av_block, c.acute_mi,",
                "  c.acute_heart_failure, c.asthma,",
                "  ... AS in_cohort,",
                "  b.first_beta_blocker_time IS NOT NULL",
                "    AS beta_blocker,",
                "  ... AS died_within_28_days",
                "FROM first_icu_stay f LEFT JOIN ...",
            ],
            "beta_blocker_septic_shock (abridged)",
            fs,
            lh,
        )
    )
    steps = [
        ("First ICU stay", 100),
        ("Aged 18 or over", 100),
        ("ICU stay of 48 h or more", 53),
        ("Suspected infection", 41),
        ("Sepsis (SOFA 2 or more)", 39),
        ("Septic shock (vasopressor)", 17),
        ("No contraindication", 10),
    ]
    scale = 2.3
    x0 = 650
    for i, (label, n) in enumerate(steps):
        y = 4 + i * 34
        b.append(text(x0 - 10, y + 19, label, 14, "end"))
        b.append(
            rect(x0, y + 2, n * scale, 24, MINT if i == 6 else "#E4E4E4", sw=1.2, rx=3)
        )
        b.append(text(x0 + n * scale + 6, y + 19, str(n), 14, "start", 700, INK))
    b.append(
        text(
            x0 + 10 * scale + 32,
            4 + 6 * 34 + 19,
            "2 with a beta-blocker, 8 without",
            14,
            "start",
            400,
            MUTED,
        )
    )
    b.append(
        lines(
            440,
            318,
            [
                "Of the 17 with septic shock: acute heart failure 5, asthma 3,",
                "acute myocardial infarction 2, complete heart block 0",
            ],
            13,
            400,
            MUTED,
            anchor="start",
            lh=1.35,
        )
    )
    return svg(940, 345, b)


def timeline():
    """One row per cohort patient, in days from the baseline."""
    b = []
    x0, x1, d0, d1 = 170, 905, -3, 28
    top, pitch = 46, 24

    def tx(day):
        return x0 + (day - d0) / (d1 - d0) * (x1 - x0)

    bottom = top + pitch * len(TIMELINE)
    b.append(
        f'<rect x="{tx(0)}" y="{top - 14}" width="{tx(2) - tx(0)}" '
        f'height="{bottom - top + 6}" fill="{MINT}" fill-opacity="0.6"/>'
    )
    b.append(line(tx(0), top - 14, tx(0), bottom - 8, RED, 1.6, arrow=None))
    for i, (bb, label, admit, discharge, sepsis, death, doses) in enumerate(TIMELINE):
        y = top + i * pitch
        group = "Beta-blocker" if bb else "No beta-blocker"
        b.append(
            text(x0 - 10, y + 5, f"{group} · {label}", 13, "end", 700 if bb else 400)
        )
        b.append(
            f'<rect x="{tx(max(admit, d0))}" y="{y - 6}" '
            f'width="{tx(min(discharge, d1)) - tx(max(admit, d0))}" height="12" rx="3" '
            f'fill="{BLUE if bb else LAVENDER}"/>'
        )
        for d in doses:
            b.append(line(tx(d), y - 9, tx(d), y + 9, TEAL, 2, arrow=None))
        b.append(circle(tx(sepsis), y, 5, AMBER, INK, 1.2))
        if death is not None:
            cx = tx(death)
            b.append(line(cx - 6, y - 6, cx + 6, y + 6, INK, 2.4, arrow=None))
            b.append(line(cx - 6, y + 6, cx + 6, y - 6, INK, 2.4, arrow=None))
    ay = bottom + 2
    b.append(line(x0, ay, x1, ay, INK, 1.2, arrow=None))
    for d in (0, 7, 14, 21, 28):
        b.append(line(tx(d), ay, tx(d), ay + 5, INK, 1.2, arrow=None))
        b.append(text(tx(d), ay + 20, str(d), 13))
    b.append(
        text(
            (x0 + x1) / 2,
            ay + 40,
            "Days from the first vasopressor",
            14,
            "middle",
            400,
            MUTED,
        )
    )
    # Legend.
    lx = x0
    b.append(rect(lx, 6, 30, 12, LAVENDER, rx=3))
    b.append(text(lx + 38, 17, "ICU stay", 13, "start"))
    lx += 120
    b.append(circle(lx + 6, 12, 5, AMBER, INK, 1.2))
    b.append(text(lx + 18, 17, "onset of sepsis", 13, "start"))
    lx += 150
    b.append(line(lx + 6, 3, lx + 6, 21, TEAL, 2, arrow=None))
    b.append(text(lx + 16, 17, "beta-blocker dose", 13, "start"))
    lx += 160
    b.append(line(lx, 6, lx + 12, 18, INK, 2.4, arrow=None))
    b.append(line(lx, 18, lx + 12, 6, INK, 2.4, arrow=None))
    b.append(text(lx + 20, 17, "death", 13, "start"))
    lx += 90
    b.append(rect(lx, 6, 30, 12, MINT, sw=0, rx=2))
    b.append(text(lx + 38, 17, "first 48 hours", 13, "start"))
    return svg(940, 345, b)


def results():
    """28-day mortality in each group, beside the published figures."""
    b = []
    ox, oy, ph = 70, 290, 240
    top = 60  # Percent at the top of the axis.

    def bar_y(v):
        return oy - v / top * ph

    b.append(line(ox, oy, ox, oy - ph - 6, INK, 1.4, arrow=None))
    b.append(line(ox, oy, 540, oy, INK, 1.4, arrow=None))
    for v in (0, 20, 40, 60):
        y = bar_y(v)
        b.append(line(ox - 5, y, ox, y, INK, 1.2, arrow=None))
        b.append(text(ox - 10, y + 5, f"{v}%", 13, "end", fill=MUTED))
    b.append(
        text(ox - 40, oy - ph - 16, "Died within 28 days", 13, "start", fill=MUTED)
    )
    groups = [
        ("Beta-blocker", BLUE, 50.0, "1 of 2", 21.5),
        ("No beta-blocker", LAVENDER, 37.5, "3 of 8", 27.1),
    ]
    for i, (name, fill, v, n, z) in enumerate(groups):
        x = ox + 40 + i * 230
        b.append(rect(x, bar_y(v), 80, oy - bar_y(v), fill, rx=2))
        b.append(text(x + 40, bar_y(v) - 26, f"{v}%", 15, weight=700))
        b.append(text(x + 40, bar_y(v) - 8, n, 13, fill=MUTED))
        b.append(rect(x + 90, bar_y(z), 80, oy - bar_y(z), "#E4E4E4", rx=2))
        b.append(text(x + 130, bar_y(z) - 8, f"{z}%", 15, weight=700, fill=MUTED))
        b.append(text(x + 85, oy + 22, name, 15, weight=700))
    b.append(rect(ox + 20, oy + 36, 14, 14, BLUE, sw=1.2, rx=2))
    b.append(rect(ox + 36, oy + 36, 14, 14, LAVENDER, sw=1.2, rx=2))
    b.append(text(ox + 56, oy + 48, "MIMIC-IV demo", 13, "start"))
    b.append(rect(ox + 170, oy + 36, 14, 14, "#E4E4E4", sw=1.2, rx=2))
    b.append(text(ox + 190, oy + 48, "Zhang et al., after matching", 13, "start"))
    b.append(rect(580, 0, 355, 340, YELLOW, rx=12))
    b.append(lines(757, 40, ["The method, not a finding"], 18, 700))
    for i, rows in enumerate(
        [
            ["10 patients: one death moves", "a group by 12.5 to 50 points"],
            ["Unadjusted: no propensity", "score matching"],
            ["Zhang et al. matched 619", "pairs from 4,860 patients"],
            ["The same SQL runs unchanged", "on the full MIMIC-IV"],
        ]
    ):
        y = 90 + i * 64
        b.append(text(600, y, "·", 18, "start", 700))
        for j, r in enumerate(rows):
            b.append(text(616, y + j * 22, r, 15, "start"))
    return svg(940, 345, b)


def demo_steps():
    """Three steps of the live demo, left to right."""
    b = []
    steps = [
        (
            LAVENDER,
            "Notebook",
            "beta_blocker_view",
            [
                ["create_beta_blocker_", "septic_shock_views"],
                ["Three code lists,", "three code systems"],
                ["Patients by record"],
                ["Result: 1,457 doses"],
            ],
        ),
        (
            BLUE,
            "SQL file",
            "the CTE chain",
            [
                ["combine_beta_blocker_", "septic_shock_views.sql"],
                ["One CTE per step,", "one column each"],
                ["in_cohort joins them"],
                ["Result: 10 in cohort"],
            ],
        ),
        (
            MINT,
            "SQL editor",
            "summary query",
            [
                ["Serverless Starter", "Warehouse"],
                ["28-day mortality", "by group"],
                ["Paste, then Run all"],
                ["Result: two rows"],
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


WINDOW_SQL = [
    "WITH treated AS (",
    "  SELECT c.patient_id, c.died_within_28_days,",
    "         COUNT(b.start_time) > 0 AS beta_blocker",
    "  FROM mimic_iv_beta_blocker_views.beta_blocker_septic_shock AS c",
    "  LEFT JOIN mimic_iv_beta_blocker_views.beta_blocker_view AS b",
    "    ON b.patient_id = c.patient_id",
    "   AND b.start_time BETWEEN c.baseline_time",
    "                        AND c.baseline_time + INTERVAL 48 HOURS",
    "  WHERE c.in_cohort",
    "  GROUP BY c.patient_id, c.died_within_28_days",
    ")",
    "SELECT beta_blocker, COUNT(*) AS patients,",
    "       COUNT_IF(died_within_28_days) AS deaths",
    "FROM treated",
    "GROUP BY beta_blocker ORDER BY beta_blocker DESC",
]


def your_turn():
    """The starting query, and what to do with it."""
    b = []
    fs, lh = 12, 1.35
    b.append(
        code(0, 0, 610, WINDOW_SQL, "Starting point (catalog hive_metastore)", fs, lh)
    )
    b.append(mark(6, code_row_y(0, 7, fs=fs, lh=lh), 598, fs * lh, AMBER))
    b.append(rect(0, 300, 610, 40, LAVENDER, rx=8))
    b.append(
        text(
            16,
            326,
            "As written: 2 patients with a beta-blocker, 8 without. Save tables to your own schema.",
            14,
            "start",
        )
    )
    b.append(rect(630, 0, 305, 180, MINT, rx=12))
    b.append(text(648, 30, "Move the window", 17, "start", 700))
    for i, s in enumerate(
        [
            "1  Run it: the same 2 and 8",
            "    as the summary query",
            "2  Try 24 HOURS, then 7 DAYS:",
            "    who changes group?",
            "3  Why not count everyone",
            "    ever given a beta-blocker?",
        ]
    ):
        b.append(text(648, 58 + i * 21, s, 15, "start"))
    b.append(rect(630, 192, 305, 148, AMBER, rx=12))
    b.append(text(648, 220, "Stretch", 17, "start", 700))
    for i, s in enumerate(
        [
            "Add a heart disease subgroup",
            "from diagnosis_view: Zhang",
            "et al. found the most benefit",
            "there. Or compare icu_hours.",
        ]
    ):
        b.append(text(648, 248 + i * 22, s, 14, "start"))
    return svg(940, 345, b)


def summary_screenshot():
    """The summary query and its result in the SQL editor, with callouts."""
    b = []
    name = "sql-septic-shock-summary"
    s1, _, h1, p1 = screenshot(name, 0, 0, 600, crop=(243, 92, 800, 210))
    s2, w2, h2, p2 = screenshot(name, 0, h1 + 20, 450, crop=(243, 576, 640, 82))
    b += [s1, s2]
    x, y = p1(252, 103)
    b.append(highlight(x - 2, y - 12, 102, 24))
    b.append(callout(1, x + 116, y))
    b.append(highlight(*p1(300, 220), *[v * 0.75 for v in (520, 41)]))
    b.append(callout(2, *p1(1000, 239)))
    b.append(
        highlight(
            *p2(296, 604),
            w2 - (p2(296, 0)[0] - p2(243, 0)[0]) - 4,
            h2 - (p2(0, 604)[1] - p2(0, 576)[1]) - 2,
        )
    )
    b.append(callout(3, *p2(905, 617)))
    notes = [
        (1, ["Warehouse attached;", "Run all"]),
        (2, ["The patient-level view,", "in_cohort rows only"]),
        (3, ["Two rows: 1 of 2 and", "3 of 8 died within", "28 days"]),
    ]
    for i, (n, rows) in enumerate(notes):
        ty = 30 + i * 105
        b.append(callout(n, 660, ty))
        b.append(
            lines(690, ty + (len(rows) - 1) * 9, rows, 15, 400, "#222", anchor="start")
        )
    return svg(940, 340, b)


def expected_outputs():
    """Row counts and Your turn results, for when the live demo is not available."""
    b = []
    b.append(
        code(
            0,
            0,
            450,
            [
                "patient_view                  100",
                "icu_stay_view                 140",
                "diagnosis_view              5,051",
                "antibiotic_view             2,193",
                "microbiology_specimen_view  1,291",
                "sofa_observation_view      28,134",
                "vasoactive_view             1,110",
                "beta_blocker_view           1,457",
                "beta_blocker_septic_shock     100",
                "  where in_cohort              10",
            ],
            "Rows in mimic_iv_beta_blocker_views",
            fs=13,
            lh=1.38,
        )
    )
    b.append(text(480, 20, "Your turn query: deaths / patients", 15, "start", 700))
    b.append(
        table(
            480,
            34,
            [("Window", 130), ("Beta-blocker", 150), ("No beta-blocker", 175)],
            [
                ("48 HOURS", "1 / 2", "3 / 8"),
                ("24 HOURS", "1 / 1", "3 / 9"),
                ("7 DAYS", "3 / 5", "1 / 5"),
                ("28 DAYS", "3 / 6", "1 / 4"),
            ],
            BLUE,
            14,
            32,
            mono_cols=(0,),
        )
    )
    b.append(rect(0, 254, 935, 86, YELLOW, rx=10))
    b.append(
        text(
            20,
            284,
            "The window decides who counts as treated: from 1 to 6 of the 10 patients",
            15,
            "start",
            700,
        )
    )
    b.append(
        text(
            20,
            308,
            "Every group is too small to compare; the pipeline is what carries to the full MIMIC-IV",
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
    "file": "track-3-d2-5-septic-shock-study",
    "slides": [
        title_slide(
            "A real-world study on FHIR: beta-blockers in septic shock",
            f"Day 2, 11:00 · {EVENT}",
            "This block is a worked example of a real research question, answered on FHIR data. "
            "We'll take a published study of beta-blockers in septic shock, rebuild its cohort "
            "from the MIMIC-IV demo data on FHIR, using SQL on FHIR views and Spark SQL, and "
            "look at what the shape of the data does to the analysis. About twenty minutes of "
            "slides, a short demo, and then the rest of the block is yours to extend it.",
        ),
        diagram(
            "The clinical question",
            "Does a beta-blocker early in septic shock change 28-day mortality?",
            "clinical-question",
            clinical_question(),
            "Septic shock is sepsis that needs vasopressors, usually norepinephrine, to keep the "
            "blood pressure up. Many patients stay tachycardic after fluid resuscitation. "
            "Beta-blockers slow the heart and protect it from catecholamine stress, but they "
            "also lower cardiac output, so their use is controversial. In 2024 Zhang and "
            "colleagues looked at 4,860 patients with septic shock in the full MIMIC-IV "
            "database. After propensity score matching, 28-day mortality was 21.5 percent in "
            "patients given a beta-blocker within 48 hours of starting vasopressors, and 27.1 "
            "percent in those who were not. Our question is whether we can select the same "
            "cohort from FHIR data.",
        ),
        diagram(
            "The data: MIMIC-IV demo on FHIR",
            "100 de-identified ICU patients from PhysioNet, already loaded into the workspace",
            "the-data",
            the_data(),
            "MIMIC-IV is a de-identified intensive care dataset used widely in research, and it's "
            "the database Zhang et al. used. PhysioNet publishes an open demo of 100 patients, "
            "converted to FHIR. We imported the NDJSON files with Pathling - there's one file per "
            "MIMIC profile, so the import maps file names to resource types - and wrote one table "
            "per resource type. This study leans on MedicationAdministration: 56,535 of them, "
            "beside 813,540 Observations. Note the codes: MIMIC uses its own item ids, so 221906 "
            "is norepinephrine in the ICU medication code system, and you need the MIMIC "
            "dictionary to know that.",
        ),
        diagram(
            "Study design",
            "Most criteria are about when one event happened relative to another",
            "study-design",
            study_design(),
            "This is the timing of each criterion. A suspected infection, following Sepsis-3, is "
            "an antibiotic and a microbiology culture close together: the culture within 24 hours "
            "after the antibiotic, or the antibiotic within 72 hours after the culture. Its onset "
            "is the earlier of the two. Sepsis is a SOFA score of 2 or more, from the worst "
            "values in the 48 hours before to 24 hours after that onset. Septic shock is "
            "norepinephrine or vasopressin started within 48 hours of the onset of sepsis, and "
            "the first start is the baseline. A beta-blocker in the 48 hours after the baseline "
            "puts a patient in the treatment group, and the outcome is death within 28 days. On "
            "top of that: first ICU stay, adults, at least 48 hours in the ICU, and no "
            "contraindication.",
        ),
        diagram(
            "Views, then one patient-level view",
            "SQL on FHIR flattens six resource types; plain SQL does the study logic",
            "views",
            views(),
            "The work is split into layers. Eight SQL on FHIR views, run by Pathling in the "
            "create_beta_blocker_septic_shock_views notebook, turn nested FHIR into flat tables: "
            "patients, ICU stays, diagnoses, antibiotics, microbiology specimens, the "
            "observations behind the SOFA score, vasoactive infusions and beta-blocker doses. They "
            "contain no study logic. A SQL file then builds one view with a row per patient and a "
            "column per criterion, as a chain of common table expressions. The summary query "
            "counts deaths by group. These row counts are from the workspace today.",
        ),
        diagram(
            "FHIRPath does the selecting",
            "The antibiotic view: join keys, a choice type, and a category instead of a code list",
            "fhirpath",
            fhirpath(),
            "Here's one view in full. One: getReferenceKey on the subject gives a key that "
            "matches getResourceKey on the Patient, so views join on it. Two: effective is a "
            "choice type. An infusion has a Period and a bolus has a dateTime; ofType picks each, "
            "and the union operator takes whichever is present. Three: rather than listing every "
            "antibiotic, the where clause selects administrations in the ICU's two antibiotic "
            "categories. The categories also include the diluent rows, like dextrose 5 percent, "
            "which doesn't change the result here. Antibiotics given on the ward have no "
            "category, so they aren't seen.",
        ),
        diagram(
            "One medicine, two records",
            "Beta-blockers are charted in the ICU and in the hospital's eMAR, in different code systems",
            "two-records",
            two_records(),
            "MIMIC records medicines in two systems, and FHIR keeps the code system of each. The "
            "ICU bedside system codes intravenous doses with item ids. The hospital's electronic "
            "medication administration record uses the pharmacy's formulary codes, and sometimes "
            "the medicine's name. Oral metoprolol, the most common beta-blocker, is only in the "
            "eMAR. Looking at the ICU record alone finds 30 patients; both records find 53. The "
            "trap: formulary codes have no display text, and METO10 and METO10I look like "
            "metoprolol, but the NDC codes they were dispensed under show they are "
            "metoclopramide, an anti-emetic. So the view lists confirmed codes, not prefixes.",
        ),
        diagram(
            "Scoring SOFA in SQL",
            "Six components from ten ICU items and the vasoactive infusions, each scored 0 to 4",
            "sofa",
            sofa(),
            "The SOFA score drives the sepsis criterion. It has six components, and the table "
            "shows the MIMIC items behind each and how many of the 100 patients have any value. "
            "Bilirubin and blood gases are only measured when there's a reason, so a component "
            "with no measurement scores zero. The SQL takes the worst value of each measurement "
            "in the window around the suspected infection and scores it with a CASE expression, "
            "like this one for the cardiovascular component. It is simplified: no urine output, "
            "and the respiratory score doesn't check for ventilation. Every patient in the cohort "
            "scores 4 for cardiovascular, because the vasopressors that make them eligible also "
            "score.",
        ),
        diagram(
            "Each criterion is a column",
            "The patient-level view makes the attrition at every step visible",
            "attrition",
            attrition(),
            "The combine SQL file builds one common table expression per step and then selects "
            "one row per patient, with each criterion as a column. in_cohort is true when they "
            "all hold. That makes the attrition easy to see: all 100 patients are adults, about "
            "half are out on the 48-hour ICU stay, 41 have a suspected infection, 39 meet "
            "Sepsis-3, 17 have septic shock, and 7 of those are excluded for a contraindication, "
            "mostly acute heart failure. That leaves 10 patients: 2 with a beta-blocker and 8 "
            "without. If a number looks wrong, you can filter on any column and see why.",
        ),
        diagram(
            "What happened to each patient",
            "The 10 patients in days from the first vasopressor; groups are set by the first 48 hours",
            "timeline",
            timeline(),
            "Each row is one patient, aligned on the baseline. The bar is the ICU stay, the "
            "orange dot is the onset of sepsis, the teal ticks are beta-blocker doses and a cross "
            "is a death within 28 days. The shaded band is the 48-hour window that decides the "
            "group. Two patients were given esmolol in that window. Four in the control group "
            "were given beta-blockers later in their stay, and the first patient's doses carry on "
            "after ICU discharge, from the eMAR. So the groups are defined by what happened in "
            "the first 48 hours, not by whether someone was ever treated.",
        ),
        diagram(
            "Did beta-blockers make a difference?",
            "28-day mortality in the demo cohort, beside the published figures",
            "results",
            results(),
            "Here is the summary query's result: one of two patients died in the beta-blocker "
            "group, and three of eight in the control group. Please don't read anything into "
            "these numbers. With two patients, one death is 50 points. The comparison is also "
            "unadjusted, where Zhang et al. matched 619 pairs on age, sex, weight and severity "
            "scores. What this shows is that the cohort definition runs end to end on FHIR, and "
            "the same views and SQL would run unchanged on the full MIMIC-IV.",
        ),
        diagram(
            "Demo",
            "From a code list in a view to a result in three steps",
            "demo",
            demo_steps(),
            "Here's what I'll show. One: open notebooks/mimic_iv/"
            "create_beta_blocker_septic_shock_views in the Git folder, attached to the Open FHIR "
            "Training Cluster. Scroll to the beta-blocker view, show the three code lists, one per "
            "code system, and the chart of patients by record. I won't rewrite the shared tables. "
            "Two: open sql/mimic_iv/combine_beta_blocker_septic_shock_views.sql and walk through "
            "the common table expressions, from first ICU stay to the beta-blocker window. Three: "
            "open the SQL editor on the Serverless Starter Warehouse, paste the summary query from "
            "the bottom of that file, run it, and read out the two rows.",
        ),
        diagram(
            "Your turn",
            "Recount the groups with a different treatment window",
            "your-turn",
            your_turn(),
            "For the rest of the block, take this query as a starting point. It runs as is in the "
            "SQL editor with the hive_metastore catalog. It joins the cohort to every "
            "beta-blocker dose in the 48 hours after the baseline and counts patients and deaths "
            "by group. Run it, then change the interval on the highlighted line to 24 hours and "
            "to 7 days, and watch patients change group. Then think about why the study fixes the "
            "window from the baseline: a patient who dies early has less time to be given a "
            "beta-blocker, so a longer window starts to sort patients by how long they lived. If "
            "you want more, add a heart disease subgroup from diagnosis_view. If you create "
            "tables, put them in your own schema.",
        ),
        section(
            "Demo walkthrough (backup)",
            "If the live demo doesn't cooperate, here's what you would have seen. The next two "
            "slides show the summary query in the SQL editor, with its result, and then the row "
            "counts of each view and the output of the Your turn query. They're also a useful "
            "reference later in the block: if your own numbers differ from these, check that "
            "you're reading the shared mimic_iv_beta_blocker_views tables.",
        ),
        diagram(
            "The summary query",
            "SQL editor on the Serverless Starter Warehouse, 28-day mortality by group",
            "summary-screenshot",
            summary_screenshot(),
            "This is the SQL editor with the Serverless Starter Warehouse attached. One: the Run "
            "all button. Two: the query reads the patient-level view and keeps the rows where "
            "in_cohort is true, grouped by the beta_blocker column. Three: the result - two "
            "patients in the beta-blocker group with one death, 50 percent, and eight in the "
            "control group with three deaths, 37.5 percent.",
        ),
        diagram(
            "Expected outputs",
            "Row counts and query results to check your work against",
            "expected-outputs",
            expected_outputs(),
            "On the left are the row counts of the eight views and the patient-level view, with "
            "the 10 patients where in_cohort is true. On the right is the Your turn query with "
            "four windows, shown as deaths over patients. At 48 hours it matches the summary. At "
            "24 hours one patient moves to the control group; at 7 days five patients are "
            "treated, and at 28 days six. That's the honest answer for a 100-patient demo: the "
            "pipeline works, and the definition matters, but the question needs the full "
            "dataset.",
        ),
        closing(
            "Questions?",
            PRESENTER,
            "That's the septic shock study. We took a published question, rebuilt its cohort from "
            "FHIR with SQL on FHIR views and plain SQL, and found that timing and the shape of the "
            "medication records mattered more than the SQL. The notebook and SQL are in the "
            "open-fhir-training repository, and the SQL on FHIR and Pathling sites have the "
            "specification and the documentation. Grab me or one of the other leads if you get "
            "stuck on the window query.",
            [
                (REPO_URL, "Exercises"),
                (SOF_URL, "sql-on-fhir.org"),
                (PATHLING_URL, "pathling.csiro.au"),
            ],
        ),
    ],
}
