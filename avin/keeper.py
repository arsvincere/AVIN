#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

""" doc
ord_id
opr_id
pos_id
trd_id
"""

import asyncio
import asyncpg
from datetime import datetime, UTC
from avin.core import Bar, Asset, TimeFrame, AssetList
from avin.data import Exchange, AssetType, DataType, Data
from avin.const import Usr

class Keeper():
    def __init__(self):# {{{
        self.user = Usr.PG_USER
        self.database = Usr.PG_DATABASE
        self.host= Usr.PG_HOST
    # }}}
    async def transaction(self, request: str):# {{{
        conn = await asyncpg.connect(
            user=       self.user,
            database=   self.database,
            host=       self.host
            )

        values = await conn.fetch(request)
        await conn.close()

        return values
# }}}
    async def addExchange(self, exchange: Exchange):# {{{
        request = f"""
        INSERT INTO exchange (
            name,
            session_begin,
            session_end,
            evening_begin,
            evening_end
            )
        VALUES (
            '{exchange.name}',
            '{exchange.SESSION_BEGIN}',
            '{exchange.SESSION_END}',
            '{exchange.EVENING_BEGIN}',
            '{exchange.EVENING_END}'
            );
        """
        res = await self.transaction(request)
        return res
# }}}
    async def addAsset(self, asset: Asset):# {{{
        request = f"""
        INSERT INTO asset (
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
    async def addNewData(self, asset, data_type, data):# {{{
        def formatBarData(bar: Bar):# {{{
            dt = f"'{bar.dt.isoformat()}'"
            string = (
                "("
                f"{dt},{bar.open},{bar.high},{bar.low},{bar.close},{bar.vol}"
                "),\n"
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
    async def addAccount(self, broker: str, broker_id: str, name: str):# {{{
        request = f"""
        INSERT INTO account (
            broker,
            broker_id,
            name
            )
        VALUES (
            '{broker}',
            '{broker_id}',
            '{name}'
            );
        """
        res = await self.transaction(request)
        return res

    async def createDataBase(self):# {{{
        # await self.__createEnums()
        # await self.__createExchangeTable()
        # await self.__createAssetTable()
        await self.__createAccountTable()
        ...
    # }}}
    async def __createEnums(self):# {{{
        requests = [# {{{
            """ CREATE TYPE "DataSource" AS ENUM (
                'MOEX',
                'TINKOFF'
                );""",
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
            """ CREATE TYPE "DataType" AS ENUM (
                'BAR_1M',
                'BAR_10M',
                'BAR_1H',
                'BAR_D',
                'BAR_W',
                'BAR_M',
                'BAR_Q',
                'BAR_Y,'
                );""",
            """ CREATE TYPE "TimeFrame" AS ENUM (
                '1M',
                '10M',
                '1H',
                'D',
                'W',
                'M',
                'Q',
                'Y'
                );""",
            """ CREATE TYPE "OrderDirection" AS ENUM (
                'BUY',
                'SELL'
                );""",
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
            """ CREATE TYPE "OperationDirection" AS ENUM (
                'BUY',
                'SELL'
                );""",
            """ CREATE TYPE "TradeType" AS ENUM (
                'LONG',
                'SHORT'
                );""",
            """ CREATE TYPE "TradeStatus" AS ENUM (
                'INITIAL',
                'NEW',
                'POST',
                'OPEN',
                'CLOSE',
                'ARCHIVE',
                'CANCELED'
                );""",
            ]# }}}

        for i in requests:
            await self.transaction(i)
    # }}}
    async def __createExchangeTable(self):# {{{
        keeper = Keeper()
        request = """
        CREATE TABLE exchange (
            name text PRIMARY KEY,
            session_begin TIME WITH TIME ZONE,
            session_end TIME WITH TIME ZONE,
            evening_begin TIME WITH TIME ZONE,
            evening_end TIME WITH TIME ZONE
            );
        """
        res = await self.transaction(request)
        return res
# }}}
    async def __createAssetTable(self):# {{{
        keeper = Keeper()
        request = """
        CREATE TABLE asset (
            exchange text REFERENCES exchange(name),
            type "AssetType",
            ticker text,
            name text,
            figi text PRIMARY KEY
            );
        """
        res = await self.transaction(request)
        return res
# }}}
    async def __createBarsDataTable(self, asset: Asset, data_type: DataType):# {{{
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
    async def __createAccountTable(self):# {{{
        request = """
        CREATE TABLE account(
            broker text,
            broker_id text,
            name text
            );
        """
        res = await self.transaction(request)
        return res
# }}}

    async def __createOrderTable(self):# {{{
        request = """
        CREATE TABLE trades(
            trd_id      REFERENCES trades(trd_id),
            ord_id      float PRIMARY KEY,
            status      "OrderStatus",

            figi        "Asset" REFERENCES asset(figi),
            lots        integer,
            price       float,
            stop_price  float,
            exec_price  float,
            );
            """
        res = await self.transaction(request)
        return res
# }}}
    async def __createOperationTable(self):# {{{
        request = """
        CREATE TABLE trades(
            trd_id      REFERENCES trades(trd_id),
            opr_id      float PRIMARY KEY,

            dt TIMESTAMP WITH TIME ZONE PRIMARY KEY,
            figi        "Asset" REFERENCES asset(figi),
            lots        integer,
            price       float,
            stop_price  float,
            exec_price  float,
            );
            """
        res = await self.transaction(request)
        return res
# }}}
    async def __createTradeTable(self):# {{{
        request = """
        CREATE TABLE trades(
            id TIMESTAMP PRIMARY KEY,
            status text,
            dt TIMESTAMP WITH TIME ZONE,
            strategy text,
            version text,
            type text
            );
            """
        res = await self.transaction(request)
        return res
# }}}

    async def loadBars(self, asset, data_type, begin, end):# {{{
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
    async def view(self):# {{{
        request = "SELECT * FROM afks"
        res = await self.transaction(request)
        return res
# }}}

    async def _createStrategyTable(self):# {{{
        request = """
        CREATE TABLE strategy(
            name text,
            version text,
            PRIMARY KEY (name, version)
            );
        """
        res = await self.transaction(request)
        return res
# }}}
    async def _createOrderTable(self):# {{{
        request = """
        CREATE TABLE orders(
            trade_id ___ _ # тайм штамп флоат как впихнуть в постгрес? попробовать
            dt TIMESTAMP WITH TIME ZONE PRIMARY KEY,
            direction "OrderDirection",
            PRIMARY KEY (name, version)
            );
        """
        res = await self.transaction(request)
        return res
# }}}

#     async def __isExistTable(self, table_name: str):# {{{
#         print(table_name)
#         input("STOP")
#         request = f"""
#         SELECT * FROM INFORMATION_SCHEMA.TABLES
#         WHERE TABLE_NAME="{table_name}";
#         """
#         try:
#             res = await self.transaction(request)
#             print(res)
#             input("try")
#         except asyncpg.exceptions.UndefinedColumnError as err:
#             input("col")
#             return False
#         except asyncpg.exceptions.DuplicateTableError as err:
#             input("dubl")
#             return True
#         except asyncpg.exceptions.UndefinedTableError as err:
#             input("undef table")
#             return False
# # }}}

async def main():
    k = Keeper()
    await k.createDataBase()
    ...

if __name__ == "__main__":
    asyncio.run(main())

