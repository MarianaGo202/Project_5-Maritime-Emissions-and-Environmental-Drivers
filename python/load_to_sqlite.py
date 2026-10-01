import sqlite3
import pandas as pd

DB_PATH = "northsea_project.db"

combined = pd.read_csv("outputs/processed/northsea_monthly_combined.csv")
by_country = pd.read_csv("outputs/processed/oecd_northsea_monthly_co2_by_country.csv")

conn = sqlite3.connect(DB_PATH)
combined.to_sql("monthly_combined", conn, if_exists="replace", index=False)
by_country.to_sql("emissions_by_country", conn, if_exists="replace", index=False)
conn.close()

print(f"Loaded into {DB_PATH}: monthly_combined ({len(combined)} rows), "
      f"emissions_by_country ({len(by_country)} rows)")
