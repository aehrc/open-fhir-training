# Databricks notebook source
# MAGIC %md
# MAGIC # Beta-blockers in septic shock
# MAGIC
# MAGIC Septic shock is sepsis that needs vasopressors to maintain blood pressure. Patients often stay tachycardic after fluid resuscitation, and beta-blockers have been proposed to slow the heart and protect it from catecholamine stress. Their use is controversial, because they also reduce the heart's output. [Zhang et al. (2024)](https://doi.org/10.3389/fcvm.2024.1438798) studied 4,860 patients with septic shock in the full MIMIC-IV database. After propensity score matching, 28-day mortality was 21.5% in patients given a beta-blocker within 48 hours of starting vasopressors, and 27.1% in those who were not.
# MAGIC
# MAGIC This notebook selects the same cohort from the MIMIC-IV demo dataset in FHIR format, using [SQL on FHIR](https://sql-on-fhir.org/) view definitions and Spark SQL. The cohort definition is:
# MAGIC
# MAGIC | Step | Criterion |
# MAGIC | --- | --- |
# MAGIC | 1 | First ICU stay of each patient |
# MAGIC | 2 | Aged 18 or over at ICU admission |
# MAGIC | 3 | ICU stay of at least 48 hours |
# MAGIC | 4 | Suspected infection: an antibiotic and a microbiology culture close together in time |
# MAGIC | 5 | Sepsis ([Sepsis-3](https://doi.org/10.1001/jama.2016.0287)): a SOFA score of 2 or more around the time of the suspected infection |
# MAGIC | 6 | Septic shock: norepinephrine or vasopressin started within 48 hours of the onset of sepsis. The first start is the *baseline*. |
# MAGIC | 7 | No contraindication to beta-blockers: complete heart block, acute myocardial infarction, acute heart failure or asthma |
# MAGIC
# MAGIC Patients given esmolol, metoprolol or labetalol within 48 hours after the baseline form the beta-blocker group; the rest form the control group. The outcome is death within 28 days of the baseline.
# MAGIC
# MAGIC Compared with the pulse oximetry study in `create_spo2_views`, this study draws on more resource types (Patient, Encounter, Condition, MedicationAdministration, Specimen and Observation), and most of its criteria are defined by the timing of one event relative to another.
# MAGIC
# MAGIC The notebook creates eight views, then runs `sql/mimic_iv/combine_beta_blocker_septic_shock_views.sql` to combine them.

# COMMAND ----------

# Author: John Grimes

import matplotlib.pyplot as plt
import pandas as pd
from pathling import PathlingContext
from pyspark.sql import DataFrame

VIEWS_SCHEMA = "mimic_iv_beta_blocker_views"

# Code systems used by MIMIC-IV on FHIR.
MIMIC = "http://mimic.mit.edu/fhir/mimic/CodeSystem"
ICU_ITEMS = f"{MIMIC}/mimic-chartevents-d-items"
ICU_MEDICATIONS = f"{MIMIC}/mimic-medication-icu"
ICU_MEDICATION_CATEGORIES = f"{MIMIC}/mimic-medadmin-category-icu"
FORMULARY_CODES = f"{MIMIC}/mimic-medication-formulary-drug-cd"
MEDICATION_NAMES = f"{MIMIC}/mimic-medication-name"
MICROBIOLOGY_SPECIMEN_TYPES = f"{MIMIC}/mimic-spec-type-desc"

# Colours used for the two groups in every chart.
GROUP_COLOURS = {"Beta-blocker": "#3a9d5d", "No beta-blocker": "#1b6ca8"}

plt.rcParams.update(
    {
        "figure.figsize": (10, 4.5),
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titleweight": "bold",
    }
)


def save_view(view: DataFrame, name: str) -> None:
    """Save a view as a table in the views schema, replacing any earlier version.

    The table's schema is replaced too, so a view definition can be changed and the
    notebook run again.

    :param view: The result of a view definition.
    :param name: The name of the table.
    """
    view.write.option("overwriteSchema", "true").saveAsTable(
        f"{VIEWS_SCHEMA}.{name}", mode="overwrite"
    )


# COMMAND ----------

