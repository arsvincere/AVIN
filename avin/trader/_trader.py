#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import asyncio

from avin.core import AssetList, TimeFrame
from avin.logger import logger
from avin.trader.tinkoff import Tinkoff
from avin.utils import Cmd


class Trader:  # {{{
    def __init__(self):  # {{{
        logger.debug("Genera.__init__()")
        self.work = False
        self.event = None

    # }}}
    def __loadConfig(self):  # {{{
        logger.info(":: Trader load config")
        self.cfg = {
            "broker": Tinkoff,
            # "broker":           Sandbox,
            # "broker":           AsyncTinkoff,
            "token": Tinkoff.TOKEN,
            "account": 0,
            "strategyes": "One,Two,Three,Four,Five",
            "timeframe_list": [TimeFrame("1M")],
        }

    # }}}
    def __loadTimeTable(self):  # {{{
        logger.info(":: Trader load timetable")
        self.timetable = None

    # }}}
    def __loadStrategyes(self):  # {{{
        logger.info(":: Trader load strategyes")
        self.strategyes = list()

    # }}}
    def __loadTeam(self):  # {{{
        logger.info(":: Trader load team")
        self.broker = self.cfg["broker"](trader=self)
        # self.analytic = Analytic(trader=self)
        # self.market = Market(trader=self)
        # self.risk = Risk(trader=self)
        # self.ruler = Ruler(trader=self)
        # self.adviser = Adviser(trader=self)
        # self.trader = Trader(trader=self)
        self.observer = Observer(trader=self)

    # }}}
    def __makeGeneralAssetList(self):  # {{{
        logger.info(":: Trader make asset list")
        # self.alist = AssetList.load(Cmd.path(ASSET_DIR, "afks"), parent=self)
        self.alist = AssetList.load(
            Cmd.path(ASSET_DIR, "Trio.al"), parent=self
        )

    # }}}
    async def __updateData(self):  # {{{
        logger.info(":: Trader update historical data")
        for asset in self.alist:
            self.scout.updateAllData(asset)

    # }}}
    async def __loadCharts(self):  # {{{
        logger.info(":: Trader load all chart")
        for asset in self.alist:
            logger.info(f"  loading chart {asset.ticker}")
            asset.loadAllChart()

    # }}}
    async def __updateAnalytic(self):  # {{{
        logger.info(":: Trader update data analytic")
        # for asset in self.alist:
        #     self.analytic.updateAll(asset)

    # }}}
    async def __processStrategy(self, asset):  # {{{
        logger.info(f":: Trader process {asset.ticker}")
        for s in self.strategyes:
            s.process(asset)

    # }}}
    async def __processSignals(self):  # {{{
        logger.info(":: Trader process signals")

    # }}}
    async def __processPositions(self):  # {{{
        logger.info(":: Trader process positions")

    # }}}
    async def __finishWork(self):  # {{{
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
    async def __attemptConnect(self):  # {{{
        logger.debug("Trader.__attemptConnect()")
        asyncio.create_task(self.broker.connect(self.cfg["token"]))
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
        self.scout.setBroker(self.broker)
        accounts = self.broker.getAllAccounts()
        self.account = accounts[0]

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
        status = self.broker.isMarketOpen()
        while not status:
            logger.info("  waiting to open market, sleep 1 minute")
            await asyncio.sleep(60)
            status = self.broker.isMarketOpen()
        logger.info("  market is open!")

    # }}}
    async def __waitMarketEvent(self):  # {{{
        logger.debug("  wait market event")
        self.event = self.scout.observe()

    # }}}
    async def __processEvent(self):  # {{{
        if self.event is None:
            return
        elif self.event.type == Event.Type.NEW_BAR:
            logger.info(f"-> receive event {self.event.type}")
            updated_asset = self.alist.receive(self.event)
        await self.__processSignals()
        await self.__processPositions()
        self.event = None

    # }}}
    async def __mainCycle(self):  # {{{
        logger.info(":: Trader run main cycle")
        self.work = True
        while self.work:
            await self.__ensureMarketOpen()
            await self.__waitMarketEvent()
            await self.__processEvent()
            # print(self.account)
            # print(type(self.account))
            # print(self.account.money())
            # p = self.account.portfolio()
            # for i in p.money:
            #     print(i)

        await self.__finishWork()

    # }}}
    async def initialize(self):  # {{{
        logger.info(":: Trader start initialization")
        self.__loadConfig()
        self.__loadTimeTable()
        self.__loadStrategyes()
        self.__loadTeam()
        self.__makeGeneralAssetList()

    # }}}
    async def run(self):  # {{{
        logger.info(":: Trader run")
        await self.__ensureConnection()
        await self.__updateData()
        await self.__loadCharts()
        await self.__updateAnalytic()
        await self.__makeDataStream()
        await self.__mainCycle()

    # }}}
    def stop(self):  # {{{
        if self.work:
            logger.info(":: Trader shuting down")
            self.work = False
        else:
            logger.warning("Trader.stop() called, but now he is not work")

    # }}}


# }}}
