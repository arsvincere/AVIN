#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from avin.core import Chart
from avin.tester._virtual_broker import _VirtualBroker
from avin.tester.test import Test
from avin.utils import logger


class Tester:
    def __init__(self):  # {{{
        self.__test = None
        self.__slist = None
        self.__alist = None
        self.__current_asset = None
        self.__time = None

    # }}}
    def setTest(self, test: Test):  # {{{
        self.__clearAll()
        self.__test = test

    # }}}
    async def runTest(self):  # {{{
        logger.info(f":: Tester run {self.__test}")
        assert self.__test is not None

        await self.__test.clear()
        self.__test.status = Test.Status.PROCESS

        await self.__loadBroker()
        await self.__loadAssetList()
        await self.__loadStrategyList()
        self.__createTimeFrameList()
        self.__setAccount()
        self.__setTradeList()

        for asset in self.__alist:
            self.__setCurrentAsset(asset)
            self.__createEmptyCharts()
            await self.__connectStrategy()
            await self.__startTest()
            await self.__finishTest()

        print("exit 100500")
        exit(100500)

        self.__test.status = Test.Status.COMPLETE
        self.__createReport()
        self.__saveTest()
        logger.info(f":: '{self.test}' complete!")
        self.__clearAll()

    # }}}

    def __clearAll(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__clearAll()")

        self.__test = None
        self.__broker = None
        self.__alist = None  # common asset list
        self.__slist = None  # common strategy list
        self.__tflist = None  # common timeframe list
        self.__current_asset = None
        self.__time = None
        self.__total_time = None
        self.__last_emit = None

    # }}}
    async def __loadBroker(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setVirtualBroker()")

        self.__broker = _VirtualBroker
        self.__broker.setTest(self.__test)
        await self.__broker.new_bar.async_connect(self.__onNewBar)
        await self.__broker.bar_changed.async_connect(self.__onNewBar)

        # TODO:
        # self.__broker.reset()  # clear orders, subscriptions...

    # }}}
    async def __loadAssetList(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadAssetList()")

        self.__alist = await self.__test.strategy_set.createAssetList()

    # }}}
    async def __loadStrategyList(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadStrategyList()")

        self.__slist = await self.__test.strategy_set.createStrategyList()

    # }}}
    def __createTimeFrameList(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createTimeFrameList()")

        self.__tflist = self.__slist.createTimeFrameList()

    # }}}
    def __setAccount(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__setAccount()")

        account = self.__broker.getAccount(self.__test.account)
        for strategy in self.__slist:
            strategy.setAccount(account)

    # }}}
    def __setTradeList(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__setAccount()")

        tlist = self.__test.trade_list
        for strategy in self.__slist:
            strategy.setTradeList(tlist)

    # }}}
    def __setCurrentAsset(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__setCurrentAsset()")

        self.__current_asset = asset
        for timeframe in self.__tflist:
            self.__broker.createBarStream(asset, timeframe)

    # }}}
    def __createEmptyCharts(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createCharts()")

        for timeframe in self.__tflist:
            chart = Chart(self.__current_asset, timeframe, [])
            self.__current_asset.setChart(chart)

    # }}}
    async def __connectStrategy(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connectStrategy()")

        for strategy in self.__slist:
            items = self.__test.strategy_set[strategy]
            items = filter(
                lambda x: x.figi == self.__current_asset.figi, items
            )
            for i in items:
                await strategy.connect(self.__current_asset, i.long, i.short)

    # }}}

    async def __startTest(self) -> None:  # {{{
        logger.info(f":: Start testing {self.__current_asset.ticker}")

        # initialize strategy
        for strategy in self.__slist:
            await strategy.start()

        # start time
        await self.__broker.startDataStream()

    # }}}
    async def __onNewBar(  # {{{
        self, event: NewBarEvent | BarChanged
    ) -> None:
        logger.info(f"-> receive {event}")

        # TODO:
        # сюда теперь приходят и новые исторические бары и
        # и обновленные реал тайм бары
        # теперь название функции не очень подходящее
        # вообще возможно весь этот треш нужно внутри
        # брокера оставить, я ведь передаю ему ассеты когда подписываюсь
        # так что список у него есть вот пусть он их там и обновляет
        # нахер не нужен тут еще один вызов функции

        asset = self.__alist.find(figi=event.figi)
        await asset.receive(event)

    # }}}

    async def __finishTest(self):  # {{{
        logger.info(f"Finish test {self.__current_asset.ticker}")
        for i in self.__slist:
            await i.finish()
        self.__current_asset.clearCache()

    # }}}
    #     def __createReport(self):  # {{{
    #         self.test.updateReport()
    #
    #     # }}}
    #     def __saveTest(self):  # {{{
    #         Test.save(self.test)
    #         logger.info("Test saved")
    #
    #     # }}}


if __name__ == "__main__":
    ...
