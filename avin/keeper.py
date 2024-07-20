#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

""" doc
"""

import asyncio
from datetime import UTC, datetime

import asyncpg
from avin.const import Usr
from avin.core import Asset, AssetList, Bar, TimeFrame
from avin.data import AssetType, Data, DataType, Exchange


class Keeper:
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
    async def addAsset(self, asset: Asset):  # {{{
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
    async def addNewData(self, asset, data_type, data):  # {{{
        def formatBarData(bar: Bar):  # {{{
            dt = f"'{bar.dt.isoformat()}'"
            string = (
                "(" f"{dt},{bar.open},{bar.high},{bar.low},{bar.close},{bar.vol}" "),\n"
            )
            return string

        # }}}
        values = str()
        for bar in data:
            value = formatBarData(bar)
            values += value
        values = values[0:-2] + ";"

        table_name = f"{asset.figi}_{data_type.name}"
        await self.__createBarsDataTable(asset, data_type)

        request = f"""
        INSERT INTO "{table_name}" (dt, open, high, low, close, volume)
        VALUES
            {values}
        """

        res = await self.transaction(request)
        return res

    # }}}
    async def addAccount(self, broker: str, broker_id: str, name: str):  # {{{
        request = f"""
        INSERT INTO "Account" (
            name,
            broker,
            broker_id
            )
        VALUES (
            '{name}',
            '{broker}',
            '{broker_id}'
            );
        """
        res = await self.transaction(request)
        return res

    # }}}
    async def addStrategy(self, name: str, version: str):  # {{{
        request = f"""
        INSERT INTO "Strategy" (
            name,
            version
            )
        VALUES (
            '{name}',
            '{version}'
            );
        """
        res = await self.transaction(request)
        return res

    # }}}
    async def loadBars(self, asset, data_type, begin, end):  # {{{
        table_name = f"{asset.figi}_{data_type.name}"
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
    async def __createBarsDataTable(self, asset: Asset, data_type: DataType):  # {{{
        assert data_type != DataType.TIC
        assert data_type != DataType.BOOK
        table_name = f"{asset.figi}_{data_type.name}"
        request = f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
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
            broker text,
            broker_id text
            );
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
            type        "TradeType",
            status      "TradeStatus",
            dt          TIMESTAMP WITH TIME ZONE,
            strategy    text,
            version     text,
            figi        text REFERENCES "Asset"(figi),

			FOREIGN KEY (strategy, version)
                REFERENCES "Strategy" (name, version)
			);
            """
        res = await self.transaction(request)
        return res

    # }}}
    async def __createOrderTable(self):  # {{{
        request = """
        CREATE TABLE IF NOT EXISTS "Order" (
            order_id        float PRIMARY KEY,
            account         text REFERENCES "Account"(name),
            type            "OrderType",
            direction       "OrderDirection",
            status          "OrderStatus",
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
			meta            text
			);
            """
        res = await self.transaction(request)
        return res


# }}}


async def main():
    k = Keeper()
    await k.createDataBase()
    ...


if __name__ == "__main__":
    asyncio.run(main())
