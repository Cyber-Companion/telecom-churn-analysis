-- ============================================================
-- 02_data_cleaning.sql — Telco Customer Churn: data quality fixes
-- Run after 01_schema.sql. Raw data is never mutated.
-- ============================================================

-- Issue: 11 rows have TotalCharges = '' (blank). All 11 have tenure = 0,
-- i.e. brand-new customers with no billing history yet.
-- Rule: load blanks as NULL (a missing total is not $0), keep the rows.
DROP TABLE IF EXISTS customers_clean;
CREATE TABLE customers_clean AS
SELECT
    customer_id, gender, senior_citizen, partner, dependents, tenure,
    phone_service, multiple_lines, internet_service, online_security,
    online_backup, device_protection, tech_support, streaming_tv,
    streaming_movies, contract, paperless_billing, payment_method,
    monthly_charges,
    NULLIF(TRIM(total_charges::text), '')::NUMERIC(10, 2) AS total_charges,
    churn,
    -- derived flags used across the analysis
    (churn = 'Yes') AS is_churned,
    CASE
        WHEN tenure <= 6  THEN '0-6 months'
        WHEN tenure <= 12 THEN '7-12 months'
        WHEN tenure <= 24 THEN '13-24 months'
        WHEN tenure <= 48 THEN '25-48 months'
        ELSE '49+ months'
    END AS tenure_band
FROM customers;

-- Validation checks (all should return 0)
SELECT COUNT(*) AS blank_totals_left
FROM customers_clean
WHERE total_charges IS NULL AND tenure > 0;

SELECT COUNT(*) AS bad_churn_flags
FROM customers_clean
WHERE churn NOT IN ('Yes', 'No');

SELECT COUNT(*) AS dup_customers
FROM (SELECT customer_id FROM customers_clean GROUP BY 1 HAVING COUNT(*) > 1) t;
