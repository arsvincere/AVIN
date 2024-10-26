#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from datetime import UTC, datetime

from avin.const import DAY_BEGIN, ONE_SECOND
from avin.core import Bar, Broker, Chart
from avin.keeper import Keeper
from avin.tester.test import Test
from avin.utils import Signal, logger, now


class _VirtualBroker(Broker):  # {{{
    @classmethod  # getAccount
    def getAccount(cls, account_name: str) -> Account:
        logger.debug(f"Tinkoff.postStopLoss({account}, {order})")

    @classmethod  # postMarketOrder
    def postMarketOrder(cls, account: Account, order: Order) -> bool: ...

    @classmethod  # postLimitOrder
    async def postLimitOrder(
        cls, account: Account, order: LimitOrder
    ) -> bool: ...

    @classmethod  # postStopOrder
    async def postStopOrder(
        cls, account: Account, order: StopOrder
    ) -> bool: ...

    @classmethod  # postStopLoss
    async def postStopLoss(
        cls, account: Account, order: StopLoss
    ) -> bool: ...

    @classmethod  # startDataStream
    async def startDataStream(cls) -> bool: ...

    @classmethod  # startTransactionStream
    async def startTransactionStream(cls): ...

    @classmethod  # __checkOrders
    async def __checkOrders(cls): ...


# }}}
class Tester:
    PROGRESS_EMIT_PERIOD = ONE_SECOND
    progress = Signal(int)

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

        self.__test.clear()
        self.__test.status = Test.Status.PROCESS
        self.__setVirtualBroker()
        await self.__loadAssetList()
        await self.__loadStrategyList()
        self.__createTimeFrameList()

        for asset in self.__alist:
            self.__setCurrentAsset(asset)
            await self.__loadMarketData()
            self.__createCharts()
            await self.__startTest()
            await self.__finishTest()

        self.__test.status = Test.Status.COMPLETE
        self.__createReport()
        self.__saveTest()
        logger.info(f"'{self.test}' complete!")
        self.__clearAll()

    # }}}

    def __clearAll(self):  # {{{
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
    def __setTime(self):  # {{{
        begin = datetime.combine(self.__test.begin, DAY_BEGIN, UTC)
        end = datetime.combine(self.__test.end, DAY_BEGIN, UTC)
        total_timedelta = self.__test.end - self.__test.begin

        self.__time = begin
        self.__begin = begin
        self.__end = end
        self.__total_time = total_timedelta.total_seconds()
        self.__last_emit = now()
        self.progress.emit(0)

    # }}}
    def __setVirtualBroker(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setVirtualBroker()")

        self.__broker = _VirtualBroker
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
    def __setCurrentAsset(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__setCurrentAsset()")

        self.__current_asset = asset

    # }}}
    async def __loadMarketData(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadMarketData()")

        self.__bars = dict()
        for timeframe in self.__tflist:
            bars = await Keeper.get(
                Bar,
                instrument=self.__current_asset,
                timeframe=timeframe,
                begin=self.__test.begin,
                end=self.__test.end,
            )

            self.__bars[timeframe] = bars

    # }}}
    def __createCharts(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createCharts()")

        for timeframe in self.__tflist:
            bar = self.__bars[timeframe].pop(0)
            chart = Chart(self.__current_asset, timeframe, [])
            chart.now = bar
            self.__current_asset.setChart(chart)

        # }}}

    async def __startTest(self):  # {{{
        logger.info(f":: Start testing {self.__current_asset.ticker}")

        # initialize strategy
        for i in self.__slist:
            await i.start()

        # run time
        self.__setTime()
        while self.__time < self.__end:
            ...
            await self.__timeStep()
            # self.__emitProgress()

    # }}}

    async def __timeStep(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__timeStep()")

        self.__time += self.__test.time_step
        for timeframe in self.__tflist:
            chart = self.__current_asset.chart(timeframe)
            now_bar = chart.now

            if self.__time < now_bar.dt + timeframe:
                continue

            last_historical_bar = now_bar
            new_bar = self.__bars[timeframe].pop(0)

            await chart.addHistoricalBar(last_historical_bar)
            await chart.updateNowBar(new_bar)

            print(self.__time, chart.timeframe, chart.now.dt)
            input(3)

    # }}}
    def __emitProgress(self):  # {{{
        passed_time = now() - self.last_emit
        if passed_time > self.PROGRESS_EMIT_PERIOD:
            complete = (self.__time - self.test.begin).total_seconds()
            progress = int(complete / self.__total_time * 100)
            self.progress.emit(progress)
            self.last_emit = now()

    # }}}

    #     def __finishTest(self):  # {{{
    #         logger.info(f"Finish test {self.current_asset.ticker}")
    #         self.strategy.finish()
    #         self.portfolio.positions.clear()
    #         self.current_asset.closeAllChart()
    #         self.signals.clear()
    #
    #     # }}}
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
