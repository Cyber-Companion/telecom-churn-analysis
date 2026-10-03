-- ============================================================
-- 01_schema.sql — Telco Customer Churn: table definition
-- Dialect: PostgreSQL. Source: IBM telco-customer-churn-on-icp4d (open data)
-- 7,043 customers, 21 columns.
-- ============================================================

DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id       TEXT PRIMARY KEY,
    gender            TEXT NOT NULL,
    senior_citizen    INTEGER NOT NULL CHECK (senior_citizen IN (0, 1)),
    partner           TEXT NOT NULL,
    dependents        TEXT NOT NULL,
    tenure            INTEGER NOT NULL CHECK (tenure >= 0),
    phone_service     TEXT NOT NULL,
    multiple_lines    TEXT NOT NULL,
    internet_service  TEXT NOT NULL,
    online_security   TEXT NOT NULL,
    online_backup     TEXT NOT NULL,
    device_protection TEXT NOT NULL,
    tech_support      TEXT NOT NULL,
    streaming_tv      TEXT NOT NULL,
    streaming_movies  TEXT NOT NULL,
    contract          TEXT NOT NULL,
    paperless_billing TEXT NOT NULL,
    payment_method    TEXT NOT NULL,
    monthly_charges   NUMERIC(8, 2) NOT NULL,
    total_charges     NUMERIC(10, 2),          -- NULL for tenure-0 customers
    churn             TEXT NOT NULL CHECK (churn IN ('Yes', 'No'))
);

-- Load with: \copy customers FROM 'data/raw/Telco-Customer-Churn.csv' CSV HEADER;
-- (TotalCharges blanks land as empty strings; 02_data_cleaning.sql fixes them.)
