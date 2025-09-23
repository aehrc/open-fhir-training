-- SpO2 readings for study subjects
-- Converted from original study to use FHIR-derived views
-- Extracts pulse oximetry readings within patient index periods

CREATE OR REPLACE TEMP VIEW st_reading_spo2 AS
SELECT
    sbj.subject_id,
    vs.charttime AS chart_time,
    vs.valuenum AS spo2
FROM st_subject AS sbj
JOIN mimic_iv_views.rv_obs_vitalsigns AS vs
    ON sbj.stay_id = vs.stay_id
WHERE vs.charttime BETWEEN sbj.ip_starttime AND sbj.ip_endtime
    AND vs.itemid = '220277'  -- SpO2 item ID
    AND vs.valuenum IS NOT NULL;