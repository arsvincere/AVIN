-- ===========================================================================
-- URL:          http://arsvincere.com
-- AUTHOR:       Alex Avin
-- E-MAIL:       mr.alexavin@gmail.com
-- LICENSE:      GNU GPLv3
-- ===========================================================================

DROP TYPE IF EXISTS public."DataSource";--{{{
CREATE TYPE "DataSource" AS ENUM (
    'MOEX', 'TINKOFF'
    );
--}}}
DROP TYPE IF EXISTS public."DataType";--{{{
CREATE TYPE "DataType" AS ENUM (
    'BAR_1M', 'BAR_5M', 'BAR_10M', 'BAR_1H',
    'BAR_D', 'BAR_W', 'BAR_M', 'BAR_Q', 'BAR_Y'
    );
--}}}
DROP TYPE IF EXISTS public."TimeFrame";--{{{
CREATE TYPE "TimeFrame" AS ENUM (
    '1M', '5M', '10M', '1H', 'D', 'W', 'M', 'Q', 'Y'
    );
--}}}
DROP TYPE IF EXISTS public."Instrument.Type";--{{{
CREATE TYPE "Instrument.Type" AS ENUM (
    'CASH', 'INDEX', 'SHARE', 'BOND', 'FUTURE',
    'OPTION', 'CURRENCY', 'ETF'
    );
--}}}
DROP TYPE IF EXISTS public."Direction";--{{{
CREATE TYPE "Direction" AS ENUM (
    'BUY', 'SELL'
    );
--}}}
DROP TYPE IF EXISTS public."Order.Type";--{{{
CREATE TYPE "Order.Type" AS ENUM (
    'MARKET', 'LIMIT', 'STOP',
    'STOP_LOSS', 'TAKE_PROFIT',
    'WAIT', 'TRAILING'
    );
--}}}
DROP TYPE IF EXISTS public."Order.Status";--{{{
CREATE TYPE "Order.Status" AS ENUM (
    'NEW', 'SUBMIT',
    'POSTED', 'OFF',
    'PARTIAL', 'FILLED',
    'EXECUTED', 'TRIGGERED',
    'CANCELED', 'BLOCKED', 'REJECTED', 'EXPIRED'
    );
--}}}
DROP TYPE IF EXISTS public."Trade.Type";--{{{
CREATE TYPE "Trade.Type" AS ENUM (
    'LONG', 'SHORT'
    );
--}}}
DROP TYPE IF EXISTS public."Trade.Status";--{{{
CREATE TYPE "Trade.Status" AS ENUM (
    'INITIAL', 'PENDING', 'TRIGGERED',
    'MAKE_ORDER', 'POST_ORDER', 'AWAIT_EXEC', 'OPENED',
    'MAKE_STOP', 'MAKE_TAKE', 'POST_STOP', 'POST_TAKE',
    'ACTIVE', 'CLOSING',
    'CLOSED', 'CANCELED', 'BLOCKED'
    );
--}}}
DROP TYPE IF EXISTS public."Test.Status";--{{{
CREATE TYPE "Test.Status" AS ENUM (
    'NEW', 'EDITED', 'PROGRESS', 'COMPLETE'
    );
--}}}
