-- Ventilation status categorisation for MIMIC-IV pulse oximetry bias analysis
-- Converted from original study to use FHIR-derived views
-- Based on mimic-code/mimic-iv/concepts_postgres/treatment/ventilation.sql

CREATE OR REPLACE VIEW mimic_iv_views.st_ventilation AS
WITH combined_o2_data AS (
    -- Combine oxygen flow and delivery device data
    SELECT
        f.subject_id,
        f.stay_id,
        f.charttime,
        f.valuenum AS o2_flow,
        d.value AS o2_delivery_device
    FROM mimic_iv_views.rv_obs_o2_flow f
    LEFT JOIN mimic_iv_views.rv_o2_delivery_device d
        ON f.subject_id = d.subject_id
        AND f.stay_id = d.stay_id
        AND ABS(UNIX_TIMESTAMP(f.charttime) - UNIX_TIMESTAMP(d.charttime)) <= 3600 -- Within 1 hour
),

-- Create multiple device columns by using window functions to get up to 4 devices per timepoint
numbered_devices AS (
    SELECT
        subject_id,
        stay_id,
        charttime,
        o2_flow,
        o2_delivery_device,
        ROW_NUMBER() OVER (
            PARTITION BY subject_id, stay_id, charttime
            ORDER BY o2_delivery_device
        ) AS device_rank
    FROM combined_o2_data
    WHERE o2_delivery_device IS NOT NULL
),

pivoted_devices AS (
    SELECT
        subject_id,
        stay_id,
        charttime,
        MAX(CASE WHEN device_rank = 1 THEN o2_delivery_device END) AS o2_delivery_device_1,
        MAX(CASE WHEN device_rank = 2 THEN o2_delivery_device END) AS o2_delivery_device_2,
        MAX(CASE WHEN device_rank = 3 THEN o2_delivery_device END) AS o2_delivery_device_3,
        MAX(CASE WHEN device_rank = 4 THEN o2_delivery_device END) AS o2_delivery_device_4,
        MAX(o2_flow) AS o2_flow
    FROM numbered_devices
    GROUP BY subject_id, stay_id, charttime
),

unpivot_o2_delivery AS (
    SELECT subject_id, stay_id, charttime, o2_delivery_device_1 AS o2_delivery_device, o2_flow
    FROM pivoted_devices
    WHERE o2_delivery_device_1 IS NOT NULL

    UNION

    SELECT subject_id, stay_id, charttime, o2_delivery_device_2 AS o2_delivery_device, o2_flow
    FROM pivoted_devices
    WHERE o2_delivery_device_2 IS NOT NULL

    UNION

    SELECT subject_id, stay_id, charttime, o2_delivery_device_3 AS o2_delivery_device, o2_flow
    FROM pivoted_devices
    WHERE o2_delivery_device_3 IS NOT NULL

    UNION

    SELECT subject_id, stay_id, charttime, o2_delivery_device_4 AS o2_delivery_device, o2_flow
    FROM pivoted_devices
    WHERE o2_delivery_device_4 IS NOT NULL
)

SELECT
    subject_id,
    stay_id,
    charttime,
    o2_delivery_device,
    CASE
        -- Tracheostomy
        WHEN o2_delivery_device IN (
            'Tracheostomy tube',
            'Trach mask'
        ) THEN 'Tracheostomy'

        -- Mechanical / invasive ventilation
        WHEN o2_delivery_device IN (
            'Endotracheal tube'
        ) THEN 'InvasiveVent'

        -- Non-invasive ventilation
        WHEN o2_delivery_device IN (
            'Bipap mask',
            'CPAP mask'
        ) THEN 'NonInvasiveVent'

        -- High flow nasal cannula
        WHEN o2_delivery_device IN (
            'High flow nasal cannula'
        ) THEN 'HFNC'

        -- Supplemental oxygen
        WHEN o2_delivery_device IN (
            'Nasal cannula',
            'Face mask',
            'Aerosol-cool',
            'Venti mask',
            'Medium conc mask',
            'Partial rebreath mask',
            'High flow neb',
            'Non-rebreath mask'
        ) OR (o2_delivery_device = 'None' AND o2_flow > 0) THEN 'SupplementalOxygen'

        -- None
        WHEN o2_delivery_device = 'None' OR o2_delivery_device IS NULL THEN 'None'

        -- Default case for unrecognised devices
        ELSE 'SupplementalOxygen'
    END AS ventilation_status
FROM unpivot_o2_delivery;