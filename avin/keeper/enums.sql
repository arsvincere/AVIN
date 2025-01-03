-- ===========================================================================
-- URL:          http://arsvincere.com
-- AUTHOR:       Alex Avin
-- E-MAIL:       mr.alexavin@gmail.com
-- LICENSE:      GNU GPLv3
-- ===========================================================================

CREATE TYPE "DataSource" AS ENUM (--{{{
    'CONVERT','MOEX', 'TINKOFF'
    );
--}}}
CREATE TYPE "DataType" AS ENUM (--{{{
    'BAR_1M', 'BAR_5M', 'BAR_10M', 'BAR_1H',
    'BAR_D', 'BAR_W', 'BAR_M', 'BAR_Q', 'BAR_Y'
    );
--}}}
CREATE TYPE "InstrumentType" AS ENUM (--{{{
    'CASH', 'INDEX', 'SHARE', 'BOND', 'FUTURE',
    'OPTION', 'CURRENCY', 'ETF'
    );
--}}}
CREATE TYPE "Exchange" AS ENUM (--{{{
    'MOEX', 'SPB'
    );
--}}}
CREATE TYPE "TimeFrame" AS ENUM (--{{{
    '1M', '5M', '10M', '1H', 'D', 'W', 'M', 'Q', 'Y'
    );
--}}}
CREATE TYPE "Direction" AS ENUM (--{{{
    'BUY', 'SELL'
    );
--}}}
CREATE TYPE "Order.Type" AS ENUM (--{{{
    'MARKET', 'LIMIT', 'STOP',
    'STOP_LOSS', 'TAKE_PROFIT',
    'WAIT', 'TRAILING'
    );
--}}}
CREATE TYPE "Order.Status" AS ENUM (--{{{
    'NEW', 'SUBMIT',
    'POSTED', 'OFF',
    'PARTIAL', 'FILLED',
    'EXECUTED', 'TRIGGERED',
    'CANCELED', 'BLOCKED', 'REJECTED', 'EXPIRED'
    );
--}}}
CREATE TYPE "Trade.Type" AS ENUM (--{{{
    'LONG', 'SHORT'
    );
--}}}
CREATE TYPE "Trade.Status" AS ENUM (--{{{
    'INITIAL', 'PENDING', 'TRIGGERED',
    'MAKE_ORDER', 'POST_ORDER', 'AWAIT_EXEC', 'OPENED',
    'MAKE_STOP', 'MAKE_TAKE', 'POST_STOP', 'POST_TAKE',
    'ACTIVE', 'CLOSING',
    'CLOSED', 'CANCELED', 'BLOCKED'
    );
--}}}
CREATE TYPE "Test.Status" AS ENUM (--{{{
    'NEW', 'EDITED', 'PROCESS', 'COMPLETE'
    );
--}}}

