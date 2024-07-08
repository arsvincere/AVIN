#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

""" doc """

import asyncio
import asyncpg
from datetime import datetime, UTC
from avin.core import Bar, Asset, TimeFrame
from avin.data import Exchange, AssetType

class Keeper():
    def __init__(self):# {{{
        self.user = "alex"
        self.database = "appdb"
        self.host='127.0.0.1'
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
    async def view(self):# {{{
        request = "SELECT * FROM afks"
        res = await self.transaction(request)
        return res
    # }}}
    async def create(self):# {{{
        request = """
        CREATE TABLE afks(
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
    async def createTradeTable(self):# {{{
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
    async def addData(self, asset, timeframe, bars):# {{{
        all_values = str()
        for bar in bars:
            value = self.__formatBarData(bar)
            all_values += value
        all_values = all_values[0:-2] + ";"

        request = f"""
        INSERT INTO aflt (dt, open, high, low, close, volume)
        VALUES
            {all_values}
        """

        res = await self.transaction(request)
        return res

    # }}}
    async def loadBars(self, asset, timeframe, begin, end):# {{{
        request = f"""
        SELECT dt, open, high, low, close, volume
        FROM afks
        WHERE dt >= '{begin}' AND dt < '{end}'
        ORDER BY dt
        ;
        """

        res = await self.transaction(request)
        return res

# }}}
    def __formatBarData(self, bar: Bar):# {{{
        dt = f"'{bar.dt.isoformat()}'"
        string = (
            "("
            f"{dt}, {bar.open}, {bar.high}, {bar.low}, {bar.close}, {bar.vol}"
            "),\n"
            )
        return string
    # }}}

async def main():
    asset = Asset.byTicker(Exchange.MOEX, AssetType.Share, "AFKS")
    timeframe = TimeFrame("D")
    chart = asset.loadChart(timeframe, "2023-01-01", "2024-01-01")
    k = Keeper()
    # res = await k.create()
    # res = await k.addData(asset, timeframe, chart.getBars())
    # res = await k.view()
    # for i in res:
    #     dt = i["dt"]
    #     print(dt)
    #     print(type(dt))
    # res = await k.createTradeTable()

    begin = datetime(2023, 10, 13, tzinfo=UTC)
    end = datetime(2023, 11, 2, tzinfo=UTC)
    res = await k.loadBars(asset, timeframe, begin, end)
    for i in res:
        # print(i["dt"])
        print(i[4])



if __name__ == "__main__":
    asyncio.run(main())

