# Databricks notebook source
# MAGIC %md
# MAGIC # Create views from MIMIC-IV data
# MAGIC
# MAGIC This notebook implements the transformation between FHIR data in managed tables and the SQL on FHIR views 
# MAGIC defined in the MIMIC-IV example documentation.
# MAGIC
# MAGIC The notebook:
# MAGIC - Reads FHIR data from tables in the `mimic_iv_demo` schema
# MAGIC - Transforms the data using SQL on FHIR view definitions
# MAGIC - Saves the results as managed tables with the `mimic_iv_views.` prefix
# MAGIC
# MAGIC ## Overview
# MAGIC
# MAGIC We'll create 6 views that extract clinical data from MIMIC-IV:
# MAGIC 1. **rv_patient** - Patient demographics including race and ethnicity
# MAGIC 2. **rv_icu_encounter** - ICU encounter details with admission/discharge times
# MAGIC 3. **rv_obs_vitalsigns** - Vital signs measurements (heart rate, O2 saturation, respiratory rate)
# MAGIC 4. **rv_obs_o2_flow** - Oxygen flow measurements from respiratory equipment
# MAGIC 5. **rv_o2_delivery_device** - Oxygen delivery device information
# MAGIC 6. **rv_obs_bg** - Blood gas analysis results

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Import Pathling and connect
# MAGIC
# MAGIC First, we'll import the Pathling library and establish a connection to the Pathling engine.

# COMMAND ----------

from pathling import PathlingContext
pc = PathlingContext.create()
pc.spark.sql("CREATE SCHEMA IF NOT EXISTS mimic_iv_views")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Load MIMIC-IV FHIR data
# MAGIC
# MAGIC Load the MIMIC-IV FHIR data from managed tables in the `mimic_iv_demo` schema.

# COMMAND ----------

datasource = pc.read.tables("mimic_iv_demo")
datasource.resource_types()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Create Patient Demographics View (rv_patient)
# MAGIC
# MAGIC This view extracts basic patient information including demographics and race/ethnicity.
# MAGIC
# MAGIC **What this extracts**: 
# MAGIC - Each patient's unique identifier
# MAGIC - Gender
# MAGIC - Racial/ethnic background from US Core extensions
# MAGIC
# MAGIC Race and ethnicity information is stored in standardised extensions following US healthcare conventions.

# COMMAND ----------

rv_patient = datasource.view(
    resource="Patient",
    select=[
        {
            "column": [
                {
                    "name": "subject_id",
                    "path": "getResourceKey()",
                    "type": "string"
                },
                {
                    "name": "gender",
                    "path": "gender",
                    "type": "code"
                },
                {
                    "name": "race_code",
                    "path": "extension('http://hl7.org/fhir/us/core/StructureDefinition/us-core-race').extension('ombCategory').value.ofType(Coding).code",
                    "type": "code"
                },
                {
                    "name": "ethnicity_code",
                    "path": "extension('http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity').extension('ombCategory').value.ofType(Coding).code",
                    "type": "code"
                }
            ]
        }
    ]
)

rv_patient.write.saveAsTable("mimic_iv_views.rv_patient")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Create ICU Encounter View (rv_icu_encounter)
# MAGIC
# MAGIC This view captures information about patients' stays in the intensive care unit.
# MAGIC
# MAGIC **What this extracts**:
# MAGIC - Each ICU stay with unique identifier
# MAGIC - Reference to the patient
# MAGIC - Admission and discharge times
# MAGIC - Filtered to acute care encounters only
# MAGIC
# MAGIC This provides the time boundaries for each patient's ICU stay, which helps researchers identify when medical interventions occurred.

# COMMAND ----------

# Create rv_icu_encounter view.
print("Creating view: rv_icu_encounter")

rv_icu_encounter = datasource.view(
    resource="Encounter",
    select=[
        {
            "column": [
                {
                    "name": "stay_id",
                    "path": "getResourceKey()",
                    "type": "string"
                },
                {
                    "name": "subject_id",
                    "path": "subject.getReferenceKey()",
                    "type": "string"
                },
                {
                    "name": "admittime",
                    "path": "period.start",
                    "type": "dateTime",
                    "tag": [
                        {
                            "name": "ansi/type",
                            "value": "TIMESTAMP"
                        }
                    ]
                },
                {
                    "name": "dischtime",
                    "path": "period.end",
                    "type": "dateTime",
                    "tag": [
                        {
                            "name": "ansi/type",
                            "value": "TIMESTAMP"
                        }
                    ]
                }
            ]
        }
    ],
    where=[
        {
            "path": "class.code = 'ACUTE'"
        }
    ]
)

# Save as managed table.
rv_icu_encounter.write.mode("overwrite").saveAsTable("mimic_iv_views.rv_icu_encounter")
print("✓ View rv_icu_encounter created and saved as table mimic_iv_views.rv_icu_encounter")

