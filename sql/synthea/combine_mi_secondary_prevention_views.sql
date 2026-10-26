-- Secondary prevention after myocardial infarction
-- Combines the patient, myocardial infarction and medication request views with
-- the product-to-classification ConceptMap, created by the
-- create_mi_secondary_prevention_views notebook.
--
-- Author: John Grimes

-- One row per patient with a myocardial infarction (MI), indexed on their first
-- MI. For each drug class, the number of days from the index MI to the first
-- prescription of that class written on or after it, or NULL if there was none.
CREATE OR REPLACE VIEW synthea_mi_secondary_prevention_views.mi_secondary_prevention AS

WITH drug_class (class_code, drug_class) AS (
  -- The SNOMED CT classes in the ConceptMap that make up each drug class.
  VALUES ('771452004', 'Antiplatelet'),         -- Platelet aggregation inhibitor
         ('372912004', 'Statin'),               -- HMG-CoA reductase inhibitor
         ('373254001', 'Beta-blocker'),         -- Beta blocker
         ('372733002', 'ACE inhibitor or ARB'), -- Angiotensin-converting enzyme inhibitor
         ('372913009', 'ACE inhibitor or ARB')  -- Angiotensin II receptor antagonist
),

index_mi AS (
  -- Each patient's first MI.
  SELECT patient_id,
         CAST(onset AS DATE) AS index_date,
         code AS index_code,
         display AS index_display
  FROM synthea_mi_secondary_prevention_views.myocardial_infarction_view
  QUALIFY ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY onset, id) = 1
),

classified_request AS (
  -- Medication requests joined to the ConceptMap. A product in more than one of
  -- the classes produces a row for each, and a product in none produces no row.
  SELECT DISTINCT r.id,
         r.patient_id,
         CAST(r.authored_on AS DATE) AS authored_date,
         d.drug_class
  FROM synthea_mi_secondary_prevention_views.medication_request_view r
  JOIN synthea_mi_secondary_prevention_views.product_to_class m
    ON m.source_system = 'http://snomed.info/sct'
   AND m.source_code = r.code
   AND m.relationship = 'related-to'
  JOIN drug_class d ON d.class_code = m.target_code
),

first_prescription AS (
  -- Days from the index MI to the first prescription of each class on or after it.
  SELECT i.patient_id,
         c.drug_class,
         MIN(DATEDIFF(c.authored_date, i.index_date)) AS days
  FROM index_mi i
  JOIN classified_request c
    ON c.patient_id = i.patient_id
   AND c.authored_date >= i.index_date
  GROUP BY i.patient_id, c.drug_class
)

SELECT i.patient_id,
       p.gender,
       CAST(p.birth_date AS DATE) AS birth_date,
       FLOOR(MONTHS_BETWEEN(i.index_date, CAST(p.birth_date AS DATE)) / 12) AS age_at_index,
       CAST(p.deceased AS DATE) AS deceased_date,
       i.index_date,
       i.index_code,
       i.index_display,
       MAX(CASE WHEN f.drug_class = 'Antiplatelet' THEN f.days END) AS days_to_antiplatelet,
       MAX(CASE WHEN f.drug_class = 'Statin' THEN f.days END) AS days_to_statin,
       MAX(CASE WHEN f.drug_class = 'Beta-blocker' THEN f.days END) AS days_to_beta_blocker,
       MAX(CASE WHEN f.drug_class = 'ACE inhibitor or ARB' THEN f.days END)
         AS days_to_ace_inhibitor_or_arb
FROM index_mi i
JOIN synthea_mi_secondary_prevention_views.patient_view p ON p.id = i.patient_id
LEFT JOIN first_prescription f ON f.patient_id = i.patient_id
GROUP BY i.patient_id, p.gender, p.birth_date, p.deceased, i.index_date, i.index_code,
         i.index_display;

-- The number and percentage of the cohort prescribed each class within
-- :follow_up_days days of their index MI, and the number prescribed all four.
WITH treated AS (
  SELECT patient_id,
         drug_class,
         COALESCE(days <= :follow_up_days, FALSE) AS treated
  FROM synthea_mi_secondary_prevention_views.mi_secondary_prevention
  UNPIVOT INCLUDE NULLS (
    days FOR drug_class IN (
      days_to_antiplatelet AS `Antiplatelet`,
      days_to_statin AS `Statin`,
      days_to_beta_blocker AS `Beta-blocker`,
      days_to_ace_inhibitor_or_arb AS `ACE inhibitor or ARB`
    )
  )
),

per_class AS (
  SELECT drug_class, COUNT(*) AS patients, COUNT_IF(treated) AS treated
  FROM treated
  GROUP BY drug_class
),

all_four AS (
  SELECT 'All four' AS drug_class,
         COUNT(*) AS patients,
         COUNT_IF(classes = 4) AS treated
  FROM (
    SELECT patient_id, COUNT_IF(treated) AS classes
    FROM treated
    GROUP BY patient_id
  )
)

SELECT drug_class,
       patients,
       treated,
       ROUND(100 * treated / patients, 1) AS percent_treated
FROM (SELECT * FROM per_class UNION ALL SELECT * FROM all_four)
ORDER BY CASE drug_class
           WHEN 'Antiplatelet' THEN 1
           WHEN 'Statin' THEN 2
           WHEN 'Beta-blocker' THEN 3
           WHEN 'ACE inhibitor or ARB' THEN 4
           ELSE 5
         END
