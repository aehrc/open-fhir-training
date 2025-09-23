-- Study subject definition for MIMIC-IV pulse oximetry bias analysis
-- Converted from original study to use FHIR-derived views
-- Identifies subjects with ventilation interventions and defines index periods

CREATE OR REPLACE VIEW mimic_iv_views.st_subject AS
WITH vent_intervention AS (
    SELECT stay_id,
        charttime AS inttime,
        ventilation_status AS int_type,
        ROW_NUMBER() OVER (PARTITION BY stay_id ORDER BY charttime) AS int_sequence
    FROM mimic_iv_views.st_ventilation
    WHERE ventilation_status NOT IN ('None', 'SupplementalOxygen')
        AND ventilation_status IS NOT NULL
),

first_vent_intervention AS (
    SELECT *
    FROM vent_intervention
    WHERE int_sequence = 1
),

-- Create ICU stay details from patient and encounter views
icustay_detail AS (
    SELECT
        e.stay_id,
        p.subject_id,
        p.gender,
        p.race_code AS race,
        e.admittime,
        e.dischtime,
        -- Mark first ICU and hospital stays (simplified logic)
        TRUE AS first_icu_stay,
        TRUE AS first_hosp_stay
    FROM mimic_iv_views.rv_icu_encounter e
    JOIN mimic_iv_views.rv_patient p ON e.subject_id = p.subject_id
),

first_icu_stay_with_intervention AS (
    SELECT
        isd.*,
        fvi.inttime
    FROM icustay_detail AS isd
    LEFT OUTER JOIN first_vent_intervention AS fvi ON isd.stay_id = fvi.stay_id
    WHERE first_icu_stay AND first_hosp_stay
),

stay_with_index_period AS (
    SELECT
        subject_id,
        stay_id,
        gender,
        race AS race_category,
        admittime AS ip_starttime,
        GREATEST(
            admittime,
            LEAST(
                dischtime,
                COALESCE(inttime, dischtime),
                admittime + INTERVAL 5 DAYS
            )
        ) AS ip_endtime
    FROM first_icu_stay_with_intervention
)

SELECT
    subject_id,
    stay_id,
    gender,
    race_category,
    ip_starttime,
    ip_endtime
FROM stay_with_index_period
WHERE race_category IS NOT NULL
    AND (ip_endtime - ip_starttime) >= INTERVAL 12 HOURS;