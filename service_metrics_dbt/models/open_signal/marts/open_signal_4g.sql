WITH ranked AS (
    SELECT 
        report_end_date,
        network_name,
        province,
        download_mean,
        latency_mean,
        ROW_NUMBER() OVER (
            PARTITION BY network_name, province
            ORDER BY report_end_date DESC
        ) AS rn
    FROM {{ ref('stg_open_signal_4g') }}
)

SELECT * FROM ranked
WHERE rn <= 13