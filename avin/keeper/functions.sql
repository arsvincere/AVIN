-- ===========================================================================
-- URL:          http://arsvincere.com
-- AUTHOR:       Alex Avin
-- E-MAIL:       mr.alexavin@gmail.com
-- LICENSE:      GNU GPLv3
-- ===========================================================================

CREATE OR REPLACE FUNCTION add_asset_if_not_exist(
    a_figi text,
    a_type "Instrument.Type",
    a_exchange text,
    a_ticker text,
    a_name text,
    a_info jsonb
    )
RETURNS void
LANGUAGE plpgsql
AS $$
    BEGIN
        IF NOT EXISTS (SELECT figi FROM "Asset" WHERE figi = a_figi)
        THEN
            INSERT INTO "Asset" (figi, type, exchange, ticker, name, info)
            VALUES
                (a_figi, a_type, a_exchange, a_ticker, a_name, a_info);
        END IF;
    END;
$$;

