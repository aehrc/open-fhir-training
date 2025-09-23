-- Final cohort subject definition for MIMIC-IV pulse oximetry bias analysis
-- Converted from original study to use FHIR-derived views
-- Identifies subjects with complete measurement sets for analysis

CREATE OR REPLACE TEMP VIEW coh_subject AS
SELECT
    subject_id,
    gender,
    race_category
FROM st_subject AS sbj
WHERE EXISTS(
    SELECT 1
    FROM st_reading_o2_flow AS rof
    WHERE sbj.subject_id = rof.subject_id
)
AND EXISTS(
    SELECT 1
    FROM st_reading_spo2 AS rspo2
    WHERE sbj.subject_id = rspo2.subject_id
)
AND EXISTS(
    SELECT 1
    FROM st_reading_so2 AS rso2
    WHERE sbj.subject_id = rso2.subject_id
);