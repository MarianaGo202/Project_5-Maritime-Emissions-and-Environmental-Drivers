-- 1) Data quality checks (should all return 0)
SELECT 'negative_co2' AS check_name, COUNT(*) AS n_failed
FROM monthly_combined WHERE co2_tonnes < 0
UNION ALL
SELECT 'negative_wind_speed', COUNT(*)
FROM monthly_combined WHERE wind_speed_ms < 0
UNION ALL
SELECT 'negative_current_speed', COUNT(*)
FROM monthly_combined WHERE current_speed_ms < 0
UNION ALL
SELECT 'missing_co2', COUNT(*)
FROM monthly_combined WHERE co2_tonnes IS NULL
UNION ALL
SELECT 'missing_wind', COUNT(*)
FROM monthly_combined WHERE wind_speed_ms IS NULL
UNION ALL
SELECT 'missing_current', COUNT(*)
FROM monthly_combined WHERE current_speed_ms IS NULL
UNION ALL
SELECT 'duplicate_months', COUNT(*) - COUNT(DISTINCT TIME_PERIOD)
FROM monthly_combined;

-- 2) Per-country volatility (coefficient of variation), using window
--    functions instead of a GROUP BY + manual std calculation
WITH stats AS (
    SELECT
        "Reference area" AS country,
        AVG(co2_tonnes) OVER (PARTITION BY "Reference area") AS mean_co2,
        co2_tonnes
    FROM emissions_by_country
),
agg AS (
    SELECT
        country,
        mean_co2,
        AVG((co2_tonnes - mean_co2) * (co2_tonnes - mean_co2)) AS variance
    FROM stats
    GROUP BY country, mean_co2
)
SELECT
    country,
    ROUND(mean_co2, 0) AS mean_co2,
    ROUND(SQRT(variance), 0) AS std_co2,
    ROUND(SQRT(variance) / mean_co2, 4) AS coefficient_of_variation
FROM agg
ORDER BY coefficient_of_variation DESC;

-- 3) Complete vs. partial years (sanity check before any year-over-year
--    comparison -- avoids treating a partial year as a real decline)
SELECT
    SUBSTR(TIME_PERIOD, 1, 4) AS year,
    COUNT(*) AS n_months,
    CASE WHEN COUNT(*) = 12 THEN 'complete' ELSE 'partial' END AS status
FROM monthly_combined
GROUP BY year
ORDER BY year;