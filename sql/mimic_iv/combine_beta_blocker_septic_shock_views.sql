-- Beta-blockers in septic shock
-- Combines the views created by the create_beta_blocker_septic_shock_views
-- notebook to select the cohort of Zhang et al. (2024), "Effectiveness of
-- β-blockers in improving 28-day mortality in septic shock"
-- (https://doi.org/10.3389/fcvm.2024.1438798).
--
-- Author: John Grimes

-- One row per patient, describing their first ICU stay. Each criterion of the
-- cohort definition is a column, so the number of patients remaining after each
-- step can be counted from this one view. Patients in the final cohort have
-- in_cohort = true.
CREATE OR REPLACE VIEW mimic_iv_beta_blocker_views.beta_blocker_septic_shock AS

WITH first_icu_stay AS (
  -- Each patient's first ICU stay, with their age at admission.
  SELECT s.patient_id,
         s.stay_id,
         s.hospital_admission_id,
         s.admit_time,
         s.discharge_time,
         p.gender,
         p.deceased,
         FLOOR(MONTHS_BETWEEN(s.admit_time, p.birth_date) / 12) AS age
  FROM mimic_iv_beta_blocker_views.icu_stay_view s
  JOIN mimic_iv_beta_blocker_views.patient_view p ON p.patient_id = s.patient_id
  QUALIFY ROW_NUMBER() OVER (PARTITION BY s.patient_id ORDER BY s.admit_time, s.stay_id) = 1
),

suspected_infection AS (
  -- Sepsis-3 suspected infection: an antibiotic and a microbiology specimen,
  -- where the specimen was collected within 24 hours after the antibiotic, or
  -- the antibiotic was given within 72 hours after the specimen. The onset is
  -- the earlier of the two. Only onsets from 24 hours before ICU admission to
  -- ICU discharge are kept.
  SELECT DISTINCT f.patient_id,
                  LEAST(a.start_time, m.collected_time) AS onset
  FROM first_icu_stay f
  JOIN mimic_iv_beta_blocker_views.antibiotic_view a ON a.patient_id = f.patient_id
  JOIN mimic_iv_beta_blocker_views.microbiology_specimen_view m ON m.patient_id = f.patient_id
  WHERE (m.collected_time BETWEEN a.start_time AND a.start_time + INTERVAL 24 HOURS
         OR a.start_time BETWEEN m.collected_time AND m.collected_time + INTERVAL 72 HOURS)
    AND LEAST(a.start_time, m.collected_time)
        BETWEEN f.admit_time - INTERVAL 24 HOURS AND f.discharge_time
),

pf_ratio AS (
  -- PaO2 / FiO2, pairing each arterial PaO2 with the most recent FiO2 charted
  -- in the 4 hours before it. FiO2 is charted as a percentage.
  SELECT pao2.patient_id,
         pao2.charted_time,
         pao2.value / (fio2.value / 100) AS value
  FROM mimic_iv_beta_blocker_views.sofa_observation_view pao2
  JOIN mimic_iv_beta_blocker_views.sofa_observation_view fio2
    ON fio2.patient_id = pao2.patient_id
   AND fio2.item_id = '223835'
   AND fio2.value > 0
   AND fio2.charted_time BETWEEN pao2.charted_time - INTERVAL 4 HOURS AND pao2.charted_time
  WHERE pao2.item_id = '220224'
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY pao2.patient_id, pao2.charted_time ORDER BY fio2.charted_time DESC
  ) = 1
),

gcs AS (
  -- Glasgow Coma Scale total, where all three components were charted at the
  -- same time.
  SELECT patient_id,
         charted_time,
         MAX(IF(item_id = '220739', value, NULL))
           + MAX(IF(item_id = '223900', value, NULL))
           + MAX(IF(item_id = '223901', value, NULL)) AS value
  FROM mimic_iv_beta_blocker_views.sofa_observation_view
  WHERE item_id IN ('220739', '223900', '223901')
  GROUP BY patient_id, charted_time
  HAVING value IS NOT NULL
),

