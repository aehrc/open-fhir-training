# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # Transform Synthea CSV to FHIR Resources
# MAGIC
# MAGIC ## What this notebook does
# MAGIC This notebook takes healthcare data stored in CSV format (from Synthea, a synthetic patient data generator) and transforms it into FHIR format, which is the international standard for healthcare data exchange.
# MAGIC
# MAGIC ## Resources we'll create
# MAGIC We'll transform three types of CSV data into FHIR resources:
# MAGIC
# MAGIC 1. **[Patient Resources](https://hl7.org/fhir/R4/patient.html)** - Contains demographic information like:
# MAGIC    - Names and identifiers (SSN, driver's license)
# MAGIC    - Birth dates and addresses
# MAGIC    - Gender and marital status
# MAGIC
# MAGIC 2. **[Encounter Resources](https://hl7.org/fhir/R4/encounter.html)** - Represents healthcare visits:
# MAGIC    - When the visit occurred
# MAGIC    - What type of visit (emergency, outpatient, wellness check)
# MAGIC    - Which patient and provider were involved
# MAGIC    - The reason for the visit
# MAGIC
# MAGIC 3. **[Immunization Resources](https://hl7.org/fhir/R4/immunization.html)** - Records of vaccinations:
# MAGIC    - Which vaccine was given
# MAGIC    - When it was administered
# MAGIC    - Which patient received it
# MAGIC    - During which encounter
# MAGIC
# MAGIC ## Output format
# MAGIC The transformed data will be saved in two ways:
# MAGIC 1. **NDJSON files** (Newline Delimited JSON) - text files with one JSON resource per line, suitable for bulk import
# MAGIC 2. **Delta tables** - Databricks managed tables for querying and further analysis

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup and Configuration
# MAGIC
# MAGIC In this section, we'll:
# MAGIC 1. Import the necessary Python libraries for data transformation
# MAGIC 2. Set up helper functions to clean and format data
# MAGIC
# MAGIC **What is Spark?** Apache Spark is a data processing engine that can handle large amounts of data efficiently. In Databricks, it's already set up and ready to use through the `spark` variable.

# COMMAND ----------

import json

