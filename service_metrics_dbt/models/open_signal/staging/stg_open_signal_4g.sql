WITH source AS (
    SELECT * FROM {{ source('raw_open_signal_4g', 'raw_open_signal_4g') }}
),
cleaned AS (
    SELECT
        aggregation,
        report_end_date,
        trim(network_name) AS network_name,
        technology,
        trim(location_category) AS location_category,
        trim(area) AS area,
        trim("location") AS province,
        availability_devices,
        availability_mean,
        availability_readings,
        download_devices,
        download_mean,
        download_readings,
        upload_devices,
        upload_mean,
        upload_readings,
        latency_devices,
        latency_mean,
        latency_readings,
        videoexperience_devices,
        videoexperience_mean,
        videoexperience_readings,
        voiceappexperience_devices,
        voiceappexperience_mean,
        voiceappexperience_readings,
        number_of_records
    FROM source
    where report_end_date IS NOT NULL
      AND network_name IS NOT NULL
)
SELECT * FROM cleaned