sofa_input AS (
  -- Every measurement that contributes to the SOFA score, in a long format.
  SELECT patient_id, charted_time AS time, 'pf_ratio' AS measure, value FROM pf_ratio
  UNION ALL
  SELECT patient_id, charted_time, 'gcs', value FROM gcs
  UNION ALL
  SELECT patient_id,
         charted_time,
         CASE item_id
           WHEN '227457' THEN 'platelets'
           WHEN '225690' THEN 'bilirubin'
           WHEN '220615' THEN 'creatinine'
           ELSE 'map'
         END,
         value
  FROM mimic_iv_beta_blocker_views.sofa_observation_view
  WHERE item_id IN ('227457', '225690', '220615', '220052', '220181')
  UNION ALL
  SELECT patient_id,
         start_time,
         CASE item_id
           WHEN '221906' THEN 'norepinephrine'
           WHEN '221289' THEN 'epinephrine'
           WHEN '221662' THEN 'dopamine'
           WHEN '221653' THEN 'dobutamine'
         END,
         rate
  FROM mimic_iv_beta_blocker_views.vasoactive_view
  WHERE item_id IN ('221906', '221289', '221662', '221653')
),

worst_values AS (
  -- The worst value of each measurement from 48 hours before to 24 hours after
  -- each suspected infection onset.
  SELECT s.patient_id,
         s.onset,
         MIN(IF(i.measure = 'pf_ratio', i.value, NULL)) AS pf_ratio,
         MIN(IF(i.measure = 'platelets', i.value, NULL)) AS platelets,
         MAX(IF(i.measure = 'bilirubin', i.value, NULL)) AS bilirubin,
         MIN(IF(i.measure = 'map', i.value, NULL)) AS map,
         MAX(IF(i.measure = 'norepinephrine', i.value, NULL)) AS norepinephrine,
         MAX(IF(i.measure = 'epinephrine', i.value, NULL)) AS epinephrine,
         MAX(IF(i.measure = 'dopamine', i.value, NULL)) AS dopamine,
         MAX(IF(i.measure = 'dobutamine', i.value, NULL)) AS dobutamine,
         MIN(IF(i.measure = 'gcs', i.value, NULL)) AS gcs,
         MAX(IF(i.measure = 'creatinine', i.value, NULL)) AS creatinine
  FROM suspected_infection s
  LEFT JOIN sofa_input i
    ON i.patient_id = s.patient_id
   AND i.time BETWEEN s.onset - INTERVAL 48 HOURS AND s.onset + INTERVAL 24 HOURS
  GROUP BY s.patient_id, s.onset
),

sofa AS (
  -- The six SOFA components, each scored from 0 to 4. A component with no
  -- measurement in the window scores 0.
  SELECT patient_id,
         onset,
         CASE WHEN pf_ratio < 100 THEN 4
              WHEN pf_ratio < 200 THEN 3
              WHEN pf_ratio < 300 THEN 2
              WHEN pf_ratio < 400 THEN 1
              ELSE 0 END AS sofa_respiration,
         CASE WHEN platelets < 20 THEN 4
              WHEN platelets < 50 THEN 3
              WHEN platelets < 100 THEN 2
              WHEN platelets < 150 THEN 1
              ELSE 0 END AS sofa_coagulation,
         CASE WHEN bilirubin >= 12 THEN 4
              WHEN bilirubin >= 6 THEN 3
              WHEN bilirubin >= 2 THEN 2
              WHEN bilirubin >= 1.2 THEN 1
              ELSE 0 END AS sofa_liver,
         CASE WHEN dopamine > 15 OR epinephrine > 0.1 OR norepinephrine > 0.1 THEN 4
              WHEN dopamine > 5 OR epinephrine > 0 OR norepinephrine > 0 THEN 3
              WHEN dopamine > 0 OR dobutamine > 0 THEN 2
              WHEN map < 70 THEN 1
              ELSE 0 END AS sofa_cardiovascular,
         CASE WHEN gcs < 6 THEN 4
              WHEN gcs < 10 THEN 3
              WHEN gcs < 13 THEN 2
              WHEN gcs < 15 THEN 1
              ELSE 0 END AS sofa_cns,
         CASE WHEN creatinine >= 5 THEN 4
              WHEN creatinine >= 3.5 THEN 3
              WHEN creatinine >= 2 THEN 2
              WHEN creatinine >= 1.2 THEN 1
              ELSE 0 END AS sofa_renal
  FROM worst_values
),

sepsis AS (
  -- Sepsis-3: the first suspected infection with a SOFA score of 2 or more.
  SELECT *,
         sofa_respiration + sofa_coagulation + sofa_liver + sofa_cardiovascular
           + sofa_cns + sofa_renal AS sofa
  FROM sofa
  WHERE sofa_respiration + sofa_coagulation + sofa_liver + sofa_cardiovascular
          + sofa_cns + sofa_renal >= 2
  QUALIFY ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY onset) = 1
),

