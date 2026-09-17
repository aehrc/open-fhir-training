# Databricks notebook source
# MAGIC %md
# MAGIC # Create prostate cancer views from Synthea AU data
# MAGIC
# MAGIC This notebook provides a demonstration of the [SQL on FHIR](https://sql-on-fhir.org/) view runner implementation currently in development within [Pathling](https://pathling.csiro.au/docs).
# MAGIC
# MAGIC The user provides a [view definition](https://build.fhir.org/ig/FHIR/sql-on-fhir-v2/StructureDefinition-ViewDefinition.html) and a data source, and the result will be returned as a Spark data frame.
# MAGIC
# MAGIC At this point the user has the option of:
# MAGIC
# MAGIC - Composing the result with other Spark operations
# MAGIC - Converting the result to a Pandas data frame
# MAGIC - Writing the result to a table or a file

# COMMAND ----------

from pathling import PathlingContext
from pyspark.sql.functions import to_date, to_timestamp, round, min, nth_value
from pyspark.sql.window import Window

# COMMAND ----------

# MAGIC %md
# MAGIC As a first step, we will initialise the Pathling context.
# MAGIC
# MAGIC You can call this with no arguments and it will either create a new Spark session with some sensible defaults, or pick up an existing Spark session.

# COMMAND ----------

pc = PathlingContext.create()
pc.spark.sql("CREATE SCHEMA IF NOT EXISTS synthea")
pc.spark.sql("CREATE SCHEMA IF NOT EXISTS synthea_prostate_cancer_views")
pc.spark.catalog.setCurrentDatabase("synthea")

# COMMAND ----------

# MAGIC %md
# MAGIC # Read data from tables
# MAGIC
# MAGIC Now we will read some data from a set of previously persisted Delta tables. The data we are using here is an Australian [Synthea](https://synthetichealth.github.io/synthea/) dataset containing approximately 8,000 patients from Queensland, generated with [synthea-au-core](https://github.com/aehrc/synthea-au-core) and conforming to [AU Core](https://build.fhir.org/ig/hl7au/au-fhir-core/) profiles. It was imported by the `import_synthea` notebook.
# MAGIC
# MAGIC The object returned is a "data source", which contains each of the data frames that have been encoded, as well as methods to run queries over them.

# COMMAND ----------

data = pc.read.tables()

# COMMAND ----------

# MAGIC %md
# MAGIC Here are the resources that are contained within our new data source:

# COMMAND ----------

data.resource_types()

# COMMAND ----------

# MAGIC %md
# MAGIC Here are the row counts for some of the resources:

# COMMAND ----------

data.read('Patient').count()

# COMMAND ----------

data.read('Observation').count()

# COMMAND ----------

data.read('Condition').count()

# COMMAND ----------

# MAGIC %md
# MAGIC # Prostate cancer risk factors
# MAGIC
# MAGIC To demonstrate the SQL on FHIR query functionality, we will describe a simple scenario that involves the extraction of data to support an analysis of prostate cancer risk factors.
# MAGIC
# MAGIC We will extract some patient demographic data along with some candidate risk factors:
# MAGIC
# MAGIC - Hyperlipidemia (recorded total cholesterol > 240 mg/dL)
# MAGIC - High BMI (recorded BMI > 30 kg/m2)
# MAGIC
# MAGIC Our target view will be a table containing one row per patient, with the following columns:
# MAGIC
# MAGIC - Patient ID
# MAGIC - Birth date
# MAGIC - Postal code
# MAGIC - Deceased status
# MAGIC - Prostate cancer onset
# MAGIC - High BMI observed date
# MAGIC - Hyperlipidemia observed date
# MAGIC - Total cholesterol (mg/dL)
# MAGIC
# MAGIC In order to construct this view, we will create four different views, and then compose them together using regular Spark SQL:
# MAGIC
# MAGIC - Patient demographics
# MAGIC - Hyperlipidemia observations
# MAGIC - High BMI observations
# MAGIC - Prostate cancer diagnoses

# COMMAND ----------

# MAGIC %md
# MAGIC ## Patient demographic view
# MAGIC
# MAGIC This view will provide the following data elements:
# MAGIC
# MAGIC - Patient ID
# MAGIC - Birth date
# MAGIC - Postal code
# MAGIC - Deceased status
# MAGIC
# MAGIC Patient ID will be extracted using the `getResourceKey()` function. This returns an identifier that can be used along with the `getReferenceKey()` function to join the related rows from different views together.
# MAGIC
# MAGIC Birth date and deceased time are pretty straightforward, and are singular so do not require any kind of unnesting.
# MAGIC
# MAGIC Postal code returns multiple values, as a patient can have more than one address. In this example we have chosen to keep this as an array, by setting the `collection` element to `true`.

# COMMAND ----------

patients = data.view(
    "Patient",
    select=[
        {
            "column": [
                {
                    "description": "Patient ID",
                    "path": "getResourceKey()",
                    "name": "id",
                },
                {
                    "description": "Birth date",
                    "path": "birthDate",
                    "name": "birth_date",
                },
                {
                    "description": "Postal code",
                    "path": "address.postalCode",
                    "name": "postal_code",
                    "collection": True
                },
                {
                    "description": "Deceased time",
                    "path": "deceased.ofType(dateTime)",
                    "name": "deceased",
                },
            ]
        },
    ],
)

# COMMAND ----------

patients.explain()

# COMMAND ----------

patients.show(10, truncate=False)

# COMMAND ----------

