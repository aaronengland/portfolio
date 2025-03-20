# Indirect Lending Model (i.e., Gen 13)

## Contents

- Overview
- Data
- PD Model
- LGD
- Performance
- Identity
- Swap-in swap-out
- Local Dark Scoring
- Compliance
- Simulations
- Early Pay
- Additional Information

---

## Overview

- ECNL = Probability of Default (PD) x Loss Given Default (LGD)
- Where:
	- PD = Probability of going 60+ days past due (DPD) in the first 720 days (24 months) on books
	- LGD = Average charge-off severity by LTV bin (i.e., LTV grid)
		- LTV grid dependent on BK/Non-BK (see LGD section)

---

## Data

- Bad Definition: 60+ DPD in the first 720 days (24 months) on books
- Origin:
	- Payloads stored in snowflake
	- Cost of data set: $0.00
	
![Data Information](./output/plt_info.png)
![Plot Information](./output/plt_info_img.png)
![Bad BK Dataset](./output/plt_bad_bk_dataset.png)
![Bad Franchise Dataset](./output/plt_bad_franchise_dataset.png)

---

## PD Model

![Performance](./output/performance.png)
![Distributions BK](./output/plt_distributions_bk.png)
![Distributions Dealer](./output/plt_distributions_dealer.png)

- [Feature Selection](https://github.com/PFS-Risk-DS/20241112_simple_model_test/blob/main/10_60_in_720_test/02_model/notebook.ipynb)
	- Remove non-numeric features
	- Remove features missing at least 80% of the time in any data set (train, test, holdout)
	- Remove features missing at least 80% of the time in the most recent month of payloads
	- Bin features using OptBinning
	- Remove features with fewer than 2 bins
	- Simple logistic regression models (single variable) to prepare for multicollinearity test
	- Check for multicollinearity
	- Forward stepwise feature selection
	- Remove any features that reduce training AUC via sensitivity analysis (also used for disparate impact analysis)
	- Remove any features that flip direction (contribution vs bad rate by bin)

![Feature Selection](../../10_60_in_720_test/02_model/output/plt_forward_stepwise.png)
![Feature Importance](./output/feat_importance.png)
![Bins](./output/plt_scorecard.png)

- PD Calculation
	- To manually calculate the PD score:
		- Determine the bin for each feature sand corresponding contribution (bin * coefficient)
		- Sum the contributions (1 per feature) and intercept (this is the "log odds" or "logit")
		- Convert the log odds to a probability

![Probability Formula](./img/probability_formula.PNG)
![Best Bin](./output/best_bin.png)
![Worst Bin](./output/worst_bin.png)

---

## LGD

![LTV Bins Original](../../create_grid/01_60_in_720_bk_chargeoff/output/plt_bins_original.png)
![LTV Bins Original](../../create_grid/02_60_in_720_nobk_chargeoff/output/plt_bins_original.png)

---

## Performance

![PD](../13_ecnl_evaluation/output/plt_pd.png)
![ECNL](../13_ecnl_evaluation/output/plt_ecnl.png)

---

## Identity

BK
![BK](../17_identity/output/plt_tree_bk.png)
Non BK
![NoBK](../17_identity/output/plt_tree_nobk.png)

---

## Swap-in swap-out

![Distribution Comparisons](../10_swap_in_swap_out/output/plt_distributions.png)
![Distribution BK No BK](../10_swap_in_swap_out/output/plt_ecnl_bk_nobk.png)
![Correlation PD](../10_swap_in_swap_out/output/plt_correlation_pd.png)
![Correlation LGD](../10_swap_in_swap_out/output/plt_correlation_lgd.png)
![Correlation](../10_swap_in_swap_out/output/plt_correlation.png)
![Swap in Swap out](../10_swap_in_swap_out/output/plt_swap_in_swap_out.png)
![Swap in Swap out Tier Proportion](../16_swap_in_swap_out_plots/output/plt_stacked_tier.png)
![Swap in Swap out Franchise Proportion](../16_swap_in_swap_out_plots/output/plt_stacked_franchise_prop.png)
![Swap in Swap out Median Income](../16_swap_in_swap_out_plots/output/plt_stacked_income.png)
![Correlation LTV](../10_swap_in_swap_out/output/plt_correlation_ltv_ecnl.png)
![3D BK](../10_swap_in_swap_out/output/plt_ltv_income_miles_bk.png)
![3D BK](../10_swap_in_swap_out/output/plt_ltv_income_miles_nobk.png)
![Gen 13 Mean LTV](../16_swap_in_swap_out_plots/output/plt_stacked_ltv.png)
![Gen 13 BK Proportion](../16_swap_in_swap_out_plots/output/plt_stacked_bk.png)
![Gen 13 Mean Miles ODO](../16_swap_in_swap_out_plots/output/plt_stacked_miles_odometer.png)

---

## Local Dark Scoring

- [Predictions Samples](https://github.com/PFS-Risk-DS/20241112_simple_model_test/blob/main/09_60_in_720/11_show_sample/output)

---

## Compliance

![Disparate Impact](../12_disparate_impact/output/disparate_impact.png)
![Race](../15_disparate_distributions/output/plt_distribution_race.png)
![Age](../15_disparate_distributions/output/plt_distribution_age.png)
![Gender](../15_disparate_distributions/output/plt_distribution_gender.png)
![Adverse Action Freq](../11_show_sample/output/plt_aa_reasons.png)
![Adverse Action](../11_show_sample/output/plt_worst_feat_freq.png)

---

## Simulations

![Income](../14_simulations/output/plt_iterations_income.png)
![Mileage](../14_simulations/output/plt_iterations_mileage.png)
![LTV](../14_simulations/output/plt_iterations_ltv.png)

---

## Early Pay

![Early Pay](../../ad_hoc/02_score_all_apps/output/plt_early_pay_tier.png)

---

## Additional Information

- [Detailed Bins](https://github.com/PFS-Risk-DS/20241112_simple_model_test/blob/main/show_bins/output/df_bins_indirect.csv)

- [Adverse Action](https://github.com/PFS-Risk-DS/20241112_simple_model_test/blob/main/get_aa_dfs/output/df_aa_indirect.csv)

- [Imputations](https://github.com/PFS-Risk-DS/20241112_simple_model_test/blob/main/imputations/output/df_imputations_indirect.csv)

- [EDA](https://github.com/PFS-Risk-DS/20241112_simple_model_test/blob/main/eda/notebook.ipynb)

- [Early Indicator Models](https://github.com/PFS-Risk-DS/20241112_simple_model_test/tree/main/17_fit_early_indicator_models)

![15 in 60 Tier](../../18_early_indicator_analysis/output/plt_15_60_tier.png)
![15 in 60 BK](../../18_early_indicator_analysis/output/plt_15_60_bk.png)
![30 in 90 Tier](../../18_early_indicator_analysis/output/plt_30_90_tier.png)
![30 in 90 BK](../../18_early_indicator_analysis/output/plt_30_90_bk.png)
![30 in 180 Tier](../../18_early_indicator_analysis/output/plt_30_180_tier.png)
![30 in 180 BK](../../18_early_indicator_analysis/output/plt_30_180_bk.png)
![30 in 360 Tier](../../18_early_indicator_analysis/output/plt_30_360_tier.png)
![30 in 360 BK](../../18_early_indicator_analysis/output/plt_30_360_bk.png)

- [Data Dictionary](https://github.com/PFS-Risk-DS/20241112_simple_model_test/blob/main/data_dictionary/data_dictionary.csv)
