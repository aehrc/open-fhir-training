"""Day 2, 3:30 main room: the Track 3 wrap-up, then show and tell from the groups.

Author: John Grimes

To fill in the "What we achieved" slide, add one string per achievement to
ACHIEVEMENTS below (or ("text", 1) tuples for sub-points), then rebuild with
`uv run build.py d2_wrapup` from the slides directory. Leave ACHIEVEMENTS empty to
get a blank, editable bullet list that can be typed into directly in PowerPoint.
"""

from kit import bullets, closing, diagram, title_slide

from decks._shared import EVENT, LINKS, PRESENTER, show_and_tell, strands

# One string per achievement, e.g. "11 groups, 40 people in the workspace".
ACHIEVEMENTS = []


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
            "strands",
            strands(),
            "Over the two days Track 3 ran as four strands. In the analytics strand we worked "
            "through six topics: the environment and the standards map; mapping a legacy CSV extract into "
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
