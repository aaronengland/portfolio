# Credit Builder Analysis

Aaron England (2025)

#### Contents:
- Abstract
- Introduction
- Methods
- Results
- Discussion
- Conclusion

#### Abstract:

The use of credit builders (i.e., Chime) has been growing rapidly over time with an estimated 31.8 million users by the end of 2024.

This growth has been reflected in the company's funded accounts as they were sub 15% in 2021 and are now over 45% in 2025 (see Image 3). Thus, **the funded population has shifted and continues to shift rapidly**.

Anecdotal evidence suggests that accounts with credit builders are much riskier than traditional accounts.

Performance of accounts with credit builders has been worse by about 0.08 CNL at 24 months (estimated 0.188 at 72 months). The models underestimate risk of credit builder accounts (0.0928 ECNL) and overestimate the risk of traditional accounts (0.0236 ECNL; see Image 4).

This is because credit builder accounts, on average, have features that the models (and common sense) see as less-risky:
- More open-to-buy
- More tradelines
- More satisfactory trades
- etc.

The lack of awareness of the riskiness and growing prominence of accounts with credit builders, along with attributes in the models that see these accounts favorably, needs to be addressed.

Possible solutions include auto-declining or penalizing credit builder accounts.

---

#### Introduction:

The use of credit-building products, including services like Chime's Credit Builder, has been increasing over time. Chime, a prominent neobank, has experienced significant growth in its user base, expanding from **0.5 million users in 2017 to 22.3 million users in 2023**. This growth reflects a broader trend in the adoption of digital banking services and credit-building tools (see Image 1).

![Chime Users](./img/chime_users.PNG)
**Image 1**. *Chime customers have increased from 0.5 million in 2017 to 22.3 million in 2023.*

According to a report by the Federal Reserve, as of early 2024, over 3 million individuals held secured small-dollar products, such as secured credit cards and credit-builder loans, with a median origination amount of $500. **These products are primarily utilized by younger, nonprime borrowers seeking to establish or improve their credit scores**.

Chime's Credit Builder card is designed to help users build credit by reporting on-time payments to major credit bureaus. The average Chime member sees a 30-point increase in their credit score after approximately eight months of using the Credit Builder card.

Overall, the increasing adoption of credit-building products like Chime's Credit Builder indicates a growing awareness and utilization of tools aimed at improving creditworthiness among consumers.

Additionally, anecdotal evidence suggests that accounts with credit builders are much riskier than traditional accounts.

The company had not treated credit builder customers any differently from traditional accounts and had no insight into its impact on the accounts that were funded.

Thus, the purpose of this analysis was to investigate the adoption of credit builders like Chime among funded accounts. More specifically, the proportion and rate over time and subsequent performance. A secondary purpose aimed to calculate the cause and extent of mispricing using the lens of credit builders relative to non-credit builders.

---

### Methods:

Using the most recent [available] payload (application) for every funded [indirect] account with a request date from 2021-07-26 through 2024-11-26 (N<sub>Accounts</sub> = 78074; N<sub>Debtors</sub> = 94397), the tradeline institutions were extracted from the TransUnion XML (TUXML). An account was deemed as having a credit builder if any of the institutions associated with credit builders were in the list of institutions for the debtor or codebtor (see Appendix I).

Delinquency and charge-off severity targets were joined to the account. After extracting the data from each payload, each account was scored with the classification and regression models.

Total fundings, proportion of funded accounts with a credit builder, and mean charge-off severity at 24 months were calculated by month. The proportion of funded accounts with a credit builder debtor has grown from sub 15% in 2021 to over 45% in 2025.

Additionally, charge-off severity is positively correlated with the proportion of funded credit builders (see Image 2).

![Our Fundings](./03_analysis/output/plt_fundings.png)
**Image 2**. *Funded accounts from 2021-07-26 through 2024-11-26.*

