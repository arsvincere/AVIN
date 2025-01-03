-- ===========================================================================
-- URL:          http://arsvincere.com
-- AUTHOR:       Alex Avin
-- E-MAIL:       mr.alexavin@gmail.com
-- LICENSE:      GNU GPLv3
-- ===========================================================================

CREATE SCHEMA IF NOT EXISTS public -- {{{
    AUTHORIZATION pg_database_owner;
COMMENT ON SCHEMA public
    IS 'user data';
GRANT USAGE ON SCHEMA public TO PUBLIC;
GRANT ALL ON SCHEMA public TO pg_database_owner;
-- }}}

CREATE TABLE IF NOT EXISTS "Asset" ( -- {{{
    figi text PRIMARY KEY
    );
-- }}}
CREATE TABLE IF NOT EXISTS "AssetList" ( -- {{{
    asset_list_name text PRIMARY KEY
    );
-- }}}
CREATE TABLE IF NOT EXISTS "AssetList-Asset" ( -- {{{
    asset_list_name text REFERENCES "AssetList"(asset_list_name)
        ON DELETE CASCADE ON UPDATE CASCADE,
    figi text REFERENCES "Asset"(figi)
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Strategy" ( -- {{{
    strategy_name text NOT NULL,
    version text NOT NULL,
    PRIMARY KEY (strategy_name, version)
    );
    INSERT INTO "Strategy" (strategy_name, version)
    VALUES
        ('Every', 'minute'),
        ('Every', 'five'),
        ('Every', 'day');
-- }}}
CREATE TABLE IF NOT EXISTS "StrategySet" ( -- {{{
    strategy_set_name text PRIMARY KEY
    );
-- }}}
CREATE TABLE IF NOT EXISTS "StrategySet-Strategy" ( -- {{{
    strategy_set_name   text REFERENCES "StrategySet"(strategy_set_name)
        ON UPDATE CASCADE,
    strategy            text,
    version             text,
    figi                text REFERENCES "Asset"(figi),
    long                bool NOT NULL,
    short               bool NOT NULL,
    FOREIGN KEY (strategy, version)
        REFERENCES "Strategy" (strategy_name, version) ON UPDATE CASCADE
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Broker" ( -- {{{
    broker_name text PRIMARY KEY
    );
    INSERT INTO "Broker" (broker_name)
    VALUES
        ('_VirtualBroker'),
        ('Tinkoff');
-- }}}
CREATE TABLE IF NOT EXISTS "Account" ( -- {{{
    account_name text PRIMARY KEY,
    broker text REFERENCES "Broker"(broker_name) ON UPDATE CASCADE
    );
    INSERT INTO "Account" (account_name, broker)
    VALUES
        ('_backtest', '_VirtualBroker'),
        ('_unittest', '_VirtualBroker'),
        ('Alex', 'Tinkoff'),
        ('Agni', 'Tinkoff');
-- }}}
CREATE TABLE IF NOT EXISTS "AnalyticData" ( -- {{{
    analytic_name   text,
    figi            text REFERENCES "Asset"(figi),
    analyse_json    jsonb NOT NULL,
    PRIMARY KEY     (analytic_name, figi)
    );
-- }}}
