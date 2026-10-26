# Open FHIR Training

A comprehensive training repository for learning FHIR data processing and
analysis using SQL on FHIR techniques in Databricks. This repository is part of
the Open FHIR Training environment used by CSIRO for education and training
purposes, demonstrating practical applications of
the [Pathling](https://pathling.csiro.au/) library for healthcare data
analytics.

## Overview

This repository provides hands-on examples of working with FHIR (Fast Healthcare
Interoperability Resources) data, from basic transformation to advanced clinical
research analytics. It includes:

- **Educational notebooks** for learning FHIR data processing
- **Real-world clinical studies** demonstrating advanced analytics
- **SQL on FHIR implementations** using industry-standard techniques
- **Complete analysis pipelines** from data import to final results

## Repository Structure

```
open-fhir-training/
├── notebooks/                    # Databricks/Jupyter notebooks
│   ├── csv_to_fhir/              # Basic FHIR transformation tutorial
│   │   └── transform_csv_to_fhir.py
│   ├── synthea/                  # Synthea AU synthetic patient data
│   │   ├── import_synthea.py     # Data import from S3
│   │   ├── create_prostate_cancer_views.py
│   │   └── create_mi_secondary_prevention_views.py
│   ├── terminology/              # Local terminology store
│   │   └── import_amt_classification.py
│   └── mimic_iv/                 # MIMIC-IV clinical database
│       ├── import_mimic_iv_demo.py
│       └── create_spo2_views.py
├── sql/                          # Spark SQL analysis scripts
│   ├── synthea/                  # Synthea AU studies
│   │   ├── combine_prostate_cancer_views.sql
│   │   └── combine_mi_secondary_prevention_views.sql
│   └── mimic_iv/                 # Pulse oximetry bias study
│       ├── st_subject.sql        # Study subject definition
│       ├── st_ventilation.sql    # Ventilation categorisation
│       ├── st_reading_*.sql      # Clinical measurements
│       └── coh_*.sql            # Final cohort definitions
```

## Getting Started

### Prerequisites

- Access to a Databricks workspace with the Pathling library installed
  (version 10.0.0 or later for the secondary prevention study, which uses
  Terminology in SQL)
- Access to the training datasets (Synthea and MIMIC-IV demo)

### Setting Up in Databricks

1. **Connect this repository to Databricks:**
    - In your Databricks workspace, go to **Repos** in the sidebar
    - Click **Add Repo** and enter the Git URL for this repository
    - Select **Clone remote Git repo** to import all notebooks and SQL files

2. **Install Pathling:**
   Follow
   the [Pathling Databricks installation guide](https://pathling.csiro.au/docs/libraries/installation/databricks)
   to:
    - Install the Pathling library on your cluster
    - Configure cluster settings for optimal FHIR data processing
    - Verify installation by running the provided test commands

### Recommended Learning Path

1. **Start with CSV to FHIR** - Learn basic FHIR concepts
2. **Import training datasets** - Understand FHIR data structures
3. **Explore analytical views** - See SQL on FHIR in action
4. **Run clinical studies** - Apply concepts to real research questions

## Datasets and Examples

### Synthea AU synthetic patient data

[Synthea](https://synthetichealth.github.io/synthea/) generates realistic
synthetic patient data in FHIR format. Our examples use an Australian dataset
of 800 Queensland patients, generated with
[synthea-au-core](https://github.com/aehrc/synthea-au-core) and conforming to
[AU Core](https://build.fhir.org/ig/hl7au/au-fhir-core/) profiles, with:

- Patient demographics, including Australian addresses and identifiers
- Medical encounters
- Observations and vital signs
- Conditions and diagnoses
- Medications and procedures

**Key files:**

- `notebooks/synthea/import_synthea.py` - Import data from S3 to Delta tables
- `notebooks/synthea/create_prostate_cancer_views.py` - Create analytical views
- `sql/synthea/combine_prostate_cancer_views.sql` - Final analysis query
- `notebooks/terminology/import_amt_classification.py` - Import an AMT
  medicine classification ConceptMap into a local terminology store
- `notebooks/synthea/create_mi_secondary_prevention_views.py` - Create views,
  classify medicines with the ConceptMap and chart the results
- `sql/synthea/combine_mi_secondary_prevention_views.sql` - Patient-level view
  and summary query

### MIMIC-IV Clinical Database

[MIMIC-IV](https://mimic.mit.edu/) is a real-world critical care database. The
demo version contains de-identified data from:

- ICU patient encounters
- Vital signs monitoring
- Laboratory results
- Medication administration
- Respiratory support devices

**Key files:**

- `notebooks/mimic_iv/import_mimic_iv_demo.py` - Import data from S3
- `notebooks/mimic_iv/create_spo2_views.py` - Create analytical views
- `sql/mimic_iv/*.sql` - Complete pulse oximetry bias study

### CSV to FHIR Transformation

Learn the basics of FHIR with a step-by-step tutorial that transforms CSV data
into proper FHIR resources:

- **Patient resources** - Demographics and identifiers
- **Encounter resources** - Healthcare visits and encounters
- **Immunisation resources** - Vaccination records

The notebook reads the `synthea_csv.patients`, `synthea_csv.encounters` and
`synthea_csv.immunizations` tables. No notebook in this repository creates
them; they are pre-loaded into the training workspace from Synthea CSV output.

## Clinical Studies

### 1. Prostate Cancer Risk Factors Analysis (Synthea AU)

This study demonstrates extraction of cancer risk factor data using SQL on FHIR:

**Objective:** Identify patients with prostate cancer and analyse associated
risk factors including:

- Hyperlipidaemia (cholesterol > 240 mg/dL)
- High BMI (> 30 kg/m²)
- Patient demographics

**Implementation:**

- Creates 4 individual views for different data types
- Combines views using temporal logic (risk factors before diagnosis)
- Produces a final analytical dataset for statistical analysis

### 2. Secondary Prevention After Myocardial Infarction (Synthea AU)

This study measures whether patients were prescribed guideline-recommended
medicines after a myocardial infarction, following
[Halvorsen et al. 2016](https://pubmed.ncbi.nlm.nih.gov/27246583/).

**Objective:** For each patient with a myocardial infarction, indexed on their
first, determine whether they were prescribed each of four drug classes within
a follow-up window (365 days by default):

- Antiplatelet
- Statin
- Beta-blocker
- ACE inhibitor or angiotensin receptor blocker

**Implementation:**

- Creates views of patients, myocardial infarction diagnoses and medication
  requests, with no drug class logic in the views
- Classifies the AMT-coded medicines in SQL by joining to an AMT
  product-to-classification ConceptMap, presented as a table through
  [Terminology in SQL](https://build.fhir.org/ig/HL7/sql-on-fhir/en/terminology-in-sql.html)
  and read from a Pathling local terminology store
- Produces a patient-level view of the days to the first prescription of each
  class, and a summary query that takes the follow-up window as a parameter
- Charts the cohort, the treatment rates against the published figures, time to
  treatment, combinations of classes and treatment by age

The ConceptMap source is
`s3://open-fhir-training-data/terminology/amt/product-to-classification.json`,
and `notebooks/terminology/import_amt_classification.py` imports it into the
store at `s3://open-fhir-training-data/terminology/tx-store`. The store only
needs to be built once.

### 3. Pulse Oximetry Bias Study (MIMIC-IV)

A comprehensive study examining potential bias in pulse oximetry readings across
different patient populations:

**Objective:** Compare pulse oximetry (SpO₂) readings with arterial blood gas
measurements (SaO₂) to identify potential measurement disparities.

**Study Design:**

- **Subject selection:** ICU patients with ventilation beyond supplemental
  oxygen
- **Index period:** Up to 5 days from first ventilation intervention
- **Measurements:** SpO₂ from monitors, SaO₂ from blood gas, oxygen flow rates
- **Covariates:** Patient demographics, ventilation status, oxygen delivery

**Implementation files:**

- `st_*.sql` - Study view definitions (subjects, readings, ventilation)
- `coh_*.sql` - Final cohort with complete measurement sets

## Usage Instructions in Databricks

### Using a Shared Training Workspace

In a shared training workspace, the datasets and views are already built, so
you do not need to run the import or view creation steps.

- Run the notebooks in place to explore the data and the queries
- To change a notebook, clone it to your home folder first
- Write any tables or views to a personal schema (for example,
  `CREATE SCHEMA IF NOT EXISTS <your_name>`), not to the shared schemas
- Do not upload sensitive or identifiable data

### Running the Notebooks

1. **Navigate to the imported repository:**
    - In Databricks, go to **Repos** and select your cloned repository
    - Browse to the `notebooks/` directory

2. **Start with data import:**
    - Open `notebooks/csv_to_fhir/transform_csv_to_fhir.py` for basic FHIR
      concepts
    - Run `notebooks/synthea/import_synthea.py` to import Synthea data
    - Run `notebooks/mimic_iv/import_mimic_iv_demo.py` to import MIMIC-IV data
    - Run `notebooks/terminology/import_amt_classification.py` to build the
      local terminology store used by the secondary prevention study

3. **Create analytical views:**
    - Run `notebooks/synthea/create_prostate_cancer_views.py` for cancer study
      views
    - Run `notebooks/synthea/create_mi_secondary_prevention_views.py` for the
      secondary prevention study; it also runs
      `sql/synthea/combine_mi_secondary_prevention_views.sql` and charts the
      results
    - Run `notebooks/mimic_iv/create_spo2_views.py` for pulse oximetry study
      views

### Running SQL Scripts

1. **Using Databricks SQL Editor:**
    - Go to **SQL** in the Databricks sidebar
    - Create a new query and copy the contents of the SQL files
    - Execute queries in the following order for the pulse oximetry study:
        - `sql/mimic_iv/st_ventilation.sql`
        - `sql/mimic_iv/st_subject.sql`
        - `sql/mimic_iv/st_reading_*.sql`
        - `sql/mimic_iv/coh_*.sql`

2. **Using notebooks with SQL cells:**
    - Create a new notebook and use `%sql` magic commands
    - Copy and execute the SQL script contents in SQL cells
    - This allows mixing SQL queries with Python analysis code

3. **Opening the files directly:**
    - `%run` only runs notebooks, so it cannot execute a `.sql` file
    - In a Databricks Git folder, open a file such as
      `sql/synthea/combine_prostate_cancer_views.sql` from the workspace browser
      to view and run it in the SQL editor, or paste its contents into a `%sql`
      notebook cell

## Key Concepts

### SQL on FHIR

[SQL on FHIR](https://sql-on-fhir.org/) is a standard for expressing clinical
data queries using SQL syntax over FHIR data. Benefits include:

- **Familiar syntax** for analysts and researchers
- **Reusable view definitions** that can be shared across studies
- **Database-agnostic** queries that work across different platforms
- **Clinical concept abstraction** hiding FHIR implementation details

### Pathling Library

[Pathling](https://pathling.csiro.au/) is an open-source implementation of SQL
on FHIR that provides:

- **FHIR data encoding** into Apache Spark DataFrames
- **FHIRPath expression** evaluation for complex data extraction
- **View runner** for executing SQL on FHIR view definitions
- **Performance optimisation** for large-scale healthcare analytics

### Terminology in SQL

[Terminology in SQL](https://build.fhir.org/ig/HL7/sql-on-fhir/en/terminology-in-sql.html)
is the part of the SQL on FHIR specification that presents value sets and
concept maps to SQL as tables with fixed columns. A query classifies or
translates codes by joining to the table, so the SQL does not need to contain
lists of codes. Pathling's `value_set` and `concept_map` methods return these
tables as Spark DataFrames.

### View-Based Analytics

The examples demonstrate a layered approach to healthcare analytics:

1. **Raw FHIR resources** - Individual clinical records (Patient, Observation,
   etc.)
2. **Base views** - Clean, standardised extracts (demographics, vital signs)
3. **Study views** - Research-specific transformations (subjects, measurements)
4. **Cohort views** - Final analytical datasets for statistical analysis

## Contributing

Contributions are welcome! Please consider:

- Adding new clinical study examples
- Improving documentation and tutorials
- Expanding SQL on FHIR view libraries
- Optimising query performance

## Related Resources

- [Pathling Documentation](https://pathling.csiro.au/docs)
- [Pathling Databricks Installation Guide](https://pathling.csiro.au/docs/libraries/installation/databricks)
- [SQL on FHIR Specification](https://sql-on-fhir.org/)
- [FHIR R4 Specification](https://hl7.org/fhir/R4/)
- [Databricks Documentation](https://docs.databricks.com/)
- [Synthea Documentation](https://synthetichealth.github.io/synthea/)
- [MIMIC-IV Documentation](https://mimic.mit.edu/docs/iv/)

## License

Copyright © 2025, Commonwealth Scientific and Industrial Research Organisation (CSIRO) ABN 41 687 119 230. Licensed under the [Apache License, version 2.0](LICENSE).
