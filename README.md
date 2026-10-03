# Telecom Customer Churn Analysis

Which customers leave, why, and how much revenue is at risk?
**SQL → Python → interactive dashboard.**

## Business questions

1. What is the overall churn rate?
2. Which contract, payment, and service factors drive churn?
3. When in the customer lifecycle does churn happen?
4. How much monthly revenue is at risk?
5. Which segment should a retention program target first?

## Dataset

IBM telco customer churn (open data), 7,043 customers × 21 columns:
https://github.com/IBM/telco-customer-churn-on-icp4d

Run `python python/download_data.py` to fetch `data/raw/Telco-Customer-Churn.csv`.

## Tech stack

- **SQL (PostgreSQL)** — schema, data cleaning, business analysis (`sql/`)
- **Python (pandas, NumPy, matplotlib)** — EDA notebook (`python/analysis_notebook.ipynb`)
- **Plotly** — interactive dashboard (`dashboard/telco_churn_dashboard.html`, open in browser)

## Project structure

```
├── sql/
│   ├── 01_schema.sql        # table definition (PostgreSQL)
│   ├── 02_data_cleaning.sql # documented data-quality fixes
│   └── 03_analysis.sql      # 10 business-question queries
├── python/
│   ├── download_data.py     # fetches the raw CSV
│   ├── build_notebook.py    # regenerates the EDA notebook
│   ├── build_dashboard.py   # regenerates the HTML dashboard
│   └── analysis_notebook.ipynb
├── dashboard/
│   ├── telco_churn_dashboard.html  # finished dashboard (open in browser)
│   └── preview.png
└── README.md
```

## Methodology

1. **Profile**: 7,043 rows, no duplicates, no nulls — but 11 blank `TotalCharges`.
2. **Clean** (documented in `sql/02_data_cleaning.sql`): the 11 blanks all belong to
   `tenure = 0` customers (no billing history yet) → coerced to NULL, rows kept;
   derived `is_churned` flag and `tenure_band`.
3. **Analyze** in SQL (10 queries) and Python (EDA notebook).
4. **Visualize**: 3-page interactive dashboard.

## Key findings

- **26.5% churn rate** (1,869 of 7,043 customers).
- **Contract is the #1 driver**: month-to-month **42.7%** vs two-year **2.8%** — a 15x gap.
- **Electronic check = 45.3% churn** vs 15.2% for automatic credit card.
- **Fiber optic 41.9%** vs DSL 19.0% — the premium product retains worst.
- **53.3% churn in the first 6 months**; only 9.5% after 4 years.
- **Tech support cuts churn 41.6% → 15.2%.** Seniors churn at 41.7% vs 23.6%.
- **$139,131/month (30.5%) of revenue is at risk** — and churned customers paid
  *more* ($74.44 vs $61.27): the company loses high-value customers.
- **High-risk segment** (month-to-month + electronic check + tenure ≤ 12 mo):
  954 customers (13.5% of base) at **63.1% churn** — one-third of all churners.

## Recommendations

1. **Push annual contracts** with a first-year discount — the 15x contract gap is
   the biggest lever.
2. **Migrate electronic-check users to autopay** (in-app nudge + small incentive).
3. **Bundle free tech support for fiber customers** (41.6% → 15.2%).
4. **90-day onboarding save program**: more than half of churn happens in month 0–6.
5. **Target the high-risk segment first** — cutting its churn to 30% recovers
   **$21,871/month**.

## Reproduce

```bash
python python/download_data.py    # fetch raw data
python python/build_notebook.py   # build the EDA notebook
python python/build_dashboard.py  # build the dashboard
# then run sql/01_schema.sql → 02 → 03 in PostgreSQL, or open the notebook
```

## Author

Adnan Habib — entry-level Data Analyst
(SQL · Python · Power BI · Excel)
