-- O2 flow readings for final cohort subjects
-- Converted from original study to use FHIR-derived views
-- Filters O2 flow readings to only include subjects in the final cohort

CREATE OR REPLACE TEMP VIEW coh_reading_o2_flow AS
SELECT *
FROM st_reading_o2_flow AS rd
WHERE EXISTS(
    SELECT 1
    FROM coh_subject AS cs
    WHERE rd.subject_id = cs.subject_id
)
ORDER BY subject_id, chart_time;