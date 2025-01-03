-- ===========================================================================
-- URL:          http://arsvincere.com
-- AUTHOR:       Alex Avin
-- E-MAIL:       mr.alexavin@gmail.com
-- LICENSE:      GNU GPLv3
-- ===========================================================================

CREATE SCHEMA IF NOT EXISTS trader -- {{{
    AUTHORIZATION pg_database_owner;
COMMENT ON SCHEMA trader
    IS 'trader data';
-- }}}

CREATE TABLE IF NOT EXISTS trader."Trader" ( -- {{{
    trader_name     text PRIMARY KEY,
    account         text REFERENCES "Account"(account_name)
                    ON UPDATE CASCADE,
    strategy_set    text REFERENCES "StrategySet"(strategy_set_name)
                    ON UPDATE CASCADE
    );
-- }}}
CREATE TABLE IF NOT EXISTS trader."TradeList" ( -- {{{
    trade_list_name text PRIMARY KEY,
    test            text REFERENCES tester."Test"(test_name)
                    ON UPDATE CASCADE ON DELETE CASCADE
    );
-- }}}
CREATE TABLE IF NOT EXISTS trader."Trade" ( -- {{{
    trade_id    text PRIMARY KEY,
    trade_list  text REFERENCES trader."TradeList"(trade_list_name)
                ON UPDATE CASCADE,
    figi        text NOT NULL,
    strategy    text NOT NULL,
    version     text NOT NULL,
    dt          TIMESTAMP WITH TIME ZONE NOT NULL,
    status      "Trade.Status" NOT NULL,
    type        "Trade.Type" NOT NULL,
    info        jsonb NOT NULL,
    FOREIGN KEY (strategy, version)
        REFERENCES "Strategy" (strategy_name, version) ON UPDATE CASCADE
    );
-- }}}
CREATE TABLE IF NOT EXISTS trader."Order" ( -- {{{
    order_id        text PRIMARY KEY,
    trade_id        text REFERENCES trader."Trade"(trade_id)
                    ON DELETE CASCADE,
    account         text REFERENCES "Account"(account_name)
                    ON UPDATE CASCADE,
    figi            text NOT NULL,

    type            "Order.Type" NOT NULL,
    status          "Order.Status" NOT NULL,
    direction       "Direction" NOT NULL,

    lots            integer NOT NULL,
    quantity        integer NOT NULL,
    price           float,
    stop_price      float,
    exec_price      float,
    exec_lots       integer NOT NULL,
    exec_quantity   integer NOT NULL,

    meta            text NOT NULL,
    broker_id       text NOT NULL
    );
-- }}}
CREATE TABLE IF NOT EXISTS trader."Transaction" ( -- {{{
    order_id        text REFERENCES trader."Order"(order_id)
                    ON DELETE CASCADE,
    dt              TIMESTAMP WITH TIME ZONE NOT NULL,
    price           float NOT NULL,
    quantity        integer NOT NULL,
    broker_id       text NOT NULL
    );
-- }}}
CREATE TABLE IF NOT EXISTS trader."Operation" ( -- {{{
    operation_id    text PRIMARY KEY,
    order_id        text REFERENCES trader."Order"(order_id)
                    ON DELETE CASCADE,
    trade_id        text REFERENCES trader."Trade"(trade_id)
                    ON DELETE CASCADE,
    account         text REFERENCES "Account"(account_name)
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
