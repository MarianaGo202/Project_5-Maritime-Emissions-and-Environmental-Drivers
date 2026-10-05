library(dplyr)
library(lmtest)

df <- read.csv("outputs/processed/northsea_monthly_combined_with_index.csv")
df$date <- as.Date(paste0(df$TIME_PERIOD, "-01"), format = "%Y-%m-%d")
df <- df %>% arrange(date)
df$month <- as.numeric(format(df$date, "%m"))
df$month_sin <- sin(2 * pi * df$month / 12)
df$month_cos <- cos(2 * pi * df$month / 12)

model <- lm(co2_tonnes ~ env_index + month_sin + month_cos, data = df)

# Durbin-Watson test for autocorrelated residuals
# A monthly time series regression like this one assumes independent
# residuals; if nearby months are still correlated after removing
# seasonality, the model's p-values are too optimistic (standard
# errors underestimated).
cat("Durbin-Watson test (checks residual autocorrelation)\n")
print(dwtest(model))
cat("(DW close to 2 = no autocorrelation; well below 1.5 signals\n")
cat("positive autocorrelation -- treat the regression p-values above\n")
cat("as optimistic, not as the final word.)\n")

df$env_index_lag1 <- lag(df$env_index, 1)
df_lag <- df %>% filter(!is.na(env_index_lag1))

cat("\nSame-month correlation: CO2(t) vs env_index(t)\n")
print(cor.test(df_lag$co2_tonnes, df_lag$env_index))

cat("\nLagged correlation: CO2(t) vs env_index(t-1)\n")
print(cor.test(df_lag$co2_tonnes, df_lag$env_index_lag1))

cat("\n(If the lagged correlation isn't stronger than the same-month one,\n")
cat("there's no evidence conditions act with a one-month delay -- the\n")
cat("relationship is with current conditions, not last month's.)\n")
