-- ===========================================================================
-- URL:          http://arsvincere.com
-- AUTHOR:       Alex Avin
-- E-MAIL:       mr.alexavin@gmail.com
-- LICENSE:      GNU GPLv3
-- ===========================================================================

CREATE SCHEMA IF NOT EXISTS data -- {{{
    AUTHORIZATION pg_database_owner;
COMMENT ON SCHEMA data
    IS 'market data';
-- }}}

CREATE TABLE IF NOT EXISTS data."Instrument" ( -- {{{
    figi text PRIMARY KEY,
    exchange "Exchange" NOT NULL,
    type "InstrumentType" NOT NULL,
    ticker text NOT NULL,
    name text NOT NULL,
    lot integer NOT NULL,
    min_price_step double precision
    );
-- }}}
CREATE TABLE IF NOT EXISTS data."InstrumentInfo" ( -- {{{
    data_source "DataSource" NOT NULL,
    instrument_type "InstrumentType" NOT NULL,
    figi text NOT NULL,
    instrument_info jsonb NOT NULL,
    PRIMARY KEY (data_source, figi)
    );
-- }}}
CREATE TABLE IF NOT EXISTS data."DataInfo" ( -- {{{
    data_source "DataSource" NOT NULL,
    data_type "DataType" NOT NULL,
    figi text NOT NULL,
    first_dt TIMESTAMP WITH TIME ZONE NOT NULL,
    last_dt TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (data_source, data_type, figi)
    );
-- }}}

