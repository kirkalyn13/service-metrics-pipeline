WITH source AS (
    SELECT * FROM {{ source('raw_high_utilization', 'raw_high_utilization') }}
),
cleaned AS (
    SELECT
        "week",
        "date",
        trim(tech) AS tech,
        trim(vendor) AS vendor,
        trim(site_no) AS site_no,
        trim(site_name) AS site_name,
        trim(bts_name) AS bts_name,
        trim(cell_name) AS cell_name,
        trim(municipality) AS municipality,
        trim(province) AS province,
        trim(area) AS area,
        trim(band) AS band,
        prb_utilization,
        rrc_user,
        payload,
        dl_user_throughput_kbps,
        ul_user_throughput_kbps,
        site_status
    FROM source
    WHERE "week" IS NOT NULL
      AND "date" IS NOT NULL
      AND province IS NOT NULL
      AND municipality IS NOT NULL
      AND area IS NOT NULL
)
SELECT * FROM cleaned