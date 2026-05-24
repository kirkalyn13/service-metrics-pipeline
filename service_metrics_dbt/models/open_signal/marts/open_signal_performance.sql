WITH open_signal_4g AS (
    SELECT *, '4G' AS technology_band FROM {{ ref('stg_open_signal_4g') }}
),
final AS (
    SELECT
        report_end_date,
        network_name,
        technology_band,
        location_category,
        area,
        province,
        round(avg(availability_mean)::NUMERIC, 2) AS avg_availability_pct,
        round(avg(download_mean)::NUMERIC, 2) AS avg_download_mbps,
        round(avg(upload_mean)::NUMERIC, 2) AS avg_upload_mbps,
        round(avg(latency_mean)::NUMERIC, 2) AS avg_latency_ms,
        round(avg(videoexperience_mean)::NUMERIC, 2) AS avg_video_score,
        round(avg(voiceappexperience_mean)::NUMERIC, 2) AS avg_voice_score,
        sum(number_of_records) AS total_records
    FROM open_signal_4g
    GROUP BY 1, 2, 3, 4, 5, 6
)
SELECT * FROM final