from pyspark.sql.functions import (
    array,
    col,
    concat_ws,
    lit,
    struct,
    to_json,
    when,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Helper Functions
# MAGIC
# MAGIC These are small utility functions that help us clean and format data:
# MAGIC
# MAGIC - **clean_uuid**: Cleans UUID strings for use as resource IDs
# MAGIC - **format_datetime**: Ensures date/time formats match FHIR standards

# COMMAND ----------


def clean_uuid(uuid_str):
    """Clean UUID string for use as FHIR resource ID."""
    if uuid_str:
        # Return the UUID as-is - FHIR allows hyphens in IDs
        return uuid_str.strip()
    return None


def format_datetime(dt_str):
    """Format datetime string to FHIR format."""
    if dt_str and dt_str.strip():
        # Synthea uses format: 2012-09-11T23:57:37Z
        # This is already FHIR compliant.
        return dt_str
    return None


# Register UDFs.
spark.udf.register("clean_uuid", clean_uuid)
spark.udf.register("format_datetime", format_datetime)

print("Helper functions defined")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Transform Patient Resources
# MAGIC
# MAGIC Now we'll transform the patient CSV data into FHIR Patient resources. This involves:
# MAGIC
# MAGIC 1. **Loading the data** from the `synthea_csv.patients` table
# MAGIC 2. **Mapping CSV columns** to FHIR fields
# MAGIC 3. **Creating JSON structure** that follows FHIR standards
# MAGIC
# MAGIC ### What we're transforming:
# MAGIC - **CSV fields like**: Id, FIRST, LAST, GENDER, BIRTHDATE, ADDRESS, etc.
# MAGIC - **Into FHIR structure with**: resourceType, identifier, name, gender, birthDate, address
# MAGIC
# MAGIC ### Key transformations:
# MAGIC - Remove hyphens from IDs (FHIR doesn't allow them)
# MAGIC - Map gender codes (M → male, F → female)
# MAGIC - Structure addresses with proper fields (line, city, state, postalCode)
# MAGIC - Create identifier objects for SSN, driver's license, and passport

# COMMAND ----------

# MAGIC %md
# MAGIC ### Loading the Patient Data
# MAGIC
# MAGIC First, we load the patient data from our CSV table. In Spark:
# MAGIC - A **DataFrame** (df) is like a table or spreadsheet with rows and columns
# MAGIC - We can transform this data using SQL-like operations
# MAGIC - The `printSchema()` shows us what columns exist and their data types

# COMMAND ----------

# Load patients table.
patients_df = spark.table("synthea_csv.patients")
print(f"Loaded {patients_df.count()} patient records")

# Display schema.
patients_df.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Understanding the Transformation Code
# MAGIC
# MAGIC The code below uses Spark SQL functions to transform flat CSV data into nested JSON structures required by FHIR.
# MAGIC
# MAGIC **Key Spark SQL functions we'll use:**
# MAGIC - `col("column_name")`: References a column from the CSV
# MAGIC - `lit("value")`: Creates a literal/constant value
# MAGIC - `when().otherwise()`: Like an if-then-else statement
# MAGIC - `struct()`: Creates a nested JSON object
# MAGIC - `array()`: Creates a JSON array (list)
# MAGIC - `regexp_replace()`: Modifies text using patterns
# MAGIC - `alias()`: Names the output column
# MAGIC
# MAGIC **How it works:**
# MAGIC 1. Each `select()` statement defines what will be in our output
# MAGIC 2. We're building a nested structure that matches FHIR requirements
# MAGIC 3. The result will be one JSON object per patient

# COMMAND ----------

# Transform to FHIR Patient resources.
# This is where the magic happens - we're reshaping flat CSV data into nested JSON.
patient_fhir_df = patients_df.select(
    # STEP 1: Create the resource ID
    # Use the original UUID as-is for the FHIR resource ID
    col("Id").alias("id"),
    # STEP 2: Set the resource type
    # Every FHIR resource must declare its type - this tells systems what kind of resource it is
    lit("Patient").alias("resourceType"),
    # STEP 3: Create identifiers array
    # Identifiers are how we link patients across different systems
    # We create an array because patients can have multiple IDs (SSN, driver's license, etc.)
    array(
        # SSN identifier - only include if patient has an SSN
        # The when() function is like an if statement: if SSN exists and isn't empty, create this structure
        when(
            col("SSN").isNotNull() & (col("SSN") != ""),
            struct(  # struct() creates a nested JSON object
                # The 'type' field tells what kind of identifier this is
                struct(
                    lit("http://terminology.hl7.org/CodeSystem/v2-0203").alias(
                        "system"
                    ),  # The code system
                    lit("SS").alias("code"),  # SS = Social Security Number
                    lit("Social Security Number").alias(
                        "display"
                    ),  # Human-readable name
                ).alias("type"),
                # The actual identifier value and its system
                lit("http://hl7.org/fhir/sid/us-ssn").alias("system"),  # SSN namespace
                col("SSN").alias("value"),  # The actual SSN from the CSV
            ),
        ),
        # Driver's license identifier - only include if patient has one
        when(
            col("DRIVERS").isNotNull() & (col("DRIVERS") != ""),
            struct(
                struct(
                    lit("http://terminology.hl7.org/CodeSystem/v2-0203").alias(
                        "system"
                    ),
                    lit("DL").alias("code"),
                    lit("Driver's License").alias("display"),
                ).alias("type"),
                concat_ws(
                    "", lit("urn:oid:2.16.840.1.113883.4.3."), col("STATE")
                ).alias("system"),
                col("DRIVERS").alias("value"),
            ),
        ),
        # Passport.
        when(
            col("PASSPORT").isNotNull() & (col("PASSPORT") != ""),
            struct(
                struct(
                    lit("http://terminology.hl7.org/CodeSystem/v2-0203").alias(
                        "system"
                    ),
                    lit("PPN").alias("code"),
                    lit("Passport Number").alias("display"),
                ).alias("type"),
                lit("http://hl7.org/fhir/sid/us-passport").alias("system"),
                col("PASSPORT").alias("value"),
            ),
        ),
    ).alias("identifier"),
    # STEP 4: Create the name structure
    # FHIR allows multiple names (maiden name, nickname, etc.) so we use an array
    array(
        struct(
            lit("official").alias("use"),  # This is their official/legal name
            col("LAST").alias("family"),  # Family name (last name)
            # Given names are also an array (people can have multiple first names)
            # We only create the array if FIRST name exists
            when(col("FIRST").isNotNull(), array(col("FIRST"))).alias("given"),
            col("PREFIX").alias("prefix"),  # Mr., Mrs., Dr., etc.
            col("SUFFIX").alias("suffix"),  # Jr., Sr., III, etc.
        )
    ).alias("name"),
    # STEP 5: Map gender codes
    # CSV has M/F, but FHIR uses male/female/other/unknown
    # This is a chained when() - like a switch/case statement
    when(col("GENDER") == "M", lit("male"))
    .when(col("GENDER") == "F", lit("female"))
    .otherwise(lit("unknown"))
    .alias("gender"),
    # Birth date.
    col("BIRTHDATE").alias("birthDate"),
    # Deceased date.
    when(
        col("DEATHDATE").isNotNull() & (col("DEATHDATE") != ""), col("DEATHDATE")
    ).alias("deceasedDateTime"),
    # Address.
    when(
        col("ADDRESS").isNotNull(),
        array(
            struct(
                when(col("ADDRESS").isNotNull(), array(col("ADDRESS"))).alias("line"),
                col("CITY").alias("city"),
                col("STATE").alias("state"),
                col("ZIP").alias("postalCode"),
            )
        ),
    ).alias("address"),
    # Marital status.
    when(
        col("MARITAL") == "M",
        struct(
            array(
                struct(
                    lit("http://terminology.hl7.org/CodeSystem/v3-MaritalStatus").alias(
                        "system"
                    ),
                    lit("M").alias("code"),
                    lit("Married").alias("display"),
                )
            ).alias("coding"),
            lit("Married").alias("text"),
        ),
    )
    .when(
        col("MARITAL") == "S",
        struct(
            array(
                struct(
                    lit("http://terminology.hl7.org/CodeSystem/v3-MaritalStatus").alias(
                        "system"
                    ),
                    lit("S").alias("code"),
                    lit("Never Married").alias("display"),
                )
            ).alias("coding"),
            lit("Never Married").alias("text"),
        ),
    )
    .alias("maritalStatus"),
    # Extension for race.
    when(
        col("RACE").isNotNull() & (col("RACE") != ""),
        array(
            struct(
                lit(
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race"
                ).alias("url"),
                array(
                    struct(lit("text").alias("url"), col("RACE").alias("valueString"))
                ).alias("extension"),
            )
        ),
    ).alias("extension"),
)

# Convert to JSON strings.
patient_json_df = patient_fhir_df.select(to_json(struct("*")).alias("json"))

print(f"Transformed {patient_json_df.count()} patient resources")

# COMMAND ----------

# Write Patient NDJSON file.
output_path = "/tmp/fhir_output"
patient_output = f"{output_path}/Patient.ndjson"

patient_json_df.coalesce(1).write.mode("overwrite").text(patient_output)

print(f"Written Patient resources to {patient_output}")

# Display sample.
patient_json_df.show(2, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Transform Encounter Resources
# MAGIC
# MAGIC An **Encounter** in FHIR represents an interaction between a patient and healthcare provider(s). This could be:
# MAGIC - An emergency room visit
# MAGIC - A routine check-up
# MAGIC - A hospital admission
# MAGIC - A telehealth consultation
# MAGIC
# MAGIC ### What we're transforming:
# MAGIC - **CSV fields**: Id, START, STOP, PATIENT, PROVIDER, ENCOUNTERCLASS, CODE, REASONCODE
# MAGIC - **Into FHIR Encounter** with proper structure and references
# MAGIC
# MAGIC ### Key concepts:
# MAGIC - **Status**: All historical encounters are marked as "finished"
# MAGIC - **Class**: The type of encounter (emergency, outpatient, inpatient, etc.)
# MAGIC - **References**: Links to other resources (Patient, Provider, Organization)
# MAGIC - **Period**: When the encounter started and ended
# MAGIC - **Reason**: Why the patient sought care (if documented)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Loading and Transforming Encounter Data
# MAGIC
# MAGIC Now we'll transform encounter data. Each encounter represents a healthcare interaction between a patient and provider.

# COMMAND ----------

# Load encounters table.
encounters_df = spark.table("synthea_csv.encounters")
print(f"Loaded {encounters_df.count()} encounter records")

# Display schema.
encounters_df.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Building the Encounter FHIR Structure
# MAGIC
# MAGIC The transformation below shows how we:
# MAGIC 1. **Create references** between resources (Patient, Provider, Organization)
# MAGIC 2. **Map encounter classes** from simple strings to FHIR coding systems
# MAGIC 3. **Handle optional fields** like reason codes (not all encounters have a documented reason)
# MAGIC 4. **Structure time periods** with start and end timestamps

# COMMAND ----------

# Transform to FHIR Encounter resources.
encounter_fhir_df = encounters_df.select(
    # Resource ID - use the original UUID as-is
    col("Id").alias("id"),
    # Resource type
    lit("Encounter").alias("resourceType"),
    # Status - all historical encounters are marked as "finished"
    # Other possible values: planned, arrived, triaged, in-progress, onleave
    lit("finished").alias("status"),
    # Class - this describes the setting/type of encounter
    # We map CSV values (wellness, outpatient, etc.) to standard FHIR codes
    struct(
        lit("http://terminology.hl7.org/CodeSystem/v3-ActCode").alias("system"),
        when(col("ENCOUNTERCLASS") == "wellness", lit("WELLNESS"))
        .when(col("ENCOUNTERCLASS") == "outpatient", lit("AMB"))
        .when(col("ENCOUNTERCLASS") == "emergency", lit("EMER"))
        .when(col("ENCOUNTERCLASS") == "inpatient", lit("IMP"))
        .when(col("ENCOUNTERCLASS") == "urgentcare", lit("ACUTE"))
        .when(col("ENCOUNTERCLASS") == "ambulatory", lit("AMB"))
        .otherwise(lit("AMB"))
        .alias("code"),
        col("ENCOUNTERCLASS").alias("display"),
    ).alias("class"),
    # Type.
    when(
        col("CODE").isNotNull() & col("DESCRIPTION").isNotNull(),
        array(
            struct(
                array(
                    struct(
                        lit("http://snomed.info/sct").alias("system"),
                        col("CODE").alias("code"),
                        col("DESCRIPTION").alias("display"),
                    )
                ).alias("coding"),
                col("DESCRIPTION").alias("text"),
            )
        ),
    ).alias("type"),
    # Subject (Patient reference).
    struct(concat_ws("", lit("Patient/"), col("PATIENT")).alias("reference")).alias(
        "subject"
    ),
    # Participant (Provider).
    when(
        col("PROVIDER").isNotNull(),
        array(
            struct(
                array(
                    struct(
                        array(
                            struct(
                                lit(
                                    "http://terminology.hl7.org/CodeSystem/v3-ParticipationType"
                                ).alias("system"),
                                lit("PPRF").alias("code"),
                                lit("primary performer").alias("display"),
                            )
                        ).alias("coding")
                    )
                ).alias("type"),
                struct(
                    concat_ws("", lit("Practitioner/"), col("PROVIDER")).alias(
                        "reference"
                    )
                ).alias("individual"),
            )
        ),
    ).alias("participant"),
    # Period.
    struct(col("START").alias("start"), col("STOP").alias("end")).alias("period"),
    # Reason code.
    when(
        col("REASONCODE").isNotNull() & col("REASONDESCRIPTION").isNotNull(),
        array(
            struct(
                array(
                    struct(
                        lit("http://snomed.info/sct").alias("system"),
                        col("REASONCODE").alias("code"),
                        col("REASONDESCRIPTION").alias("display"),
                    )
                ).alias("coding"),
                col("REASONDESCRIPTION").alias("text"),
            )
        ),
    ).alias("reasonCode"),
    # Service provider (Organization).
    when(
        col("ORGANIZATION").isNotNull(),
        struct(
            concat_ws("", lit("Organization/"), col("ORGANIZATION")).alias("reference")
        ),
    ).alias("serviceProvider"),
)

# Convert to JSON strings.
encounter_json_df = encounter_fhir_df.select(to_json(struct("*")).alias("json"))

print(f"Transformed {encounter_json_df.count()} encounter resources")

# COMMAND ----------

# Write Encounter NDJSON file.
encounter_output = f"{output_path}/Encounter.ndjson"

encounter_json_df.coalesce(1).write.mode("overwrite").text(encounter_output)

print(f"Written Encounter resources to {encounter_output}")

# Display sample.
encounter_json_df.show(2, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Transform Immunization Resources
# MAGIC
# MAGIC **Immunization resources** record vaccines administered to patients. This is crucial for:
# MAGIC - Tracking vaccination history
# MAGIC - Ensuring patients are up-to-date with immunizations
# MAGIC - Public health reporting
# MAGIC - Preventing duplicate vaccinations
# MAGIC
# MAGIC ### What we're transforming:
# MAGIC - **CSV fields**: DATE, PATIENT, ENCOUNTER, CODE, DESCRIPTION
# MAGIC - **Into FHIR Immunization** resources with proper vaccine coding
# MAGIC
# MAGIC ### Key elements:
# MAGIC - **Vaccine Code**: Uses CVX codes (standardised vaccine codes used in the US)
# MAGIC - **Status**: All marked as "completed" since these are historical records
# MAGIC - **References**: Links to the Patient who received it and the Encounter when it was given
# MAGIC - **Route/Site**: Default values for typical vaccine administration (intramuscular injection in left arm)

# COMMAND ----------

# Load immunizations table.
immunizations_df = spark.table("synthea_csv.immunizations")
print(f"Loaded {immunizations_df.count()} immunization records")

# Display schema.
immunizations_df.printSchema()

# COMMAND ----------

# Transform to FHIR Immunization resources.
immunization_fhir_df = immunizations_df.select(
    # Generate unique ID from patient, encounter and code.
    concat_ws("-", col("PATIENT"), col("ENCOUNTER"), col("CODE")).alias("id"),
    # Resource type.
    lit("Immunization").alias("resourceType"),
    # Status - all historical immunizations are completed.
    lit("completed").alias("status"),
    # Vaccine code (CVX).
    struct(
        array(
            struct(
                lit("http://hl7.org/fhir/sid/cvx").alias("system"),
                col("CODE").alias("code"),
                col("DESCRIPTION").alias("display"),
            )
        ).alias("coding"),
        col("DESCRIPTION").alias("text"),
    ).alias("vaccineCode"),
    # Patient reference.
    struct(concat_ws("", lit("Patient/"), col("PATIENT")).alias("reference")).alias(
        "patient"
    ),
    # Encounter reference.
    struct(concat_ws("", lit("Encounter/"), col("ENCOUNTER")).alias("reference")).alias(
        "encounter"
    ),
    # Occurrence date/time.
    col("DATE").alias("occurrenceDateTime"),
    # Primary source - true for all Synthea data.
    lit(True).alias("primarySource"),
)

# Convert to JSON strings.
immunization_json_df = immunization_fhir_df.select(to_json(struct("*")).alias("json"))

print(f"Transformed {immunization_json_df.count()} immunization resources")

# COMMAND ----------

# Write Immunization NDJSON file.
immunization_output = f"{output_path}/Immunization.ndjson"

immunization_json_df.coalesce(1).write.mode("overwrite").text(immunization_output)

print(f"Written Immunization resources to {immunization_output}")

# Display sample.
immunization_json_df.show(2, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validation and Summary
# MAGIC
# MAGIC Let's verify our transformation was successful by:
# MAGIC 1. Counting the number of resources created
# MAGIC 2. Checking that the JSON is properly formatted
# MAGIC 3. Ensuring references between resources are valid

# COMMAND ----------

# Count resources created.
print("Resource Summary:")
print("=" * 50)

# Read back the NDJSON files to verify.
patient_count = spark.read.text(patient_output).count()
encounter_count = spark.read.text(encounter_output).count()
immunization_count = spark.read.text(immunization_output).count()

print(f"Patient resources: {patient_count}")
print(f"Encounter resources: {encounter_count}")
print(f"Immunization resources: {immunization_count}")
print(
    f"\nTotal resources created: {patient_count + encounter_count + immunization_count}"
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Sample Resources

# COMMAND ----------

# Display a sample Patient resource.
print("Sample Patient Resource:")
print("=" * 50)
sample_patient = spark.read.text(patient_output).first()[0]
patient_json = json.loads(sample_patient)
print(json.dumps(patient_json, indent=2))

# COMMAND ----------

# Display a sample Encounter resource.
print("Sample Encounter Resource:")
print("=" * 50)
sample_encounter = spark.read.text(encounter_output).first()[0]
encounter_json = json.loads(sample_encounter)
print(json.dumps(encounter_json, indent=2))

# COMMAND ----------

# Display a sample Immunization resource.
print("Sample Immunization Resource:")
print("=" * 50)
sample_immunization = spark.read.text(immunization_output).first()[0]
immunization_json = json.loads(sample_immunization)
print(json.dumps(immunization_json, indent=2))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Referential Integrity Check
# MAGIC
# MAGIC **Referential integrity** means ensuring that all references between resources are valid. For example:
# MAGIC - Every Encounter should reference a Patient that exists
# MAGIC - Every Immunization should reference both a valid Patient and Encounter
# MAGIC
# MAGIC This check helps us identify any "orphan" records that reference non-existent resources, which would cause errors when loading into a FHIR server.

# COMMAND ----------

# Check that all patient references in encounters exist.
encounters_patients = encounters_df.select(
    col("PATIENT").alias("patient_id")
).distinct()

patients_ids = patients_df.select(col("Id").alias("patient_id")).distinct()

orphan_encounters = encounters_patients.join(
    patients_ids, on="patient_id", how="left_anti"
).count()

print(f"Orphan encounters (no matching patient): {orphan_encounters}")

# Check that all encounter references in immunizations exist.
immunizations_encounters = immunizations_df.select(
    col("ENCOUNTER").alias("encounter_id")
).distinct()

encounters_ids = encounters_df.select(col("Id").alias("encounter_id")).distinct()

orphan_immunizations = immunizations_encounters.join(
    encounters_ids, on="encounter_id", how="left_anti"
).count()

print(f"Orphan immunizations (no matching encounter): {orphan_immunizations}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Steps
# MAGIC
# MAGIC The NDJSON files have been created and are ready for:
# MAGIC
# MAGIC 1. **Bulk upload to FHIR server** using the FHIR Bulk Data API
# MAGIC 2. **Validation** using FHIR validators to ensure compliance
# MAGIC 3. **Additional transformations** for other resource types (Condition, Procedure, Observation, etc.)
# MAGIC
# MAGIC ### Output locations:
# MAGIC - `/tmp/fhir_output/Patient.ndjson`
# MAGIC - `/tmp/fhir_output/Encounter.ndjson`
# MAGIC - `/tmp/fhir_output/Immunization.ndjson`

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Managed Tables
# MAGIC
# MAGIC Now we'll save our transformed FHIR JSON resources to **managed Delta tables** in Databricks.
# MAGIC
# MAGIC ### What are managed tables?
# MAGIC - **Managed tables** are tables where Databricks manages both the metadata and the data files
# MAGIC - They're stored in the Databricks workspace and are optimised for query performance
# MAGIC - You can query them using SQL, making it easy to analyse the transformed data
# MAGIC
# MAGIC ### Why use Delta format?
# MAGIC - **Delta Lake** provides ACID transactions, ensuring data consistency
# MAGIC - Supports time travel (viewing previous versions of data)
# MAGIC - Optimised for both batch and streaming operations
# MAGIC
# MAGIC We'll create three tables in the `synthea_transformed` schema:
# MAGIC - `synthea_transformed.patient`
# MAGIC - `synthea_transformed.encounter`
# MAGIC - `synthea_transformed.immunization`

# COMMAND ----------

# Create schema if it doesn't exist.
spark.sql("CREATE SCHEMA IF NOT EXISTS synthea_transformed")
print("Created synthea_transformed schema")

# Drop and recreate Patient table.
spark.sql("DROP TABLE IF EXISTS synthea_transformed.patient")
patient_json_df.write.mode("overwrite").saveAsTable("synthea_transformed.patient")
print(
    f"✓ Created table synthea_transformed.patient with {patient_json_df.count()} rows"
)

# Drop and recreate Encounter table.
spark.sql("DROP TABLE IF EXISTS synthea_transformed.encounter")
encounter_json_df.write.mode("overwrite").saveAsTable("synthea_transformed.encounter")
print(
    f"✓ Created table synthea_transformed.encounter with {encounter_json_df.count()} rows"
)

# Drop and recreate Immunization table.
spark.sql("DROP TABLE IF EXISTS synthea_transformed.immunization")
immunization_json_df.write.mode("overwrite").saveAsTable(
    "synthea_transformed.immunization"
)
print(
    f"✓ Created table synthea_transformed.immunization with {immunization_json_df.count()} rows"
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Managed Tables

# COMMAND ----------

# Show tables in synthea_transformed schema.
print("Tables in synthea_transformed schema:")
spark.sql("SHOW TABLES IN synthea_transformed").show()

# Show sample records from each table.
print("\nSample from synthea_transformed.patient:")
spark.sql("SELECT * FROM synthea_transformed.patient LIMIT 2").show(truncate=False)

print("\nSample from synthea_transformed.encounter:")
spark.sql("SELECT * FROM synthea_transformed.encounter LIMIT 2").show(truncate=False)

print("\nSample from synthea_transformed.immunization:")
spark.sql("SELECT * FROM synthea_transformed.immunization LIMIT 2").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load FHIR Resources with Pathling
# MAGIC
# MAGIC Now we'll use **Pathling** to read our NDJSON FHIR resources and create structured DataFrames.
# MAGIC
# MAGIC ### What is Pathling?
# MAGIC **Pathling** is a library specifically designed for working with FHIR data in Apache Spark. It provides:
# MAGIC - **Encoders** that understand FHIR structure and convert JSON to structured DataFrames
# MAGIC - **FHIRPath** query capabilities for complex healthcare data analysis
# MAGIC - **Optimised storage** formats for FHIR resources
# MAGIC
# MAGIC ### Why use Pathling encoders?
# MAGIC - Automatically handles complex FHIR nested structures
# MAGIC - Creates properly typed columns for all FHIR elements
# MAGIC - Enables efficient querying and analytics on healthcare data
# MAGIC - Validates data against FHIR specifications

# COMMAND ----------

from pathling import PathlingContext

# Initialise Pathling context.
pc = PathlingContext.create()

print("Pathling context created")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Read NDJSON Files with Pathling Encoders
# MAGIC
# MAGIC Pathling's encoders API reads NDJSON files and automatically structures them according to FHIR specifications:

# COMMAND ----------

# Read Patient resources using Pathling encoders.
patient_text_df = spark.read.text(patient_output)
patient_pathling_df = pc.encode(patient_text_df, "Patient")
print(f"Loaded {patient_pathling_df.count()} Patient resources with Pathling")

# Read Encounter resources using Pathling encoders.
encounter_text_df = spark.read.text(encounter_output)
encounter_pathling_df = pc.encode(encounter_text_df, "Encounter")
print(f"Loaded {encounter_pathling_df.count()} Encounter resources with Pathling")

# Read Immunization resources using Pathling encoders.
immunization_text_df = spark.read.text(immunization_output)
immunization_pathling_df = pc.encode(immunization_text_df, "Immunization")
print(f"Loaded {immunization_pathling_df.count()} Immunization resources with Pathling")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Pathling Dataset
# MAGIC
# MAGIC We'll create a Dataset that contains all our FHIR resource types for integrated querying:

# COMMAND ----------

# Create Dataset with all resource types using the datasets method.
data = pc.read.datasets(
    {
        "Patient": patient_pathling_df,
        "Encounter": encounter_pathling_df,
        "Immunization": immunization_pathling_df,
    }
)

print("Pathling Dataset created with Patient, Encounter, and Immunization resources")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Managed Tables in synthea_encoded Schema
# MAGIC
# MAGIC Finally, we'll write the structured FHIR data to managed Delta tables for optimised querying:

# COMMAND ----------

# Create schema if it doesn't exist.
spark.sql("CREATE SCHEMA IF NOT EXISTS synthea_encoded")
print("Created synthea_encoded schema")

# Write Pathling-structured resources to managed tables in synthea_encoded schema.
data.write.tables("synthea_encoded")

print("✓ Written all FHIR resources to synthea_encoded schema using Pathling")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Pathling Tables

# COMMAND ----------

# Show tables in synthea_encoded schema.
print("Tables in synthea_encoded schema:")
spark.sql("SHOW TABLES IN synthea_encoded").show()

# Show schema of Patient table to see Pathling's FHIR structure.
print("\nSchema of synthea_encoded.Patient (showing FHIR structure):")
spark.sql("DESCRIBE synthea_encoded.Patient").show(50, truncate=False)

# Sample Patient records.
print("\nSample Patient records from Pathling:")
spark.sql("SELECT id, gender, birthDate FROM synthea_encoded.Patient LIMIT 5").show()

# COMMAND ----------

print("Transformation and Pathling encoding complete!")
