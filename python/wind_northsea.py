from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr

BASE_DIR = Path(__file__).resolve().parent

INPUT_NC = (
    BASE_DIR
    / "data"
    / "winds"
    / "wind_data"
    / "data_stream-oper_stepType-instant.nc"
)

OUTPUT_CSV = BASE_DIR / "era5_northsea_monthly_wind.csv"

LON_MIN, LON_MAX = -4, 9
LAT_MIN, LAT_MAX = 51, 61

def inspect():
    ds = xr.open_dataset(INPUT_NC)

    print(ds)
    print("\nVariables:", list(ds.data_vars))
    print("Dimensions:", list(ds.dims))

    ds.close()

def resolve_names(ds: xr.Dataset) -> dict:
    return {
        "u": "u10" if "u10" in ds.data_vars else "10u",
        "v": "v10" if "v10" in ds.data_vars else "10v",
        "lat": "latitude" if "latitude" in ds.coords else "lat",
        "lon": "longitude" if "longitude" in ds.coords else "lon",
        "time": "valid_time" if "valid_time" in ds.coords else "time",
    }

def compute_wind_series(ds: xr.Dataset, names: dict) -> pd.DataFrame:
    sub = ds.sel(
        {
            names["lat"]: slice(LAT_MAX, LAT_MIN),
            names["lon"]: slice(LON_MIN, LON_MAX),
        }
    )

    u_mean = sub[names["u"]].mean(dim=[names["lat"], names["lon"]])
    v_mean = sub[names["v"]].mean(dim=[names["lat"], names["lon"]])

    speed = np.sqrt(u_mean**2 + v_mean**2)
    direction = (180 + np.degrees(np.arctan2(u_mean, v_mean))) % 360

    df = pd.DataFrame(
        {
            "time": sub[names["time"]].values,
            "u10_mean": u_mean.values,
            "v10_mean": v_mean.values,
            "wind_speed_ms": speed.values,
            "wind_dir_deg": direction.values,
        }
    )

    df["date"] = pd.to_datetime(df["time"])
    df["TIME_PERIOD"] = df["date"].dt.strftime("%Y-%m")

    return df

def main():
    print("PROJECT 4 — NORTH SEA WIND DATA (ERA5)")

    print("\nOpening dataset...")
    ds = xr.open_dataset(INPUT_NC)

    names = resolve_names(ds)

    print("\nComputing spatial average and wind speed/direction...")
    df = compute_wind_series(ds, names)

    df.to_csv(OUTPUT_CSV, index=False)

    print(f"\nSaved: {OUTPUT_CSV}")
    print("\nPreview:")
    print(df.head())

    ds.close()

    print("\nSTEP COMPLETE")

if __name__ == "__main__":
    main()