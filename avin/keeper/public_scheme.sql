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
CREATE TABLE IF NOT EXISTS "InstrumentInfo" ( -- {{{
    source "DataSource" NOT NULL,
    type "Instrument.Type" NOT NULL,
    info jsonb NOT NULL
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Exchange" ( -- {{{
    name text PRIMARY KEY
    );
    INSERT INTO "Exchange" (name)
    VALUES
        ('MOEX'),
        ('SPB');
-- }}}
CREATE TABLE IF NOT EXISTS "Asset" ( -- {{{
    figi text PRIMARY KEY,
    type "Instrument.Type" NOT NULL,
    exchange text REFERENCES "Exchange"(name),
    ticker text NOT NULL,
    name text NOT NULL,
    info jsonb NOT NULL
    );
-- }}}
CREATE TABLE IF NOT EXISTS "AssetList" ( -- {{{
    name text PRIMARY KEY
    );
-- }}}
CREATE TABLE IF NOT EXISTS "AssetList-Asset" ( -- {{{
    name text REFERENCES "AssetList"(name) ON DELETE CASCADE ON UPDATE CASCADE,
    figi text REFERENCES "Asset"(figi)
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Data" ( -- {{{
    figi text REFERENCES "Asset"(figi),
    type "DataType" NOT NULL,
    source "DataSource" NOT NULL,
    first_dt TIMESTAMP WITH TIME ZONE NOT NULL,
    last_dt TIMESTAMP WITH TIME ZONE NOT NULL
    );
-- }}}

CREATE TABLE IF NOT EXISTS "Strategy" ( -- {{{
    name text NOT NULL,
    version text NOT NULL,
    CONSTRAINT strategy_pkey PRIMARY KEY (name, version)
    );
    INSERT INTO "Strategy" (name, version)
    VALUES
        ('Every', 'minute'),
        ('Every', 'five'),
        ('Every', 'day');
-- }}}
CREATE TABLE IF NOT EXISTS "StrategySet" ( -- {{{
    name text PRIMARY KEY
    );
-- }}}
CREATE TABLE IF NOT EXISTS "StrategySet-Strategy" ( -- {{{
    name        text REFERENCES "StrategySet"(name) ON UPDATE CASCADE,
    strategy    text,
    version     text,
    FOREIGN KEY (strategy, version) REFERENCES "Strategy" (name, version) ON UPDATE CASCADE,
    figi        text REFERENCES "Asset"(figi),
    long        bool NOT NULL,
    short       bool NOT NULL
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Broker" ( -- {{{
    name text PRIMARY KEY
    );
    INSERT INTO "Broker" (name)
    VALUES
        ('_VirtualBroker'),
        ('Tinkoff');
-- }}}
CREATE TABLE IF NOT EXISTS "Account" ( -- {{{
    name text PRIMARY KEY,
    broker text REFERENCES "Broker"(name) ON UPDATE CASCADE
    );
    INSERT INTO "Account" (name, broker)
    VALUES
        ('_backtest', '_VirtualBroker'),
        ('_unittest', '_VirtualBroker'),
        ('Alex', 'Tinkoff'),
        ('Agni', 'Tinkoff');
-- }}}
CREATE TABLE IF NOT EXISTS "TradeList" ( -- {{{
    name text PRIMARY KEY
    );
    INSERT INTO "TradeList" (name)
    VALUES
        ('_unittest');

-- }}}
CREATE TABLE IF NOT EXISTS "Trade" ( -- {{{
    trade_id    text PRIMARY KEY,
    trade_list  text REFERENCES "TradeList"(name) ON UPDATE CASCADE,
    figi        text REFERENCES "Asset"(figi),
    strategy    text,
    version     text,
    FOREIGN KEY (strategy, version) REFERENCES "Strategy" (name, version) ON UPDATE CASCADE,
    dt          TIMESTAMP WITH TIME ZONE,
    status      "Trade.Status",
    type        "Trade.Type"
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Order" ( -- {{{
    order_id        text PRIMARY KEY,
    trade_id        text REFERENCES "Trade"(trade_id) ON DELETE CASCADE,
    account         text REFERENCES "Account"(name) ON UPDATE CASCADE,
    figi            text REFERENCES "Asset"(figi),

    type            "Order.Type",
    status          "Order.Status",
    direction       "Direction",

    lots            integer,
    quantity        integer,
    price           float,
    stop_price      float,
    exec_price      float,
    exec_lots       integer,
    exec_quantity   integer,

    meta            text,
    broker_id       text
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Transaction" ( -- {{{
    order_id        text REFERENCES "Order"(order_id) ON DELETE CASCADE,
    dt              TIMESTAMP WITH TIME ZONE,
    price           float,
    quantity        integer,
    broker_id       text
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Operation" ( -- {{{
    operation_id    text PRIMARY KEY,
    order_id        text REFERENCES "Order"(order_id) ON DELETE CASCADE,
    trade_id        text REFERENCES "Trade"(trade_id) ON DELETE CASCADE,
    account         text REFERENCES "Account"(name) ON UPDATE CASCADE,
    figi            text REFERENCES "Asset"(figi),
    dt              TIMESTAMP WITH TIME ZONE,
    direction       "Direction",
    lots            integer,
    quantity        integer,
    price           float,
    amount          float,
    commission      float,
    meta            text
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Test" ( -- {{{
    name            text PRIMARY KEY,
    strategy        text,
    version         text,
    FOREIGN KEY (strategy, version) REFERENCES "Strategy" (name, version) ON UPDATE CASCADE,
    figi            text REFERENCES "Asset"(figi),
    trade_list      text REFERENCES "TradeList"(name) ON UPDATE CASCADE,
    account         text REFERENCES "Account"(name) ON UPDATE CASCADE,
    status          "Test.Status" NOT NULL,
    deposit         float,
    commission      float,
    begin_date      date,
    end_date        date,
    description     text
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Trader" ( -- {{{
    name            text PRIMARY KEY,
    account         text REFERENCES "Account"(name) ON UPDATE CASCADE,
    strategy_set    text REFERENCES "StrategySet"(name) ON UPDATE CASCADE,
    trade_list      text REFERENCES "TradeList"(name) ON UPDATE CASCADE
    );
-- }}}