pc = PathlingContext.create()
pc.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {VIEWS_SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC # Read data from tables
# MAGIC
# MAGIC The data is the [MIMIC-IV Clinical Database demo on FHIR](https://physionet.org/content/mimic-iv-fhir-demo/), imported by the `import_mimic_iv_demo` notebook into the `mimic_iv_demo` schema. It holds 100 patients, so expect a cohort of about ten. The point is the method, which would run unchanged against the full database. The code lists are taken from the full MIMIC-IV code systems, not just the codes that appear in the demo.

# COMMAND ----------

data = pc.read.tables("mimic_iv_demo")
data.read("Patient").count()

# COMMAND ----------

# MAGIC %md
# MAGIC # Views
# MAGIC
# MAGIC We will create eight views with [view definitions](https://build.fhir.org/ig/FHIR/sql-on-fhir-v2/StructureDefinition-ViewDefinition.html):
# MAGIC
# MAGIC | View | Resource | Used for |
# MAGIC | --- | --- | --- |
# MAGIC | `patient_view` | Patient | Age, gender and death |
# MAGIC | `icu_stay_view` | Encounter | First ICU stay and its length |
# MAGIC | `diagnosis_view` | Condition | Contraindications |
# MAGIC | `antibiotic_view` | MedicationAdministration | Suspected infection |
# MAGIC | `microbiology_specimen_view` | Specimen | Suspected infection |
# MAGIC | `sofa_observation_view` | Observation | SOFA score |
# MAGIC | `vasoactive_view` | MedicationAdministration | SOFA score and septic shock |
# MAGIC | `beta_blocker_view` | MedicationAdministration | Treatment group |
# MAGIC
# MAGIC Timestamps are given the `ansi/type` tag `TIMESTAMP`, which gives Spark timestamps in the local time of the record. MIMIC-IV shifts dates into the future to protect privacy, so the ICU stays in the demo dataset run from 2110 to 2201.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Patient view
# MAGIC
# MAGIC One row per patient, with their gender, birth date and date of death. `getResourceKey()` gives an identifier that matches the `getReferenceKey()` of a reference to the patient, so the views can be joined. In MIMIC-IV, deaths are recorded up to one year after the last hospital discharge, which covers the 28-day outcome.

# COMMAND ----------

patients = data.view(
    "Patient",
    select=[
        {
            "column": [
                {
                    "description": "Patient ID",
                    "path": "getResourceKey()",
                    "name": "patient_id",
                },
                {
                    "description": "Administrative gender",
                    "path": "gender",
                    "name": "gender",
                },
                {
                    "description": "Birth date",
                    "path": "birthDate",
                    "name": "birth_date",
                    "type": "date",
                    "tag": [{"name": "ansi/type", "value": "DATE"}],
                },
                {
                    "description": "Date of death (recorded without a time)",
                    "path": "deceased.ofType(dateTime)",
                    "name": "deceased",
                    "type": "dateTime",
                    "tag": [{"name": "ansi/type", "value": "TIMESTAMP"}],
                },
            ]
        }
    ],
)
save_view(patients, "patient_view")
patients.show(5, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## ICU stay view
# MAGIC
# MAGIC One row per ICU stay. MIMIC-IV on FHIR represents an ICU stay as an Encounter with the class `ACUTE`, which is `partOf` the Encounter for the hospital admission. We keep the hospital admission, because diagnoses are recorded against it.

# COMMAND ----------

icu_stays = data.view(
    "Encounter",
    select=[
        {
            "column": [
                {
                    "description": "ICU stay ID",
                    "path": "getResourceKey()",
                    "name": "stay_id",
                },
                {
                    "description": "Patient ID",
                    "path": "subject.getReferenceKey()",
                    "name": "patient_id",
                },
                {
                    "description": "Hospital admission ID",
                    "path": "partOf.getReferenceKey()",
                    "name": "hospital_admission_id",
                },
                {
                    "description": "Admission to the ICU",
                    "path": "period.start",
                    "name": "admit_time",
                    "type": "dateTime",
                    "tag": [{"name": "ansi/type", "value": "TIMESTAMP"}],
                },
                {
                    "description": "Discharge from the ICU",
                    "path": "period.end",
                    "name": "discharge_time",
                    "type": "dateTime",
                    "tag": [{"name": "ansi/type", "value": "TIMESTAMP"}],
                },
            ]
        }
    ],
    where=[{"path": "class.code = 'ACUTE'"}],
)
save_view(icu_stays, "icu_stay_view")
icu_stays.show(5, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC The study needs an ICU stay of at least 48 hours. Here is how long the ICU stays in the demo dataset were. About half of the patients are left out by this step alone.

# COMMAND ----------

stay_hours = pc.spark.sql(f"""
    SELECT (UNIX_TIMESTAMP(discharge_time) - UNIX_TIMESTAMP(admit_time)) / 3600 AS hours
    FROM {VIEWS_SCHEMA}.icu_stay_view
""").toPandas()

fig, ax = plt.subplots()
ax.hist(stay_hours.hours.clip(upper=480), bins=range(0, 492, 12), color="#7f8c8d")
ax.axvline(48, color="#c0392b", linestyle="--")
ax.text(52, ax.get_ylim()[1] * 0.9, "48 hours", color="#c0392b")
ax.set_title(f"Length of ICU stay ({len(stay_hours)} stays)")
ax.set_xlabel("Hours in the ICU (stays over 480 hours shown at 480)")
ax.set_ylabel("ICU stays")
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Diagnosis view
# MAGIC
# MAGIC One row per coded diagnosis, with the hospital admission it belongs to. MIMIC-IV codes diagnoses in ICD-9-CM before late 2015 and ICD-10-CM after, so the `forEach` returns every coding, and the SQL checks both code systems. The Conditions in MIMIC-IV are the billing diagnoses of the admission, so we cannot tell whether a diagnosis was made before or after the ICU stay.

# COMMAND ----------

diagnoses = data.view(
    "Condition",
    select=[
        {
            "column": [
                {
                    "description": "Hospital admission ID",
                    "path": "encounter.getReferenceKey()",
                    "name": "hospital_admission_id",
                },
            ],
            "select": [
                {
                    "forEach": "code.coding",
                    "column": [
                        {
                            "description": "ICD-9-CM or ICD-10-CM code system",
                            "path": "system",
                            "name": "system",
                        },
                        {
                            "description": "ICD code",
                            "path": "code",
                            "name": "code",
                        },
                        {
                            "description": "ICD display",
                            "path": "display",
                            "name": "display",
                        },
                    ],
                }
            ],
        }
    ],
)
save_view(diagnoses, "diagnosis_view")
diagnoses.show(5, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Antibiotic view
# MAGIC
# MAGIC One row per administration of a medicine in the ICU's antibiotic categories. Medicines given in the ICU are recorded by the bedside system with a category, so rather than listing every antibiotic, the `where` clause selects administrations in the two antibiotic categories. The categories also hold antifungals and antivirals, and a separate row for the fluid each antibiotic is diluted in (such as `Dextrose 5%`). Only the times are used, and every diluent row is given alongside its antibiotic, so neither affects the result. Medicines given on the wards are recorded in a different system without these categories, so antibiotics started before the ICU admission are not seen here.
# MAGIC
# MAGIC Infusions have an `effectivePeriod` and one-off doses an `effectiveDateTime`. The union operator `|` takes whichever is present.

# COMMAND ----------

antibiotics = data.view(
    "MedicationAdministration",
    select=[
        {
            "column": [
                {
                    "description": "Patient ID",
                    "path": "subject.getReferenceKey()",
                    "name": "patient_id",
                },
                {
                    "description": "Time the administration started",
                    "path": "effective.ofType(dateTime) | effective.ofType(Period).start",
                    "name": "start_time",
                    "type": "dateTime",
                    "tag": [{"name": "ansi/type", "value": "TIMESTAMP"}],
                },
                {
                    "description": "Medicine",
                    "path": "medication.ofType(CodeableConcept).coding.display",
                    "name": "medicine",
                },
            ]
        }
    ],
    where=[
        {
            "path": f"category.coding.where(system = '{ICU_MEDICATION_CATEGORIES}'"
            " and (code = '08-Antibiotics (IV)' or code = '09-Antibiotics (Non IV)'))"
            ".exists()"
        }
    ],
)
save_view(antibiotics, "antibiotic_view")
antibiotics.show(5, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Microbiology specimen view
# MAGIC
# MAGIC One row per specimen sent for microbiology, with the time it was collected. Specimens for other laboratory tests are coded in a different code system, so the `where` clause selects specimens by the system of their type.

# COMMAND ----------

specimens = data.view(
    "Specimen",
    select=[
        {
            "column": [
                {
                    "description": "Specimen ID",
                    "path": "getResourceKey()",
                    "name": "specimen_id",
                },
                {
                    "description": "Patient ID",
                    "path": "subject.getReferenceKey()",
                    "name": "patient_id",
                },
                {
                    "description": "Time the specimen was collected",
                    "path": "collection.collected.ofType(dateTime)",
                    "name": "collected_time",
                    "type": "dateTime",
                    "tag": [{"name": "ansi/type", "value": "TIMESTAMP"}],
                },
                {
                    "description": "Specimen type",
                    "path": "type.coding.display",
                    "name": "specimen_type",
                },
            ]
        }
    ],
    where=[
        {
            "path": f"type.coding.where(system = '{MICROBIOLOGY_SPECIMEN_TYPES}').exists()"
            " and collection.collected.ofType(dateTime).exists()"
        }
    ],
)
save_view(specimens, "microbiology_specimen_view")
specimens.show(5, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC Sepsis-3 defines a suspected infection as an antibiotic and a culture close together: the culture within 24 hours after the antibiotic, or the antibiotic within 72 hours after the culture. Here is the time from each culture to the nearest antibiotic given within five days of it, for every patient. The shaded band is the window that counts.

# COMMAND ----------

gaps = pc.spark.sql(f"""
    SELECT m.specimen_id,
           MIN_BY(
             (UNIX_TIMESTAMP(a.start_time) - UNIX_TIMESTAMP(m.collected_time)) / 3600,
             ABS(UNIX_TIMESTAMP(a.start_time) - UNIX_TIMESTAMP(m.collected_time))
           ) AS hours
    FROM {VIEWS_SCHEMA}.microbiology_specimen_view m
    JOIN {VIEWS_SCHEMA}.antibiotic_view a
      ON a.patient_id = m.patient_id
     AND a.start_time BETWEEN m.collected_time - INTERVAL 5 DAYS
         AND m.collected_time + INTERVAL 5 DAYS
    GROUP BY m.specimen_id
""").toPandas()

fig, ax = plt.subplots()
ax.axvspan(-24, 72, color="#3a9d5d", alpha=0.15, label="Counts as suspected infection")
ax.hist(gaps.hours, bins=range(-120, 126, 6), color="#7f8c8d")
ax.axvline(0, color="#555", linewidth=1)
ax.set_title(f"Time from culture to nearest antibiotic ({len(gaps)} cultures)")
ax.set_xlabel("Hours (negative: antibiotic before the culture)")
ax.set_ylabel("Cultures")
ax.legend(frameon=False)
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## SOFA observation view
# MAGIC
# MAGIC One row per observation used to calculate the [Sequential Organ Failure Assessment](https://doi.org/10.1007/BF01709751) (SOFA) score. The score has six components, each from 0 to 4:
# MAGIC
# MAGIC | Component | Measurement | MIMIC-IV item |
# MAGIC | --- | --- | --- |
# MAGIC | Respiration | PaO2 / FiO2 ratio | `220224` Arterial O2 pressure, `223835` Inspired O2 fraction |
# MAGIC | Coagulation | Platelets | `227457` Platelet count |
# MAGIC | Liver | Bilirubin | `225690` Total bilirubin |
# MAGIC | Cardiovascular | Mean arterial pressure, vasopressors | `220052` Arterial BP mean, `220181` Non-invasive BP mean, and the vasoactive view below |
# MAGIC | Central nervous system | Glasgow Coma Scale | `220739` Eye opening, `223900` Verbal response, `223901` Motor response |
# MAGIC | Renal | Creatinine | `220615` Creatinine (serum) |
# MAGIC
# MAGIC These are items charted in the ICU, coded with the MIMIC-IV `d_items` code system. The `forEach` selects only the codings for these items, so other observations produce no rows.
# MAGIC
# MAGIC The `value` column is given the `ansi/type` tag `DOUBLE PRECISION`, so that SQL can do arithmetic with it.

# COMMAND ----------

SOFA_ITEMS = [
    "220224",
    "223835",
    "227457",
    "225690",
    "220052",
    "220181",
    "220739",
    "223900",
    "223901",
    "220615",
]

sofa_observations = data.view(
    "Observation",
    select=[
        {
            "column": [
                {
                    "description": "Patient ID",
                    "path": "subject.getReferenceKey()",
                    "name": "patient_id",
                },
                {
                    "description": "Time the observation was charted",
                    "path": "effective.ofType(dateTime)",
                    "name": "charted_time",
                    "type": "dateTime",
                    "tag": [{"name": "ansi/type", "value": "TIMESTAMP"}],
                },
                {
                    "description": "Value",
                    "path": "value.ofType(Quantity).value",
                    "name": "value",
                    "type": "decimal",
                    "tag": [{"name": "ansi/type", "value": "DOUBLE PRECISION"}],
                },
            ],
            "select": [
                {
                    "forEach": f"code.coding.where(system = '{ICU_ITEMS}'"
                    f" and code in ({' | '.join(repr(i) for i in SOFA_ITEMS)}))",
                    "column": [
                        {
                            "description": "MIMIC-IV item ID",
                            "path": "code",
                            "name": "item_id",
                        },
                        {
                            "description": "Item label",
                            "path": "display",
                            "name": "label",
                        },
                    ],
                }
            ],
        }
    ],
    where=[{"path": "value.ofType(Quantity).value.exists()"}],
)
save_view(sofa_observations, "sofa_observation_view")
sofa_observations.show(5, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC Not every patient has every measurement. Bilirubin and arterial blood gases are only measured when there is a clinical reason, which is why a component with no measurement is scored as normal.

# COMMAND ----------

coverage = pc.spark.sql(f"""
    SELECT label, COUNT(DISTINCT patient_id) AS patients
    FROM {VIEWS_SCHEMA}.sofa_observation_view
    GROUP BY label
    ORDER BY patients
""").toPandas()

fig, ax = plt.subplots()
ax.barh(coverage.label, coverage.patients, color="#7f8c8d")
for i, n in enumerate(coverage.patients):
    ax.text(n + 1, i, str(n), va="center")
ax.set_xlim(0, 110)
ax.set_title("Patients with each SOFA measurement")
ax.set_xlabel("Patients (of 100)")
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Vasoactive view
# MAGIC
# MAGIC One row per infusion of a vasoactive drug, with its rate. The SOFA cardiovascular component is scored from the rates of norepinephrine, epinephrine, dopamine and dobutamine, in micrograms per kilogram per minute. Septic shock is defined by norepinephrine or vasopressin. Vasopressin is charted in units per hour, and only its start time is used.
# MAGIC
# MAGIC | Drug | MIMIC-IV item |
# MAGIC | --- | --- |
# MAGIC | Norepinephrine | `221906` |
# MAGIC | Epinephrine | `221289` |
# MAGIC | Dopamine | `221662` |
# MAGIC | Dobutamine | `221653` |
# MAGIC | Vasopressin | `222315` |
# MAGIC
# MAGIC The rate is a choice element (`rate[x]`), so `ofType(Quantity)` selects the rate given as a quantity.

# COMMAND ----------

VASOACTIVE_ITEMS = ["221906", "221289", "221662", "221653", "222315"]

vasoactives = data.view(
    "MedicationAdministration",
    select=[
        {
            "column": [
                {
                    "description": "Patient ID",
                    "path": "subject.getReferenceKey()",
                    "name": "patient_id",
                },
                {
                    "description": "Time the infusion started",
                    "path": "effective.ofType(dateTime) | effective.ofType(Period).start",
                    "name": "start_time",
                    "type": "dateTime",
                    "tag": [{"name": "ansi/type", "value": "TIMESTAMP"}],
                },
                {
                    "description": "Infusion rate",
                    "path": "dosage.rate.ofType(Quantity).value",
                    "name": "rate",
                    "type": "decimal",
                    "tag": [{"name": "ansi/type", "value": "DOUBLE PRECISION"}],
                },
                {
                    "description": "Unit of the infusion rate",
                    "path": "dosage.rate.ofType(Quantity).unit",
                    "name": "rate_unit",
                },
            ],
            "select": [
                {
                    "forEach": f"medication.ofType(CodeableConcept).coding"
                    f".where(system = '{ICU_MEDICATIONS}'"
                    f" and code in ({' | '.join(repr(i) for i in VASOACTIVE_ITEMS)}))",
                    "column": [
                        {
                            "description": "MIMIC-IV item ID",
                            "path": "code",
                            "name": "item_id",
                        },
                        {
                            "description": "Drug",
                            "path": "display",
                            "name": "drug",
                        },
                    ],
                }
            ],
        }
    ],
)
save_view(vasoactives, "vasoactive_view")
vasoactives.show(5, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Beta-blocker view
# MAGIC
# MAGIC One row per dose of esmolol, metoprolol or labetalol. MIMIC-IV records medicines in two systems, and FHIR keeps the code system of each:
# MAGIC
# MAGIC - The ICU bedside system codes intravenous doses with `d_items` item IDs (`mimic-medication-icu`).
# MAGIC - The hospital's electronic medication administration record (eMAR) codes most doses with the pharmacy's formulary code (`mimic-medication-formulary-drug-cd`), and some with the medicine's name (`mimic-medication-name`). Oral metoprolol, the most common beta-blocker, is recorded only here. `TOPR` is Toprol XL, a brand of metoprolol succinate.
# MAGIC
# MAGIC The lists below hold every matching code in the [MIMIC-IV on FHIR code systems](https://kind-lab.github.io/mimic-fhir/), following the list in [the thesis this study is taken from](https://github.com/fhnaumann/master_thesis_pipeline/blob/main/langgraph-orchestration/dataset/case_002/notes.md). The trial's placebo is recorded under names such as `Esmolol Study Control (0.9% NaCl)`, which are left out. The `forEach` keeps only the codings that match one of the three lists.

# COMMAND ----------

BETA_BLOCKER_ICU_ITEMS = [
    "221429",  # Esmolol
    "225974",  # Metoprolol
    "225153",  # Labetalol
]
BETA_BLOCKER_FORMULARY_CODES = [
    "ESMO100I",
    "ESMO2.5PM",
    "ESMO2IND",
    "ESMO2PM",
    "ESMOB100",
    "ESMOBASE",
    "ESMOIND",
    "LABE100",
    "LABE100I",
    "LABE1200/400",
    "LABE200",
    "LABE600/200",
    "LABE600/200NS",
    "METO10",
    "METO10I",
    "METO10L",
    "METO10PB",
    "METO12.5HT",
    "METO1L",
    "METO25",
    "METO37.5",
    "METO5",
    "METO50",
    "METO50I",
    "METO5I",
    "METOSUSP",
    "METOSUSP10L",
    "TOPR100",
    "TOPR25",
    "TOPR50",
]
BETA_BLOCKER_NAMES = [
    "Dutoprol",
    "Esmolol",
    "esmolol",
    "Esmolol 2000mg/100mL 100mL Bag",
    "Esmolol Study Drug",
    "Esmolol study drug",
    "esmolol study drug",
    "Labet",
    "Labetalol",
    "laBETalol",
    "Labetalol 100mg/20mL 20mL VIAL",
    "Metoprol",
    "Metoprolo",
    "Metoprolol",
    "metoprolol",
    "Metoprolol Succinate",
    "meTOPROLOL succinate",
    "metoprolol succinate",
    "Metoprolol Succinate XL",
    "Metoprolol Tart 5mg/5mL 5mL VIAL",
    "Metoprolol Tartra 12.5mg HALFTAB",
    "Metoprolol Tartrate",
    "metoprolol tartrate",
    "Metoprolol Tartrate Suspension",
    "Metoprolol XL (Toprol XL)",
    "toprol",
    "Toprol XL",
]


def in_list(system: str, codes: list[str]) -> str:
    """Build a FHIRPath criterion matching a coding against a list of codes.

    :param system: The code system URI that the coding must have.
    :param codes: The codes, any of which the coding may have.
    :returns: A FHIRPath boolean expression, evaluated against a Coding.
    """
    return f"(system = '{system}' and code in ({' | '.join(repr(c) for c in codes)}))"


beta_blockers = data.view(
    "MedicationAdministration",
    select=[
        {
            "column": [
                {
                    "description": "Patient ID",
                    "path": "subject.getReferenceKey()",
                    "name": "patient_id",
                },
                {
                    "description": "Time the administration started",
                    "path": "effective.ofType(dateTime) | effective.ofType(Period).start",
                    "name": "start_time",
                    "type": "dateTime",
                    "tag": [{"name": "ansi/type", "value": "TIMESTAMP"}],
                },
            ],
            "select": [
                {
                    "forEach": "medication.ofType(CodeableConcept).coding.where("
                    + " or ".join(
                        [
                            in_list(ICU_MEDICATIONS, BETA_BLOCKER_ICU_ITEMS),
                            in_list(FORMULARY_CODES, BETA_BLOCKER_FORMULARY_CODES),
                            in_list(MEDICATION_NAMES, BETA_BLOCKER_NAMES),
                        ]
                    )
                    + ")",
                    "column": [
                        {
                            "description": "Code system",
                            "path": "system",
                            "name": "system",
                        },
                        {
                            "description": "Code",
                            "path": "code",
                            "name": "code",
                        },
                    ],
                }
            ],
        }
    ],
)
save_view(beta_blockers, "beta_blocker_view")
beta_blockers.show(5, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC Counting the patients who received a beta-blocker in each record shows why both are needed. A query that looked only at the ICU record would miss the patients who were given oral metoprolol.

# COMMAND ----------

by_source = pc.spark.sql(f"""
    SELECT IF(system = '{ICU_MEDICATIONS}', 'ICU record', 'eMAR') AS source,
           COUNT(*) AS doses,
           COUNT(DISTINCT patient_id) AS patients
    FROM {VIEWS_SCHEMA}.beta_blocker_view
    GROUP BY 1
    UNION ALL
    SELECT 'Either', COUNT(*), COUNT(DISTINCT patient_id)
    FROM {VIEWS_SCHEMA}.beta_blocker_view
""").toPandas()

fig, (left, right) = plt.subplots(1, 2, figsize=(12, 3.5))
for ax, column in [(left, "doses"), (right, "patients")]:
    ax.barh(by_source.source, by_source[column], color="#3a9d5d")
    for i, n in enumerate(by_source[column]):
        ax.text(n, i, f" {n}", va="center")
    ax.set_title(f"Beta-blocker {column}")
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC # Combine the views
# MAGIC
# MAGIC `sql/mimic_iv/combine_beta_blocker_septic_shock_views.sql` holds two statements:
# MAGIC
# MAGIC 1. A view, `beta_blocker_septic_shock`, with one row per patient describing their first ICU stay. It is built as a chain of common table expressions, one for each step of the cohort definition, and each criterion becomes a column. `in_cohort` is true for the patients who meet them all.
# MAGIC 2. A summary query, giving the 28-day mortality of each group in the cohort.
# MAGIC
# MAGIC The SOFA score is the worst value of each measurement from 48 hours before to 24 hours after the suspected infection, following [Seymour et al. (2016)](https://doi.org/10.1001/jama.2016.0288). It is simplified in four ways:
# MAGIC
# MAGIC - The respiratory component is scored on the PaO2 / FiO2 ratio alone, without checking for mechanical ventilation.
# MAGIC - The renal component uses creatinine but not urine output.
# MAGIC - Vasopressor rates are taken from the start of each administration record. MIMIC-IV starts a new record whenever the rate changes, so this sees most rate changes.
# MAGIC - The Glasgow Coma Scale is summed as charted. Intubated patients cannot speak, and MIMIC-IV charts their verbal response as 1, the lowest score, so their central nervous system component may be overstated.
# MAGIC
# MAGIC For acute heart failure, the query uses the ICD codes for acute and acute on chronic heart failure. It does not use the unspecified code `428.0` (congestive heart failure, unspecified), which is the most common heart failure code in the data and would exclude many patients with chronic heart failure.
# MAGIC
# MAGIC You can also run the file in the Databricks SQL editor. Here we read it from the repository, create the view, and keep the summary query for the Results section.

# COMMAND ----------

with open("../../sql/mimic_iv/combine_beta_blocker_septic_shock_views.sql") as f:
    create_view_sql, summary_sql = [
        statement for statement in f.read().split(";\n") if statement.strip()
    ]

pc.spark.sql(create_view_sql)
patients_first_stay = pc.spark.table(
    f"{VIEWS_SCHEMA}.beta_blocker_septic_shock"
).toPandas()
cohort = patients_first_stay[patients_first_stay.in_cohort].copy()
cohort["group"] = cohort.beta_blocker.map(
    {True: "Beta-blocker", False: "No beta-blocker"}
)
# A label for each patient in the charts, e.g. "Beta-blocker  74 F".
cohort["label"] = (
    cohort.group
    + "  "
    + cohort.age.astype(int).astype(str)
    + " "
    + cohort.gender.str[0].str.upper()
)
display(cohort)

# COMMAND ----------

# MAGIC %md
# MAGIC # Results
# MAGIC
# MAGIC ## Who is left after each step?
# MAGIC
# MAGIC Each criterion is a column of the view, so the number of patients remaining after each step is a running conjunction of the columns.

# COMMAND ----------

p = patients_first_stay
contraindicated = p.av_block | p.acute_mi | p.acute_heart_failure | p.asthma
steps = [
    ("First ICU stay", pd.Series(True, index=p.index)),
    ("Aged 18 or over", p.adult),
    ("ICU stay of 48 hours or more", p.stay_48_hours),
    ("Suspected infection", p.suspected_infection_time.notna()),
    ("Sepsis (SOFA 2 or more)", p.sepsis_time.notna()),
    ("Septic shock (vasopressor)", p.baseline_time.notna()),
    ("No contraindication", ~contraindicated),
]
remaining = []
mask = pd.Series(True, index=p.index)
for label, criterion in steps:
    mask &= criterion
    remaining.append((label, int(mask.sum())))

fig, ax = plt.subplots(figsize=(10, 4))
labels = [label for label, _ in remaining][::-1]
counts = [n for _, n in remaining][::-1]
ax.barh(labels, counts, color=["#3a9d5d"] + ["#7f8c8d"] * (len(counts) - 1))
for i, n in enumerate(counts):
    ax.text(n + 1, i, str(n), va="center")
ax.set_xlim(0, 110)
ax.set_title("Patients remaining after each step of the cohort definition")
ax.set_xlabel("Patients")
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC Of the patients with septic shock, these are the contraindications that excluded them. A patient can have more than one.

# COMMAND ----------

shock = p[p.adult & p.stay_48_hours & p.baseline_time.notna()]
reasons = pd.Series(
    {
        "Complete heart block": shock.av_block.sum(),
        "Acute myocardial infarction": shock.acute_mi.sum(),
        "Acute heart failure": shock.acute_heart_failure.sum(),
        "Asthma": shock.asthma.sum(),
    }
).sort_values()

fig, ax = plt.subplots(figsize=(8, 3))
ax.barh(reasons.index, reasons.values, color="#c0392b")
for i, n in enumerate(reasons.values):
    ax.text(n + 0.1, i, str(n), va="center")
ax.set_title(f"Contraindications among the {len(shock)} patients with septic shock")
ax.set_xlabel("Patients")
ax.xaxis.get_major_locator().set_params(integer=True)
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## How sick were they?
# MAGIC
# MAGIC The SOFA score of each patient in the cohort at the onset of sepsis, broken down by component. The cardiovascular component scores 4 for every patient in the demo cohort, because of the vasopressors that make them eligible.

# COMMAND ----------

components = {
    "sofa_respiration": ("Respiration", "#1b6ca8"),
    "sofa_coagulation": ("Coagulation", "#e07b39"),
    "sofa_liver": ("Liver", "#8e6c8a"),
    "sofa_cardiovascular": ("Cardiovascular", "#c0392b"),
    "sofa_cns": ("Central nervous system", "#3a9d5d"),
    "sofa_renal": ("Renal", "#d4a017"),
}
ordered = cohort.sort_values(["group", "sofa"]).reset_index(drop=True)
fig, ax = plt.subplots(figsize=(10, 0.4 * len(ordered) + 1.5))
left = pd.Series(0, index=ordered.index)
for column, (label, colour) in components.items():
    ax.barh(ordered.index, ordered[column], left=left, color=colour, label=label)
    left += ordered[column]
ax.set_yticks(ordered.index, ordered.label)
ax.invert_yaxis()
ax.set_xlim(0, 24)
ax.set_xlabel("SOFA score (maximum 24)")
ax.set_title("SOFA score at the onset of sepsis")
ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1, 1))
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## What happened to each patient?
# MAGIC
# MAGIC A timeline for each patient in the cohort, in days from the baseline (the first vasopressor). The shaded band is the 48-hour window in which a beta-blocker assigns a patient to the beta-blocker group. Several patients in the control group were given beta-blockers later in their stay: the groups are defined by what happened in the first 48 hours, not by whether a patient was ever treated.

# COMMAND ----------


def days_since(times: pd.Series, baseline: pd.Series) -> pd.Series:
    """Convert timestamps to days since a baseline.

    :param times: Timestamps.
    :param baseline: The baseline for each timestamp, aligned with `times`.
    :returns: The number of days from the baseline to each timestamp.
    """
    return (times - baseline).dt.total_seconds() / 86400


# One row per patient, from top to bottom of the chart.
timeline = cohort.sort_values(["group", "baseline_time"]).reset_index(drop=True)
for column in ["admit_time", "discharge_time", "sepsis_time", "deceased"]:
    timeline[f"{column}_day"] = days_since(timeline[column], timeline.baseline_time)
died = timeline[timeline.died_within_28_days]

# Every beta-blocker dose given to a patient in the cohort.
doses = (
    pc.spark.table(f"{VIEWS_SCHEMA}.beta_blocker_view")
    .toPandas()
    .merge(timeline.reset_index(names="row")[["row", "patient_id", "baseline_time"]])
)
doses["day"] = days_since(doses.start_time, doses.baseline_time)

fig, ax = plt.subplots(figsize=(11, 0.5 * len(timeline) + 1.5))
ax.axvspan(0, 2, color="#3a9d5d", alpha=0.12)
ax.hlines(
    timeline.index,
    timeline.admit_time_day,
    timeline.discharge_time_day,
    colors=timeline.group.map(GROUP_COLOURS),
    linewidth=6,
    alpha=0.35,
)
ax.plot(timeline.sepsis_time_day, timeline.index, "o", color="#e07b39", markersize=7)
ax.plot(doses.day, doses.row, "|", color="#3a9d5d", markersize=12, markeredgewidth=2)
ax.plot(died.deceased_day, died.index, "X", color="black", markersize=9)
ax.axvline(0, color="#c0392b", linewidth=1)
ax.set_yticks(timeline.index, timeline.label)
ax.invert_yaxis()
ax.set_xlim(-3, 28)
ax.set_xlabel("Days from first vasopressor")
ax.set_title("Timeline of each patient in the cohort")
handles = [
    plt.Line2D([], [], color="#7f8c8d", linewidth=6, alpha=0.35, label="ICU stay"),
    plt.Line2D(
        [], [], color="#e07b39", marker="o", linestyle="", label="Onset of sepsis"
    ),
    plt.Line2D([], [], color="#c0392b", linewidth=1, label="First vasopressor"),
    plt.Line2D(
        [],
        [],
        color="#3a9d5d",
        marker="|",
        markersize=12,
        markeredgewidth=2,
        linestyle="",
        label="Beta-blocker dose",
    ),
    plt.Line2D([], [], color="black", marker="X", linestyle="", label="Death"),
]
ax.legend(handles=handles, frameon=False, loc="upper left", bbox_to_anchor=(1, 1))
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## How do the groups compare?
# MAGIC
# MAGIC Baseline characteristics of the two groups, alongside those reported by Zhang et al. before propensity score matching.

# COMMAND ----------

baseline = cohort.groupby("group").agg(
    patients=("patient_id", "count"),
    median_age=("age", "median"),
    male_percent=("gender", lambda g: round(100 * (g == "male").mean(), 1)),
    median_sofa=("sofa", "median"),
)
baseline["zhang_patients"] = baseline.index.map(
    {"Beta-blocker": 621, "No beta-blocker": 4239}
)
baseline["zhang_median_age"] = baseline.index.map(
    {"Beta-blocker": 72.4, "No beta-blocker": 67.3}
)
baseline["zhang_male_percent"] = baseline.index.map(
    {"Beta-blocker": 56.8, "No beta-blocker": 56.6}
)
display(baseline.reset_index())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Did beta-blockers make a difference?
# MAGIC
# MAGIC The 28-day mortality of each group, from the summary query in the SQL file, against the figures Zhang et al. reported after propensity score matching. With a handful of patients in each group, one death more or less moves the percentage by 10 points or more, so no conclusion can be drawn from the demo data. The comparison is also unadjusted: patients who were given a beta-blocker may have differed from the others in ways that affect survival.

# COMMAND ----------

summary = pc.spark.sql(summary_sql).toPandas()
display(summary)

# COMMAND ----------

zhang = {"Beta-blocker": 21.5, "No beta-blocker": 27.1}
groups = list(GROUP_COLOURS)
by_group = summary.set_index("treatment_group").reindex(groups)

fig, ax = plt.subplots(figsize=(8, 4.5))
x = range(len(groups))
ax.bar(
    [i - 0.2 for i in x],
    by_group.mortality_percent,
    width=0.4,
    color=[GROUP_COLOURS[g] for g in groups],
    label="MIMIC-IV demo",
)
ax.bar(
    [i + 0.2 for i in x],
    [zhang[g] for g in groups],
    width=0.4,
    color="#c8cdd2",
    label="Zhang et al. 2024, after matching",
)
for i, g in enumerate(groups):
    ax.text(
        i - 0.2,
        by_group.mortality_percent[g] + 1,
        f"{by_group.deaths[g]} of {by_group.patients[g]}",
        ha="center",
    )
    ax.text(i + 0.2, zhang[g] + 1, f"{zhang[g]}%", ha="center", color="#555")
ax.set_xticks(list(x), groups)
ax.set_ylim(0, 100)
ax.set_ylabel("Died within 28 days (%)")
ax.set_title("28-day mortality")
ax.legend(frameon=False)
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC The same outcome as survival curves: the percentage of each group alive on each day after the baseline. Every patient is followed for the full 28 days, because MIMIC-IV records deaths up to a year after discharge, so no censoring is needed.

# COMMAND ----------

died_day = days_since(cohort.deceased, cohort.baseline_time).where(
    cohort.died_within_28_days
)
days = [d / 4 for d in range(28 * 4 + 1)]

fig, ax = plt.subplots()
for group, colour in GROUP_COLOURS.items():
    members = cohort.group == group
    alive = [100 * (1 - (died_day[members] <= d).sum() / members.sum()) for d in days]
    ax.step(days, alive, where="post", color=colour, label=f"{group} ({members.sum()})")
ax.set_xlim(0, 28)
ax.set_ylim(0, 105)
ax.set_xlabel("Days from first vasopressor")
ax.set_ylabel("Alive (%)")
ax.set_title("28-day survival")
ax.legend(frameon=False, loc="lower left")
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Going further
# MAGIC
# MAGIC Zhang et al. went further than this notebook in ways that you could try:
# MAGIC
# MAGIC - They balanced the groups with propensity score matching on age, sex, weight, SOFA, SAPS II, the Charlson comorbidity index, heart disease and atrial arrhythmia. Each of these can be added as a column with another view and another common table expression.
# MAGIC - They looked for subgroups that benefit most, and found that patients with heart disease or atrial arrhythmias did. Both can be identified from `diagnosis_view`.
# MAGIC - Their secondary outcomes included length of stay and days free of ventilation, vasopressors and renal replacement therapy within 28 days.
