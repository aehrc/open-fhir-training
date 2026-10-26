# Databricks notebook source
# MAGIC %md
# MAGIC # Secondary prevention after myocardial infarction
# MAGIC
# MAGIC After a myocardial infarction (MI), guidelines recommend four classes of medicine to prevent another cardiovascular event: an antiplatelet, a statin, a beta-blocker, and an angiotensin-converting enzyme (ACE) inhibitor or angiotensin receptor blocker (ARB). [Halvorsen et al. (2016)](https://pubmed.ncbi.nlm.nih.gov/27246583/) followed 42,707 patients in Norway after an acute MI, and found that 91% were discharged on antiplatelet therapy, 90% on a statin, 82% on a beta-blocker and 60% on an ACE inhibitor or ARB.
# MAGIC
# MAGIC This notebook asks the same question of an Australian [Synthea](https://synthetichealth.github.io/synthea/) dataset: of the patients who had an MI, how many were prescribed each class of medicine afterwards?
# MAGIC
# MAGIC It builds on the prostate cancer notebook in three ways:
# MAGIC
# MAGIC - It extracts data from [MedicationRequest](https://hl7.org/fhir/R4/medicationrequest.html) resources, whose medicines are coded with the [Australian Medicines Terminology](https://www.healthterminologies.gov.au/) (AMT).
# MAGIC - It classifies those medicines using a FHIR [ConceptMap](https://hl7.org/fhir/R4/conceptmap.html), through [Terminology in SQL](https://build.fhir.org/ig/HL7/sql-on-fhir/en/terminology-in-sql.html). The ConceptMap is presented to SQL as an ordinary table that queries join to, rather than as a list of codes written into the query.
# MAGIC - The ConceptMap is read from a [local terminology store](https://pathling.csiro.au/docs/libraries/terminology/local), so no terminology server is needed.
# MAGIC
# MAGIC The notebook creates three views and a table of the ConceptMap's mappings, then runs `sql/synthea/combine_mi_secondary_prevention_views.sql` to combine them.

# COMMAND ----------

# Author: John Grimes

import matplotlib.pyplot as plt
import pandas as pd
from pathling import PathlingContext

TERMINOLOGY_STORE = "s3://open-fhir-training-data/terminology/tx-store"
PRODUCT_TO_CLASS = "https://example.org/amt-extended-91b6e2c4/ConceptMap/product-to-classification|0.1.0"
VIEWS_SCHEMA = "synthea_mi_secondary_prevention_views"

# Colours used for the four drug classes in every chart.
CLASS_COLOURS = {
    "Antiplatelet": "#1b6ca8",
    "Statin": "#e07b39",
    "Beta-blocker": "#3a9d5d",
    "ACE inhibitor or ARB": "#b8336a",
}
DRUG_CLASSES = list(CLASS_COLOURS)

# The column of the combined view that holds the days to the first prescription of each class.
DAY_COLUMNS = {
    "Antiplatelet": "days_to_antiplatelet",
    "Statin": "days_to_statin",
    "Beta-blocker": "days_to_beta_blocker",
    "ACE inhibitor or ARB": "days_to_ace_inhibitor_or_arb",
}

plt.rcParams.update(
    {
        "figure.figsize": (10, 4.5),
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titleweight": "bold",
    }
)

# COMMAND ----------

# MAGIC %md
# MAGIC The follow-up window is the number of days after the MI within which a prescription counts as treatment. Change it in the widget at the top of the notebook and re-run the results section to see its effect.

# COMMAND ----------

dbutils.widgets.text("follow_up_days", "365", "Follow-up window (days)")
follow_up_days = int(dbutils.widgets.get("follow_up_days"))

# COMMAND ----------

# MAGIC %md
# MAGIC We initialise the Pathling context in local terminology mode, pointing at the terminology store built by the `notebooks/terminology/import_amt_classification` notebook.

# COMMAND ----------

