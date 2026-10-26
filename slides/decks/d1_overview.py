"""Day 1, 10:30 main room: a 10 minute overview of Track 3 for all attendees.

Author: John Grimes
"""

from kit import (
    BLUE,
    INK,
    LAVENDER,
    MINT,
    MUTED,
    PEACH,
    TEAL,
    circle,
    closing,
    diagram,
    lines,
    qr,
    rect,
    svg,
    text,
    title_slide,
)

from decks._shared import (
    EVENT,
    FORM_URL,
    PRESENTER,
    TRACK,
    environment,
    schedule,
    standards_map,
)


def adventures():
    """Four strands of Track 3, each with its lead, around the shared data."""
    b = []
    strands = [
        (
            BLUE,
            "Analytics with SQL on FHIR",
            "John Grimes",
            ["Pathling and Databricks", "standards for analytics"],
        ),
        (
            LAVENDER,
            "Terminology",
            "James Grant",
            ["SNOMED CT-AU, AMT", "enrich, classify, group"],
        ),
        (
            MINT,
            "Text to structured data",
            "Dion McMurtrie",
            ["NLP and terminology", "notes to FHIR resources"],
        ),
        (
            PEACH,
            "Queensland Health context",
            "Duncan Pullen",
            ["how QH data and systems work", "which questions matter locally"],
        ),
    ]
    pos = [(10, 10), (500, 10), (10, 185), (500, 185)]
    for (fill, title, lead, rows), (x, y) in zip(strands, pos):
        b.append(rect(x, y, 430, 145, fill, rx=12))
        b.append(text(x + 20, y + 36, title, 19, "start", 700))
        b.append(text(x + 20, y + 62, lead, 15, "start", 400, MUTED))
        for j, r in enumerate(rows):
            b.append(text(x + 20, y + 96 + j * 24, "· " + r, 15, "start"))
    b.append(circle(470, 167, 58, "#fff", TEAL, 2.5))
    b.append(lines(470, 167, ["Your", "question"], 17, 700, INK))
    return svg(940, 340, b)


def join_in():
    """How to get into the analytics environment, with the form QR code."""
    b = [
        rect(10, 10, 600, 315, "#fff", rx=12),
        text(30, 50, "To use the Databricks workspace", 20, "start", 700),
    ]
    steps = [
        "Scan the code and give us your email address",
        "Accept the invitation email from Databricks",
        "Sign in, then open Workspace > Repos >",
        "    John.Grimes@csiro.au > open-fhir-training",
        "Synthetic and de-identified data only - please",
        "    do not upload anything sensitive",
    ]
    for i, s in enumerate(steps):
        b.append(text(30, 92 + i * 38, s, 17, "start"))
    b.append(qr(FORM_URL, 680, 20, 220, "forms.cloud.microsoft/r/inJ0BxKvw7", 14))
    return svg(940, 340, b)


DECK = {
    "file": "track-3-day-1-overview",
    "slides": [
        title_slide(
            TRACK,
            f"Track overview · {EVENT}",
            "Track 3 is about getting value out of FHIR data: analytics, terminology and text. "
            "I'm John Grimes from CSIRO's Australian e-Health Research Centre, and I'll be one of "
            "four people looking after the track over the two days.",
        ),
        diagram(
            "What Track 3 is about",
            "Using FHIR data for insights and decision support",
            "standards-map",
            standards_map(),
            "The track is about the whole path from data to decisions. First you have to get the "
            "data - from a FHIR server with bulk export, or by mapping the extracts you already "
            "have. Then you shape it into tables you can analyse, using SQL on FHIR views and "
            "terminology. Then you analyse it with whatever tools you prefer. And finally you put "
            "the results back in front of clinicians, with standards like CQL, CDS Hooks and SMART "
            "apps. Over the two days we'll touch every box on this slide, with most of the "
            "hands-on time in the middle two.",
        ),
        diagram(
            "Pick your own adventure",
            "Four strands, four leads - you can move between them, and between tracks",
            "adventures",
            adventures(),
            "There are four strands, each with a lead. I'll run the analytics strand: SQL on FHIR, "
            "Pathling, and the standards around analytics, in a shared Databricks workspace. James "
            "Grant leads terminology: SNOMED CT-AU, AMT, and how to use terminology to enrich, "
            "classify and group data. Dion McMurtrie leads the text strand, turning clinical notes "
            "into structured, coded FHIR data. Duncan Pullen brings the Queensland Health "
            "perspective. Bring a question you care about and we'll help you find the right "
            "strand. You can move between strands, and between tracks.",
        ),
        diagram(
            "A hands-on analytics environment",
            "A shared Databricks workspace with synthetic and de-identified FHIR data loaded",
            "environment",
            environment(),
            "For the analytics strand we've set up a Databricks workspace. It already has two "
            "datasets loaded as FHIR: 8,297 synthetic Queensland patients from Synthea, conforming to "
            "AU Core, and the MIMIC-IV demo, 100 de-identified intensive care patients. There is "
            "also a flat CSV extract to practise mapping legacy data into FHIR. The notebooks from "
            "our open FHIR training repository are ready to run against a shared cluster. Everyone "
            "reads the same shared tables, and if you want to change things you write to your own "
            "schema.",
        ),
        diagram(
            "Getting access",
            "Scan now - we'll send your invitation before the kick-off",
            "join-in",
            join_in(),
            "If you'd like to use the workspace, scan this code now. The form asks only for your "
            "email address, and explains how we use it: we send you a Databricks invitation, and "
            "we remove your account and delete the responses by the end of November. Please only "
            "use the synthetic and de-identified data we provide - nothing sensitive goes into "
            "this environment. If you don't want an account, you can still follow along and pair "
            "with someone.",
        ),
        diagram(
            "Track 3 over two days",
            "Each block opens with 30 minutes of context and a demo, then hands-on time",
            "schedule",
            schedule(),
            "Each Track 3 block starts with about 30 minutes from me: some context on a standard "
            "or a technique, then a live demonstration in the workspace. The rest of each block is "
            "yours, working on the exercises or your own questions, with James, Dion, Duncan and "
            "me on hand. On Friday afternoon each group gets a few minutes in the main room for "
            "show and tell, so keep track of what you try and what you learn.",
        ),
        closing(
            "See you there",
            PRESENTER,
            "That's Track 3. Scan the form if you want a workspace account, and come and find us "
            "in the Track 3 room after morning tea.",
            [
                (FORM_URL, "Databricks access"),
                ("https://github.com/aehrc/open-fhir-training", "Exercises"),
            ],
        ),
    ],
}
