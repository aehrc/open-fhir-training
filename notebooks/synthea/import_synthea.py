# Databricks notebook source
# MAGIC %md
# MAGIC # Import Synthea AU data to tables
# MAGIC
# MAGIC This notebook imports an Australian [Synthea](https://synthetichealth.github.io/synthea/) dataset from NDJSON files, and persists it to tables within the Databricks catalog.
# MAGIC
# MAGIC The dataset was generated with [synthea-au-core](https://github.com/aehrc/synthea-au-core), which localises Synthea for Australia (Queensland population, Australian addresses and identifiers) and transforms the output to conform to [AU Core](https://build.fhir.org/ig/hl7au/au-fhir-core/) profiles.
# MAGIC
# MAGIC The files are named in the FHIR bulk data style (e.g. `Patient.00000.ndjson`), which Pathling recognises by default.

# COMMAND ----------

from pathling import PathlingContext

# COMMAND ----------

pc = PathlingContext.create()
pc.spark.sql("CREATE SCHEMA IF NOT EXISTS synthea")
pc.spark.catalog.setCurrentDatabase("synthea")

# COMMAND ----------

source = pc.read.ndjson("s3://open-fhir-training-data/synthea/au/fhir")
source.resource_types()

# COMMAND ----------

source.write.tables()