library(dplyr)
library(ggplot2)

df <- read.csv("outputs/processed/northsea_monthly_combined_with_index.csv")

df$date <- as.Date(paste0(df$TIME_PERIOD, "-01"), format = "%Y-%m-%d")
df$month <- as.numeric(format(df$date, "%m"))
df$month_sin <- sin(2 * pi * df$month / 12)
df$month_cos <- cos(2 * pi * df$month / 12)
df <- df %>% arrange(date)

cat("PCA check (prcomp), should match env_index from Python\n")
pca <- prcomp(df[, c("wind_speed_ms", "current_speed_ms")], scale. = TRUE)
print(summary(pca))
cat("Correlation between R's PC1 and Python's env_index:\n")
print(cor(pca$x[, 1], df$env_index))

cat("\nRegression: CO2 ~ env_index + seasonality\n")
model_index <- lm(co2_tonnes ~ env_index + month_sin + month_cos, data = df)
print(summary(model_index))

median_idx <- median(df$env_index)
df$condition_group <- ifelse(df$env_index > median_idx, "strong_wind_current", "weak_wind_current")

cat("\nGroup means\n")
print(df %>% group_by(condition_group) %>% summarise(avg_co2 = mean(co2_tonnes), n = n()))

cat("\nWelch two-sample t-test: strong vs. weak conditions\n")
t_result <- t.test(co2_tonnes ~ condition_group, data = df)
print(t_result)

p <- ggplot(df, aes(x = condition_group, y = co2_tonnes, fill = condition_group)) +
  geom_boxplot() +
  geom_jitter(width = 0.1, alpha = 0.5) +
  labs(
    title = "CO2 by combined wind+current condition",
    x = NULL, y = "CO2 (tonnes)"
  ) +
  theme_minimal() +
  theme(legend.position = "none")

ggsave("northsea_co2_by_condition_group.png", p, width = 6, height = 5, dpi = 150)
cat("\nPlot saved: northsea_co2_by_condition_group.png\n")
