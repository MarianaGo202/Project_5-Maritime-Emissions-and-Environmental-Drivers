-- 1) Top 5 highest-emission months, with wind/current conditions that month
SELECT TIME_PERIOD, co2_tonnes, wind_speed_ms, current_speed_ms
FROM monthly_combined
ORDER BY co2_tonnes DESC
LIMIT 5;

-- 2) Bottom 5 lowest-emission months
SELECT TIME_PERIOD, co2_tonnes, wind_speed_ms, current_speed_ms
FROM monthly_combined
ORDER BY co2_tonnes ASC
LIMIT 5;

-- 3) Average monthly CO2 by country, ranked (North Sea coastal countries)
SELECT "Reference area", ROUND(AVG(co2_tonnes), 0) AS avg_co2_tonnes
FROM emissions_by_country
GROUP BY "Reference area"
ORDER BY avg_co2_tonnes DESC;

-- 4) Yearly totals, to see the overall trend across 2022-2026
SELECT SUBSTR(TIME_PERIOD, 1, 4) AS year, ROUND(SUM(co2_tonnes), 0) AS total_co2_tonnes
FROM monthly_combined
GROUP BY year
ORDER BY year;

-- 5) Seasonal profile: average CO2, wind and current by calendar month
--    (across all years) -- this is the core "seasonality" check for the
--    project hypothesis
SELECT
    SUBSTR(TIME_PERIOD, 6, 2) AS month,
    ROUND(AVG(co2_tonnes), 0) AS avg_co2,
    ROUND(AVG(wind_speed_ms), 2) AS avg_wind,
    ROUND(AVG(current_speed_ms), 4) AS avg_current
FROM monthly_combined
GROUP BY month
ORDER BY month;

-- 6) 3-month moving average of CO2 (window function), to smooth noise
--    before eyeballing trend/seasonality
SELECT
    TIME_PERIOD,
    co2_tonnes,
    ROUND(
        AVG(co2_tonnes) OVER (ORDER BY TIME_PERIOD ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),
        0
    ) AS moving_avg_3m
FROM monthly_combined
ORDER BY TIME_PERIOD;

-- 7) Month-over-month change in CO2 (window function: LAG)
SELECT
    TIME_PERIOD,
    co2_tonnes,
    co2_tonnes - LAG(co2_tonnes) OVER (ORDER BY TIME_PERIOD) AS change_vs_prev_month
FROM monthly_combined
ORDER BY TIME_PERIOD;

-- 8) Months where wind was above average AND current was above average
--    (candidate "favorable conditions" months, for a quick eyeball check
--    against the CO2 column)
SELECT TIME_PERIOD, co2_tonnes, wind_speed_ms, current_speed_ms
FROM monthly_combined
WHERE wind_speed_ms > (SELECT AVG(wind_speed_ms) FROM monthly_combined)
  AND current_speed_ms > (SELECT AVG(current_speed_ms) FROM monthly_combined)
ORDER BY TIME_PERIOD;