-- ============================================================
-- 03_analysis.sql — Telco Customer Churn: business analysis
-- Run after 01_schema.sql and 02_data_cleaning.sql.
-- ============================================================

-- ---------- Q1. Headline churn rate ----------
SELECT
    COUNT(*) AS customers,
    SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) AS churned,
    ROUND(100.0 * SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) / COUNT(*), 1)
        AS churn_rate_pct
FROM customers_clean;

-- ---------- Q2. Churn by contract type ----------
SELECT
    contract,
    COUNT(*) AS customers,
    ROUND(100.0 * SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) / COUNT(*), 1)
        AS churn_rate_pct
FROM customers_clean
GROUP BY 1
ORDER BY churn_rate_pct DESC;

-- ---------- Q3. Churn by payment method ----------
SELECT
    payment_method,
    COUNT(*) AS customers,
    ROUND(100.0 * SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) / COUNT(*), 1)
        AS churn_rate_pct
FROM customers_clean
GROUP BY 1
ORDER BY churn_rate_pct DESC;

-- ---------- Q4. Churn by internet service ----------
SELECT
    internet_service,
    COUNT(*) AS customers,
    ROUND(100.0 * SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) / COUNT(*), 1)
        AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges
FROM customers_clean
GROUP BY 1
ORDER BY churn_rate_pct DESC;

-- ---------- Q5. Churn by tenure band: when do customers leave? ----------
SELECT
    tenure_band,
    COUNT(*) AS customers,
    ROUND(100.0 * SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) / COUNT(*), 1)
        AS churn_rate_pct
FROM customers_clean
GROUP BY 1
ORDER BY MIN(tenure);

-- ---------- Q6. Churn by demographics ----------
SELECT 'senior_citizen' AS segment,
       CASE WHEN senior_citizen = 1 THEN 'senior' ELSE 'non-senior' END AS value,
       COUNT(*) AS customers,
       ROUND(100.0 * SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) / COUNT(*), 1)
           AS churn_rate_pct
FROM customers_clean GROUP BY 2
UNION ALL
SELECT 'partner', partner, COUNT(*),
       ROUND(100.0 * SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) / COUNT(*), 1)
FROM customers_clean GROUP BY 2
UNION ALL
SELECT 'dependents', dependents, COUNT(*),
       ROUND(100.0 * SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) / COUNT(*), 1)
FROM customers_clean GROUP BY 2
UNION ALL
SELECT 'paperless_billing', paperless_billing, COUNT(*),
       ROUND(100.0 * SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) / COUNT(*), 1)
FROM customers_clean GROUP BY 2
ORDER BY 1, 4 DESC;

-- ---------- Q7. Revenue at risk ----------
SELECT
    ROUND(SUM(CASE WHEN is_churned THEN monthly_charges ELSE 0 END), 0)
        AS monthly_revenue_lost,
    ROUND(SUM(monthly_charges), 0) AS monthly_revenue_total,
    ROUND(100.0 * SUM(CASE WHEN is_churned THEN monthly_charges ELSE 0 END)
          / SUM(monthly_charges), 1) AS pct_revenue_at_risk,
    ROUND(AVG(CASE WHEN is_churned THEN monthly_charges END), 2)
        AS avg_monthly_churned,
    ROUND(AVG(CASE WHEN NOT is_churned THEN monthly_charges END), 2)
        AS avg_monthly_stayed
FROM customers_clean;

-- ---------- Q8. The highest-risk segment (actionable) ----------
-- Month-to-month + electronic check + short tenure: who are they?
SELECT
    COUNT(*) AS customers_in_segment,
    SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) AS churned,
    ROUND(100.0 * SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) / COUNT(*), 1)
        AS churn_rate_pct,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers_clean), 1)
        AS pct_of_base
FROM customers_clean
WHERE contract = 'Month-to-month'
  AND payment_method = 'Electronic check'
  AND tenure <= 12;

-- ---------- Q9. Add-on services: does tech support retain? ----------
SELECT
    tech_support,
    COUNT(*) AS customers,
    ROUND(100.0 * SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) / COUNT(*), 1)
        AS churn_rate_pct
FROM customers_clean
WHERE internet_service <> 'No'
GROUP BY 1
ORDER BY churn_rate_pct DESC;

-- ---------- Q10. Tenure vs monthly charges for churned customers ----------
SELECT
    tenure_band,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges,
    SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) AS churned_customers
FROM customers_clean
GROUP BY 1
ORDER BY MIN(tenure);