pc = PathlingContext.create(
    terminology_mode="local",
    terminology_storage_path=TERMINOLOGY_STORE,
)
pc.spark.sql("CREATE SCHEMA IF NOT EXISTS synthea")
pc.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {VIEWS_SCHEMA}")
pc.spark.catalog.setCurrentDatabase("synthea")

# COMMAND ----------

# MAGIC %md
# MAGIC # Read data from tables
# MAGIC
# MAGIC The data is the Australian Synthea dataset imported by the `import_synthea` notebook. It was generated with [synthea-au-core](https://github.com/aehrc/synthea-au-core) and conforms to [AU Core](https://build.fhir.org/ig/hl7au/au-fhir-core/) profiles.

# COMMAND ----------

data = pc.read.tables()
data.read("Patient").count()

# COMMAND ----------

data.read("MedicationRequest").count()

# COMMAND ----------

# MAGIC %md
# MAGIC # Views
# MAGIC
# MAGIC We will create three views with [view definitions](https://build.fhir.org/ig/FHIR/sql-on-fhir-v2/StructureDefinition-ViewDefinition.html):
# MAGIC
# MAGIC - Patient demographics
# MAGIC - Myocardial infarction diagnoses
# MAGIC - Medication requests
# MAGIC
# MAGIC None of the views knows anything about drug classes. The medication request view keeps every coded medicine, and the classification is done later in SQL, by joining to the ConceptMap.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Patient demographic view
# MAGIC
# MAGIC One row per patient, with their gender, birth date and date of death. `getResourceKey()` gives an identifier that matches the `getReferenceKey()` of a reference to the patient, so the views can be joined.

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
                    "description": "Administrative gender",
                    "path": "gender",
                    "name": "gender",
                },
                {
                    "description": "Birth date",
                    "path": "birthDate",
                    "name": "birth_date",
                },
                {
                    "description": "Date and time of death",
                    "path": "deceased.ofType(dateTime)",
                    "name": "deceased",
                },
            ]
        },
    ],
)

# COMMAND ----------

patients.show(10, truncate=False)

# COMMAND ----------

patients.write.saveAsTable(f"{VIEWS_SCHEMA}.patient_view", mode="overwrite")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Myocardial infarction view
# MAGIC
# MAGIC One row per Condition coded as a myocardial infarction, with its SNOMED CT code, display and onset. The data uses three SNOMED CT codes:
# MAGIC
# MAGIC - `22298006` Myocardial infarction
# MAGIC - `401303003` Acute ST segment elevation myocardial infarction
# MAGIC - `401314000` Acute non-ST segment elevation myocardial infarction
# MAGIC
# MAGIC Rather than a separate `where` clause, the `forEach` iterates over only the codings that match. A Condition with no matching coding produces no rows, so it is left out of the view.

# COMMAND ----------

mi_diagnoses = data.view(
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
                    "description": "Date and time of onset",
                    "path": "onset.ofType(dateTime)",
                    "name": "onset",
                },
            ],
            "select": [
                {
                    "forEach": "code.coding.where(system = 'http://snomed.info/sct'"
                    " and (code = '22298006' or code = '401303003'"
                    " or code = '401314000'))",
                    "column": [
                        {
                            "description": "SNOMED CT code",
                            "path": "code",
                            "name": "code",
                        },
                        {
                            "description": "SNOMED CT display",
                            "path": "display",
                            "name": "display",
                        },
                    ],
                }
            ],
        }
    ],
)

# COMMAND ----------

mi_diagnoses.show(10, truncate=False)

# COMMAND ----------

mi_diagnoses.write.saveAsTable(
    f"{VIEWS_SCHEMA}.myocardial_infarction_view", mode="overwrite"
)

# COMMAND ----------

# MAGIC %md
# MAGIC Some patients have more than one MI. The analysis will take each patient's first MI as their index event. Here is when those index events happened, and which type of MI they were. Note that from 2017 onwards, every first MI in this dataset is coded with the general concept `22298006 |Myocardial infarction|` rather than as a STEMI or NSTEMI. Coding practice can change over time, which is one reason to define a cohort with all of the relevant codes.

