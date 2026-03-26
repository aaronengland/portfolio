# Aaron England — Data Science Portfolio

This portfolio contains selected work from my role as a data scientist at an auto lending company, where I built production credit risk models, deployed ML-powered web applications, and conducted strategic analyses that directly influenced business decisions.

> **Note:** Some outputs have been redacted to protect proprietary information.

---

## Technical Skills

**Languages & Querying:** Python, SQL (Snowflake)
**Machine Learning:** scikit-learn, CatBoost, XGBoost, LightGBM, OptBinning
**Data & Visualization:** pandas, NumPy, matplotlib, seaborn
**Cloud & Infrastructure:** AWS (Batch, Lambda, Step Functions, ECR, S3), Docker
**Web Development:** Flask, HTML/CSS/JavaScript
**Tools & Workflow:** Git/GitHub, Jupyter, pip packaging

---

## Projects

### 1. Onboarding — Foundational Skills (`01_onboarding/`)

A series of notebooks I built during onboarding that cover core data science competencies. These demonstrate breadth across the stack — from writing Python libraries to deploying cloud infrastructure.

| Topic | Description |
|---|---|
| **Python & Data Wrangling** | Stock data retrieval (yfinance), pandas pipelines, and visualization with matplotlib |
| **Custom Python Library** | Installable pip package with object-oriented design (fit/transform pattern for a custom MinMaxScaler) |
| **SQL** | Snowflake querying with RSA key authentication and programmatic data extraction |
| **Machine Learning** | Supervised learning (6 classifiers and regressors), hyperparameter tuning, and unsupervised clustering |
| **Time Series Forecasting** | ARIMA modeling with pmdarima's auto_arima for stock price forecasting with confidence intervals |
| **AWS Batch** | Containerized batch jobs — both single and parallel execution patterns using Docker + ECR |
| **AWS Lambda & Step Functions** | Serverless function deployment and orchestrated multi-step workflows |
| **Web Application** | Flask app with static frontend, deployed via Docker container |

---

### 2. Production Credit Risk Models (`02_models/`)

#### CatBoost Classification & Regression

End-to-end model development using CatBoost for both classification and regression tasks. Includes thorough exploratory data analysis (3-part EDA), feature engineering, data preparation, model training, and a parser utility for scoring new records.

#### Logistic Regression Scorecard (Probability of Default)

This was the centerpiece of my modeling work — a full production credit risk model built using logistic regression with 45+ binned features. The project spans the entire model lifecycle:

- **Data Preparation:** Feature engineering and extraction from credit bureau XML data sourced via Snowflake
- **Feature Selection:** Forward stepwise selection, multicollinearity testing, and binning via OptBinning
- **Model Training:** Logistic regression scorecard with bin-level probability contributions
- **Risk Quantification:** Probability of Default (PD), Loss Given Default (LGD) via LTV grids, and Expected Credit Net Loss (ECNL = PD × LGD)
- **Compliance & Fairness:** Disparate impact analysis across race, gender, and age to ensure fair lending standards
- **Model Governance:** Sensitivity analysis, swap-in/swap-out comparisons against alternative models, and performance monitoring
- **Deployment:** Scoring API built with Flask, deployed via AWS Lambda with S3 integration

---

### 3. Web Applications (`03_apps/`)

Three Flask-based web applications containerized with Docker and deployed to AWS Elastic Container Registry (ECR). These apps serve model predictions via REST APIs and include HTML/CSS/JavaScript frontends for interactive use. The applications demonstrate a full deployment pipeline: local development, containerization, image registry, and cloud hosting.

---

### 4. Strategic Analyses (`04_analyses/`)

#### Credit Builder Risk Analysis

An analysis I initiated that uncovered a major population shift in the company's loan portfolio. Credit builder accounts (e.g., Chime, Self) grew from under 15% to over 45% of funded accounts between 2021 and 2025, while consistently performing worse than traditional accounts. Key findings:

- **Quantified mispricing:** Models underestimated credit builder risk by 0.09 ECNL and overestimated traditional account risk by 0.02 ECNL
- **Root cause analysis:** Built a CatBoost classifier (AUC 0.937) to identify features distinguishing credit builder applicants — found that these accounts paradoxically exhibit traits associated with lower risk (more tradelines, more open-to-buy), masking their true performance
- **Business impact:** Presented findings to leadership, leading to policy recommendations for credit builder identification and risk adjustment

#### Funded Trends & Performance Monitoring

A data pipeline and analysis framework integrating multiple model generations (Gen 12, Gen 13) with Snowflake-sourced performance data. Includes credit builder tagging logic across 30+ institutions, model scoring across three risk components (AD, PD, LGD), and structured output for ongoing disparate impact monitoring.

---

## Repository Structure

```
├── 01_onboarding/
│   ├── 01_github/           # Version control basics
│   ├── 02_python/           # Python data wrangling & visualization
│   ├── 03_python_library/   # Custom pip-installable library
│   ├── 04_sql/              # Snowflake SQL querying
│   ├── 05_ml/               # Supervised & unsupervised ML
│   ├── 06_forecasting/      # ARIMA time series forecasting
│   ├── 07_aws_batch/        # Containerized batch jobs
│   ├── 08_aws_lambda/       # Serverless function deployment
│   ├── 09_aws_step_function/# Orchestrated multi-step workflows
│   └── 09_web_app/          # Flask web application
├── 02_models/
│   ├── 01_catboost/         # CatBoost classification & regression
│   └── 02_logistic_regression/  # Production PD scorecard
├── 03_apps/
│   ├── 01_app/              # Flask + Docker app
│   ├── 02_app/              # Flask + Docker app
│   └── 03_app/              # Flask + Docker app
└── 04_analyses/
    ├── 01_analysis/         # Credit builder risk analysis
    └── 02_analysis/         # Funded trends & monitoring
```
