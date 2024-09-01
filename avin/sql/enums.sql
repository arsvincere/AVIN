-- Enums ---------------------------------------------------------------------
-- TODO: enums переименовать, сделать единообразно
-- Data.Source
-- Data.Type
-- Asset.Type - и ассет в модуль дата внести????, да, абстрактный можно

DROP TYPE IF EXISTS public."DataSource";--{{{
CREATE TYPE "DataSource" AS ENUM (
    'MOEX', 'TINKOFF'
    );
--}}}
DROP TYPE IF EXISTS public."AssetType";--{{{
CREATE TYPE "AssetType" AS ENUM (
    'CASH', 'INDEX', 'SHARE', 'BOND', 'FUTURE',
    'OPTION', 'CURRENCY', 'ETF'
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
DROP TYPE IF EXISTS public."Order.Type";--{{{
CREATE TYPE "Order.Type" AS ENUM (
    'MARKET', 'LIMIT', 'STOP',
    'STOP_LOSS', 'TAKE_PROFIT',
    'WAIT', 'TRAILING'
    );
--}}}
DROP TYPE IF EXISTS public."Order.Direction";--{{{
CREATE TYPE "Order.Direction" AS ENUM (
    'BUY', 'SELL'
    );
--}}}
DROP TYPE IF EXISTS public."Order.Status";--{{{
CREATE TYPE "Order.Status" AS ENUM (
    'NEW', 'PENDING', 'TIMEOUT', 'TRIGGERED',
    'SUBMIT', 'POSTED', 'PARTIAL', 'OFF', 'EXECUTED',
    'CANCELED', 'BLOCKED', 'REJECTED', 'EXPIRED',
    'ARCHIVE'
    );
--}}}
DROP TYPE IF EXISTS public."Operation.Direction";--{{{
CREATE TYPE "Operation.Direction" AS ENUM (
    'BUY', 'SELL'
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
    'MAKE_ORDER', 'POST_ORDER', 'POSTED', 'OPENED',
    'MAKE_STOP', 'MAKE_TAKE', 'POST_STOP', 'POST_TAKE',
    'ACTIVE',
    'OFF',
    'FINISH', 'CLOSING', 'REMOVING',
    'CLOSE',
    'CANCELED', 'BLOCKED',
    'ARCHIVE'
    );
--}}}
