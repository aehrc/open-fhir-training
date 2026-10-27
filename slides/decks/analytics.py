"""The Track 3 analytics content in one deck, one PowerPoint section per part.

The parts are in decks/parts/, in the order they are presented. There is no
fixed time for each: the room works through them at its own pace.

Author: John Grimes
"""

from kit import closing, title_slide

from decks._shared import EVENT, LINKS, PRESENTER
from decks.parts import bulk, closing_the_loop, legacy, septic_shock, sql_on_fhir

DECK = {
    "file": "track-3-analytics",
    "slides": [
        title_slide(
            "FHIR for Data track",
            f"Tools and techniques for transforming and analysing FHIR data · {EVENT}",
            "These are the slides for the analytics strand of Track 3. There are five sections: "
            "FHIR amid legacy and proprietary systems; getting data out with Bulk Data and "
            "Pathling; SQL on FHIR views and terminology; a real-world study of beta-blockers in "
            "septic shock; and closing the loop with CQL, CDS Hooks, SMART and OMOP. Each section "
            "opens with some context and a demo, followed by hands-on time with its exercise. We "
            "take them at the pace of the room rather than to a timetable.",
        ),
        *legacy.SLIDES,
        *bulk.SLIDES,
        *sql_on_fhir.SLIDES,
        *septic_shock.SLIDES,
        *closing_the_loop.SLIDES,
        closing(
            "Thank you",
            PRESENTER,
            "Thank you. Everything we've used in the track is open, so you can keep going after "
            "the connectathon. The links are here: workspace access, the exercises repository, "
            "SQL on FHIR and Pathling. Workspace accounts are removed by 30 November. If you have "
            "questions later, use the connectathon Zulip chat or email fhir-training@csiro.au.",
            LINKS,
        ),
    ],
}
