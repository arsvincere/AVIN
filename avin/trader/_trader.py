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
from avin.utils import logger

# FIX: обновление данных сейчас идет с моэкс а там задержка...
# после обновления данных в БД и загрузки графиков - надо еще
# раз обновлять данные но уже у брокера запрашивать

# TODO: вот примерно так выглядеть будет попытка создания
# дата стрима и пересоздание если не получилось
# сделай из этого говнокода цикл аккуратный с нормальными логами
# и запихай в какой нибудь метод типо
# trader.__createDataStream

# TODO: причесать логи и отступы в них


class Trader:
    def __init__(self):  # {{{
        logger.debug("Genera.__init__()")
        self.work = False
        self.event = None

    # }}}
    async def __loadConfig(self):  # {{{
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
    async def __loadTimeTable(self):  # {{{
        logger.info(":: Trader load timetable")
        self.timetable = None

    # }}}
    async def __loadStrategyes(self):  # {{{
        logger.info(":: Trader load strategyes")
        self.strategyes = list()
        for i in self.cfg["strategy_list"]:
            strategy = await Strategy.load(*i)
            self.strategyes.append(strategy)

    # }}}
    async def __loadTimeFrameList(self):  # {{{
        logger.info(":: Trader load timeframe list")

        self.timeframe_list = list()
        for i in self.cfg["timeframe_list"]:
            timeframe = TimeFrame(i)
            self.timeframe_list.append(timeframe)

    # }}}
    async def __loadBroker(self):  # {{{
        logger.info(":: Trader load broker")
        self.broker = self.cfg["broker"]

    # }}}
    async def __makeGeneralAssetList(self):  # {{{
        logger.info(":: Trader make asset list")
        self.alist = await AssetList.load("Trio")

    # }}}
    async def __cacheAssetsInfo(self):  # {{{
        logger.info(":: Trader caching assets info")
        for asset in self.alist:
            logger.info(f"  - caching {asset}")
            await asset.cacheInfo()

    # }}}
    async def __updateHistoricalData(self):  # {{{
        logger.info(":: Trader update historical data")
        for asset in self.alist:
            for timeframe in self.timeframe_list:
                await Data.update(
                    ID=asset.ID,
                    data_type=timeframe.toDataType(),
                )

    # }}}
    async def __updateAnalytic(self):  # {{{
        logger.info(":: Trader update data analytic")
        # for asset in self.alist:
        #     self.analytic.updateAll(asset)

    # }}}
    async def __setAccount(self):  # {{{
        logger.info(":: Trader set account")

        account = await self.broker.getAccount(self.cfg["account"])
        if account:
            self.account = account
            for strategy in self.strategyes:
                strategy.setAccount(self.account)
        else:
            assert False, "Account not found"

    # }}}
    async def __cacheCharts(self):  # {{{
        logger.info(":: Trader caching all chart")
        timeframe_list = self.cfg["timeframe_list"]
        for asset in self.alist:
            for timeframe in timeframe_list:
                logger.info(f"  - caching chart {asset.ticker}-{timeframe}")
                await asset.cacheChart(timeframe)

    # }}}
    async def __updateRealTimeData(self):  # {{{
        logger.info(":: Trader update real time data")

        # TODO: тут добавлять бары к графикам в озу
        # пока у них сигналы не подключены

    # }}}
    async def __startStrategyes(self):  # {{{
        logger.info(":: Trader start strategyes")
        for strategy in self.strategyes:
            await strategy.start()

    # }}}
    async def __connectStrategyes(self):  # {{{
        logger.info(":: Trader connect strategyes")
        for strategy in self.strategyes:
            await strategy.connect(self.alist)

    # }}}
    async def __createTransactionStream(self):  # {{{
        logger.info(":: Trader create transaction stream")

        await self.broker.createTransactionStream(self.account)

    # }}}
    async def __createBarStream(self):  # {{{
        logger.info(":: Trader make data stream")
        for asset in self.alist:
            for timeframe in self.timeframe_list:
                await self.broker.createBarStream(asset, timeframe)

        await self.broker.new_bar.async_connect(self.__onNewBar)

    # }}}
    async def __startTransactionStream(self):  # {{{
        logger.info(":: Trader start transaction stream")

        await self.broker.startTransactionStream()

    # }}}
    async def __startBarStream(self):  # {{{
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
    async def __mainCycle(self):  # {{{
        logger.info(":: Trader run main cycle")
        self.work = True
        while self.work:
            # await self.__ensureConnection()
            # await self.__ensureMarketOpen()
            await asyncio.sleep(60)

        await self.__finishWork()

    # }}}
    async def __ensureConnection(self):  # {{{
        logger.info(":: Trader ensure connection")
        result = await self.broker.connect()

        while not result:
            logger.info("  sleep 1 minute...")
            await asyncio.sleep(60)
            logger.info("  try again")
            result = await self.broker.connect()

        logger.info("  connection ok")

    # }}}
    async def __ensureMarketOpen(self):  # {{{
        """
        Loop until the market is openly.
        :return: when market is available for trading
        """
        logger.info(":: Trader ensure market open")

        status = await self.broker.isMarketOpen()
        while not status:
            logger.info("  waiting to open market, sleep 1 minute")
            await asyncio.sleep(60)
            status = self.broker.isMarketOpen()

        logger.info("  market is open!")

    # }}}
    async def __onNewBar(self, event: NewBarEvent):  # {{{
        logger.info(f"-> receive event {event}")
        assert event.type == Event.Type.NEW_BAR

        asset = self.alist.find(figi=event.figi)
        await asset.receiveNewBar(event)

    # }}}
    async def __finishWork(self):  # {{{
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
    async def initialize(self):  # {{{
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
    async def run(self):  # {{{
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
    async def stop(self):  # {{{
        if self.work:
            logger.info(":: Trader shuting down")
            self.work = False
        else:
            logger.warning("Trader.stop() called, but now he is not work")

    # }}}
