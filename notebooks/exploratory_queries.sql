-- ============================================================
-- N100 FINANCIAL INTELLIGENCE PLATFORM
-- Sprint 1 - Day 07
-- Exploratory SQL Queries
-- ============================================================


-- ============================================================
-- Query 1: Total number of companies
-- Expected result: 92
-- ============================================================

SELECT COUNT(*) AS total_companies
FROM companies;


-- ============================================================
-- Query 2: List companies with their sector information
-- ============================================================

SELECT
    c.id AS company_id,
    c.company_name,
    s.broad_sector,
    s.sub_sector,
    s.market_cap_category
FROM companies c
LEFT JOIN sectors s
    ON c.id = s.company_id
ORDER BY s.broad_sector, c.company_name;


-- ============================================================
-- Query 3: Companies with highest ROE from company master
-- ============================================================

SELECT
    id AS company_id,
    company_name,
    roe_percentage,
    roce_percentage
FROM companies
WHERE roe_percentage IS NOT NULL
ORDER BY roe_percentage DESC
LIMIT 10;


-- ============================================================
-- Query 4: Latest Profit & Loss records
-- ============================================================

SELECT
    p.company_id,
    c.company_name,
    p.year,
    p.sales,
    p.operating_profit,
    p.net_profit,
    p.eps
FROM profitandloss p
JOIN companies c
    ON p.company_id = c.id
ORDER BY p.year DESC, p.sales DESC
LIMIT 20;


-- ============================================================
-- Query 5: Top companies by latest available sales
-- ============================================================

SELECT
    p.company_id,
    c.company_name,
    p.year,
    p.sales,
    p.net_profit
FROM profitandloss p
JOIN companies c
    ON p.company_id = c.id
WHERE p.year = (
    SELECT MAX(p2.year)
    FROM profitandloss p2
    WHERE p2.company_id = p.company_id
)
ORDER BY p.sales DESC
LIMIT 10;


-- ============================================================
-- Query 6: Companies with highest borrowings
-- ============================================================

SELECT
    b.company_id,
    c.company_name,
    b.year,
    b.borrowings,
    b.total_assets,
    b.total_liabilities
FROM balancesheet b
JOIN companies c
    ON b.company_id = c.id
WHERE b.year = (
    SELECT MAX(b2.year)
    FROM balancesheet b2
    WHERE b2.company_id = b.company_id
)
ORDER BY b.borrowings DESC
LIMIT 10;


-- ============================================================
-- Query 7: Latest cash flow position by company
-- ============================================================

SELECT
    cf.company_id,
    c.company_name,
    cf.year,
    cf.operating_activity,
    cf.investing_activity,
    cf.financing_activity,
    cf.net_cash_flow
FROM cashflow cf
JOIN companies c
    ON cf.company_id = c.id
WHERE cf.year = (
    SELECT MAX(cf2.year)
    FROM cashflow cf2
    WHERE cf2.company_id = cf.company_id
)
ORDER BY cf.operating_activity DESC
LIMIT 20;


-- ============================================================
-- Query 8: Companies with less than 5 years of P&L data
-- Useful for manual data-quality review
-- ============================================================

SELECT
    p.company_id,
    c.company_name,
    COUNT(DISTINCT p.year) AS years_available
FROM profitandloss p
JOIN companies c
    ON p.company_id = c.id
GROUP BY
    p.company_id,
    c.company_name
HAVING COUNT(DISTINCT p.year) < 5
ORDER BY years_available ASC;


-- ============================================================
-- Query 9: Financial ratio overview
-- ============================================================

SELECT
    fr.company_id,
    c.company_name,
    fr.year,
    fr.net_profit_margin_pct,
    fr.operating_profit_margin_pct,
    fr.return_on_equity_pct,
    fr.debt_to_equity,
    fr.interest_coverage,
    fr.asset_turnover,
    fr.free_cash_flow_cr
FROM financial_ratios fr
JOIN companies c
    ON fr.company_id = c.id
ORDER BY
    fr.return_on_equity_pct DESC
LIMIT 20;


-- ============================================================
-- Query 10: Data coverage summary for major tables
-- ============================================================

SELECT
    'companies' AS table_name,
    COUNT(*) AS row_count
FROM companies

UNION ALL

SELECT
    'profitandloss',
    COUNT(*)
FROM profitandloss

UNION ALL

SELECT
    'balancesheet',
    COUNT(*)
FROM balancesheet

UNION ALL

SELECT
    'cashflow',
    COUNT(*)
FROM cashflow

UNION ALL

SELECT
    'analysis',
    COUNT(*)
FROM analysis

UNION ALL

SELECT
    'documents',
    COUNT(*)
FROM documents

UNION ALL

SELECT
    'prosandcons',
    COUNT(*)
FROM prosandcons

UNION ALL

SELECT
    'sectors',
    COUNT(*)
FROM sectors

UNION ALL

SELECT
    'stock_prices',
    COUNT(*)
FROM stock_prices

UNION ALL

SELECT
    'financial_ratios',
    COUNT(*)
FROM financial_ratios;