# COMMAND ----------

first_mi = (
    pc.spark.sql(f"""
        SELECT patient_id, display, CAST(onset AS DATE) AS onset_date
        FROM {VIEWS_SCHEMA}.myocardial_infarction_view
        QUALIFY ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY onset, id) = 1
    """)
    .toPandas()
    .assign(year=lambda df: pd.to_datetime(df.onset_date).dt.year)
)
by_year = first_mi.pivot_table(
    index="year", columns="display", values="patient_id", aggfunc="count", fill_value=0
)
ax = by_year.plot.bar(stacked=True, width=0.8, color=["#7f8c8d", "#c0392b", "#2980b9"])
ax.set_title(f"First myocardial infarction by year ({len(first_mi)} patients)")
ax.set_xlabel("Year of first MI")
ax.set_ylabel("Patients")
ax.legend(title=None, frameon=False)
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Medication request view
# MAGIC
# MAGIC One row per MedicationRequest with an AMT code, with the date it was written and its status. AMT is distributed as part of SNOMED CT-AU, so its codes use the SNOMED CT system URI.
# MAGIC
# MAGIC The medicine is a choice element (`medication[x]`), so `ofType(CodeableConcept)` selects the coded form. A handful of requests in the data name a medicine in text without a code; the `forEach` leaves them out, as they cannot be classified.

# COMMAND ----------

medication_requests = data.view(
    "MedicationRequest",
    select=[
        {
            "column": [
                {
                    "description": "MedicationRequest ID",
                    "path": "getResourceKey()",
                    "name": "id",
                },
                {
                    "description": "Patient ID",
                    "path": "subject.getReferenceKey()",
                    "name": "patient_id",
                },
                {
                    "description": "Date and time the request was written",
                    "path": "authoredOn",
                    "name": "authored_on",
                },
                {
                    "description": "Request status",
                    "path": "status",
                    "name": "status",
                },
            ],
            "select": [
                {
                    "forEach": "medication.ofType(CodeableConcept).coding"
                    ".where(system = 'http://snomed.info/sct')",
                    "column": [
                        {
                            "description": "AMT code",
                            "path": "code",
                            "name": "code",
                        },
                        {
                            "description": "AMT display",
                            "path": "display",
                            "name": "display",
                        },
                    ],
                }
            ],
        }
    ],
)

# COMMAND ----------

medication_requests.show(10, truncate=False)

# COMMAND ----------

medication_requests.write.saveAsTable(
    f"{VIEWS_SCHEMA}.medication_request_view", mode="overwrite"
)

# COMMAND ----------

# MAGIC %md
# MAGIC # Terminology in SQL
# MAGIC
# MAGIC The ConceptMap relates each AMT product to the classes of substance it contains, using SNOMED CT concepts as the classes. For example, `Atenolol 100 mg tablet` is related to `373254001 |Beta blocker|`, and also to broader classes such as `372586001 |Antihypertensive agent|`.
# MAGIC
# MAGIC `concept_map()` returns the map as a table with the columns defined by the SQL on FHIR specification: one row per mapping, with `source_system`, `source_code` and `source_display`, `target_system`, `target_code` and `target_display`, and a `relationship`. Every mapping in this map is `related-to`. The map holds 925,540 mappings, more than the default limit of 100,000, so we raise the limit.
# MAGIC
# MAGIC We save the table alongside the views, so that the SQL file can join to it under the name `product_to_class`.

# COMMAND ----------

product_to_class = pc.concept_map(PRODUCT_TO_CLASS, max_mappings=1_000_000)
product_to_class.show(5, truncate=False)

# COMMAND ----------

product_to_class.write.saveAsTable(f"{VIEWS_SCHEMA}.product_to_class", mode="overwrite")

# COMMAND ----------

# MAGIC %md
# MAGIC Before we use the map, let's see what it says about the medicines in our data. First, how many of the medication requests have a product that the map classifies?

