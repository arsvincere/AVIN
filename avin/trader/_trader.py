#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import asyncio

from avin.core import AssetList, Event, Strategy, TimeFrame
from avin.data import Data
from avin.trader.scout import Scout
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

# await broker.createDataStream(mvid, DataType.BAR_1M)
# await broker.new_bar.async_connect(onNewBar)
# started = await broker.startDataStream()
# if not started:
#     print("попытка 2")
#     await broker.disconnect()
#     print("sleep 10 sec")
#     await asyncio.sleep(10)
#     await broker.connect()
#     await broker.createDataStream(mvid, DataType.BAR_1M)
#     started = await broker.startDataStream()
# if not started:
#     print("попытка 3")
#     await broker.disconnect()
#     print("sleep 10 sec")
#     await asyncio.sleep(10)
#     await broker.connect()
#     await broker.createDataStream(mvid, DataType.BAR_1M)
#     started = await broker.startDataStream()
# if not started:
#     print("попытка 4")
#     await broker.disconnect()
#     print("sleep 10 sec")
#     await asyncio.sleep(10)
#     await broker.connect()
#     await broker.createDataStream(mvid, DataType.BAR_1M)
#     started = await broker.startDataStream()
# if not started:
#     print("попытка 5")
#     await broker.disconnect()
#     print("sleep 10 sec")
#     await asyncio.sleep(10)
#     await broker.connect()
#     await broker.createDataStream(mvid, DataType.BAR_1M)
#     started = await broker.startDataStream()
# if not started:
#     print("Game over.")
#     exit(0)
#
# await asyncio.sleep(600)


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
            # "broker":           Sandbox,
            # "broker":           AsyncTinkoff,
            "token": Tinkoff.TOKEN,
            "account": 0,
            "strategy_list": [
                ("Every", "minute"),
            ],
            "timeframe_list": [TimeFrame("1M")],
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
            name, version = i
            strategy = await Strategy.load(name, version)
            self.strategyes.append(strategy)

    # }}}
    async def __loadTeam(self):  # {{{
        logger.info(":: Trader load team")
        self.broker = self.cfg["broker"](trader=self)
        # self.analytic = Analytic(trader=self)
        # self.market = Market(trader=self)
        # self.risk = Risk(trader=self)
        # self.ruler = Ruler(trader=self)
        # self.adviser = Adviser(trader=self)
        # self.trader = Trader(trader=self)
        self.scout = Scout(broker=self.broker, trader=self)

    # }}}
    async def __makeGeneralAssetList(self):  # {{{
        logger.info(":: Trader make asset list")
        # self.alist = AssetList.load(Cmd.path(ASSET_DIR, "afks"), parent=self)
        self.alist = await AssetList.load("Trio")

    # }}}
    async def __cacheAssetsInfo(self):  # {{{
        logger.info(":: Trader caching assets info")
        for asset in self.alist:
            logger.info(f"  - caching {asset}")
            await asset.cacheInfo()

    # }}}
    async def __updateData(self):  # {{{
        logger.info(":: Trader update historical data")
        timeframe_list = self.cfg["timeframe_list"]
        for asset in self.alist:
            for timeframe in timeframe_list:
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
    async def __cacheCharts(self):  # {{{
        logger.info(":: Trader caching all chart")
        timeframe_list = self.cfg["timeframe_list"]
        for asset in self.alist:
            for timeframe in timeframe_list:
                logger.info(f"  - caching chart {asset.ticker}-{timeframe}")
                await asset.cacheChart(timeframe)

    # }}}
    async def __connectStrategyes(self):  # {{{
        for strategy in self.strategyes:
            await strategy.start()
            await strategy.connect(self.alist)

    # }}}
    async def __processStrategy(self, asset):  # {{{
        logger.info(f":: Trader process {asset.ticker}")
        for s in self.strategyes:
            s.process(asset)

    # }}}
    async def __attemptConnect(self):  # {{{
        logger.debug("Trader.__attemptConnect()")

        asyncio.create_task(self.broker.connect())
        for n in range(5):
            if self.broker.isConnect():
                logger.info("  successfully connected!")
                return True
            else:
                logger.info(f"  waiting connection... ({n})")
                await asyncio.sleep(1)
        else:
            logger.error("  fail to connect!")
            return False

    # }}}
    async def __ensureConnection(self):  # {{{
        logger.info(":: Trader ensure connection")
        result = await self.__attemptConnect()

        while not result:
            logger.info("  sleep 1 minute...")
            await asyncio.sleep(60)
            logger.info("  try again:")
            result = await self.__attemptConnect()

        # FIX: пусть этот треш пока тут полежит, надо подумать
        # куда это вынести и в какой момент лучше конетить стратегию
        # к аккаунту и конетить ли вообще, или стратегия вообще не
        # будет знать ничего про аккаунт...
        self.scout.setBroker(self.broker)
        accounts = self.broker.getAllAccounts()
        self.account = accounts[0]
        for strategy in self.strategyes:
            strategy.setAccount(self.account)

    # }}}
    async def __makeDataStream(self):  # {{{
        logger.info(":: Trader make data stream")
        self.scout.makeStream(self.alist, self.cfg["timeframe_list"])

    # }}}
    async def __ensureMarketOpen(self):  # {{{
        logger.debug(":: Trader ensure market open")
        """
        Loop until the market is openly.
        :return: when market is available for trading
        """
        status = await self.broker.isMarketOpen()
        while not status:
            logger.info("  waiting to open market, sleep 1 minute")
            await asyncio.sleep(60)
            status = self.broker.isMarketOpen()
        logger.debug("  market is open!")

    # }}}
    async def __waitMarketEvent(self):  # {{{
        logger.debug("  wait market event")
        self.event = self.scout.observe()

    # }}}
    async def __processEvent(self):  # {{{
        if self.event is None:
            return
        elif self.event.type == Event.Type.NEW_BAR:
            logger.debug(f"-> receive event {self.event.type}")
            asset = self.alist.find(figi=self.event.figi)
            await asset.update(self.event)

        self.event = None

    # }}}
    async def __mainCycle(self):  # {{{
        logger.info(":: Trader run main cycle")
        self.work = True
        while self.work:
            await self.__ensureMarketOpen()
            await self.__waitMarketEvent()
            await self.__processEvent()

        await self.__finishWork()

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
        await self.__loadTeam()
        await self.__makeGeneralAssetList()
        await self.__cacheAssetsInfo()

    # }}}
    async def run(self):  # {{{
        logger.info(":: Trader run")
        await self.__ensureConnection()
        await self.__updateData()
        await self.__updateAnalytic()
        await self.__cacheCharts()
        await self.__connectStrategyes()
        await self.__makeDataStream()
        await self.__mainCycle()

    # }}}
    async def stop(self):  # {{{
        if self.work:
            logger.info(":: Trader shuting down")
            self.work = False
        else:
            logger.warning("Trader.stop() called, but now he is not work")

    # }}}
