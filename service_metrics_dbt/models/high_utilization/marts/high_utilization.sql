WITH base AS (
    SELECT * FROM {{ ref('stg_high_utilization') }}
    WHERE area = 'NL'
),
high_util_cells AS (
    SELECT DISTINCT site_name, municipality, province
    FROM base
    WHERE prb_utilization > 90
),
enriched AS (
    SELECT
        b."week",
        b."date",
        b.tech,
        b.vendor,
        b.site_name,
        b.cell_name,
        b.municipality,
        b.province,
        b.band,
        b.prb_utilization,
        b.rrc_user,
        b.payload,
        b.dl_user_throughput_kbps,
        b.site_status,
        CASE WHEN b.prb_utilization > 90 THEN TRUE ELSE FALSE END AS is_high_util
    FROM base b
    INNER JOIN high_util_cells h
        ON b.site_name = h.site_name
)
SELECT * FROM enriched
ORDER BY "date" DESC, site_name, cell_name