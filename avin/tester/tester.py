#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from avin.core import BarChangedEvent, Chart, NewHistoricalBarEvent
from avin.tester.test import Test
from avin.tester.virtual_broker import VirtualBroker
from avin.utils import logger


class Tester:
    def __init__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.__test = None
        self.__broker = None

    # }}}

    async def run(self, test: Test):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")
        assert test is not None

        logger.info(f":: Tester run {test}")
        self.__test = test

        self.__loadBroker()
        self.__setAccount()
        self.__createEmptyCharts()
        self.__createBarStream()

        await self.__clearTest()
        await self.__setTradeList()
        await self.__connectStrategy()
        await self.__startStrategy()
        await self.__runDataStream()
        await self.__finishStrategy()
        await self.__updateTestStatus()

        logger.info(f":: {self.__test} complete!")
        self.__clearAll()

    # }}}

    def __loadBroker(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadBroker()")

        self.__broker = VirtualBroker
        self.__broker.setTest(self.__test)
        self.__broker.new_bar.aconnect(self.__onBarEvent)
        self.__broker.bar_changed.aconnect(self.__onBarEvent)

    # }}}
    def __setAccount(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__setAccount()")

        account = self.__broker.getAccount(self.__test.account)
        self.__test.strategy.setAccount(account)

    # }}}
    def __createEmptyCharts(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createEmptyCharts()")

        Chart.MAX_BARS_COUNT = 2000
        for timeframe in self.__test.strategy.timeframes():
            bars = list()
            chart = Chart(self.__test.asset, timeframe, bars)
            self.__test.asset.setChart(chart)

    # }}}
    def __createBarStream(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createBarStream()")

        timeframe_list = self.__test.strategy.timeframes()
        for timeframe in timeframe_list:
            self.__broker.createBarStream(timeframe)

    # }}}
    def __clearAll(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__clearAll()")

        self.__broker.reset()  # clear orders, subscriptions...
        self.__test.asset.clearCache()
        self.__broker = None
        self.__test = None

    # }}}

    async def __clearTest(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__clearTest()")

        await Test.deleteTrades(self.__test)
        self.__test.status = Test.Status.PROCESS
        await Test.update(self.__test)

    # }}}
    async def __setTradeList(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__setTradeList()")

        trade_list = self.__test.trade_list
        self.__test.strategy.setTradeList(trade_list)

    # }}}
    async def __connectStrategy(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connectStrategy()")

        strategy = self.__test.strategy
        asset = self.__test.asset
        long = self.__test.enable_long
        short = self.__test.enable_short

        await strategy.connect(asset, long, short)

    # }}}
    async def __startStrategy(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__startStrategy()")
        logger.info(f":: Start {self.__test.strategy}")

        await self.__test.strategy.start()

    # }}}
    async def __runDataStream(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__runDataStream()")
        logger.info(":: Run data stream")

        await self.__broker.runDataStream()

    # }}}
    async def __finishStrategy(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__finishStrategy()")

        await self.__test.strategy.finish()

    # }}}
    async def __updateTestStatus(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__updateTestStatus()")

        self.__test.status = Test.Status.COMPLETE
        await Test.update(self.__test)

    # }}}

    async def __onBarEvent(  # {{{
        self, event: NewHistoricalBarEvent | BarChangedEvent
    ) -> None:
        logger.debug(f"{self.__class__.__name__}.__onBarEvent()")

        await self.__test.asset.receive(event)

    # }}}


if __name__ == "__main__":
    ...