# COMMAND ----------

pc.spark.sql(f"""
    WITH mapped AS (
      SELECT DISTINCT source_code AS code
      FROM {VIEWS_SCHEMA}.product_to_class
      WHERE source_system = 'http://snomed.info/sct'
    )
    SELECT COUNT(*) AS requests,
           COUNT(m.code) AS classified,
           ROUND(100 * COUNT(m.code) / COUNT(*), 1) AS percent_classified
    FROM {VIEWS_SCHEMA}.medication_request_view r
    LEFT JOIN mapped m ON m.code = r.code
""").show()

# COMMAND ----------

# MAGIC %md
# MAGIC Joining the medication request view to the map gives every class that each prescribed product belongs to. A product usually belongs to several classes at different levels, e.g. `Atenolol 100 mg tablet` is a beta blocker, an antihypertensive agent and an autonomic agent. These are the 20 classes with the most patients among the prescriptions written to patients on or after their first MI.

# COMMAND ----------

classes_after_mi = pc.spark.sql(f"""
    WITH first_mi AS (
      SELECT patient_id, MIN(CAST(onset AS DATE)) AS index_date
      FROM {VIEWS_SCHEMA}.myocardial_infarction_view
      GROUP BY patient_id
    )
    SELECT m.target_code, m.target_display, COUNT(DISTINCT r.patient_id) AS patients
    FROM {VIEWS_SCHEMA}.medication_request_view r
    JOIN first_mi f
      ON f.patient_id = r.patient_id
     AND CAST(r.authored_on AS DATE) >= f.index_date
    JOIN {VIEWS_SCHEMA}.product_to_class m
      ON m.source_system = 'http://snomed.info/sct'
     AND m.source_code = r.code
     AND m.relationship = 'related-to'
    GROUP BY m.target_code, m.target_display
    ORDER BY patients DESC
    LIMIT 20
""").toPandas()

highlighted = {"771452004", "372912004", "373254001", "372733002", "372913009"}
colours = [
    "#1b6ca8" if code in highlighted else "#c8cdd2"
    for code in classes_after_mi["target_code"]
]
ax = classes_after_mi.iloc[::-1].plot.barh(
    x="target_display", y="patients", color=colours[::-1], legend=False, figsize=(10, 7)
)
ax.set_title("Classes prescribed on or after the first MI (top 20)")
ax.set_xlabel("Patients with an MI")
ax.set_ylabel(None)
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC The classes highlighted in blue are the ones we need. The SQL file assigns each of them to one of the four drug classes:
# MAGIC
# MAGIC | Drug class | SNOMED CT class |
# MAGIC |---|---|
# MAGIC | Antiplatelet | `771452004` Platelet aggregation inhibitor |
# MAGIC | Statin | `372912004` HMG-CoA reductase inhibitor |
# MAGIC | Beta-blocker | `373254001` Beta blocker |
# MAGIC | ACE inhibitor or ARB | `372733002` Angiotensin-converting enzyme inhibitor, `372913009` Angiotensin II receptor antagonist |
# MAGIC
# MAGIC Here are the products in each of those classes that were prescribed to patients who had an MI, with the number of those patients prescribed each one.

# COMMAND ----------

