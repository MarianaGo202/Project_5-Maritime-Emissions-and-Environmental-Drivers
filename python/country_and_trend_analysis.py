import pandas as pd
from scipy import stats

BY_COUNTRY_CSV = "outputs/processed/oecd_northsea_monthly_co2_by_country.csv"
COMBINED_CSV = "outputs/processed/northsea_monthly_combined_with_index.csv"


def per_country_correlation():
    by_country = pd.read_csv(BY_COUNTRY_CSV)
    combined = pd.read_csv(COMBINED_CSV)
    merged = by_country.merge(combined[["TIME_PERIOD", "env_index"]], on="TIME_PERIOD")

    print("Correlation between env_index and CO2, by country")
    rows = []
    for country, g in merged.groupby("Reference area"):
        r, p = stats.pearsonr(g["co2_tonnes"], g["env_index"])
        rows.append({"country": country, "r": r, "p_value": p, "n": len(g)})
    result = pd.DataFrame(rows).sort_values("r")
    print(result.to_string(index=False))
    return result


def yearly_trend():
    combined = pd.read_csv(COMBINED_CSV)
    combined["date"] = pd.to_datetime(combined["TIME_PERIOD"], format="%Y-%m")
    combined["year"] = combined["date"].dt.year

    months_per_year = combined.groupby("year").size()
    complete_years = months_per_year[months_per_year == 12].index

    print(f"\nComplete years available: {list(complete_years)}")
    if len(complete_years) < len(months_per_year):
        partial = months_per_year[months_per_year != 12]
        print(f"Partial year(s) excluded from trend: {dict(partial)}")

    yearly_total = combined[combined["year"].isin(complete_years)].groupby("year")["co2_tonnes"].sum()
    pct_change = yearly_total.pct_change() * 100

    print("\nYearly total CO2 (complete years only)")
    print(yearly_total)
    print("\nYear-over-year % change")
    print(pct_change.round(1))
    return yearly_total


def coefficient_of_variation():
    by_country = pd.read_csv(BY_COUNTRY_CSV)
    cv = by_country.groupby("Reference area")["co2_tonnes"].agg(["mean", "std"])
    cv["cv"] = cv["std"] / cv["mean"]
    cv = cv.sort_values("cv", ascending=False)

    print("\nCoefficient of variation per country (higher = more volatile month-to-month)")
    print(cv.round(4))
    return cv


if __name__ == "__main__":
    per_country_correlation()
    yearly_trend()
    coefficient_of_variation()