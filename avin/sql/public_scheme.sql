-- Public scheme -------------------------------------------------------------

CREATE TABLE IF NOT EXISTS "Exchange" ( -- {{{
    name text PRIMARY KEY
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Asset" ( -- {{{
    figi text PRIMARY KEY,
    type "AssetType",
    exchange text REFERENCES "Exchange"(name),
    ticker text,
    name text
    );
-- }}}
CREATE TABLE IF NOT EXISTS "AssetList" ( -- {{{
    name text PRIMARY KEY,
    assets text ARRAY
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Data" ( -- {{{
    figi text REFERENCES "Asset"(figi),
    type "DataType",
    source "DataSource",
    first_dt TIMESTAMP WITH TIME ZONE,
    last_dt TIMESTAMP WITH TIME ZONE
    );
-- }}}
CREATE TABLE IF NOT EXISTS "InstrumentInfoCache" ( -- {{{
    source "DataSource",
    type "AssetType",
    info jsonb
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Broker" ( -- {{{
    name text PRIMARY KEY
    );
    INSERT INTO "Broker" (name)
    VALUES
        ('_tester'),
        ('Tinkoff');
-- }}}
CREATE TABLE IF NOT EXISTS "Account" ( -- {{{
    name text PRIMARY KEY,
    broker text REFERENCES "Broker"(name)
    );
    INSERT INTO "Account" (name, broker)
    VALUES
        ('_backtest', '_tester'),
        ('_unittest', '_tester');
-- }}}
CREATE TABLE IF NOT EXISTS "Strategy" ( -- {{{
    name text,
    version text,
    CONSTRAINT strategy_pkey PRIMARY KEY (name, version)
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Trader" ( -- {{{
    name        text PRIMARY KEY,
    broker      text REFERENCES "Broker"(name),
    account     text REFERENCES "Account"(name),
    strategyes  text ARRAY
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Trade" ( -- {{{
    trade_id    float PRIMARY KEY,
    dt          TIMESTAMP WITH TIME ZONE,
    status      "Trade.Status",
    strategy    text,
    version     text,
    type        "Trade.Type",
    figi        text REFERENCES "Asset"(figi),

    FOREIGN KEY (strategy, version)
        REFERENCES "Strategy" (name, version)
    );
-- }}}
CREATE TABLE IF NOT EXISTS "TradeList" ( -- {{{
    name        text PRIMARY KEY,
    trades      float ARRAY
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Order" ( -- {{{
    order_id        float PRIMARY KEY,
    account         text REFERENCES "Account"(name),
    type            "Order.Type",
    status          "Order.Status",
    direction       "Order.Direction",
    figi            text REFERENCES "Asset"(figi),
    lots            integer,
    quantity        integer,
    price           float,
    stop_price      float,
    exec_price      float,

    trade_id        float REFERENCES "Trade"(trade_id),
    exec_lots       integer,
    exec_quantity   integer,
    meta            text
    );
-- }}}
CREATE TABLE IF NOT EXISTS "Operation" ( -- {{{
    operation_id    float PRIMARY KEY,
    account         text REFERENCES "Account"(name),
    dt              TIMESTAMP WITH TIME ZONE,
    direction       "Operation.Direction",
    figi            text REFERENCES "Asset"(figi),
    lots            integer,
    quantity        integer,
    price           float,
    amount          float,
    commission      float,
    trade_id        float REFERENCES "Trade"(trade_id),
    order_id        float REFERENCES "Order"(order_id),
    meta            text
    );
-- }}}
