"""Builds python/analysis_notebook.ipynb for the telco churn project.
Run from project root: python python/build_notebook.py
"""
import json

NB_PATH = "python/analysis_notebook.ipynb"


def md(lines):
    return {"cell_type": "markdown", "metadata": {},
            "source": [l + "\n" for l in lines]}


def code(lines):
    return {"cell_type": "code", "metadata": {},
            "execution_count": None, "outputs": [],
            "source": [l + "\n" for l in lines]}


cells = [
    md(["# Telecom Customer Churn Analysis",
        "Which customers leave, why, and how much revenue is at risk?",
        "",
        "**Business questions:**",
        "1. What is the overall churn rate?",
        "2. Which contract, payment, and service factors drive churn?",
        "3. When in the customer lifecycle does churn happen?",
        "4. How much monthly revenue is at risk?",
        "5. Which segment should retention target first?",
        "",
        "_Dataset: IBM telco customer churn, 7,043 customers (open data)._"]),
    code(["import pandas as pd, numpy as np, matplotlib.pyplot as plt",
          "plt.style.use('seaborn-v0_8-whitegrid')",
          "df = pd.read_csv('../data/raw/Telco-Customer-Churn.csv')  # run from python/, or adjust",
          "print(df.shape); print(df.dtypes.value_counts().to_string())"]),
    md(["## 1. Data cleaning",
        "- **11 blank `TotalCharges`** — all have `tenure == 0` (brand-new customers, "
        "no billing history) → coerced to NaN, rows kept.",
        "- `SeniorCitizen` is 0/1 → kept numeric; `Churn` Yes/No → boolean flag.",
        "- No duplicate customers; no other nulls. (Mirrors `sql/02_data_cleaning.sql`.)"]),
    code(["df['TotalCharges'] = pd.to_numeric(df['TotalCharges'].replace(' ', np.nan), errors='coerce')",
          "print('TotalCharges NaN:', df['TotalCharges'].isna().sum())",
          "df['is_churned'] = df['Churn'] == 'Yes'",
          "df['tenure_band'] = pd.cut(df['tenure'], [0,6,12,24,48,100],",
          "    labels=['0-6','7-12','13-24','25-48','49+'])",
          "print('overall churn rate: %.1f%%' % (df['is_churned'].mean()*100))"]),
    md(["## 2. Churn by contract — the 15x gap"]),
    code(["g = df.groupby('Contract')['is_churned'].mean().mul(100).round(1).sort_values(ascending=False)",
          "print(g.to_string())",
          "g.plot.barh(color='#e76f51', figsize=(7,3), title='Churn rate by contract (%)')",
          "plt.tight_layout(); plt.show()"]),
    md(["## 3. Payment method & internet service"]),
    code(["for c in ['PaymentMethod','InternetService']:",
          "    g = df.groupby(c)['is_churned'].mean().mul(100).round(1).sort_values(ascending=False)",
          "    print(f'-- {c} --'); print(g.to_string()); print()"]),
    md(["## 4. When do customers leave? (tenure)"]),
    code(["g = df.groupby('tenure_band', observed=True)['is_churned'].mean().mul(100).round(1)",
          "print(g.to_string())",
          "g.plot.bar(color='#2a9d8f', figsize=(8,4), title='Churn rate by tenure band (%)')",
          "plt.tight_layout(); plt.show()"]),
    md(["## 5. Who churns? demographics & add-ons"]),
    code(["df['senior'] = np.where(df['SeniorCitizen']==1,'senior','non-senior')",
          "for c in ['senior','Partner','Dependents','PaperlessBilling','TechSupport']:",
          "    g = df.groupby(c)['is_churned'].mean().mul(100).round(1).sort_values(ascending=False)",
          "    print(f'-- {c} --'); print(g.to_string()); print()"]),
    md(["## 6. Revenue at risk"]),
    code(["lost = df.loc[df.is_churned,'MonthlyCharges'].sum()",
          "total = df['MonthlyCharges'].sum()",
          "print(f'Monthly revenue lost to churn: ${lost:,.0f} ({lost/total*100:.1f}% of total)')",
          "print('Avg monthly charges — churned: $%.2f | stayed: $%.2f' % (",
          "    df.loc[df.is_churned,'MonthlyCharges'].mean(), df.loc[~df.is_churned,'MonthlyCharges'].mean()))"]),
    md(["## 7. The highest-risk segment",
        "Month-to-month + electronic check + tenure ≤ 12 months. "
        "Small enough to target, large enough to matter."]),
    code(["seg = df[(df.Contract=='Month-to-month')&(df.PaymentMethod=='Electronic check')&(df.tenure<=12)]",
          "print(f'Segment size: {len(seg):,} ({len(seg)/len(df)*100:.1f}% of base)')",
          "print('Segment churn rate: %.1f%%' % (seg['is_churned'].mean()*100))",
          "print('Share of all churners: %.1f%%' % (seg['is_churned'].sum()/df['is_churned'].sum()*100))",
          "print('Monthly revenue in segment: $%.0f' % seg['MonthlyCharges'].sum())"]),
    md(["## Key findings & recommendations",
        "1. **26.5% churn rate.** Month-to-month contracts churn at **42.7% vs 2.8%** "
        "for two-year — a 15x gap.",
        "2. **Electronic check = 45.3% churn** vs 15.2% for automatic credit card.",
        "3. **Fiber optic 41.9%** vs DSL 19.0% — the premium product has the worst retention.",
        "4. **53.3% of customers churn in the first 6 months**; only 9.5% after 4 years.",
        "5. **Tech support cuts churn 41.6% → 15.2%.** Seniors churn at 41.7%.",
        "6. **$139K/month (30.5%) of revenue is at risk** — and churned customers paid "
        "MORE ($74.44 vs $61.27).",
        "7. **Target segment:** month-to-month + electronic check + ≤12 months tenure — "
        "13.5% of base, **63.1% churn**, one-third of all churners.",
        "",
        "**Recommendations:** push annual contracts with a discount, migrate electronic-check "
        "users to autopay, bundle free tech support for fiber customers, and run a 90-day "
        "onboarding save program for new customers."]),
]

nb = {"nbformat": 4, "nbformat_minor": 5,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                 "name": "python3"}},
      "cells": cells}
with open(NB_PATH, "w") as fh:
    json.dump(nb, fh, indent=1)
print("notebook written:", NB_PATH)
