WITH source AS (
    SELECT * FROM {{ source('raw_speed_test', 'raw_speed_test') }}
),
cleaned AS (
    SELECT
        "timestamp",
        TRIM(isp) AS isp,
        TRIM(ip) AS ip,
        TRIM("location") as "location",
        download_speed_mbps,
        upload_speed_mbps,
        idle_latency_ms,
        download_latency_ms,
        upload_latency_ms 
    FROM source
    where "timestamp" IS NOT NULL
      AND ip IS NOT NULL
      AND isp IS NOT NULL
      AND "location" IS NOT NULL
)
SELECT * FROM cleaned