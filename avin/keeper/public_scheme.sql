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
    asset_list_name text
        REFERENCES "AssetList"(asset_list_name)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    figi text
        REFERENCES "Asset"(figi)
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
    strategy_set_name   text
        REFERENCES "StrategySet"(strategy_set_name)
        ON UPDATE CASCADE,
    strategy            text,
    version             text,
    FOREIGN KEY (strategy, version)
        REFERENCES "Strategy" (strategy_name, version)
        ON UPDATE CASCADE,
    figi                text
        REFERENCES "Asset"(figi),
    long                bool NOT NULL,
    short               bool NOT NULL
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
    broker text
        REFERENCES "Broker"(broker_name)
        ON UPDATE CASCADE
    );
    INSERT INTO "Account" (account_name, broker)
    VALUES
        ('_backtest', '_VirtualBroker'),
        ('_unittest', '_VirtualBroker'),
        ('Alex', 'Tinkoff'),
        ('Agni', 'Tinkoff');
-- }}}
CREATE TABLE IF NOT EXISTS "Test/Trader" ( -- {{{
    name    text PRIMARY KEY,
    type    "TradeListOwner" NOT NULL,
    config  jsonb NOT NULL
);
-- }}}
CREATE VIEW "Test" AS -- {{{
    SELECT name, config
    FROM "Test/Trader"
    WHERE type = 'TEST';
-- }}}
CREATE VIEW "Trader" AS  -- {{{
    SELECT name, config
    FROM "Test/Trader"
    WHERE type = 'TRADER'
-- }}}
CREATE TABLE IF NOT EXISTS "TradeList" ( -- {{{
    trade_list_name text PRIMARY KEY,
    owner           text
        REFERENCES "Test/Trader"(name)
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Trade" ( -- {{{
    trade_id    text PRIMARY KEY,
    trade_list  text
        REFERENCES "TradeList"(trade_list_name)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    figi        text NOT NULL,
    strategy    text NOT NULL,
    version     text NOT NULL,
    dt          TIMESTAMP WITH TIME ZONE NOT NULL,
    status      "Trade.Status" NOT NULL,
    trade_type  "Trade.Type" NOT NULL,
    trade_info  jsonb NOT NULL,
    FOREIGN KEY (strategy, version)
        REFERENCES "Strategy" (strategy_name, version) ON UPDATE CASCADE
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Order" ( -- {{{
    order_id        text PRIMARY KEY,
    trade_id        text
        REFERENCES "Trade"(trade_id)
        ON DELETE CASCADE,
    account         text
        REFERENCES "Account"(account_name)
        ON UPDATE CASCADE,
    figi            text NOT NULL,

    order_type      "Order.Type" NOT NULL,
    status          "Order.Status" NOT NULL,
    direction       "Direction" NOT NULL,

    lots            integer NOT NULL,
    quantity        integer NOT NULL,
    price           float,
    stop_price      float,
    exec_price      float,
    exec_lots       integer NOT NULL,
    exec_quantity   integer NOT NULL,

    broker_id       text NOT NULL,
    meta            text NOT NULL
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Transaction" ( -- {{{
    order_id        text
        REFERENCES "Order"(order_id)
        ON DELETE CASCADE,
    dt              TIMESTAMP WITH TIME ZONE NOT NULL,
    price           float NOT NULL,
    quantity        integer NOT NULL,
    broker_id       text NOT NULL
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Operation" ( -- {{{
    operation_id    text PRIMARY KEY,
    order_id        text UNIQUE
        REFERENCES "Order"(order_id)
        ON DELETE CASCADE,
    trade_id        text
        REFERENCES "Trade"(trade_id)
        ON DELETE CASCADE,
    account         text
        REFERENCES "Account"(account_name)
        ON UPDATE CASCADE,
    figi            text NOT NULL,
    dt              TIMESTAMP WITH TIME ZONE NOT NULL,
    direction       "Direction" NOT NULL,
    lots            integer NOT NULL,
    quantity        integer NOT NULL,
    price           float NOT NULL,
    amount          float NOT NULL,
    commission      float NOT NULL,
    meta            text NOT NULL
    );
-- }}}

CREATE TABLE IF NOT EXISTS "TestList" ( -- {{{
    test_list_name  text PRIMARY KEY
    );
    INSERT INTO "TestList" (test_list_name)
    VALUES ('unsorted');
-- }}}
CREATE TABLE IF NOT EXISTS "TestList-Tests" ( -- {{{
    test_list   text
        REFERENCES "TestList"(test_list_name)
        ON UPDATE CASCADE ON DELETE CASCADE,
    test        text
        REFERENCES "Test/Trader"(name)
        ON UPDATE CASCADE ON DELETE CASCADE
    );
-- }}}

CREATE TABLE IF NOT EXISTS "AnalyticData" ( -- {{{
    analytic_name   text,
    figi            text
        REFERENCES "Asset"(figi),
    analyse_json    jsonb NOT NULL,
    PRIMARY KEY     (analytic_name, figi)
    );
-- }}}

-- CREATE TABLE IF NOT EXISTS "Test" ( -- {{{
--     test_name       text PRIMARY KEY,
--     test_list       text REFERENCES "TestList"(test_list_name)
--                     ON UPDATE CASCADE ON DELETE CASCADE,
--     strategy        text NOT NULL,
--     version         text NOT NULL,
--     figi            text NOT NULL,
--     enable_long     bool NOT NULL,
--     enable_short    bool NOT NULL,
--     account         text REFERENCES "Account"(account_name)
--                     ON UPDATE CASCADE,
--     status          "Test.Status" NOT NULL,
--     deposit         float NOT NULL,
--     commission      float NOT NULL,
--     begin_date      date NOT NULL,
--     end_date        date NOT NULL,
--     description     text NOT NULL,
--     FOREIGN KEY (strategy, version)
--         REFERENCES "Strategy" (strategy_name, version) ON UPDATE CASCADE
--     );
-- -- }}}
-- CREATE TABLE IF NOT EXISTS "Trader" ( -- {{{
--     trader_name     text PRIMARY KEY,
--     account         text REFERENCES "Account"(account_name)
--                     ON UPDATE CASCADE,
--     strategy_set    text REFERENCES "StrategySet"(strategy_set_name)
--                     ON UPDATE CASCADE
--     );
-- -- }}}

