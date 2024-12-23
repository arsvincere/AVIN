-- ===========================================================================
-- URL:          http://arsvincere.com
-- AUTHOR:       Alex Avin
-- E-MAIL:       mr.alexavin@gmail.com
-- LICENSE:      GNU GPLv3
-- ===========================================================================

CREATE SCHEMA IF NOT EXISTS data
    AUTHORIZATION pg_database_owner;

COMMENT ON SCHEMA data
    IS 'market data';

CREATE TABLE IF NOT EXISTS data."InstrumentInfo" ( -- {{{
    source "DataSource" NOT NULL,
    type "Instrument.Type" NOT NULL,
    figi text NOT NULL,
    info jsonb NOT NULL
    );
-- }}}
CREATE TABLE IF NOT EXISTS data."DataInfo" ( -- {{{
    source "DataSource" NOT NULL,
    type "DataType" NOT NULL,
    figi text NOT NULL,
    first_dt TIMESTAMP WITH TIME ZONE NOT NULL,
    last_dt TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT datainfo_pkey PRIMARY KEY (source, type, figi)
    );
-- }}}

