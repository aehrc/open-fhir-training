-- SpO2 readings for final cohort subjects
-- Converted from original study to use FHIR-derived views
-- Filters SpO2 readings to only include subjects in the final cohort

CREATE OR REPLACE VIEW mimic_iv_views.coh_reading_spo2 AS
SELECT *
FROM mimic_iv_views.st_reading_spo2 AS rd
WHERE EXISTS(
    SELECT 1
    FROM mimic_iv_views.coh_subject AS cs
    WHERE rd.subject_id = cs.subject_id
)
ORDER BY subject_id, chart_time;