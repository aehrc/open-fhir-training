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
│   ├── synthea/                  # Synthea synthetic patient data
│   │   ├── import_synthea.py     # Data import from S3
│   │   └── create_prostate_cancer_views.py
│   └── mimic_iv/                 # MIMIC-IV clinical database
│       ├── import_mimic_iv_demo.py
│       └── create_spo2_views.py
├── sql/                          # Spark SQL analysis scripts
│   ├── synthea/                  # Prostate cancer risk analysis
│   │   └── combine_prostate_cancer_views.sql
│   └── mimic_iv/                 # Pulse oximetry bias study
│       ├── st_subject.sql        # Study subject definition
│       ├── st_ventilation.sql    # Ventilation categorisation
│       ├── st_reading_*.sql      # Clinical measurements
│       └── coh_*.sql            # Final cohort definitions
```

## Getting Started

### Prerequisites

- Access to a Databricks workspace with the Open FHIR Training environment
- Pathling library installed in the Databricks cluster
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

3. **Access training datasets:**
   The notebooks reference datasets pre-configured in the training environment:
    - `s3://open-fhir-training-data/synthea/md/fhir`
    -
    `s3://open-fhir-training-data/mimic-iv-clinical-database-demo-on-fhir-2.1.0/fhir`

### Recommended Learning Path

1. **Start with CSV to FHIR** - Learn basic FHIR concepts
2. **Import training datasets** - Understand FHIR data structures
3. **Explore analytical views** - See SQL on FHIR in action
4. **Run clinical studies** - Apply concepts to real research questions

## Datasets and Examples

### Synthea Synthetic Patient Data

[Synthea](https://synthetichealth.github.io/synthea/) generates realistic
synthetic patient data in FHIR format. Our examples include approximately 10,000
patients with:

- Patient demographics
- Medical encounters
- Observations and vital signs
- Conditions and diagnoses
- Medications and procedures

**Key files:**

- `notebooks/synthea/import_synthea.py` - Import data from S3 to Delta tables
- `notebooks/synthea/create_prostate_cancer_views.py` - Create analytical views
- `sql/synthea/combine_prostate_cancer_views.sql` - Final analysis query

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

## Clinical Studies

### 1. Prostate Cancer Risk Factors Analysis (Synthea)

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

### 2. Pulse Oximetry Bias Study (MIMIC-IV)

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

### Running the Notebooks

1. **Navigate to the imported repository:**
    - In Databricks, go to **Repos** and select your cloned repository
    - Browse to the `notebooks/` directory

2. **Start with data import:**
    - Open `notebooks/csv_to_fhir/transform_csv_to_fhir.py` for basic FHIR
      concepts
    - Run `notebooks/synthea/import_synthea.py` to import Synthea data
    - Run `notebooks/mimic_iv/import_mimic_iv_demo.py` to import MIMIC-IV data

3. **Create analytical views:**
    - Run `notebooks/synthea/create_prostate_cancer_views.py` for cancer study
      views
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

3. **Running directly from files:**
    - In a notebook cell, use:
      `%run ./sql/synthea/combine_prostate_cancer_views.sql`
    - This executes the SQL script in the current Spark context

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
