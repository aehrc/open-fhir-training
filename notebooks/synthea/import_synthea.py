# Databricks notebook source
# MAGIC %md
# MAGIC # Import Synthea data to tables
# MAGIC
# MAGIC This notebook imports Synthea data from NDJSON files, and persists it to tables within the Databricks catalog.

# COMMAND ----------

from pathling import PathlingContext

# COMMAND ----------

pc = PathlingContext.create()
pc.spark.sql("CREATE SCHEMA IF NOT EXISTS synthea")
pc.spark.catalog.setCurrentDatabase("synthea")

# COMMAND ----------

source = pc.read.ndjson("s3://open-fhir-training-data/synthea/md/fhir")
source.resource_types()

# COMMAND ----------

source.write.tables()