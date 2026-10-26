"""Day 2, 3:30 main room: the Track 3 wrap-up, then show and tell from the groups.

Author: John Grimes

To fill in the "What we achieved" slide, add one string per achievement to
ACHIEVEMENTS below (or ("text", 1) tuples for sub-points), then rebuild with
`uv run build.py d2_wrapup` from the slides directory. Leave ACHIEVEMENTS empty to
get a blank, editable bullet list that can be typed into directly in PowerPoint.
"""

from kit import (
    BLUE,
    LAVENDER,
    MINT,
    MUTED,
    PEACH,
    TEAL,
    bullets,
    closing,
    diagram,
    rect,
    svg,
    text,
    title_slide,
)

from decks._shared import EVENT, LINKS, PRESENTER, show_and_tell

# One string per achievement, e.g. "11 groups, 40 people in the workspace".
ACHIEVEMENTS = []


def two_days():
    """The whole track over two days: six analytics blocks and three other strands."""
    b = [rect(10, 10, 450, 320, BLUE, rx=12)]
    b.append(text(30, 46, "Analytics", 20, "start", 700))
    b.append(text(440, 46, "John Grimes", 14, "end", 400, MUTED))
    blocks = [
        ("Thu", "Kick-off: environment and standards"),
        ("Thu", "FHIR amid legacy systems"),
        ("Thu", "Getting data out: Bulk Data"),
        ("Fri", "SQL on FHIR and terminology"),
        ("Fri", "Beta-blockers in septic shock"),
        ("Fri", "Closing the loop: CQL to OMOP"),
    ]
    for i, (day, topic) in enumerate(blocks):
        y = 66 + i * 43
        b.append(rect(30, y, 410, 36, "#fff", rx=8))
        b.append(text(46, y + 24, day, 15, "start", 700, TEAL))
        b.append(text(92, y + 24, topic, 15, "start"))
    others = [
        (LAVENDER, "Terminology", "James Grant", "SNOMED CT-AU, AMT, Ontoserver, ECL"),
        (
            MINT,
            "Text to structured data",
            "Dion McMurtrie",
            "Clinical notes to coded FHIR data",
        ),
        (
            PEACH,
            "Queensland Health context",
            "Duncan Pullen",
            "The Queensland Health perspective",
        ),
    ]
    for i, (fill, title, lead, item) in enumerate(others):
        y = 10 + i * 110
        b.append(rect(480, y, 450, 100, fill, rx=12))
        b.append(text(500, y + 32, title, 18, "start", 700))
        b.append(text(910, y + 32, lead, 14, "end", 400, MUTED))
        b.append(text(500, y + 70, item, 15, "start"))
    return svg(940, 340, b)


DECK = {
    "file": "track-3-day-2-wrap-up",
    "slides": [
        title_slide(
            "Track 3: wrap-up and show and tell",
            f"Show and tell · {EVENT}",
            "I'm John Grimes from CSIRO's Australian e-Health Research Centre, one of the leads "
            "for Track 3, FHIR for data: analytics and text. I'll take a couple of minutes to sum "
            "up the track, and then hand over to the groups to show what they've done.",
        ),
        diagram(
            "Two days in Track 3",
            "Four strands, one set of shared data and questions",
            "two-days",
            two_days(),
            "Over the two days Track 3 ran as four strands. In the analytics strand we had six "
            "blocks: the environment and the standards map; mapping a legacy CSV extract into "
            "FHIR; getting data out with Bulk Data and Pathling; SQL on FHIR views and "
            "terminology; a real-world study of beta-blockers in septic shock in the MIMIC-IV demo data; and "
            "closing the loop with CQL, CDS Hooks, SMART and OMOP. Alongside that, James Grant led "
            "terminology, Dion McMurtrie led the work on turning clinical text into coded FHIR "
            "data, and Duncan Pullen brought the Queensland Health perspective.",
        ),
        bullets(
            "What we achieved",
            "Track 3 over the two days",
            ACHIEVEMENTS or [""],
            "Here's a summary of what the track achieved over the two days. [Fill in on Friday "
            "afternoon: the number of people and groups, the questions they took on, and anything "
            "that worked, or didn't, that's worth carrying forward.]",
        ),
        diagram(
            "Over to the groups",
            "A few minutes per group: the question, what you did and what you found",
            "show-and-tell",
            show_and_tell(),
            "Now over to the groups. Each group has a few minutes. As a reminder, we're after the "
            "question you started with, the data you used, what you did, what you found, and what "
            "you'd do next. A dead end is a good result if you can say why. [Hand over to the "
            "first group.]",
        ),
        closing(
            "Thank you",
            PRESENTER,
            "Thank you to everyone who presented, and to James, Dion and Duncan for leading the "
            "other strands. The exercises stay public on GitHub after the event: the code on the "
            "left. The other two codes take you to the SQL on FHIR specification and to Pathling, "
            "if you want to keep going with your own data.",
            LINKS[1:],
        ),
    ],
}
