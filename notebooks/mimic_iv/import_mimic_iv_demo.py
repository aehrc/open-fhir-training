# Databricks notebook source
# MAGIC %md
# MAGIC # Import MIMIC-IV demo data to tables
# MAGIC
# MAGIC This notebook imports Synthea data from NDJSON files, and persists it to tables within the Databricks catalog.

# COMMAND ----------

from pathling import PathlingContext
import re

# COMMAND ----------

pc = PathlingContext.create(enable_extensions=True)
pc.spark.sql("CREATE SCHEMA IF NOT EXISTS mimic_iv_demo")
pc.spark.catalog.setCurrentDatabase("mimic_iv_demo")

# COMMAND ----------

source = pc.read.ndjson(
    "s3://open-fhir-training-data/mimic-iv-clinical-database-demo-on-fhir-2.1.0/fhir", 
    file_name_mapper=lambda file_name: re.findall(r"Mimic(\w+?)(?:ED|ICU|"
                                                  r"Chartevents|Datetimeevents|Labevents|MicroOrg|MicroSusc|MicroTest|"
                                                  r"Outputevents|Lab|Mix|VitalSigns|VitalSignsED)?$",
                                                  file_name))
source.resource_types()

# COMMAND ----------

source.write.tables()