-- Build gold_claude.crsp: the project's CRSP daily-return extract.
--
-- Source: crsp.daily_stock_returns (CIZ format) on researchdb, database
-- "splante". Window: 1925-12-31 through 1945-12-31, all stocks. This covers
-- the investment panel (1926-1940), the event-study estimation window
-- (July 1926 - April 1933), and the full daily return sample of the
-- event-study table (July 1926 - December 1945).
--
-- Any future script in this project that needs CRSP daily data should read
-- gold_claude.crsp, NOT crsp.daily_stock_returns and NOT WRDS.
--
-- Run with:
--   psql "postgresql://splante%40ads.ssc.wisc.edu@researchdb.ssc.wisc.edu/splante?sslmode=require&gssencmode=require" \
--        -v ON_ERROR_STOP=1 -f build_gold_claude_crsp.sql
--
-- Column mapping (CIZ -> legacy-style names):
--   dlycaldt -> date, dlyret -> ret, dlyretx -> retx (delisting returns are
--   already integrated into CIZ returns), dlyprc -> prc, dlyclose -> close,
--   dlycap -> cap (market cap, $ thousands), dlyvol -> vol,
--   dlyfacprc -> facprc, dlyorddivamt/dlynonorddivamt -> ordinary/
--   non-ordinary distribution amounts.

CREATE SCHEMA IF NOT EXISTS gold_claude;

DROP TABLE IF EXISTS gold_claude.crsp;

CREATE TABLE gold_claude.crsp AS
SELECT
    permno::int                          AS permno,
    dlycaldt::date                       AS date,
    NULLIF(dlyret,  '')::float8          AS ret,
    NULLIF(dlyretx, '')::float8          AS retx,
    dlyprc                               AS prc,
    dlyclose                             AS close,
    dlycap                               AS cap,
    dlyvol                               AS vol,
    dlyfacprc                            AS facprc,
    dlyorddivamt                         AS orddivamt,
    dlynonorddivamt                      AS nonorddivamt
FROM crsp.daily_stock_returns
WHERE dlycaldt BETWEEN '1925-12-31' AND '1945-12-31';

COMMENT ON TABLE gold_claude.crsp IS
    'CRSP daily returns 1925-12-31..1945-12-31, all stocks, extracted from '
    'crsp.daily_stock_returns (CIZ). Built by code/refactor/sql/build_gold_claude_crsp.sql '
    'in the gold-clause-abrogation-and-investment repo.';

CREATE INDEX ix_gold_claude_crsp_permno_date ON gold_claude.crsp (permno, date);
CREATE INDEX ix_gold_claude_crsp_date        ON gold_claude.crsp (date);

CLUSTER gold_claude.crsp USING ix_gold_claude_crsp_permno_date;
ANALYZE gold_claude.crsp;

-- ---------------------------------------------------------------------------
-- gold_claude.crsp_names: security-info / names history (permno-permco map)
-- for the permnos in gold_claude.crsp. Source: crsp.security_info_history
-- (CIZ StkSecurityInfoHist). Each row is valid from secinfostartdt to
-- secinfoenddt; spells starting after 1945 are dropped as irrelevant.
-- ---------------------------------------------------------------------------

DROP TABLE IF EXISTS gold_claude.crsp_names;

CREATE TABLE gold_claude.crsp_names AS
SELECT
    s.permno::int              AS permno,
    s.permco::int              AS permco,
    s.secinfostartdt::date     AS secinfostartdt,
    s.secinfoenddt::date       AS secinfoenddt,
    s.securitybegdt::date      AS securitybegdt,
    s.securityenddt::date      AS securityenddt,
    s.issuernm,
    s.securitynm,
    s.shareclass,
    s.ticker,
    s.primaryexch,
    s.siccd::int               AS siccd,
    s.securitytype,
    s.securitysubtype,
    s.sharetype,
    s.usincflg,
    s.issuertype,
    s.delactiontype,
    s.delstatustype,
    s.delreasontype,
    s.cusip,
    s.hdrcusip
FROM crsp.security_info_history s
WHERE s.permno IN (SELECT permno FROM gold_claude.crsp)
  AND s.secinfostartdt <= '1945-12-31';

COMMENT ON TABLE gold_claude.crsp_names IS
    'CRSP security-info/names history (incl. permno-permco map) for the '
    'permnos in gold_claude.crsp, spells starting on or before 1945-12-31. '
    'Source: crsp.security_info_history (CIZ). Built by '
    'code/refactor/sql/build_gold_claude_crsp.sql.';

CREATE INDEX ix_gold_claude_crsp_names_permno ON gold_claude.crsp_names (permno);
CREATE INDEX ix_gold_claude_crsp_names_permco ON gold_claude.crsp_names (permco);

CLUSTER gold_claude.crsp_names USING ix_gold_claude_crsp_names_permno;
ANALYZE gold_claude.crsp_names;
