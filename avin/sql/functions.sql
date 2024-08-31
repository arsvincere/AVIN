-- Functions -----------------------------------------------------------------

CREATE OR REPLACE FUNCTION add_asset_if_not_exist(
    a_figi text,
    a_type "AssetType",
    a_exchange text,
    a_ticker text,
    a_name text
    )
RETURNS void
LANGUAGE plpgsql
AS $$
    BEGIN
        IF NOT EXISTS (SELECT figi FROM "Asset" WHERE figi = a_figi)
        THEN
            INSERT INTO "Asset" (figi, type, exchange, ticker, name)
            VALUES
                (a_figi, a_type, a_exchange, a_ticker, a_name);
        END IF;
    END;
$$;

