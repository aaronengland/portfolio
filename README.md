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

A series of notebooks I built during onboarding that cover core data science competencies. These demonstrate breadth across the full stack — from writing Python libraries to deploying cloud infrastructure.

#### 1.1 GitHub Fundamentals (`01_github/`)

Setup and workflow for Git version control: cloning private repositories with personal access tokens, branching, committing, and pushing to remote.

#### 1.2 Python & Data Wrangling (`02_python/`)

Retrieves stock data via yfinance (AAPL, NVDA), builds pandas pipelines, and creates dual-axis visualizations (OHLC prices + volume). Progresses from standalone functions to a reusable class (`PullAndPlotStock`) with method chaining, demonstrating object-oriented design and code reusability.

#### 1.3 Custom Python Library (`03_python_library/`)

A pip-installable Python package hosted on GitHub. Includes a `setup.py`, package structure with `__init__.py`, and a custom `MinMaxScaler` class following scikit-learn's fit/transform pattern. Installable locally (`pip install -e .`) or remotely from GitHub.

#### 1.4 SQL & Cloud Data Integration (`04_sql/`)

Connects to Snowflake using RSA private key authentication (`.p8` key file converted to DER format via the `cryptography` library). Executes SQL queries, reads results into pandas DataFrames, and writes output to S3 as gzip-compressed Parquet files using boto3.

#### 1.5 Machine Learning (`05_ml/`)

**Supervised Learning — Single Models:** Implements 6 classification algorithms (Logistic Regression, Decision Tree, Random Forest, XGBoost, CatBoost, LightGBM) and 6 corresponding regression algorithms on the same data. Uses a custom MinMaxScaler for feature scaling and evaluates on train/test/holdout splits using ROC-AUC (classifiers) and Mean Absolute Error (regressors).

**Supervised Learning — Hyperparameter Tuning:** Systematically tunes each classifier and regressor across a range of hyperparameters (penalty type for Logistic Regression, max_depth for tree-based models). Plots performance curves across parameter values to visualize overfitting and identify optimal settings.

**Unsupervised Learning — K-Means Clustering:** Fits K-Means with a fixed cluster count, assigns labels, and analyzes cluster distributions and feature means. Then applies the elbow method (testing k=2 through k=20, plotting inertia) to determine the optimal number of clusters and characterizes the resulting segments.

#### 1.6 Time Series Forecasting (`06_forecasting/`)

Pulls historical AAPL stock data via yfinance and forecasts the next 10 business days. Compares a manually specified ARIMA(1,1,1) model against pmdarima's `auto_arima`, which searches across parameter combinations and selects by AIC. Generates forecasts with 95% confidence intervals and visualizes actual vs. predicted with upper/lower bounds.

#### 1.7 AWS Batch (`07_aws_batch/`)

**Single Job:** Writes a Python script, packages it in a Docker container, pushes the image to AWS ECR, and provisions AWS Batch infrastructure (compute environment with m5.large instances, job queue, job definition) using boto3. The job writes a DataFrame to S3.

**Parallel Array Job:** Extends the single-job pattern to run 10 jobs in parallel using AWS Batch array jobs. Each job reads its `AWS_BATCH_JOB_ARRAY_INDEX` environment variable and writes a uniquely-named output file to S3.

#### 1.8 AWS Lambda (`08_aws_lambda/`)

Creates a containerized Lambda function (based on the AWS Lambda Python 3.9 base image) that concatenates the 10 CSV files produced by the parallel batch job. The handler lists objects in the S3 prefix, reads each into a DataFrame, concatenates them, and writes the combined result back to S3. Deployed to Lambda with 512 MB memory and 60-second timeout.

#### 1.9 AWS Step Functions (`09_aws_step_function/`)

Builds a Step Functions state machine that orchestrates the entire pipeline end to end: Single Batch Job → Parallel Batch Jobs → Lambda Concatenation. Each step waits for the previous to complete before proceeding. The Lambda invocation includes retry logic (up to 3 retries with exponential backoff and full jitter). Infrastructure created via boto3.

#### 1.10 Flask Web Application (`09_web_app/`)

A Flask web app served on port 5000 with HTML templates, custom CSS, and frontend libraries (jQuery, DataTables for interactive tables, Plotly for charts). Includes responsive design with media queries, a loading spinner for async operations, and dynamic copyright year rendering. Dependencies include pandas, scikit-learn, optbinning, and plotly for backend data processing.

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
