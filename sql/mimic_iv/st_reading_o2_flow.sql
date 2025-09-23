-- Oxygen flow readings for study subjects
-- Converted from original study to use FHIR-derived views
-- Extracts nasal cannula oxygen flow readings within patient index periods

CREATE OR REPLACE TEMP VIEW st_reading_o2_flow AS
WITH nc_o2 AS (
    -- Select nasal cannula oxygen flows from delivery device data
    SELECT
        od.subject_id,
        od.stay_id,
        od.charttime,
        of.valuenum AS o2_flow,
        NULL AS o2_flow_additional  -- Additional flow not available in FHIR views
    FROM mimic_iv_views.rv_o2_delivery_device od
    JOIN mimic_iv_views.rv_obs_o2_flow of
        ON od.subject_id = of.subject_id
        AND od.stay_id = of.stay_id
        AND ABS(UNIX_TIMESTAMP(od.charttime) - UNIX_TIMESTAMP(of.charttime)) <= 3600  -- Within 1 hour
    WHERE od.value = 'Nasal cannula'
),

nc_o2_flow AS (
    SELECT
        subject_id,
        stay_id,
        charttime,
        LEAST(o2_flow, COALESCE(o2_flow_additional, o2_flow)) AS o2_flow_nc
    FROM nc_o2
),

filtered_nc_o2_flow AS (
    SELECT
        subject_id,
        stay_id,
        charttime,
        o2_flow_nc AS o2_flow
    FROM nc_o2_flow
    WHERE o2_flow_nc <= 6  -- Limit to 6L or less
)

SELECT
    sb.subject_id,
    ncf.charttime AS chart_time,
    ncf.o2_flow
FROM filtered_nc_o2_flow AS ncf
JOIN st_subject sb
    ON ncf.subject_id = sb.subject_id
    AND ncf.stay_id = sb.stay_id
WHERE ncf.charttime BETWEEN sb.ip_starttime AND sb.ip_endtime
    AND ncf.o2_flow IS NOT NULL;