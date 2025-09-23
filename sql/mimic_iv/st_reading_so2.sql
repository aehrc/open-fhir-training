-- SO2 readings from blood gas analysis for study subjects
-- Converted from original study to use FHIR-derived views
-- Extracts arterial oxygen saturation readings within patient index periods

CREATE OR REPLACE TEMP VIEW st_reading_so2 AS
SELECT
    sbj.subject_id,
    bg.charttime AS chart_time,
    bg.valuenum AS so2
FROM st_subject AS sbj
JOIN mimic_iv_views.rv_obs_bg AS bg
    ON sbj.subject_id = bg.subject_id
WHERE bg.charttime BETWEEN sbj.ip_starttime AND sbj.ip_endtime
    AND bg.itemid = '50817'  -- SO2 from blood gas
    AND bg.valuenum IS NOT NULL
    AND bg.value = 'ART.'  -- Arterial specimens only