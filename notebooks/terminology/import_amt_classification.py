# Databricks notebook source
# MAGIC %md
# MAGIC # Import an AMT medicine classification map into a local terminology store
# MAGIC
# MAGIC This notebook imports a FHIR [ConceptMap](https://hl7.org/fhir/R4/conceptmap.html) that relates [Australian Medicines Terminology](https://www.healthterminologies.gov.au/) (AMT) products to the SNOMED CT substance classes they belong to, e.g. `Atenolol 100 mg tablet` to `373254001 |Beta blocker|`. The map is `https://example.org/amt-extended-91b6e2c4/ConceptMap/product-to-classification` version `0.1.0`, an experimental map with 925,540 mappings, all with the equivalence `relatedto`.
# MAGIC
# MAGIC The map is written to a Pathling [local terminology store](https://pathling.csiro.au/docs/libraries/terminology/local): a set of Delta tables that Pathling reads instead of calling a terminology server. Notebooks that use the map create their Pathling context in local terminology mode, pointing at the store.
# MAGIC
# MAGIC The store only needs to be built once. In a shared training workspace it is already built, so you do not need to run this notebook.

# COMMAND ----------

# Author: John Grimes

from pathling import PathlingContext

TERMINOLOGY_SOURCE = (
    "s3://open-fhir-training-data/terminology/amt/product-to-classification.json"
)
TERMINOLOGY_STORE = "s3://open-fhir-training-data/terminology/tx-store"

# COMMAND ----------

pc = PathlingContext.create()

# COMMAND ----------

# MAGIC %md
# MAGIC The import streams the map from the JSON file, so the driver never holds all of its mappings in memory. Importing the same version again replaces it. The source is a single JSON file rather than a FHIR package, so there is no registry checksum to verify.

# COMMAND ----------

pc.import_fhir_terminology(TERMINOLOGY_SOURCE, TERMINOLOGY_STORE, verify_package=False)

# COMMAND ----------

# MAGIC %md
# MAGIC The store keeps a manifest of what it holds. Each row is one imported resource, with the time it was imported and any fault found in its content.

# COMMAND ----------

display(pc.spark.read.format("delta").load(f"{TERMINOLOGY_STORE}/manifest"))
