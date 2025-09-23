-- Prostate cancer risk factors analysis
-- Combines patient demographics, prostate cancer diagnoses, hyperlipidaemia observations, and high BMI observations
-- Based on SQL on FHIR views created from Synthea FHIR data

-- Create the final combined view for prostate cancer risk factor analysis
CREATE OR REPLACE VIEW synthea_prostate_cancer_views.prostate_cancer_risk_factors AS

WITH patient_diagnoses AS (
  -- Join patient demographics with prostate cancer diagnoses
  SELECT
    p.id as patient_id,
    p.birth_date,
    p.postal_code,
    p.deceased,
    pc.onset as prostate_cancer_onset
  FROM synthea_prostate_cancer_views.patient_demographics_view p
  LEFT JOIN synthea_prostate_cancer_views.prostate_cancer_diagnosis_view pc
    ON p.id = pc.patient_id
),

cholesterol_with_rank AS (
  -- Get cholesterol observations with ranking by date (most recent first)
  -- Only include observations that occurred before prostate cancer diagnosis
  SELECT
    h.patient_id,
    h.date as cholesterol_date,
    h.value as cholesterol_value,
    h.unit as cholesterol_unit,
    pd.prostate_cancer_onset,
    ROW_NUMBER() OVER (
      PARTITION BY h.patient_id
      ORDER BY h.date DESC
    ) as rn
  FROM synthea_prostate_cancer_views.hyperlipidemia_view h
  INNER JOIN patient_diagnoses pd ON h.patient_id = pd.patient_id
  WHERE pd.prostate_cancer_onset IS NULL
     OR h.date < pd.prostate_cancer_onset
),

latest_cholesterol AS (
  -- Get the most recent cholesterol observation per patient
  SELECT
    patient_id,
    cholesterol_date as hyperlipidemia_observed,
    cholesterol_value as total_cholesterol,
    cholesterol_unit as cholesterol_unit
  FROM cholesterol_with_rank
  WHERE rn = 1
),

bmi_with_rank AS (
  -- Get BMI observations with ranking by date (most recent first)
  -- Only include observations that occurred before prostate cancer diagnosis
  SELECT
    b.patient_id,
    b.date as bmi_date,
    b.value as bmi_value,
    b.unit as bmi_unit,
    pd.prostate_cancer_onset,
    ROW_NUMBER() OVER (
      PARTITION BY b.patient_id
      ORDER BY b.date DESC
    ) as rn
  FROM synthea_prostate_cancer_views.bmi_view b
  INNER JOIN patient_diagnoses pd ON b.patient_id = pd.patient_id
  WHERE pd.prostate_cancer_onset IS NULL
     OR b.date < pd.prostate_cancer_onset
),

latest_bmi AS (
  -- Get the most recent BMI observation per patient
  SELECT
    patient_id,
    bmi_date as high_bmi_observed,
    ROUND(bmi_value, 2) as bmi_value,
    bmi_unit
  FROM bmi_with_rank
  WHERE rn = 1
)

-- Final result combining all views
SELECT
  pd.patient_id,
  DATE(pd.birth_date) as birth_date,
  pd.postal_code,
  pd.deceased,
  pd.prostate_cancer_onset,
  lb.high_bmi_observed,
  lb.bmi_value,
  lc.hyperlipidemia_observed,
  ROUND(lc.total_cholesterol, 1) as total_cholesterol_mg_dl
FROM patient_diagnoses pd
LEFT JOIN latest_cholesterol lc ON pd.patient_id = lc.patient_id
LEFT JOIN latest_bmi lb ON pd.patient_id = lb.patient_id
ORDER BY pd.patient_id;