# Aggregate Premiums in Rate PUF Files
library(dplyr)
library(ggplot2)
library(pryr)
library(purrr)
library(readr)
library(tidyr)

# Load data
rates = read_csv('Rate_PUF.csv')
object_size(rates) # 692 MB

# Aggregate Rates
# Remove zeros
rates_remove_zeros = rates %>%
  select(PlanId, IndividualRate) %>%
  mutate(IndividualRate = ifelse(IndividualRate == 0, NA, IndividualRate))
  
# Compute summary statistics
probs = seq(0, 1, 0.25)
probs_columns = c("min", "q1", "median", "q3", "max")

rates_full_summary = rates_remove_zeros %>%
  group_by(PlanId) %>%
  summarize(p = list(probs_columns),
            q = list(quantile(IndividualRate, probs = probs, na.rm = TRUE)), 
            mean = mean(IndividualRate, na.rm = TRUE), 
            sd = sd(IndividualRate, na.rm = TRUE),
            count_non_missing = sum(!is.na(IndividualRate))) %>% 
  unnest() %>%
  spread(p, q)

# Cleanup columns
(rates_final = rates_full_summary %>%
  mutate(mean = ifelse(is.nan(mean), NA, mean), 
         sd = ifelse(is.nan(sd), NA, sd)) %>%
  select(PlanId, min, q1, median, q3, max, mean, sd, count_non_missing))

# Write to csv
write_csv(rates_final, "premiums_agg.csv", na = "")

# Appendix: tobacco v. Non-tobacco rates
rates_diff = rates %>%
  select(PlanId, IndividualRate, IndividualTobaccoRate) %>%
  mutate(IndividualRate = ifelse(IndividualRate == 0, NA, IndividualRate), 
         IndividualTobaccoRate = ifelse(IndividualTobaccoRate == 0, NA, IndividualTobaccoRate)) %>%
  mutate(diff = IndividualTobaccoRate - IndividualRate)

rates_diff %>%
  filter(!is.na(diff)) %>%
  ggplot(aes(x = diff)) +
  geom_histogram(bins = 50)