products_by_class = pc.spark.sql(f"""
    WITH drug_class (class_code, drug_class) AS (
      VALUES ('771452004', 'Antiplatelet'),
             ('372912004', 'Statin'),
             ('373254001', 'Beta-blocker'),
             ('372733002', 'ACE inhibitor or ARB'),
             ('372913009', 'ACE inhibitor or ARB')
    ),
    mi_patient AS (
      SELECT DISTINCT patient_id FROM {VIEWS_SCHEMA}.myocardial_infarction_view
    ),
    opioid AS (
      -- Products that the map also relates to Opioid receptor agonist.
      SELECT DISTINCT source_code AS code
      FROM {VIEWS_SCHEMA}.product_to_class
      WHERE source_system = 'http://snomed.info/sct'
        AND relationship = 'related-to'
        AND target_code = '404642006'
    )
    SELECT d.drug_class,
           r.display AS product,
           COUNT(DISTINCT r.patient_id) AS patients,
           o.code IS NOT NULL AS also_opioid
    FROM {VIEWS_SCHEMA}.medication_request_view r
    JOIN mi_patient USING (patient_id)
    JOIN {VIEWS_SCHEMA}.product_to_class m
      ON m.source_system = 'http://snomed.info/sct'
     AND m.source_code = r.code
     AND m.relationship = 'related-to'
    JOIN drug_class d ON d.class_code = m.target_code
    LEFT JOIN opioid o ON o.code = r.code
    GROUP BY d.drug_class, r.display, r.code, o.code
""").toPandas()

fig, axes = plt.subplots(2, 2, figsize=(14, 8))
for ax, drug_class in zip(axes.flat, DRUG_CLASSES):
    rows = products_by_class[products_by_class["drug_class"] == drug_class].sort_values(
        "patients"
    )
    colours = [
        "#c0392b" if opioid else CLASS_COLOURS[drug_class]
        for opioid in rows["also_opioid"]
    ]
    ax.barh(rows["product"], rows["patients"], color=colours)
    ax.set_title(drug_class)
    ax.set_xlabel("Patients with an MI")
plt.suptitle(
    "Products prescribed to patients with an MI, by drug class", fontweight="bold"
)
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC Note the product in red. `Aspirin 325 mg + codeine phosphate hemihydrate 8 mg tablet` is an analgesic, but it contains aspirin, so the map relates it to `771452004 |Platelet aggregation inhibitor|`. It also relates it to `404642006 |Opioid receptor agonist|`, which is how the chart picks it out. This analysis uses the classes exactly as the map asserts them, so it counts as an antiplatelet. We will measure the effect of that choice at the end of the notebook.
# MAGIC
# MAGIC The chart counts prescriptions at any time, before or after the MI. The analysis below counts only those on or after it.

# COMMAND ----------

# MAGIC %md
# MAGIC # Combine the views
# MAGIC
# MAGIC `sql/synthea/combine_mi_secondary_prevention_views.sql` holds two statements:
# MAGIC
# MAGIC 1. A view, `mi_secondary_prevention`, with one row per patient with an MI. For each drug class it gives the number of days from the first MI to the first prescription of that class written on or after it. It is empty where the patient was never prescribed the class after their MI.
# MAGIC 2. A summary query, with the follow-up window as the parameter `:follow_up_days`. It gives the number and percentage of patients prescribed each class within the window, and the number prescribed all four.
# MAGIC
# MAGIC Keeping the days, rather than a yes or no for a fixed window, means that any window can be summarised from the same view. You can run the file in the Databricks SQL editor, which shows a box to enter the parameter. Here we read it from the repository and run it with the value of the widget.

# COMMAND ----------

with open("../../sql/synthea/combine_mi_secondary_prevention_views.sql") as f:
    create_view_sql, summary_sql = [
        statement for statement in f.read().split(";\n") if statement.strip()
    ]

pc.spark.sql(create_view_sql)
cohort = pc.spark.table(f"{VIEWS_SCHEMA}.mi_secondary_prevention").toPandas()
display(cohort.head(10))

# COMMAND ----------

summary = pc.spark.sql(summary_sql, args={"follow_up_days": follow_up_days}).toPandas()
display(summary)

# COMMAND ----------

# MAGIC %md
# MAGIC # Results
# MAGIC
# MAGIC ## Who is in the cohort?

# COMMAND ----------

