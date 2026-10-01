library(dplyr)
library(ggplot2)
library(car)

df <- read.csv("outputs/processed/northsea_monthly_combined.csv")

df$date <- as.Date(paste0(df$TIME_PERIOD, "-01"), format = "%Y-%m-%d")
df$month <- as.numeric(format(df$date, "%m"))
df$month_sin <- sin(2 * pi * df$month / 12)
df$month_cos <- cos(2 * pi * df$month / 12)
df <- df %>% arrange(date)

# Simple correlation
cat("Simple correlation (Pearson)\n")
print(cor(df[, c("co2_tonnes", "wind_speed_ms", "current_speed_ms")]))

# Multiple regression: CO2 ~ wind + current + seasonality
cat("\nMultiple regression: CO2 ~ wind + current + seasonality\n")
model_full <- lm(co2_tonnes ~ wind_speed_ms + current_speed_ms + month_sin + month_cos, data = df)
print(summary(model_full))

cat("\nMulticollinearity check (VIF)\n")
print(vif(model_full))
cat("(VIF > 5 signals that wind and current are too correlated with each\n")
cat("other for the multiple regression to separate their individual effect.)\n")

# Simple regressions, for comparison against the multiple model
cat("\nSimple regression: CO2 ~ wind + seasonality\n")
model_wind <- lm(co2_tonnes ~ wind_speed_ms + month_sin + month_cos, data = df)
print(summary(model_wind))

cat("\nSimple regression: CO2 ~ current + seasonality\n")
model_current <- lm(co2_tonnes ~ current_speed_ms + month_sin + month_cos, data = df)
print(summary(model_current))

# Plots
p1 <- ggplot(df, aes(x = date, y = co2_tonnes)) +
  geom_line(color = "firebrick") +
  labs(title = "Monthly CO2 - North Sea", x = NULL, y = "CO2 (tonnes)") +
  theme_minimal()

p2 <- ggplot(df, aes(x = wind_speed_ms, y = co2_tonnes)) +
  geom_point(alpha = 0.6) +
  geom_smooth(method = "lm", se = FALSE, color = "steelblue") +
  labs(title = "CO2 vs. wind speed", x = "wind speed (m/s)", y = "CO2 (tonnes)") +
  theme_minimal()

p3 <- ggplot(df, aes(x = current_speed_ms, y = co2_tonnes)) +
  geom_point(alpha = 0.6) +
  geom_smooth(method = "lm", se = FALSE, color = "seagreen") +
  labs(title = "CO2 vs. current speed", x = "current speed (m/s)", y = "CO2 (tonnes)") +
  theme_minimal()

ggsave("northsea_co2_timeseries.png", p1, width = 8, height = 4, dpi = 150)
ggsave("northsea_co2_vs_wind.png", p2, width = 6, height = 5, dpi = 150)
ggsave("northsea_co2_vs_current.png", p3, width = 6, height = 5, dpi = 150)

cat("\nPlots saved: northsea_co2_timeseries.png, northsea_co2_vs_wind.png, northsea_co2_vs_current.png\n")