import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

INPUT_CSV = "outputs/processed/northsea_monthly_combined.csv"

def ols_with_stats(X, y, names):
    Xd = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(Xd, y, rcond=None)
    resid = y - Xd @ beta
    n, k = Xd.shape
    sigma2 = (resid @ resid) / (n - k)
    cov = sigma2 * np.linalg.inv(Xd.T @ Xd)
    se = np.sqrt(np.diag(cov))
    tstats = beta / se
    pvals = 2 * (1 - stats.t.cdf(np.abs(tstats), df=n - k))
    ss_tot = ((y - y.mean()) ** 2).sum()
    r2 = 1 - (resid @ resid) / ss_tot
    r2_adj = 1 - (1 - r2) * (n - 1) / (n - k)

    print(f"\n{'variable':20s} {'coef':>14s} {'std err':>14s} {'t':>8s} {'p-value':>9s}")
    for nm, b, s, t, p in zip(["intercept"] + names, beta, se, tstats, pvals):
        sig = "  <-- significant (p<0.05)" if p < 0.05 else ""
        print(f"{nm:20s} {b:14.2f} {s:14.2f} {t:8.2f} {p:9.4f}{sig}")
    print(f"R² = {r2:.3f}   adjusted R² = {r2_adj:.3f}   n = {n}")
    return beta, r2

def vif(df, cols):
    print("\nVIF (Variance Inflation Factor):")
    for col in cols:
        others = [c for c in cols if c != col]
        X = df[others].values
        y = df[col].values
        Xd = np.column_stack([np.ones(len(X)), X])
        beta, *_ = np.linalg.lstsq(Xd, y, rcond=None)
        resid = y - Xd @ beta
        r2 = 1 - (resid @ resid) / ((y - y.mean()) ** 2).sum()
        v = 1 / (1 - r2) if r2 < 1 else np.inf
        flag = "  <-- high, watch out" if v > 5 else ""
        print(f"  {col:20s} VIF = {v:6.2f}{flag}")

def main():
    df = pd.read_csv(INPUT_CSV)
    df["date"] = pd.to_datetime(df["TIME_PERIOD"], format="%Y-%m")
    df["month"] = df["date"].dt.month
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df = df.sort_values("date").reset_index(drop=True)

    y = df["co2_tonnes"].values

    print("Simple correlation (Pearson)")
    print(df[["co2_tonnes", "wind_speed_ms", "current_speed_ms"]].corr())

    print("\nMulticollinearity between wind and current")
    vif(df, ["wind_speed_ms", "current_speed_ms"])

    print("\nMultiple regression: CO2 ~ wind + current + seasonality")
    ols_with_stats(
        df[["wind_speed_ms", "current_speed_ms", "month_sin", "month_cos"]].values,
        y,
        ["wind_speed_ms", "current_speed_ms", "month_sin", "month_cos"],
    )

    print("\nSimple regression: CO2 ~ wind + seasonality")
    ols_with_stats(
        df[["wind_speed_ms", "month_sin", "month_cos"]].values,
        y,
        ["wind_speed_ms", "month_sin", "month_cos"],
    )

    print("\nSimple regression: CO2 ~ current + seasonality")
    ols_with_stats(
        df[["current_speed_ms", "month_sin", "month_cos"]].values,
        y,
        ["current_speed_ms", "month_sin", "month_cos"],
    )

    fig, axes = plt.subplots(3, 1, figsize=(10, 10))
    axes[0].plot(df["date"], df["co2_tonnes"], color="tab:red")
    axes[0].set_title("Monthly CO2 - North Sea")
    axes[1].plot(df["date"], df["wind_speed_ms"], color="tab:blue", label="wind")
    axes[1].plot(df["date"], df["current_speed_ms"] * 100, color="tab:green", label="current x100")
    axes[1].set_title("Wind and current (current x100 to visualize together)")
    axes[1].legend()
    axes[2].scatter(df["wind_speed_ms"], df["co2_tonnes"], alpha=0.6)
    axes[2].set_xlabel("wind speed (m/s)")
    axes[2].set_ylabel("CO2 (tonnes)")
    axes[2].set_title("CO2 vs. wind speed")
    plt.tight_layout()
    plt.savefig("northsea_analysis_plots.png", dpi=150)
    print("\nPlots saved to: northsea_analysis_plots.png")

if __name__ == "__main__":
    main()