septic_shock AS (
  -- Septic shock: norepinephrine or vasopressin started within 48 hours before
  -- or after the onset of sepsis. The first such start is the baseline.
  SELECT s.patient_id, MIN(v.start_time) AS baseline_time
  FROM sepsis s
  JOIN mimic_iv_beta_blocker_views.vasoactive_view v
    ON v.patient_id = s.patient_id
   AND v.item_id IN ('221906', '222315')
   AND v.start_time BETWEEN s.onset - INTERVAL 48 HOURS AND s.onset + INTERVAL 48 HOURS
  GROUP BY s.patient_id
),

contraindication AS (
  -- Contraindications to beta-blockers, diagnosed during the hospital admission
  -- that contains the ICU stay. Codes are ICD-9-CM and ICD-10-CM.
  SELECT hospital_admission_id,
         MAX(code IN ('I442', '4260')) AS av_block,
         MAX(code LIKE 'I21%' OR code LIKE 'I22%' OR code LIKE '410%') AS acute_mi,
         MAX(code IN ('I5021', 'I5023', 'I5031', 'I5033', 'I5041', 'I5043', 'I50811',
                      'I50813', '42821', '42823', '42831', '42833', '42841', '42843'))
           AS acute_heart_failure,
         MAX(code LIKE 'J45%' OR code LIKE '493%') AS asthma
  FROM mimic_iv_beta_blocker_views.diagnosis_view
  GROUP BY hospital_admission_id
),

beta_blocker AS (
  -- The first beta-blocker given within 48 hours after the baseline.
  SELECT k.patient_id, MIN(b.start_time) AS first_beta_blocker_time
  FROM septic_shock k
  JOIN mimic_iv_beta_blocker_views.beta_blocker_view b
    ON b.patient_id = k.patient_id
   AND b.start_time BETWEEN k.baseline_time AND k.baseline_time + INTERVAL 48 HOURS
  GROUP BY k.patient_id
)

SELECT f.patient_id,
       f.stay_id,
       f.gender,
       f.age,
       f.admit_time,
       f.discharge_time,
       (UNIX_TIMESTAMP(f.discharge_time) - UNIX_TIMESTAMP(f.admit_time)) / 3600 AS icu_hours,
       f.age >= 18 AS adult,
       f.discharge_time >= f.admit_time + INTERVAL 48 HOURS AS stay_48_hours,
       si.first_onset AS suspected_infection_time,
       s.onset AS sepsis_time,
       s.sofa,
       s.sofa_respiration,
       s.sofa_coagulation,
       s.sofa_liver,
       s.sofa_cardiovascular,
       s.sofa_cns,
       s.sofa_renal,
       k.baseline_time,
       COALESCE(c.av_block, false) AS av_block,
       COALESCE(c.acute_mi, false) AS acute_mi,
       COALESCE(c.acute_heart_failure, false) AS acute_heart_failure,
       COALESCE(c.asthma, false) AS asthma,
       f.age >= 18
         AND f.discharge_time >= f.admit_time + INTERVAL 48 HOURS
         AND k.baseline_time IS NOT NULL
         AND NOT COALESCE(c.av_block OR c.acute_mi OR c.acute_heart_failure OR c.asthma, false)
         AS in_cohort,
       b.first_beta_blocker_time IS NOT NULL AS beta_blocker,
       b.first_beta_blocker_time,
       f.deceased,
       f.deceased IS NOT NULL
         AND f.deceased <= k.baseline_time + INTERVAL 28 DAYS AS died_within_28_days
FROM first_icu_stay f
LEFT JOIN (
  SELECT patient_id, MIN(onset) AS first_onset FROM suspected_infection GROUP BY patient_id
) si ON si.patient_id = f.patient_id
LEFT JOIN sepsis s ON s.patient_id = f.patient_id
LEFT JOIN septic_shock k ON k.patient_id = f.patient_id
LEFT JOIN contraindication c ON c.hospital_admission_id = f.hospital_admission_id
LEFT JOIN beta_blocker b ON b.patient_id = f.patient_id;

-- 28-day mortality in each group of the final cohort.
SELECT IF(beta_blocker, 'Beta-blocker', 'No beta-blocker') AS treatment_group,
       COUNT(*) AS patients,
       COUNT_IF(died_within_28_days) AS deaths,
       ROUND(100 * COUNT_IF(died_within_28_days) / COUNT(*), 1) AS mortality_percent
FROM mimic_iv_beta_blocker_views.beta_blocker_septic_shock
WHERE in_cohort
GROUP BY beta_blocker
ORDER BY beta_blocker DESC;
