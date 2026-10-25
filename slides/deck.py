"""The slides of the Track 3 analytics deck, in order.

Each slide is a section header or a title-only slide with one figure from
slides/figures. A figure slide's builds list the figure's layers that appear
on each click; layers not listed are on the slide from the start. In the
speaker notes, [*] marks a click.

Author: John Grimes
"""


def section(title: str, subtitle: str, notes: str) -> dict:
    """Define a section header slide.

    :param title: the section title
    :param subtitle: the line beneath it
    :param notes: speaker notes
    :returns: the slide definition
    """
    return {
        "kind": "section",
        "title": title,
        "subtitle": subtitle,
        "notes": notes.strip(),
    }


def slide(
    title: str, figure: str, notes: str, builds: list[str | list[str]] = ()
) -> dict:
    """Define a title-only slide with a figure.

    :param title: the slide title
    :param figure: the figure's file stem in slides/figures
    :param notes: speaker notes
    :param builds: the layers that appear on each click, in order; a list
        brings in several layers on the same click
    :returns: the slide definition
    """
    steps = [[step] if isinstance(step, str) else list(step) for step in builds]
    return {
        "kind": "figure",
        "title": title,
        "figure": figure,
        "builds": steps,
        "notes": notes.strip(),
    }


SLIDES: list[dict] = [
    # Part 1: standards and tools.
    section(
        "Analytics with Bulk Data, SQL on FHIR and Pathling",
        "John Grimes",
        """
My name is John Grimes and I'm an engineer at the Australian e-Health Research Centre at CSIRO.

Dion has shown you how to get structured data out of clinical text, and James has shown you how terminology can enrich it. My part is about what you do once you have a lot of FHIR data and want to analyse it.
""",
    ),
    slide(
        "This session",
        "session-plan",
        """
There are two halves to this.

First, three standards and tools: Bulk Data Access for getting data out of a FHIR server, SQL on FHIR for turning it into tables, and Pathling, our open source library that does both at scale.

[*] Second, a walkthrough of the four exercises in the open-fhir-training repository, tying each one back to those concepts.

[*] Then it is over to you. There are some suggestions for things to try at the end, but bring your own problems if you have them.
""",
        builds=["exercises", "adventure"],
    ),
    slide(
        "From FHIR server to analysis",
        "pipeline",
        """
This is the whole pipeline on one slide.

FHIR servers are built for transactions: read this patient, search for that observation. That doesn't scale to a population. Bulk Data Access gives you everything in one request, as NDJSON files with one resource per line.

[*] Pathling's encoders read those files into Spark tables that keep the full FHIR structure.

[*] SQL on FHIR ViewDefinitions flatten those resources into the tables an analyst actually wants, with one row per patient, observation or diagnosis.

[*] From there it's ordinary SQL, or Python, or R.

[*] The exercises cover different parts of this. Exercise 1 builds FHIR NDJSON from CSV, exercise 2 imports NDJSON into tables, and exercises 3 and 4 go from tables to answers.
""",
        builds=["encode", "views", "sql", "exercises"],
    ),
    slide(
        "FHIR Bulk Data Access",
        "bulk-flow",
        """
Bulk Data Access is an HL7 implementation guide for exporting large amounts of data from a FHIR server.

An export can take a while, so it is asynchronous. The client kicks it off with a GET or POST to $export, asking for an asynchronous response. The server replies straight away with 202 Accepted and a status URL.

[*] The client polls that URL. While the export is running it gets another 202, usually with a progress message and a Retry-After header telling it how long to wait. When it's done, it gets a 200 and a manifest.

[*] The manifest lists the output files, and the client downloads each one. They are NDJSON: one FHIR resource per line.

[*] You can export everything on the server, the data for all patients, or the data for the patients in a Group, which is how you would export a cohort. Parameters narrow it down: _type for resource types, _since for changes after a point in time, and _typeFilter for a FHIR search per type.

A server that holds real data will be secured with SMART Backend Services: the client signs a JWT with its private key and exchanges it for an access token, with no user involved.
""",
        builds=["poll", "download", "levels"],
    ),
    slide(
        "A real export",
        "bulk-curl",
        """
This is a real export from the SMART Bulk Data reference server, a public test server with synthetic data that doesn't require authorisation.

The kick-off asks for the patients and their observations, and gets back 202 and a status URL.

[*] This server is quick, so the first poll returns 200 and the manifest. There are 100 patients and 16,315 observations, and the observations are split across two files.

[*] Each file is NDJSON. This is the first line of the patient file: one complete Patient resource per line, which makes the files easy to split and read in parallel.
""",
        builds=[["code-manifest", "key-manifest"], ["code-ndjson", "key-ndjson"]],
    ),
    slide(
        "What we have \u2192 what analysts want",
        "tree-to-table",
        """
On the left is a BMI observation from the Synthea AU data we'll use in the exercises.

FHIR is a nested format. The code is a coding inside a CodeableConcept, the patient is a reference, and the value is one of several types the element can take. Elements like coding can repeat.

Most analysts don't want to deal with that. They want a flat table, with just the columns they need, that they can use in SQL, R or Python.

[*] SQL on FHIR defines that step. A ViewDefinition describes how to turn resources of one type into rows and columns. Here it produces one row per BMI observation over 30, and the highlighted row is the resource on the left.
""",
        builds=["table"],
    ),
    slide(
        "A ViewDefinition",
        "view-definition",
        """
This is the ViewDefinition behind that table, taken from the prostate cancer exercise. It has a handful of parts.

[*] It applies to a single resource type, in this case Observation.

[*] Columns are FHIRPath expressions. FHIRPath is the same path language that FHIR uses for invariants and search parameters. The ID and patient columns use two special functions that I'll come back to.

[*] Where an element repeats, forEach unnests it, so you get one row per item. There are a few variations: forEachOrNull keeps resources with no items, repeat walks recursive structures such as questionnaire items, and unionAll stacks selections into a common set of columns.

[*] Finally, where filters the resources. Here it keeps BMI observations with a value over 30.

That is most of the specification.
""",
        builds=[
            ["band-resource", "key-resource"],
            ["band-column", "key-column"],
            ["band-foreach", "key-foreach"],
            ["band-where", "key-where"],
        ],
    ),
    slide(
        "FHIRPath in the exercises",
        "fhirpath",
        """
You don't need much FHIRPath to write useful views. These are the expressions that do the work in the exercises.

The two key functions give you join keys. ofType picks one type from a choice element, such as effective or value. exists with a system and code is the usual way to test for a code. And extension reads values out of extensions, which the MIMIC-IV data uses for race and ethnicity.

By default a column must have a single value. If a path can return several, such as a patient's postal codes, you can either unnest it with forEach or keep it as an array with collection set to true.
""",
    ),
    slide(
        "Views don't join, they emit keys",
        "emit-keys",
        """
A view only ever covers one resource type, and views never join to each other. SQL already does joins well.

Instead, there are two functions that produce join keys. getResourceKey returns a key for the resource itself, and getReferenceKey returns the key of the resource a reference points to. The view runner guarantees that they match, whatever form the references take.

[*] So the BMI observation points to its patient through matching keys.

[*] And joining the two views is a plain SQL join, in whatever engine you are using.
""",
        builds=["arrow", "sql"],
    ),
    slide(
        "SQL on FHIR, then and next",
        "spec-timeline",
        """
SQL on FHIR version 2 defined the ViewDefinition, and that is what the exercises use.

[*] The 3.0.0 ballot, which HL7 is balloting as STU 3, adds two things. SQLView and SQLQuery let you share the SQL that sits on top of views as FHIR Library resources. And two operations, $sql-run and $sql-export, run views and queries on a server and return the results in formats such as CSV, NDJSON or Parquet.

[*] There are several independent implementations, which is the point: a view written for one runner should work on another.
""",
        builds=["v3", "runners"],
    ),
    slide(
        "Pathling",
        "pathling",
        """
Pathling is our open source implementation of these standards. It is built on Apache Spark, so the same code runs on a laptop, on Databricks, or on a cluster.

The library encodes FHIR resources into Spark data frames that keep the full structure. It reads and writes NDJSON, bundles, Parquet, Delta and catalog tables, and it has a bulk export client. It runs SQL on FHIR views, evaluates FHIRPath, and has terminology functions for value set membership, subsumption, translation and display terms, which connect to what James showed you.

[*] You can use it from Python, R, Java or Scala, and there is a command line tool.

[*] There is also a server, packaged as a Docker image, that implements bulk export and import and the SQL on FHIR operations.
""",
        builds=["interfaces", "server"],
    ),
    slide(
        "Pathling in a few lines",
        "pathling-code",
        """
This is what using it from Python looks like.

[*] Creating a Pathling context starts Spark, or picks up the Spark session that Databricks gives you.

[*] Then you read some data. Here it is a bulk export from the reference server that I just showed you: Pathling does the kick-off, polling and downloads itself, and you get back the same kind of data source you would get from reading NDJSON files or tables.

[*] You run a ViewDefinition over the data source, and get a Spark data frame.

[*] From there it is ordinary Spark. You can save it as a table, query it with Spark SQL or convert it to pandas.

I ran this code against the reference server with Pathling 10. It exported 100 patients and 16,315 observations, and the view returned 916 BMI rows.
""",
        builds=[
            ["band-create", "key-create"],
            ["band-read", "key-read"],
            ["band-view", "key-view"],
            ["band-write", "key-write"],
        ],
    ),
    # Part 2: the exercises.
    section(
        "Walkthrough: the exercises",
        "github.com/aehrc/open-fhir-training",
        """
Now to the exercises. They are in the open-fhir-training repository on GitHub, as Databricks notebooks and SQL files.
""",
    ),
    slide(
        "The exercises",
        "exercises-map",
        """
There are four exercises, and each one uses a different part of the pipeline.

The first builds FHIR resources from CSV. The second imports two FHIR datasets into tables. The third and fourth are clinical studies written as ViewDefinitions plus SQL.

There are two datasets. Synthea AU is about 8,000 synthetic Queensland patients, generated with our Australian adaptation of Synthea and shaped to AU Core. MIMIC-IV demo on FHIR is a 100-patient, de-identified sample of real intensive care records from a hospital in Boston.
""",
    ),
    slide(
        "1 \u00b7 CSV to FHIR",
        "csv-to-fhir",
        """
The first exercise takes Synthea's CSV output and builds FHIR resources from it, which is the problem you have whenever your source data isn't FHIR.

[*] It uses plain Spark functions. col and alias move a value into a FHIR element, lit sets fixed values such as the resource type, when maps codes such as M and F to FHIR's male and female, and struct and array build the nesting.

[*] Each row becomes a Patient resource, written out as NDJSON, the same format a bulk export produces.

[*] The notebook does the same for encounters and immunisations, checks that every reference points to a resource that exists, and then uses Pathling's encoders to load the result into Delta tables.
""",
        builds=["code", "json", "steps"],
    ),
    slide(
        "2 \u00b7 Importing the datasets",
        "import-code",
        """
The second exercise imports the two datasets, and it is short.

[*] The Synthea AU files are named the way a bulk export names them, such as Patient.00000.ndjson, so Pathling recognises the resource types without help. The same code would read the output of an export.

[*] The MIMIC-IV files have their own names, so a file name mapper turns names like MimicObservationChartevents into Observation.

[*] Extensions are left out of the encoding by default. The MIMIC-IV import turns them on, because a later view reads race and ethnicity from US Core extensions.

[*] write.tables saves one Delta table per resource type, and the rest of the exercises read from those.
""",
        builds=["key-read", "key-mapper", "key-extensions", "key-write"],
    ),
    slide(
        "3 \u00b7 Prostate cancer risk factors",
        "prostate-design",
        """
The third exercise extracts candidate risk factors for prostate cancer from the Synthea AU data.

It defines four ViewDefinitions: patient demographics, high cholesterol observations, high BMI observations, and prostate cancer diagnoses. Each one is a single resource type with a filter on a LOINC or SNOMED CT code.

[*] A Spark SQL view combines them.

[*] The result has one row per patient, with the latest high BMI and high cholesterol readings before any diagnosis. I ran it over an 800-patient sample from the same generator: 6 patients had prostate cancer.
""",
        builds=["sql", "output"],
    ),
    slide(
        "3 \u00b7 Risk factors before the diagnosis",
        "prostate-sql",
        """
This is the SQL that combines the views, abridged. The BMI half is the same as the cholesterol half.

[*] The views are joined on the keys they emit, with no FHIR knowledge needed in the SQL.

[*] The time logic lives here, not in the views: only observations before the diagnosis count, or all of them if there is no diagnosis.

[*] A window function keeps the latest observation per patient.

[*] And left joins keep every patient, with or without risk factors, which is what you need for a comparison.

This split is the pattern to take away: views do the flattening, and SQL does the study logic.
""",
        builds=["key-join", "key-before", "key-latest", "key-everyone"],
    ),
    slide(
        "4 \u00b7 Pulse oximetry bias (MIMIC-IV)",
        "spo2-layers",
        """
The fourth exercise is a real study design, converted from an existing MIMIC-IV analysis to run over FHIR. It asks whether pulse oximeters read differently from arterial blood gas measurements across patient groups.

[*] It starts with six raw views, each over one resource type: patients, ICU stays, vital signs, oxygen flow, oxygen delivery devices and blood gases.

[*] Study views in SQL classify ventilation, define each subject's index period, and pick the readings in that period.

[*] Cohort views keep the subjects who have all three kinds of reading.

The rv, st and coh prefixes make the layers easy to follow, and each layer only reads from the one before.
""",
        builds=["raw", "study", "cohort"],
    ),
    slide(
        "4 \u00b7 Local codes and SQL types",
        "vitalsigns-view",
        """
This is the vital signs view. Two things are different from the Synthea views.

[*] The keys: as well as the patient, it takes a key from the encounter reference, which becomes the ICU stay identifier the SQL joins on.

[*] The types: the ansi/type tag asks the runner for a SQL type, so the times are timestamps and the item IDs are integers, which the time-window SQL needs.

[*] And the codes: MIMIC-IV uses its own local item IDs rather than LOINC, so the filter lists them. This is where terminology would help, if those codes were mapped to a standard.
""",
        builds=["key-keys", "key-types", "key-where"],
    ),
    slide(
        "4 \u00b7 The index period",
        "index-period",
        """
This is the core of the study design.

Each ICU stay has an index period that starts at admission and ends at the earliest of three things: the first ventilation beyond supplemental oxygen, discharge, or five days. Periods shorter than 12 hours are dropped.

[*] Within that period, the study collects pulse oximeter readings from the vital signs, arterial oxygen saturation from blood gases, and nasal cannula oxygen flow of up to 6 litres a minute.

[*] In SQL, the end of the period is one expression. The cohort is then the subjects with all three kinds of reading.
""",
        builds=["readings", "sql"],
    ),
    slide(
        "Your turn: pick your own adventure",
        "adventures",
        """
Here are some suggestions for the rest of the track. Pick whichever is closest to your own work, or bring a problem of your own.

You can export data with Bulk Data and write views over it. You can extend the prostate cancer study with another risk factor. You can replace the hard-coded codes in the views with terminology, using what James showed you. You can bring your own CSV and take it through the same steps as exercise 1. Or you can run all of this without Databricks.

James, Dion, Duncan and I will be around to help.
""",
    ),
    slide(
        "Getting started",
        "setup",
        """
To run the exercises in Databricks, add the repository, install Pathling on your cluster using the guide on the Pathling website, and run the notebooks in order: imports first, then the views, then the SQL.

On a laptop, Pathling installs from PyPI and needs Java 21. The views and SQL run unchanged, because it is the same Spark underneath.
""",
    ),
    slide(
        "In summary",
        "summary",
        """
To summarise.

Bulk Data Access gets population data out of a FHIR server, as NDJSON files.

SQL on FHIR ViewDefinitions flatten those resources into tables, one resource type at a time, with keys for joining.

And from there it is SQL, Python or R, with Pathling doing the heavy lifting on Spark.

The links are the SQL on FHIR site, Pathling, and the exercises.
""",
    ),
]