fig, ax = plt.subplots()
cohort_genders = [("female", "#b8336a"), ("male", "#1b6ca8")]
ax.hist(
    [
        cohort[cohort["gender"] == gender]["age_at_index"]
        for gender, _ in cohort_genders
    ],
    bins=range(35, 95, 5),
    color=[colour for _, colour in cohort_genders],
    label=[
        f"{gender.title()} ({(cohort['gender'] == gender).sum()})"
        for gender, _ in cohort_genders
    ],
)
ax.set_title("Age at first myocardial infarction")
ax.set_xlabel("Age (years)")
ax.set_ylabel("Patients")
ax.legend(frameon=False)
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## How many were treated?
# MAGIC
# MAGIC The percentage of the cohort prescribed each class within the follow-up window, against the percentages that Halvorsen et al. reported at discharge. The comparison is loose: their figures are dispensings to patients under 85 who were discharged alive, ours are prescriptions written within the window.

# COMMAND ----------

halvorsen = {
    "Antiplatelet": 91,
    "Statin": 90,
    "Beta-blocker": 82,
    "ACE inhibitor or ARB": 60,
}
by_class = summary.set_index("drug_class").loc[DRUG_CLASSES]

fig, ax = plt.subplots()
x = range(len(DRUG_CLASSES))
ax.bar(
    [i - 0.2 for i in x],
    by_class.percent_treated,
    width=0.4,
    color=[CLASS_COLOURS[c] for c in DRUG_CLASSES],
    label=f"Synthea AU, within {follow_up_days} days",
)
ax.bar(
    [i + 0.2 for i in x],
    [halvorsen[c] for c in DRUG_CLASSES],
    width=0.4,
    color="#c8cdd2",
    label="Halvorsen et al. 2016, at discharge",
)
for i, c in enumerate(DRUG_CLASSES):
    ax.text(
        i - 0.2,
        by_class.percent_treated[c] + 1,
        f"{by_class.percent_treated[c]:.0f}%",
        ha="center",
    )
    ax.text(i + 0.2, halvorsen[c] + 1, f"{halvorsen[c]}%", ha="center", color="#555")
ax.set_xticks(list(x), DRUG_CLASSES)
ax.set_ylim(0, 105)
ax.set_ylabel("Patients treated (%)")
ax.set_title("Secondary prevention after myocardial infarction")
ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.1))
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## How quickly were they treated?
# MAGIC
# MAGIC The cumulative percentage of the cohort prescribed each class, by days since their MI. The dashed line is the follow-up window. Antiplatelets, statins and beta-blockers are almost all started within a few days of the MI; ACE inhibitors and ARBs are fewer and are started steadily over the following year.

# COMMAND ----------

days = range(731)
fig, ax = plt.subplots()
for drug_class in DRUG_CLASSES:
    column = cohort[DAY_COLUMNS[drug_class]]
    cumulative = [100 * (column <= d).sum() / len(cohort) for d in days]
    ax.step(
        days,
        cumulative,
        where="post",
        color=CLASS_COLOURS[drug_class],
        label=drug_class,
    )
ax.axvline(follow_up_days, color="#555", linestyle="--", linewidth=1)
ax.text(follow_up_days + 5, 3, f"{follow_up_days} days", color="#555")
ax.set_xlim(0, 730)
ax.set_ylim(0, 100)
ax.set_xlabel("Days since first MI")
ax.set_ylabel("Patients treated (%)")
ax.set_title("Time to first prescription of each class")
ax.legend(frameon=False, loc="center right")
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Which combinations did they receive?
# MAGIC
# MAGIC The number of the four classes each patient was prescribed within the window, and the most common combinations.

# COMMAND ----------

treated = pd.DataFrame(
    {c: cohort[column] <= follow_up_days for c, column in DAY_COLUMNS.items()}
)
combinations = (
    treated.apply(
        lambda row: " + ".join(c for c in DRUG_CLASSES if row[c]) or "None", axis=1
    )
    .value_counts()
    .head(8)
)

