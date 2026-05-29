-- WITH ranked AS (
--     SELECT 
--         report_end_date,
--         network_name,
--         province,
--         download_mean,
--         latency_mean,
--         ROW_NUMBER() OVER (
--             PARTITION BY network_name, province
--             ORDER BY report_end_date DESC
--         ) AS rn
--     FROM {{ ref('stg_high_utilization') }}
-- )

SELECT * FROM {{ ref('stg_high_utilization') }} LIMIT 10