# Show sample data.
row_count = rv_icu_encounter.count()
print(f"  Row count: {row_count}")
if row_count > 0:
    print("  Sample data:")
    rv_icu_encounter.show(5, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Create Vital Signs View (rv_obs_vitalsigns)
# MAGIC
# MAGIC This view extracts recorded vital signs including heart rate, respiratory rate, and oxygen saturation.
# MAGIC
# MAGIC **What this extracts**:
# MAGIC - Measurements of heart rate (220045)
# MAGIC - Oxygen saturation (220277) 
# MAGIC - Respiratory rate (220210, 224690)
# MAGIC - Timestamps and numeric values
# MAGIC
# MAGIC Pulse oximetry readings (oxygen saturation) are crucial for studying health disparities in oxygen monitoring.

# COMMAND ----------

# Create rv_obs_vitalsigns view.
print("Creating view: rv_obs_vitalsigns")

rv_obs_vitalsigns = datasource.view(
    resource="Observation",
    select=[
        {
            "column": [
                {
                    "name": "subject_id",
                    "path": "subject.getReferenceKey()",
                    "type": "string"
                },
                {
                    "name": "stay_id",
                    "path": "encounter.getReferenceKey()",
                    "type": "string"
                },
                {
                    "name": "charttime",
                    "path": "effective.ofType(dateTime)",
                    "type": "dateTime",
                    "tag": [
                        {
                            "name": "ansi/type",
                            "value": "TIMESTAMP"
                        }
                    ]
                },
                {
                    "name": "storetime",
                    "path": "issued",
                    "type": "instant",
                    "tag": [
                        {
                            "name": "ansi/type",
                            "value": "TIMESTAMP"
                        }
                    ]
                },
                {
                    "name": "valuenum",
                    "path": "value.ofType(Quantity).value",
                    "type": "decimal"
                },
                {
                    "name": "itemid",
                    "path": "code.coding.code",
                    "type": "code",
                    "tag": [
                        {
                            "name": "ansi/type",
                            "value": "INTEGER"
                        }
                    ]
                }
            ]
        }
    ],
    where=[
        {
            "path": "code.coding.code = '220045' or code.coding.code = '220277' or code.coding.code = '220210' or code.coding.code = '224690'"
        }
    ]
)

# Save as managed table.
rv_obs_vitalsigns.write.mode("overwrite").saveAsTable("mimic_iv_views.rv_obs_vitalsigns")
print("✓ View rv_obs_vitalsigns created and saved as table mimic_iv_views.rv_obs_vitalsigns")

# Show sample data.
row_count = rv_obs_vitalsigns.count()
print(f"  Row count: {row_count}")
if row_count > 0:
    print("  Sample data:")
    rv_obs_vitalsigns.show(5, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Create Oxygen Flow View (rv_obs_o2_flow)
# MAGIC
# MAGIC This view captures oxygen flow rates from respiratory equipment.
# MAGIC
# MAGIC **What this extracts**:
# MAGIC - Oxygen flow rates in litres per minute
# MAGIC - Regular oxygen flow (223834)
# MAGIC - BiPAP oxygen flow (227582)
# MAGIC - Additional oxygen flow (227287)
# MAGIC
# MAGIC These measurements show how much supplemental oxygen each patient received, which is key for studying treatment disparities.

# COMMAND ----------

# Create rv_obs_o2_flow view.
print("Creating view: rv_obs_o2_flow")

rv_obs_o2_flow = datasource.view(
    resource="Observation",
    select=[
        {
            "column": [
                {
                    "name": "subject_id",
                    "path": "subject.getReferenceKey()",
                    "type": "string"
                },
                {
                    "name": "stay_id",
                    "path": "encounter.getReferenceKey()",
                    "type": "string"
                },
                {
                    "name": "charttime",
                    "path": "effective.ofType(dateTime)",
                    "type": "dateTime",
                    "tag": [
                        {
                            "name": "ansi/type",
                            "value": "TIMESTAMP"
                        }
                    ]
                },
                {
                    "name": "storetime",
                    "path": "issued",
                    "type": "instant",
                    "tag": [
                        {
                            "name": "ansi/type",
                            "value": "TIMESTAMP"
                        }
                    ]
                },
                {
                    "name": "valuenum",
                    "path": "value.ofType(Quantity).value",
                    "type": "decimal"
                },
                {
                    "name": "itemid",
                    "path": "code.coding.code",
                    "type": "code",
                    "tag": [
                        {
                            "name": "ansi/type",
                            "value": "INTEGER"
                        }
                    ]
                }
            ]
        }
    ],
    where=[
        {
            "path": "code.coding.code = '223834' or code.coding.code = '227582' or code.coding.code = '227287'"
        }
    ]
)

# Save as managed table.
rv_obs_o2_flow.write.mode("overwrite").saveAsTable("mimic_iv_views.rv_obs_o2_flow")
print("✓ View rv_obs_o2_flow created and saved as table mimic_iv_views.rv_obs_o2_flow")

# Show sample data.
row_count = rv_obs_o2_flow.count()
print(f"  Row count: {row_count}")
if row_count > 0:
    print("  Sample data:")
    rv_obs_o2_flow.show(5, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: Create Oxygen Delivery Device View (rv_o2_delivery_device)
# MAGIC
# MAGIC This view records what types of oxygen delivery equipment were used.
# MAGIC
# MAGIC **What this extracts**:
# MAGIC - Text descriptions of oxygen delivery devices
# MAGIC - Examples: "nasal cannula", "face mask", "mechanical ventilator"
# MAGIC - Code 226732 identifies oxygen delivery device observations
# MAGIC
# MAGIC Different delivery devices provide different amounts of oxygen support, helping researchers understand treatment intensity.

# COMMAND ----------

# Create rv_o2_delivery_device view.
print("Creating view: rv_o2_delivery_device")

rv_o2_delivery_device = datasource.view(
    resource="Observation",
    select=[
        {
            "column": [
                {
                    "name": "subject_id",
                    "path": "subject.getReferenceKey()",
                    "type": "string"
                },
                {
                    "name": "stay_id",
                    "path": "encounter.getReferenceKey()",
                    "type": "string"
                },
                {
                    "name": "charttime",
                    "path": "effective.ofType(dateTime)",
                    "type": "dateTime",
                    "tag": [
                        {
                            "name": "ansi/type",
                            "value": "TIMESTAMP"
                        }
                    ]
                },
                {
                    "name": "value",
                    "path": "value.ofType(string)",
                    "type": "string"
                }
            ]
        }
    ],
    where=[
        {
            "path": "code.coding.code = '226732'"
        }
    ]
)

# Save as managed table.
rv_o2_delivery_device.write.mode("overwrite").saveAsTable("mimic_iv_views.rv_o2_delivery_device")
print("✓ View rv_o2_delivery_device created and saved as table mimic_iv_views.rv_o2_delivery_device")

# Show sample data.
row_count = rv_o2_delivery_device.count()
print(f"  Row count: {row_count}")
if row_count > 0:
    print("  Sample data:")
    rv_o2_delivery_device.show(5, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 8: Create Blood Gas View (rv_obs_bg)
# MAGIC
# MAGIC This view extracts laboratory results from blood gas analyses.
# MAGIC
# MAGIC **What this extracts**:
# MAGIC - Oxygen saturation from blood samples (50817)
# MAGIC - Carbon dioxide levels (50818)
# MAGIC - Specimen information (52033)
# MAGIC
# MAGIC Blood gas measurements provide the "gold standard" for measuring oxygen levels, which researchers compare against pulse oximeter readings to assess device accuracy.

# COMMAND ----------

# Create rv_obs_bg view.
print("Creating view: rv_obs_bg")

rv_obs_bg = datasource.view(
    resource="Observation",
    select=[
        {
            "column": [
                {
                    "name": "subject_id",
                    "path": "subject.getReferenceKey()",
                    "type": "string"
                },
                {
                    "name": "hadm_id",
                    "path": "encounter.getReferenceKey()",
                    "type": "string"
                },
                {
                    "name": "charttime",
                    "path": "effective.ofType(dateTime)",
                    "type": "dateTime",
                    "tag": [
                        {
                            "name": "ansi/type",
                            "value": "TIMESTAMP"
                        }
                    ]
                },
                {
                    "name": "storetime",
                    "path": "issued",
                    "type": "instant",
                    "tag": [
                        {
                            "name": "ansi/type",
                            "value": "TIMESTAMP"
                        }
                    ]
                },
                {
                    "name": "value",
                    "path": "value.ofType(string)",
                    "type": "string"
                },
                {
                    "name": "valuenum",
                    "path": "value.ofType(Quantity).value",
                    "type": "decimal"
                },
                {
                    "name": "itemid",
                    "path": "code.coding.code",
                    "type": "code",
                    "tag": [
                        {
                            "name": "ansi/type",
                            "value": "INTEGER"
                        }
                    ]
                },
                {
                    "name": "specimen_id",
                    "path": "specimen.getReferenceKey()",
                    "type": "string"
                }
            ]
        }
    ],
    where=[
        {
            "path": "code.coding.code = '52033' or code.coding.code = '50817' or code.coding.code = '50818'"
        }
    ]
)

# Save as managed table.
rv_obs_bg.write.mode("overwrite").saveAsTable("mimic_iv_views.rv_obs_bg")
print("✓ View rv_obs_bg created and saved as table mimic_iv_views.rv_obs_bg")

# Show sample data.
row_count = rv_obs_bg.count()
print(f"  Row count: {row_count}")
if row_count > 0:
    print("  Sample data:")
    rv_obs_bg.show(5, truncate=False)