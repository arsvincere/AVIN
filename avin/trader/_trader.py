#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import asyncio

from avin.core import AssetList, Event, NewBarEvent, Strategy, TimeFrame
from avin.data import Data
from avin.trader.tinkoff import Tinkoff
from avin.utils import logger, now


class Trader:
    def __init__(self):  # {{{
        logger.debug("Genera.__init__()")
        self.work = False
        self.event = None

    # }}}
    async def __loadConfig(self) -> None:  # {{{
        logger.info(":: Trader load config")
        self.cfg = {
            "broker": Tinkoff,
            "account": "Alex",
            "strategy_list": [
                ("Every", "five"),
            ],
            "timeframe_list": [
                "1M",
            ],
        }

    # }}}
    async def __loadTimeTable(self) -> None:  # {{{
        logger.info(":: Trader load timetable")
        self.timetable = None

    # }}}
    async def __loadStrategyes(self) -> None:  # {{{
        logger.info(":: Trader load strategyes")
        self.strategyes = list()
        for i in self.cfg["strategy_list"]:
            strategy = await Strategy.load(*i)
            self.strategyes.append(strategy)

    # }}}
    async def __loadTimeFrameList(self) -> None:  # {{{
        logger.info(":: Trader load timeframe list")

        self.timeframe_list = list()
        for i in self.cfg["timeframe_list"]:
            timeframe = TimeFrame(i)
            self.timeframe_list.append(timeframe)

    # }}}
    async def __loadBroker(self) -> None:  # {{{
        logger.info(":: Trader load broker")
        self.broker = self.cfg["broker"]

    # }}}
    async def __makeGeneralAssetList(self) -> None:  # {{{
        logger.info(":: Trader make asset list")
        self.alist = await AssetList.load("Trio")

    # }}}
    async def __cacheAssetsInfo(self) -> None:  # {{{
        logger.info(":: Trader caching assets info")
        assert self.alist is not None

        for asset in self.alist:
            logger.info(f"  - caching {asset}")
            await asset.cacheInfo()

    # }}}
    async def __updateHistoricalData(self) -> None:  # {{{
        logger.info(":: Trader update historical data")
        assert self.alist is not None

        for asset in self.alist:
            for timeframe in self.timeframe_list:
                await Data.update(
                    ID=asset.ID,
                    data_type=timeframe.toDataType(),
                )

    # }}}
    async def __updateAnalytic(self) -> None:  # {{{
        logger.info(":: Trader update data analytic")
        # for asset in self.alist:
        #     self.analytic.updateAll(asset)

    # }}}
    async def __setAccount(self) -> None:  # {{{
        logger.info(":: Trader set account")

        account = await self.broker.getAccount(self.cfg["account"])
        if account:
            self.account = account
            for strategy in self.strategyes:
                strategy.setAccount(self.account)
        else:
            assert False, "Account not found"

    # }}}
    async def __cacheCharts(self) -> None:  # {{{
        logger.info(":: Trader caching all chart")
        assert self.alist is not None

        timeframe_list = self.cfg["timeframe_list"]
        for asset in self.alist:
            for timeframe in timeframe_list:
                logger.info(f"  caching chart {asset.ticker}-{timeframe}")
                await asset.cacheChart(timeframe)

    # }}}
    async def __updateRealTimeData(self) -> None:  # {{{
        logger.info(":: Trader update real time data")

        for asset in self.alist:
            for timeframe in self.timeframe_list:
                chart = asset.chart(timeframe)
                begin = chart.last.dt + timeframe
                end = now()
                new_bars = await self.broker.getHistoricalBars(
                    asset, timeframe, begin, end
                )
                count = len(new_bars)
                if count:
                    logger.info(
                        f"  {asset.ticker}-{timeframe} add {count} bars"
                    )
                    for bar in new_bars:
                        chart.addNewBar(bar)

    # }}}
    async def __startStrategyes(self) -> None:  # {{{
        logger.info(":: Trader start strategyes")
        for strategy in self.strategyes:
            await strategy.start()

    # }}}
    async def __connectStrategyes(self) -> None:  # {{{
        logger.info(":: Trader connect strategyes")
        assert self.alist is not None

        for strategy in self.strategyes:
            await strategy.connect(self.alist)

    # }}}
    async def __createTransactionStream(self) -> None:  # {{{
        logger.info(":: Trader create transaction stream")

        await self.broker.createTransactionStream(self.account)

    # }}}
    async def __createBarStream(self) -> None:  # {{{
        logger.info(":: Trader make data stream")
        assert self.alist is not None

        for asset in self.alist:
            for timeframe in self.timeframe_list:
                await self.broker.createBarStream(asset, timeframe)

        await self.broker.new_bar.async_connect(self.__onNewBar)

    # }}}
    async def __startTransactionStream(self) -> None:  # {{{
        logger.info(":: Trader start transaction stream")

        await self.broker.startTransactionStream()

    # }}}
    async def __startBarStream(self) -> None:  # {{{
        logger.info(":: Trader start data stream")
        result = await self.broker.startDataStream()

        while not result:
            logger.info("  try again after 10 seconds")
            await self.broker.disconnect()
            await asyncio.sleep(10)
            await self.broker.connect()
            await self.__createBarStream()
            result = await self.broker.startDataStream()

    # }}}
    async def __mainCycle(self) -> None:  # {{{
        logger.info(":: Trader run main cycle")
        self.work = True
        while self.work:
            await self.__ensureConnection()
            await self.__ensureMarketOpen()
            await asyncio.sleep(60)

        await self.__finishWork()

    # }}}
    async def __ensureConnection(self) -> None:  # {{{
        logger.info(":: Trader ensure connection")
        result = await self.broker.connect()

        while not result:
            logger.info("  sleep 20 seconds")
            await asyncio.sleep(20)
            logger.info("  try again")
            result = await self.broker.connect()

        logger.info("  connection ok")

    # }}}
    async def __ensureMarketOpen(self) -> None:  # {{{
        """
        Loop until the market is openly.
        Return when market is available for trading
        """
        logger.info(":: Trader ensure market open")

        status = await self.broker.isMarketOpen()
        while not status:
            logger.info("  waiting to open market, sleep 20 seconds")
            await asyncio.sleep(20)
            status = await self.broker.isMarketOpen()

        logger.info("  market is open!")

    # }}}
    async def __onNewBar(self, event: NewBarEvent) -> None:  # {{{
        logger.info(f"-> receive bar {event}")
        assert event.type == Event.Type.NEW_BAR
        assert self.alist is not None

        asset = self.alist.find(figi=event.figi)
        assert asset is not None
        await asset.receiveNewBar(event)

    # }}}
    async def __finishWork(self) -> None:  # {{{
        for strategy in self.strategyes:
            await strategy.finish()
        ...
        # strategy.finish()
        # keeper.saveAll
        #     saveSignals()
        #     saveOrders()
        #     saveOperations()
        #     savePositions()   (Portfolio snap shot)
        # keeper.createReport()
        # sendTelegram()
        # closeConnection()
        # updateGUI
        self.work = False

    # }}}
    async def initialize(self) -> None:  # {{{
        logger.info(":: Trader start initialization")
        await self.__loadConfig()
        await self.__loadTimeTable()
        await self.__loadStrategyes()
        await self.__loadTimeFrameList()
        await self.__loadBroker()
        await self.__makeGeneralAssetList()
        await self.__cacheAssetsInfo()
        await self.__updateHistoricalData()
        await self.__updateAnalytic()

    # }}}
    async def run(self) -> None:  # {{{
        logger.info(":: Trader run")
        await self.__ensureConnection()
        await self.__setAccount()
        await self.__cacheCharts()
        await self.__updateRealTimeData()
        await self.__startStrategyes()
        await self.__connectStrategyes()
        await self.__createTransactionStream()
        await self.__createBarStream()
        await self.__startTransactionStream()
        await self.__startBarStream()
        await self.__mainCycle()

    # }}}
    async def stop(self) -> None:  # {{{
        if self.work:
            logger.info(":: Trader shuting down")
            self.work = False
        else:
            logger.warning("Trader.stop() called, but now he is not work")

    # }}}
