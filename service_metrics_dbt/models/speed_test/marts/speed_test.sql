SELECT
    DATE_TRUNC('hour', timestamp::TIMESTAMPTZ) AS timestamp,
    ip,
    isp,
    location,
    AVG(download_speed_mbps)        AS download_speed_mbps,
    AVG(download_latency_ms)        AS download_latency_ms,
    AVG(idle_latency_ms)            AS idle_latency_ms
FROM {{ ref('stg_speed_test') }}
GROUP BY 1, 2, 3, 4
ORDER BY 1 DESC