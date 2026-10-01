import numpy as np
import pandas as pd

INPUT_CSV = "outputs/processed/northsea_monthly_combined.csv"
OUTPUT_CSV = "outputs/processed/northsea_monthly_combined_with_index.csv"

def main():
    df = pd.read_csv(INPUT_CSV)

    w = (df["wind_speed_ms"] - df["wind_speed_ms"].mean()) / df["wind_speed_ms"].std()
    c = (df["current_speed_ms"] - df["current_speed_ms"].mean()) / df["current_speed_ms"].std()
    X = np.column_stack([w, c])
    Xc = X - X.mean(axis=0)

    _, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    pc1 = Xc @ Vt[0]

    # PCA sign is arbitrary -- flip it so higher env_index always means
    # stronger wind (same direction as the raw wind_speed_ms column)
    sign = np.sign(np.corrcoef(pc1, df["wind_speed_ms"])[0, 1])
    df["env_index"] = sign * pc1

    var_explained = (S**2 / np.sum(S**2))[0]
    print(f"Variance explained by env_index (PC1): {var_explained:.3f}")
    print(f"Correlation env_index vs wind_speed_ms: {np.corrcoef(df['env_index'], df['wind_speed_ms'])[0,1]:.3f}")
    print(f"Correlation env_index vs current_speed_ms: {np.corrcoef(df['env_index'], df['current_speed_ms'])[0,1]:.3f}")

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()