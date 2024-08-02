#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

""" doc
"""
from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import asyncpg

from avin.const import Usr
from avin.core import Asset, AssetList, Bar, Order, TimeFrame
from avin.data import AssetType, Data, DataType, Exchange
from avin.logger import logger

__all__ = ("Keeper",)


class Keeper:  # {{{
    def __init__(self):  # {{{
        self.user = Usr.PG_USER
        self.database = Usr.PG_DATABASE
        self.host = Usr.PG_HOST

    # }}}
    async def transaction(self, request: str):  # {{{
        conn = await asyncpg.connect(
            user=self.user, database=self.database, host=self.host
        )

        values = await conn.fetch(request)
        await conn.close()

        return values

    # }}}
    async def createDataBase(self):  # {{{
        # await self.__createEnums()
        await self.__createExchangeTable()
        await self.__createAssetTable()
        await self.__createAccountTable()
        await self.__createStrategyTable()
        await self.__createTradeTable()
        await self.__createOrderTable()
        await self.__createOperationTable()
        await self.__createMarketDataScheme()
        ...

    # }}}
    async def addExchange(self, exchange: Exchange):  # {{{
        request = f"""
        INSERT INTO "Exchange"(name)
        VALUES ('{exchange.name}');
        """
        res = await self.transaction(request)
        return res

    # }}}
    async def addAsset(self, asset: Asset | Id):  # {{{
        request = f"""
        INSERT INTO "Asset" (
            exchange,
            type,
            ticker,
            name,
            figi
            )
        VALUES (
            '{asset.exchange.name}',
            '{asset.type.name}',
            '{asset.ticker}',
            '{asset.name}',
            '{asset.figi}'
            );
        """
        res = await self.transaction(request)
        return res

    # }}}
    async def addData(self, ID: Id, data_type: DataType, data: list[object]):  # {{{
        def formatBarData(b: Bar):
            # Bar to postgres value
            dt = f"'{b.dt.isoformat()}'"
            s = f"({dt},{b.open},{b.high},{b.low},{b.close},{b.vol}),\n"
            return s

        # Format data in postges value
        values = str()
        for bar in data:
            value = formatBarData(bar)
            values += value
        values = values[0:-2] + ";"  # '<text>,\n' -> '<text>;'

        # Create table if not exist
        table_name = self.__getTableName(ID, data_type)
        await self.__createBarsDataTable(ID, data_type)

        # Add bars data
        request = f"""
        INSERT INTO data."{table_name}" (dt, open, high, low, close, volume)
        VALUES
            {values}
        """

        res = await self.transaction(request)
        return res

    # }}}
    async def addAccount(self, account: Account):  # {{{
        request = f"""
        INSERT INTO "Account" (
            name,
            broker
            )
        VALUES (
            '{account.name}',
            '{account.broker.name}'
            );
        """
        res = await self.transaction(request)
        return res

    # }}}
    async def addStrategy(self, strategy: Strategy):  # {{{
        request = f"""
        INSERT INTO "Strategy" (
            name,
            version
            )
        VALUES (
            '{strategy.name}',
            '{strategy.version}'
            );
        """
        res = await self.transaction(request)
        return res

    # }}}
    async def addTrade(self, trade: Trade):  # {{{
        request = f"""
            INSERT INTO "Trade" (
                trade_id, dt, status, strategy, version, type, figi
                )
            VALUES (
                {trade.ID},
                '{trade.dt}',
                '{trade.status.name}',
                '{trade.strategy}',
                '{trade.version}',
                '{trade.type.name}',
                '{trade.asset.figi}'
                );
            """
        res = await self.transaction(request)
        return res

    async def deleteTrade(self, trade: Trade): ...

    # }}}
    async def addOrder(self, order: Order):  # {{{
        assert order.trade_ID is not None
        assert order.account_name is not None

        if order.type == Order.Type.MARKET:
            price = "NULL"
            stop_price = "NULL"
            exec_price = "NULL"
        elif order.type == Order.Type.LIMIT:
            price = order.price
            stop_price = "NULL"
            exec_price = "NULL"
        elif order.type == Order.Type.STOP:
            price = "NULL"
            stop_price = order.stop_price
            exec_price = order.exec_price
        else:
            assert False, f"Что за новый тип ордера='{order.type}'"

        if order.meta is None:
            meta = "NULL"
        else:
            logger.warning("Напиши как правильно meta сохранять")
            logger.info(order.meta)
            assert False

        request = f"""
            INSERT INTO "Order" (
                order_id,
                account,
                type,
                status,
                direction,
                figi,
                lots,
                quantity,
                price,
                stop_price,
                exec_price,
                trade_id,
                meta
                )
            VALUES (
                {order.ID},
                '{order.account_name}',
                '{order.type.name}',
                '{order.status.name}',
                '{order.direction.name}',
                '{order.asset.figi}',
                {order.lots},
                {order.quantity},
                {price},
                {stop_price},
                {exec_price},
                {order.trade_ID},
                {meta}
                );
            """
        res = await self.transaction(request)
        return res

    async def deleteTrade(self, trade: Trade): ...

    # }}}
    async def addOperation(self, operation: Operation):  # {{{
        assert operation.trade_ID is not None
        assert operation.order_ID is not None

        if operation.meta is None:
            meta = "NULL"
        else:
            logger.warning("Напиши как правильно meta сохранять")
            logger.info(operation.meta)
            assert False
            # что то типо такого
            meta = f"'{meta}'"

        request = f"""
            INSERT INTO "Operation" (
                operation_id,
                account,
                dt,
                direction,
                figi,
                lots,
                quantity,
                price,
                amount,
                commission,
                trade_id,
                order_id,
                meta
            )
            VALUES (
                {operation.ID},
                '{operation.account_name}',
                '{operation.dt}',
                '{operation.direction.name}',
                '{operation.asset.figi}',
                {operation.lots},
                {operation.quantity},
                {operation.price},
                {operation.amount},
                {operation.commission},
                {operation.trade_ID},
                {operation.order_ID},
                {meta}
            );
        """

        res = await self.transaction(request)
        return res

    async def deleteTrade(self, trade: Trade): ...

    # }}}
    async def deleteExchange(self, exchange: Exchange):  # {{{
        request = f"""
        DELETE FROM "Exchange" WHERE name = '{exchange.name}';
        """
        res = await self.transaction(request)
        return res

    # }}}
    async def deleteAsset(self, asset: Asset):  # {{{
        request = f"""
        DELETE FROM "Asset" WHERE figi = '{asset.figi}';
        """
        res = await self.transaction(request)
        return res

    # }}}
    async def deleteData(self, ID: Id, data_type: DataType):  # {{{
        table_name = self.__getTableName(ID, data_type)
        request = f"""
        DROP TABLE data."{table_name}";
        """
        res = await self.transaction(request)
        return res

    # }}}
    async def deleteAccount(self, account: Account):  # {{{
        request = f"""
        DELETE FROM "Account" WHERE name = '{account.name}';
        """
        res = await self.transaction(request)
        return res

    # }}}
    async def deleteStrategy(self, strategy: Strategy):  # {{{
        request = f"""
        DELETE FROM "Strategy"
        WHERE name = '{strategy.name}' AND version = '{strategy.version}';
        """
        res = await self.transaction(request)
        return res

    # }}}
    async def deleteTrade(self, trade: Trade):  # {{{
        request = f"""
            DELETE FROM "Trade"
            WHERE trade_id = '{trade.ID}';
            """
        res = await self.transaction(request)
        return res

    # }}}
    async def deleteOrder(self, order: Order):  # {{{
        request = f"""
            DELETE FROM "Order"
            WHERE order_id = '{order.ID}';
            """
        res = await self.transaction(request)
        return res

    # }}}
    async def deleteOperation(self, operation: Operation):  # {{{
        request = f"""
            DELETE FROM "Operation"
            WHERE operation_id = '{operation.ID}';
            """
        res = await self.transaction(request)
        return res

    # }}}
    async def loadBars(self, ID, data_type, begin, end):  # {{{
        table_name = self.__getTableName(ID, data_type)
        request = f"""
            SELECT dt, open, high, low, close, volume
            FROM "{table_name}"
            WHERE dt >= '{begin}' AND dt < '{end}'
            ORDER BY dt
            ;
            """

        res = await self.transaction(request)
        bars = list()
        for i in res:
            bar = Bar(
                i["dt"],
                i["open"],
                i["high"],
                i["low"],
                i["close"],
                i["volume"],
            )
            bars.append(bar)
        return bars

    # }}}
    async def __createEnums(self):  # {{{
        requests = [  # {{{
            """DROP TYPE IF EXISTS public."DataSource";""",
            """ CREATE TYPE "DataSource" AS ENUM (
                'MOEX',
                'TINKOFF'
                );""",
            """DROP TYPE IF EXISTS public."AssetType";""",
            """ CREATE TYPE "AssetType" AS ENUM (
                'CASH',
                'INDEX',
                'SHARE',
                'BOND',
                'FUTURE',
                'OPTION',
                'CURRENCY',
                'ETF'
                );""",
            """DROP TYPE IF EXISTS public."DataType";""",
            """ CREATE TYPE "DataType" AS ENUM (
                'BAR_1M',
                'BAR_5M',
                'BAR_10M',
                'BAR_1H',
                'BAR_D',
                'BAR_W',
                'BAR_M',
                'BAR_Q',
                'BAR_Y'
                );""",
            """DROP TYPE IF EXISTS public."TimeFrame";""",
            """ CREATE TYPE "TimeFrame" AS ENUM (
                '1M',
                '5M',
                '10M',
                '1H',
                'D',
                'W',
                'M',
                'Q',
                'Y'
                );""",
            """DROP TYPE IF EXISTS public."OrderType";""",
            """ CREATE TYPE "OrderType" AS ENUM (
                'MARKET',
                'LIMIT',
                'STOP',
                'STOP_LOSS',
                'TAKE_PROFIT',
                'WAIT',
                'TRAILING'
                );""",
            """DROP TYPE IF EXISTS public."OrderDirection";""",
            """ CREATE TYPE "OrderDirection" AS ENUM (
                'BUY',
                'SELL'
                );""",
            """DROP TYPE IF EXISTS public."OrderStatus";""",
            """ CREATE TYPE "OrderStatus" AS ENUM (
                'NEW',
                'POST',
                'PARTIAL',
                'EXECUTED',
                'OFF',
                'CANCEL',
                'REJECT',
                'WAIT'
                );""",
            """DROP TYPE IF EXISTS public."OperationDirection";""",
            """ CREATE TYPE "OperationDirection" AS ENUM (
                'BUY',
                'SELL'
                );""",
            """DROP TYPE IF EXISTS public."TradeType";""",
            """ CREATE TYPE "TradeType" AS ENUM (
                'LONG',
                'SHORT'
                );""",
            """DROP TYPE IF EXISTS public."TradeStatus";""",
            """ CREATE TYPE "TradeStatus" AS ENUM (
                'INITIAL',
                'NEW',
                'OPEN',
                'CLOSE',
                'CANCELED'
                );""",
        ]  # }}}
        for i in requests:
            await self.transaction(i)

    # }}}
    async def __createExchangeTable(self):  # {{{
        keeper = Keeper()
        request = """
        CREATE TABLE IF NOT EXISTS "Exchange" (
            name text PRIMARY KEY
            );
        """
        res = await self.transaction(request)
        return res

    # }}}
    async def __createAssetTable(self):  # {{{
        keeper = Keeper()
        request = """
        CREATE TABLE IF NOT EXISTS "Asset" (
            exchange text REFERENCES "Exchange"(name),
            type "AssetType",
            ticker text,
            name text,
            figi text PRIMARY KEY
            );
        """
        res = await self.transaction(request)
        return res

    # }}}
    async def __createBarsDataTable(self, ID: Id, data_type: DataType):  # {{{
        assert data_type != DataType.TIC
        assert data_type != DataType.BOOK
        table_name = self.__getTableName(ID, data_type)
        request = f"""
        CREATE TABLE IF NOT EXISTS data."{table_name}" (
            dt TIMESTAMP WITH TIME ZONE PRIMARY KEY,
            open float,
            high float,
            low float,
            close float,
            volume integer
            );
            """
        res = await self.transaction(request)
        return res

    # }}}
    async def __createAccountTable(self):  # {{{
        request = """
        CREATE TABLE IF NOT EXISTS "Account" (
            name text PRIMARY KEY,
            broker text
            );
        """
        res = await self.transaction(request)

        # if not exist, create system account for back-tester
        request = f"""
        SELECT name FROM "Account"
        WHERE name = '_backtest'
        """
        res = await self.transaction(request)
        if not res:
            request = f"""
            INSERT INTO "Account" (
                name,
                broker
                )
            VALUES
                ('_backtest', 'ArsVincere')
                ;
            """
            res = await self.transaction(request)

        # if not exist, create system account for unit-tests
        request = f"""
        SELECT name FROM "Account"
        WHERE name = '_unittest'
        """
        res = await self.transaction(request)
        if not res:
            request = f"""
            INSERT INTO "Account" (
                name,
                broker
                )
            VALUES
                ('_unittest', 'ArsVincere')
                ;
            """
            res = await self.transaction(request)

        return res

    # }}}
    async def __createStrategyTable(self):  # {{{
        request = """
        CREATE TABLE IF NOT EXISTS "Strategy" (
            name text,
            version text,
            CONSTRAINT strategy_pkey PRIMARY KEY (name, version)
            );
        """
        res = await self.transaction(request)
        return res

    # }}}
    async def __createTradeTable(self):  # {{{
        request = """
        CREATE TABLE IF NOT EXISTS "Trade" (
            trade_id    float PRIMARY KEY,
            dt          TIMESTAMP WITH TIME ZONE,
            status      "TradeStatus",
            strategy    text,
            version     text,
            type        "TradeType",
            figi        text REFERENCES "Asset"(figi),

			FOREIGN KEY (strategy, version)
                REFERENCES "Strategy" (name, version)
			);
            """
        res = await self.transaction(request)
        return res

    # }}}
    async def __createOrderTable(self):  # {{{
        # TODO добавить частично исполненный - сколько там уже исполнено
        request = """
        CREATE TABLE IF NOT EXISTS "Order" (
            order_id        float PRIMARY KEY,
            account         text REFERENCES "Account"(name),
            type            "OrderType",
            status          "OrderStatus",
            direction       "OrderDirection",
            figi            text REFERENCES "Asset"(figi),
            lots            integer,
            quantity        integer,
            price           float,
            stop_price      float,
            exec_price      float,

            trade_id        float REFERENCES "Trade"(trade_id),
			meta            text
			);
            """
        res = await self.transaction(request)
        return res

    # }}}
    async def __createOperationTable(self):  # {{{
        request = """
        CREATE TABLE IF NOT EXISTS "Operation" (
            operation_id    float PRIMARY KEY,
            account         text REFERENCES "Account"(name),
            dt              TIMESTAMP WITH TIME ZONE,
            direction       "OperationDirection",
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
            """
        res = await self.transaction(request)
        return res

    # }}}
    async def __createMarketDataScheme(self):  # {{{
        request = """
        CREATE SCHEMA IF NOT EXISTS data
        """
        res = await self.transaction(request)
        return res

    # }}}
    def __getTableName(self, asset: Asset | Id, data_type):  # {{{
        table_name = f"_{asset.figi}_{data_type.name}"
        return table_name

    # }}}


# }}}
