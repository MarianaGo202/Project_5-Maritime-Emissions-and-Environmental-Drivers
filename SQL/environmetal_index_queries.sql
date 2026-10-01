-- 1) Median split: compare average CO2 in months with strong vs. weak
--    combined wind+current conditions (SQLite has no MEDIAN() function,
--    so PERCENT_RANK() is used to split at the 50th percentile)
WITH ranked AS (
    SELECT
        TIME_PERIOD,
        co2_tonnes,
        env_index,
        PERCENT_RANK() OVER (ORDER BY env_index) AS pct_rank
    FROM monthly_with_index
),
grouped AS (
    SELECT
        CASE WHEN pct_rank >= 0.5 THEN 'strong_wind_current' ELSE 'weak_wind_current' END AS condition_group,
        co2_tonnes
    FROM ranked
)
SELECT condition_group, ROUND(AVG(co2_tonnes), 0) AS avg_co2, COUNT(*) AS n_months
FROM grouped
GROUP BY condition_group;

-- 2) Top 10 months by env_index (strongest combined conditions), with
--    their CO2 -- useful to eyeball alongside the group averages above
SELECT TIME_PERIOD, ROUND(env_index, 2) AS env_index, co2_tonnes
FROM monthly_with_index
ORDER BY env_index DESC
LIMIT 10;

-- 3) Bottom 10 months by env_index (weakest combined conditions)
SELECT TIME_PERIOD, ROUND(env_index, 2) AS env_index, co2_tonnes
FROM monthly_with_index
ORDER BY env_index ASC
LIMIT 10;

-- 4) Correlation-style check: average CO2 by env_index quartile
--    (finer-grained version of the median split above)
WITH ranked AS (
    SELECT
        TIME_PERIOD,
        co2_tonnes,
        env_index,
        NTILE(4) OVER (ORDER BY env_index) AS quartile
    FROM monthly_with_index
)
SELECT quartile, ROUND(AVG(co2_tonnes), 0) AS avg_co2, COUNT(*) AS n_months
FROM ranked
GROUP BY quartile
ORDER BY quartile;