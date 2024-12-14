#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from avin.core import BarChangedEvent, Chart, NewHistoricalBarEvent
from avin.tester._virtual_broker import _VirtualBroker
from avin.tester.test import Test
from avin.utils import logger


class Tester:
    def __init__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.__test = None
        self.__broker = None

    # }}}

    async def run(self, test: Test):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        logger.info(f":: Tester run {test}")
        self.__test = test

        self.__loadBroker()
        self.__setAccount()
        self.__setTradeList()
        self.__createEmptyCharts()
        self.__createBarStream()

        await self.__clearTest()
        await self.__connectStrategy()
        await self.__startStrategy()
        await self.__runDataStream()
        await self.__finishStrategy()
        await self.__updateTest()

        logger.info(f":: {self.__test} complete!")
        self.__clearAll()

    # }}}

    def __loadBroker(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadBroker()")

        self.__broker = _VirtualBroker
        self.__broker.setTest(self.__test)
        self.__broker.new_bar.aconnect(self.__onBarEvent)
        self.__broker.bar_changed.aconnect(self.__onBarEvent)

        # TODO:
        # self.__broker.reset()  # clear orders, subscriptions...

    # }}}
    def __setAccount(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__setAccount()")

        account = self.__broker.getAccount(self.__test.account)
        self.__test.strategy.setAccount(account)

    # }}}
    def __setTradeList(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__setTradeList()")

        trade_list = self.__test.trade_list
        self.__test.strategy.setTradeList(trade_list)

    # }}}
    def __createEmptyCharts(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createEmptyCharts()")

        for timeframe in self.__test.strategy.timeframe_list():
            chart = Chart(self.__test.asset, timeframe, [])
            self.__test.asset.setChart(chart)

    # }}}
    def __createBarStream(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createBarStream()")

        timeframe_list = self.__test.strategy.timeframe_list()
        asset = self.__test.asset

        for timeframe in timeframe_list:
            self.__broker.createBarStream(asset, timeframe)

    # }}}
    def __clearAll(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__clearAll()")

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
    async def __updateTest(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__updateTest()")

        self.__test.status = Test.Status.COMPLETE
        await Test.update(self.__test)

    # }}}

    async def __onBarEvent(  # {{{
        self, event: NewHistoricalBarEvent | BarChangedEvent
    ) -> None:
        logger.debug(f"{self.__class__.__name__}.__onBarEvent()")
        logger.info(f"-> receive {event}")

        await self.__test.asset.receive(event)

    # }}}


if __name__ == "__main__":
    ...