The accounts newer than 24 months on books were removed to allow the necessary maturation duration (N<sub>Accounts</sub> = 33443; N<sub>Debtors</sub> = 41392). Mean predicted and actual charge-off severity for accounts with a credit builder and without a credit builder were calculated. Accounts with a credit builder have higher delinquency rates and greater charge-off severity than accounts without a credit builder. The models underestimate this difference (see Image 3).

![Performance](./img/performance.PNG)
**Image 3**. *Predicted and actual delinquency and charge-off severity by accounts with and without credit builder(s).*

Next, using the same data (N<sub>Accounts</sub> = 78074; N<sub>Debtors</sub> = 94397), a CatBoost model was fit to predict if a debtor has a credit builder (i.e., a supervised classification problem), and the feature importance was derived (*Note*: The AUC of this model was 0.937 after removing blatantly leaky features). The mean of each feature was then grouped by the target (i.e., credit builder or not; see Image 4). Many of the top features where a value indicates a credit builder are also associated with less risk in the models, resulting in the underestimation of risk.

![Features](./img/features.PNG)
**Image 4**. *Mean feature values grouped by has a credit builder or not in order of importance.*

---

### Results

The company's funded accounts were sub 15% credit builders in 2021 and are now over 45% in 2025 (see Image 2). Thus, **the funded population has shifted and continues to shift**. Delinquency and loss are positively related to the proportion of funded credit builder accounts.

The rapid shifting of the population and the increasing adoption of credit builder customers since 2021 renders the data used for older models questionably valid for scoring these accounts today.

The increasing proportion of accounts with credit builders also leaves the data used for newer models suspect.

Performance of accounts with credit builders has been worse by about 0.08 CNL at 24 months (estimated 0.188 at 72 months). The models underestimate risk of credit builder accounts (0.0928 ECNL) and overestimate the risk of traditional accounts (0.0236 ECNL; see Image 3).

Credit builder accounts, on average, have features that the models (and common sense) see as less-risky:
- More open-to-buy
- More tradelines
- More satisfactory trades
- etc.

![Wolf in Sheeps Clothing](./img/wolf_in_sheeps_clothing.PNG)
**Image 5**. *Credit builder customers appear as credit-worthy applicants but are riskier than anticipated; making them "Wolves in sheep's clothing".*

---

### Discussion

Measures must be taken quickly to address the shift in the funded population toward credit builder customers. Frequent and consistent monitoring of this group is critical to avoid unknowingly transitioning from a traditional lender to a credit builder lender.

Industry peers confirmed similar findings — competitors had already identified credit builders as higher risk and made underwriting changes to penalize or exclude them. One peer noted performance was "really bad" and had cut them out years prior. Another penalizes all credit builder tradelines during underwriting.

Thus, the regression model is multiplying ECNL by 1.203 on accounts with at least one credit builder debtor. Meanwhile, it is multiplying ECNL by 0.936 on accounts without at least one credit builder debtor.

*Note: these factors were calculated by dividing the charge-off at 24 months by the ECNL at 24 months.*

---

#### Conclusion

The company was years late to the identification and remedy of credit builder accounts and, as a result, had been booking risky, volatile business.

Changes to policy in an attempt to shape the portfolio's identity, model improvements, and enhanced collections efforts will be done in vain until the treatment of credit builder accounts is addressed.

---

#### Appendix I:

List of credit builder institutions:
```
'CURRENT',
'SELF',
'CHIME-STRIDE',
'CHIMEFINAL',
'SELF FIN',
'SELF/LEAD',
'SELFINC/LEAD',
'SBNASELFLNDR',
'SBNA SELF',
'CHIME',
'CLEO',
'CLEO AI',
'VARO',
'ATLAS',
'ATLCAPBKSELF',
'POSSIBLE',
'POSSIBLE FIN',
'KIKOFF',
'SUPER.COM',
'STEP',
'STEP MOBILE',
'BRIGHT',
'BRIGHT BLDR',
'FIG TECH INC',
'SELF/RENT',
'SELFBILLSE',
'PROGRESSRES',
'FLEX',
'FLEXFINANCE',
```
