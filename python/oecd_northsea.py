from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

INPUT_CSV = (
    BASE_DIR
    / "data"
    / "emissions"
    / "OECD.SDD.NAD.SEEA,DSD_MARITIME_TRANSPORT@DF_MARITIME_TRANSPORT.csv"
)

OUTPUT_TOTAL_CSV = BASE_DIR / "oecd_northsea_monthly_co2.csv"
OUTPUT_BY_COUNTRY_CSV = BASE_DIR / "oecd_northsea_monthly_co2_by_country.csv"

# Countries bordering the North Sea
NORTH_SEA_COUNTRIES = [
    "Netherlands",
    "Belgium",
    "Germany",
    "Denmark",
    "United Kingdom",
    "Norway",
]

# Keep the aggregate across all vessel types
VESSEL_FILTER = "ALL_VESSELS"

# Territorial emissions only (domestic + international traffic
# within national waters) — excludes other reporting categories
# mixed into the same OECD table
TERRITORIAL_SOURCES = ["TER_DOM", "TER_INT"]

POLLUTANT = "CO2"

def load_filtered_emissions() -> pd.DataFrame:
    df = pd.read_csv(INPUT_CSV)

    mask = (
        df["Reference area"].isin(NORTH_SEA_COUNTRIES)
        & (df["VESSEL"] == VESSEL_FILTER)
        & (df["VESSEL_EMISSIONS_SOURCE"].isin(TERRITORIAL_SOURCES))
        & (df["POLLUTANT"] == POLLUTANT)
    )

    columns = [
        "Reference area",
        "TIME_PERIOD",
        "VESSEL_EMISSIONS_SOURCE",
        "OBS_VALUE",
    ]

    return df.loc[mask, columns].copy()

def aggregate_by_country(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Reference area", "TIME_PERIOD"], as_index=False)["OBS_VALUE"]
        .sum()
        .rename(columns={"OBS_VALUE": "co2_tonnes"})
    )


def aggregate_total(df_by_country: pd.DataFrame) -> pd.DataFrame:
    monthly_total = (
        df_by_country.groupby("TIME_PERIOD", as_index=False)["co2_tonnes"]
        .sum()
        .sort_values("TIME_PERIOD")
    )

    monthly_total["date"] = pd.to_datetime(
        monthly_total["TIME_PERIOD"], format="%Y-%m"
    )
    monthly_total["year"] = monthly_total["date"].dt.year
    monthly_total["month"] = monthly_total["date"].dt.month

    return monthly_total

def main():
    print("PROJECT 4 — NORTH SEA SHIPPING EMISSIONS (OECD)")

    print("\nLoading and filtering emissions data...")
    filtered = load_filtered_emissions()

    print("\nAggregating monthly totals by country...")
    monthly_by_country = aggregate_by_country(filtered)

    print("Aggregating overall monthly total...")
    monthly_total = aggregate_total(monthly_by_country)

    print(f"\nCountries included: {NORTH_SEA_COUNTRIES}")
    print(
        f"Period covered: "
        f"{monthly_total['TIME_PERIOD'].min()} to "
        f"{monthly_total['TIME_PERIOD'].max()}"
    )
    print(f"Months in total: {len(monthly_total)}")
    print("\nPreview:")
    print(monthly_total.head())

    monthly_total.to_csv(OUTPUT_TOTAL_CSV, index=False)
    monthly_by_country.to_csv(OUTPUT_BY_COUNTRY_CSV, index=False)

    print(f"\nSaved: {OUTPUT_TOTAL_CSV}")
    print(f"Saved: {OUTPUT_BY_COUNTRY_CSV}")

    print("\nSTEP COMPLETE")

if __name__ == "__main__":
    main()