fig, (left, right) = plt.subplots(
    1, 2, figsize=(14, 4.5), gridspec_kw={"width_ratios": [1, 2]}
)
class_counts = treated.sum(axis=1).value_counts().reindex(range(5), fill_value=0)
left.bar(class_counts.index, class_counts.values, color="#1b6ca8")
left.set_title("Classes per patient")
left.set_xlabel(f"Classes prescribed within {follow_up_days} days")
left.set_ylabel("Patients")
right.barh(combinations.index[::-1], combinations.values[::-1], color="#3a9d5d")
right.set_title("Most common combinations")
right.set_xlabel("Patients")
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Does treatment vary with age?
# MAGIC
# MAGIC The percentage prescribed each class within the window, by age group at the time of the MI.

# COMMAND ----------

age_group = pd.cut(
    cohort.age_at_index,
    bins=[0, 65, 75, 200],
    right=False,
    labels=["Under 65", "65-74", "75 and over"],
)
by_age = treated.groupby(age_group, observed=False).mean().mul(100)
sizes = age_group.value_counts().reindex(by_age.index)
ax = by_age.plot.bar(color=[CLASS_COLOURS[c] for c in DRUG_CLASSES], width=0.8, rot=0)
ax.set_xticklabels([f"{label}\n({sizes[label]} patients)" for label in by_age.index])
ax.set_xlabel(None)
ax.set_ylabel("Patients treated (%)")
ax.set_ylim(0, 105)
ax.set_title(f"Treated within {follow_up_days} days, by age at first MI")
ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.2))
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## What if the map were not followed exactly?
# MAGIC
# MAGIC Earlier we saw that the map classes aspirin with codeine, an analgesic, as an antiplatelet. How many patients are counted as treated with an antiplatelet only because of it?
# MAGIC
# MAGIC The map can answer this too. Aspirin with codeine is also related to `404642006 |Opioid receptor agonist|`, so we count, for each patient, the antiplatelet products that the map does not also class as an opioid.

# COMMAND ----------

antiplatelet_products = pc.spark.sql(
    f"""
    SELECT c.patient_id,
           COUNT_IF(o.source_code IS NULL) > 0 AS non_opioid_antiplatelet
    FROM {VIEWS_SCHEMA}.mi_secondary_prevention c
    JOIN {VIEWS_SCHEMA}.medication_request_view r
      ON r.patient_id = c.patient_id
     AND CAST(r.authored_on AS DATE) BETWEEN c.index_date
         AND date_add(c.index_date, :follow_up_days)
    JOIN {VIEWS_SCHEMA}.product_to_class m
      ON m.source_system = 'http://snomed.info/sct'
     AND m.source_code = r.code
     AND m.relationship = 'related-to'
     AND m.target_code = '771452004'
    LEFT JOIN {VIEWS_SCHEMA}.product_to_class o
      ON o.source_system = 'http://snomed.info/sct'
     AND o.source_code = r.code
     AND o.relationship = 'related-to'
     AND o.target_code = '404642006'
    GROUP BY c.patient_id
    """,
    args={"follow_up_days": follow_up_days},
).toPandas()

as_asserted = len(antiplatelet_products)
non_opioid = int(antiplatelet_products.non_opioid_antiplatelet.sum())
fig, ax = plt.subplots(figsize=(8, 3))
ax.barh(
    ["Opioid combinations excluded", "Map as asserted"],
    [100 * non_opioid / len(cohort), 100 * as_asserted / len(cohort)],
    color=["#c8cdd2", CLASS_COLOURS["Antiplatelet"]],
)
for i, n in enumerate([non_opioid, as_asserted]):
    ax.text(
        100 * n / len(cohort) + 1, i, f"{n} ({100 * n / len(cohort):.0f}%)", va="center"
    )
ax.set_xlim(0, 110)
ax.set_xlabel("Patients treated with an antiplatelet (%)")
ax.set_title(f"Antiplatelet within {follow_up_days} days")
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC With the default window of 365 days, 20 patients are counted as treated with an antiplatelet only because of aspirin with codeine. Excluding it lowers the figure from 265 (97%) to 245 (89%), from above Halvorsen's 91% to below it. A classification map answers the question "what does this product contain?", which is not always the question being asked, so it is worth checking which products each class brings in.