patients.write.saveAsTable("synthea_prostate_cancer_views.patient_demographics_view", mode="overwrite")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Hyperlipidemia view
# MAGIC
# MAGIC This view will provide the following data elements:
# MAGIC
# MAGIC - Observation ID
# MAGIC - Patient ID
# MAGIC - Observation date
# MAGIC - Observation code
# MAGIC - Total cholesterol unit
# MAGIC - Total cholesterol value
# MAGIC
# MAGIC The view will be filtered to only total cholesterol observations that exceed 240 mg/dL.

# COMMAND ----------

cholesterol = data.view(
    "Observation",
    select=[
        {
            "column": [
                {
                    "description": "Observation ID",
                    "path": "getResourceKey()",
                    "name": "id",
                },
                {
                    "description": "Patient ID",
                    "path": "subject.getReferenceKey()",
                    "name": "patient_id",
                },
                {
                    "description": "Observation date",
                    "path": "effective.ofType(dateTime)",
                    "name": "date",
                },
            ],
            "select": [
                {
                    "forEach": "code.coding",
                    "column": [
                        {
                            "description": "Observation code",
                            "path": "code",
                            "name": "code",
                        },
                    ],
                },
                {
                    "forEach": "value.ofType(Quantity)",
                    "column": [
                        {
                            "description": "Total cholesterol unit",
                            "path": "unit",
                            "name": "unit",
                        },
                        {
                            "description": "Total cholesterol value",
                            "path": "value",
                            "name": "value",
                        },
                    ],
                },
            ],
        }
    ],
    where=[
        {
            "description": "Total cholesterol > 240 mg/dL",
            "path": "where(code.coding.exists(system = 'http://loinc.org'"
                    "and code = '2093-3'))"
                    ".value.ofType(Quantity).where(code = 'mg/dL')"
                    ".value > 240",
        }
    ],
)

# COMMAND ----------

cholesterol.explain()

# COMMAND ----------

cholesterol.show(10, truncate=False)

# COMMAND ----------

cholesterol.write.saveAsTable("synthea_prostate_cancer_views.hyperlipidemia_view", mode="overwrite")

# COMMAND ----------

# MAGIC %md
# MAGIC ## BMI view
# MAGIC
# MAGIC This view will provide the following data elements:
# MAGIC
# MAGIC - Observation ID
# MAGIC - Patient ID
# MAGIC - Observation date
# MAGIC - Observation code
# MAGIC - BMI unit
# MAGIC - BMI value
# MAGIC
# MAGIC The view will be filtered to only BMI observations that exceed 30 kg/m2.
# MAGIC
# MAGIC One of the nice things about the Pathling implementation is that the encoding process includes canonicalisation of UCUM units. This means that the comparison of total cholesterol values in this query will also pick up observations that were made with different but comparable units, such as mg/dL.

# COMMAND ----------

bmi = data.view(
    "Observation",
    select=[
        {
            "column": [
                {
                    "description": "Observation ID",
                    "path": "getResourceKey()",
                    "name": "id",
                },
                {
                    "description": "Patient ID",
                    "path": "subject.getReferenceKey()",
                    "name": "patient_id",
                },
                {
                    "description": "Observation date",
                    "path": "effective.ofType(dateTime)",
                    "name": "date",
                },
            ],
            "select": [
                {
                    "forEach": "code.coding",
                    "column": [
                        {
                            "description": "Observation code",
                            "path": "code",
                            "name": "code",
                        },
                    ],
                },
                {
                    "forEach": "value.ofType(Quantity)",
                    "column": [
                        {
                            "description": "BMI unit",
                            "path": "unit",
                            "name": "unit",
                        },
                        {
                            "description": "BMI value",
                            "path": "value",
                            "name": "value",
                        },
                    ],
                },
            ],
        }
    ],
    where=[
        {
            "description": "BMI > 30 kg/m2",
            "path": "where(code.coding.exists(system = 'http://loinc.org'"
                    "and code = '39156-5'))"
                    ".value.ofType(Quantity).where(code = 'kg/m2')"
                    ".value > 30",
        }
    ],
)

# COMMAND ----------

bmi.explain()

# COMMAND ----------

bmi.show(10, truncate=False)

# COMMAND ----------

bmi.write.saveAsTable("synthea_prostate_cancer_views.bmi_view", mode="overwrite")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prostate cancer diagnosis view
# MAGIC
# MAGIC This view will provide the following data elements:
# MAGIC
# MAGIC - Condition ID
# MAGIC - Patient ID
# MAGIC - Condition onset date
# MAGIC - Condition code
# MAGIC
# MAGIC The view will be filtered to only prostate cancer diagnoses.

# COMMAND ----------

prostate_cancer_diagnoses = data.view(
    "Condition",
    select=[
        {
            "column": [
                {
                    "description": "Condition ID",
                    "path": "getResourceKey()",
                    "name": "id",
                },
                {
                    "description": "Patient ID",
                    "path": "subject.getReferenceKey()",
                    "name": "patient_id",
                },
                {
                    "description": "SNOMED CT diagnosis code",
                    "path": "code.coding.where(system = 'http://snomed.info/sct').code",
                    "name": "sct_id",
                },
                {
                    "description": "Date of onset",
                    "path": "onsetDateTime",
                    "name": "onset",
                },
            ]
        }
    ],
    where=[
        {
            "description": "Neoplasm of prostate",
            "path": "code.coding.exists(system = 'http://snomed.info/sct'"
                    "and code = '126906006')",
        }
    ],
)

# COMMAND ----------

prostate_cancer_diagnoses.explain()

# COMMAND ----------

prostate_cancer_diagnoses.show(10, truncate=False)

# COMMAND ----------

prostate_cancer_diagnoses.write.saveAsTable("synthea_prostate_cancer_views.prostate_cancer_diagnosis_view", mode="overwrite")