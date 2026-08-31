-- STATION V
-- Migration 009: Country systemic tiers for Global Risk V1
--
-- Tier classification is structural and independent from Country Risk.
-- The Global Risk engine uses three tiers:
--   Tier 1 = systemic global powers
--   Tier 2 = major / strategically relevant international actors
--   Tier 3 = remaining countries in the STATION V universe
--
-- T2-A, T2-B and T2 strategic are analytical distinctions only.
-- They are represented internally as tier = 2.

BEGIN;

CREATE TABLE IF NOT EXISTS country_tiers (
    country_id BIGINT PRIMARY KEY,
    tier SMALLINT NOT NULL,

    CONSTRAINT country_tiers_country_fk
        FOREIGN KEY (country_id)
        REFERENCES countries(id)
        ON DELETE CASCADE,

    CONSTRAINT country_tiers_tier_valid
        CHECK (tier IN (1, 2, 3))
);

-- Tier 1: systemic global powers
INSERT INTO country_tiers (country_id, tier)
SELECT id, 1
FROM countries
WHERE iso2 IN (
    'US',
    'CN',
    'RU',
    'IN',
    'JP',
    'DE',
    'FR',
    'GB'
)
ON CONFLICT (country_id)
DO UPDATE SET tier = EXCLUDED.tier;

-- Tier 2-A: major international actors
INSERT INTO country_tiers (country_id, tier)
SELECT id, 2
FROM countries
WHERE iso2 IN (
    'IT',
    'CA',
    'BR',
    'AU',
    'TR',
    'SA',
    'ES',
    'MX',
    'PL',
    'ID',
    'NL',
    'IL'
)
ON CONFLICT (country_id)
DO UPDATE SET tier = EXCLUDED.tier;

-- Tier 2-B: internationally relevant actors
INSERT INTO country_tiers (country_id, tier)
SELECT id, 2
FROM countries
WHERE iso2 IN (
    'AE',
    'SG',
    'CH',
    'NO',
    'SE',
    'BE',
    'PK',
    'ZA',
    'EG',
    'VN',
    'TH',
    'PH',
    'MY',
    'NG'
)
ON CONFLICT (country_id)
DO UPDATE SET tier = EXCLUDED.tier;

-- Tier 2 strategic special case
-- North Korea is Tier 2 because of its strategic crisis-generation
-- capabilities despite its limited economic weight.
INSERT INTO country_tiers (country_id, tier)
SELECT id, 2
FROM countries
WHERE iso2 = 'KP'
ON CONFLICT (country_id)
DO UPDATE SET tier = EXCLUDED.tier;

-- Tier 3: all remaining countries in the STATION V universe
INSERT INTO country_tiers (country_id, tier)
SELECT id, 3
FROM countries
WHERE id NOT IN (
    SELECT country_id
    FROM country_tiers
)
ON CONFLICT (country_id)
DO NOTHING;

-- The complete STATION V country universe must have exactly one tier.
DO $$
DECLARE
    country_count INTEGER;
    tier_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO country_count
    FROM countries;

    SELECT COUNT(*) INTO tier_count
    FROM country_tiers;

    IF tier_count <> country_count THEN
        RAISE EXCEPTION
            'Country tier coverage mismatch: % countries, % tier assignments',
            country_count,
            tier_count;
    END IF;
END $$;

COMMIT;