# Direct Lending Model (i.e., DLv2)

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
- Additional Information

---

## Overview

- ECNL = Probability of Default (PD) x Loss Given Default (LGD)
- Where:
	- PD = Probability of going 60+ days past due (DPD) and a positive net charge-off in the first 720 days (24 months) on books
	- LGD = Average charge-off severity by LTV bin (i.e., LTV grid)

---

## Data

- Bad Definition: 60+ DPD in the first 720 days (24 months) on books and a positive net charge-off
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

- [Feature Selection](https://github.com/PFS-Risk-DS/20241112_simple_model_test/blob/main/14_60_in_720_dl_test/02_model/notebook.ipynb)
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

![Feature Selection](../../14_60_in_720_dl_test/02_model/output/plt_forward_stepwise.png)
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

![LTV Bins Original](../../create_grid/04_60_in_720_chargeoff_dl/output/plt_bins_original.png)

---

## Performance

![PD](../13_ecnl_evaluation/output/plt_pd.png)
![ECNL](../13_ecnl_evaluation/output/plt_ecnl.png)

---

## Identity

Overall
![Overall](../17_identity/output/plt_tree_overall.png)

---

## Swap-in swap-out

![Distribution Comparisons](../10_swap_in_swap_out/output/plt_distributions.png)
![Correlation PD](../10_swap_in_swap_out/output/plt_correlation_pd.png)
![Correlation LGD](../10_swap_in_swap_out/output/plt_correlation_lgd.png)
![Correlation](../10_swap_in_swap_out/output/plt_correlation.png)
![Swap in Swap out](../10_swap_in_swap_out/output/plt_swap_in_swap_out.png)
![Swap in Swap out Tier Proportion](../16_swap_in_swap_out_plots/output/plt_stacked_tier.png)
![Swap in Swap out Median Income](../16_swap_in_swap_out_plots/output/plt_stacked_income.png)
![Correlation LTV](../10_swap_in_swap_out/output/plt_correlation_ltv_ecnl.png)
![DLv2 Mean LTV](../16_swap_in_swap_out_plots/output/plt_stacked_ltv.png)
![DLv2 Mean Miles ODO](../16_swap_in_swap_out_plots/output/plt_stacked_miles_odometer.png)

---

## Local Dark Scoring

- [Predictions Samples](https://github.com/PFS-Risk-DS/20241112_simple_model_test/blob/main/13_60_in_720_dl/11_show_sample/output)

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

## Additional Information

- [Detailed Bins](https://github.com/PFS-Risk-DS/20241112_simple_model_test/blob/main/show_bins/output/df_bins_direct.csv)

- [Adverse Action](https://github.com/PFS-Risk-DS/20241112_simple_model_test/blob/main/get_aa_dfs/output/df_aa_direct.csv)

- [Imputations](https://github.com/PFS-Risk-DS/20241112_simple_model_test/blob/main/imputations/output/df_imputations_direct.csv)

- [EDA](https://github.com/PFS-Risk-DS/20241112_simple_model_test/blob/main/eda/notebook.ipynb)

- [Data Dictionary](https://github.com/PFS-Risk-DS/20241112_simple_model_test/blob/main/data_dictionary/data_dictionary.csv)
