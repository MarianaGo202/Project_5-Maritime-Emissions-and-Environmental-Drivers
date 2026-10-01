import xarray as xr
import pandas as pd
import numpy as np

CURRENT_NC = "data/currents/glorys_northsea_monthly_2022_2026.nc"
OECD_CSV = "outputs/processed/oecd_northsea_monthly_co2.csv"
WIND_CSV = "outputs/processed/era5_northsea_monthly_wind.csv"
OUTPUT_CSV = "outputs/processed/northsea_monthly_combined.csv"

def extract_current():
    ds = xr.open_dataset(CURRENT_NC)

    if "depth" in ds.dims and ds.sizes["depth"] > 1:
        surf = ds.isel(depth=0)
    else:
        surf = ds.squeeze("depth", drop=True) if "depth" in ds.dims else ds

    u_mean = surf["uo"].mean(dim=["latitude", "longitude"])
    v_mean = surf["vo"].mean(dim=["latitude", "longitude"])
    speed = np.sqrt(u_mean**2 + v_mean**2)

    df = pd.DataFrame(
        {
            "time": surf["time"].values,
            "uo_mean": u_mean.values,
            "vo_mean": v_mean.values,
            "current_speed_ms": speed.values,
        }
    )
    df["date"] = pd.to_datetime(df["time"])
    df["TIME_PERIOD"] = df["date"].dt.strftime("%Y-%m")
    return df[["TIME_PERIOD", "uo_mean", "vo_mean", "current_speed_ms"]]


def monthly_mean_wind():
    wind = pd.read_csv(WIND_CSV)
    monthly = wind.groupby("TIME_PERIOD", as_index=False)[["u10_mean", "v10_mean"]].mean()
    monthly["wind_speed_ms"] = np.sqrt(monthly["u10_mean"] ** 2 + monthly["v10_mean"] ** 2)
    monthly["wind_dir_deg"] = (
        180 + np.degrees(np.arctan2(monthly["u10_mean"], monthly["v10_mean"]))
    ) % 360
    return monthly

def main():
    current = extract_current()
    oecd = pd.read_csv(OECD_CSV)[["TIME_PERIOD", "co2_tonnes"]]
    wind = monthly_mean_wind()[
        ["TIME_PERIOD", "u10_mean", "v10_mean", "wind_speed_ms", "wind_dir_deg"]
    ]

    combined = oecd.merge(wind, on="TIME_PERIOD", how="inner").merge(
        current, on="TIME_PERIOD", how="inner"
    )
    assert combined["TIME_PERIOD"].is_unique, "Duplicate month found -- check the granularity of the source data"
    combined["date"] = pd.to_datetime(combined["TIME_PERIOD"], format="%Y-%m")
    combined["month"] = combined["date"].dt.month
    combined = combined.sort_values("date").reset_index(drop=True)

    combined.to_csv(OUTPUT_CSV, index=False)

    print(f"Combined months: {len(combined)} (from {combined['TIME_PERIOD'].min()} to {combined['TIME_PERIOD'].max()})")
    print(combined.head())

    corr = combined[["co2_tonnes", "wind_speed_ms", "current_speed_ms"]].corr()
    print("\nCorrelation (Pearson):")
    print(corr)

    print(f"\nSaved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()