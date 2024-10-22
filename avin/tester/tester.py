#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from avin.const import ONE_SECOND
from avin.utils import Signal


class Tester:
    """const"""  # {{{

    PROGRESS_EMIT_PERIOD = ONE_SECOND
    # }}}
    """ signal """  # {{{
    progress = Signal(int)

    # }}}
    def __init__(self):  # {{{
        self.test = None
        self.portfolio = None
        self.strategy = None
        self.time = None
        self.analytic = None
        self.risk = None
        self.ruler = None
        self.signals = list()

    # }}}


#     def __openPosition(self, signal: Signal):  # {{{
#         if signal.type == Signal.Type.LONG:
#             direction = Operation.Direction.BUY
#         else:
#             direction = Operation.Direction.SELL
#         open_price = signal.asset.chart("1M").now.open
#         quantity = signal.info["risk"]["max lots"] * signal.asset.lot
#         amount = open_price * quantity
#         commission = amount * self.test.commission
#         op = Operation(
#             signal=signal,
#             dt=signal.asset.chart("1M").now.dt,
#             direction=direction,
#             asset=signal.asset,
#             lots=signal.info["risk"]["max lots"],
#             price=open_price,
#             quantity=quantity,
#             amount=amount,
#             commission=commission,
#         )
#         pos = Position(signal, op)
#         signal.status = Signal.Status.OPEN
#         return pos
#
#     # }}}
#     def __closePosition(self, pos: Position, close_price: float):  # {{{
#         if pos.signal.type == Signal.Type.LONG:
#             direction = Operation.Direction.SELL
#         else:
#             direction = Operation.Direction.BUY
#         quantity = abs(pos.quantity())
#         amount = close_price * quantity
#         commission = amount * self.test.commission
#         op = Operation(
#             signal=pos.signal,
#             dt=pos.asset.chart("1M").now.dt,
#             direction=direction,
#             asset=pos.asset,
#             lots=abs(pos.lots()),
#             price=close_price,
#             quantity=quantity,
#             amount=amount,
#             commission=commission,
#         )
#         pos.add(op)
#         assert pos.status == Position.Status.CLOSE
#         return pos
#
#     # }}}
#     def __checkCloseCondition(self, pos, bar: Bar):  # {{{
#         """TODO : тут все надо перелопатить нормально создавать
#         ордер операцию и вот это вот все"""
#         info = pos.signal.info["strategy"]
#         if info["close_condition"] == Signal.Close.ON_CLOSE:
#             if bar.dt.time() == time(15, 45):
#                 close_price = bar.close
#                 self.__closePosition(pos, close_price)
#
#     # }}}
#     def __checkStopLoss(self, pos: Position, bar: Bar):  # {{{
#         info = pos.signal.info["strategy"]
#         signal = pos.signal
#         if info["close_condition"] != Signal.Close.STOP_TAKE:
#             return
#         stop_price = info["stop_price"]
#         if stop_price in bar:
#             close_price = stop_price
#             self.__closePosition(pos, close_price)
#         # проверим возможно гепом перелетели через стоп
#         elif (
#             signal.isShort()
#             and bar.open >= stop_price
#             or signal.isLong()
#             and bar.open <= stop_price
#         ):
#             close_price = bar.open
#             self.__closePosition(pos, close_price)
#
#     # }}}
#     def __checkTakeProfit(self, pos, bar):  # {{{
#         info = pos.signal.info["strategy"]
#         signal = pos.signal
#         if info["close_condition"] != Signal.Close.STOP_TAKE:
#             return
#         take_price = info["take_price"]
#         if take_price in bar:
#             close_price = take_price
#             self.__closePosition(pos, close_price)
#         # проверим возможно гепом перелетели через стоп
#         elif (
#             signal.isShort()
#             and bar.open <= take_price
#             or signal.isLong()
#             and bar.open >= take_price
#         ):
#             close_price = bar.open
#             self.__closePosition(pos, close_price)
#
#     # }}}
#     def __nextTime(self):  # {{{
#         self.time += self.test.timeframe
#         for timeframe in self.strategy.timeframe_list:
#             chart = self.current_asset.chart(timeframe)
#             while self.time >= chart.now.dt:
#                 result = chart._nextHead()
#                 if result is None:
#                     break
#
#     # }}}
#     def __emitProgress(self):  # {{{
#         passed_time = now() - self.last_emit
#         if passed_time > self.PROGRESS_EMIT_PERIOD:
#             complete = (self.time - self.test.begin).total_seconds()
#             progress = int(complete / self.total_time * 100)
#             self.progress.emit(progress)
#             self.last_emit = now()
#
#     # }}}
#     def __loadStrategy(self):  # {{{
#         logger.info(f"Tester load strategy {self.test.strategy}")
#         name = self.test.strategy
#         ver = self.test.version
#         self.strategy = Strategy.load(name, ver, general=self)
#         self.strategy.long_list = self.test.alist
#         self.strategy.short_list = self.test.alist
#         self.strategy.signal.connect(self.__receiveSignal)
#
#     # }}}
#     def __loadPortfolio(self):  # {{{
#         logger.info("Tester load portfolio")
#         self.portfolio = Portfolio(
#             cash=list(),
#             shares=list(),
#             bounds=list(),
#             futures=list(),
#             options=list(),
#         )
#         self.portfolio.virtualSetMoney(self.test.deposit)
#
#     # }}}
#     def __loadTeam(self):  # {{{
#         logger.info("Tester load team")
#         self.analytic = Analytic(general=self)
#         self.market = Market(general=self)
#         self.risk = Risk(general=self)
#         self.ruler = Ruler(general=self)
#         self.ruler.setPortfolio(self.portfolio)
#         self.adviser = Adviser(general=self)
#
#     # }}}
#     def __loadChart(self):  # {{{
#         for timeframe in self.strategy.timeframe_list:
#             logger.info(
#                 f"Tester load chart {self.current_asset.ticker}-{timeframe}"
#             )
#             self.current_asset.loadChart(
#                 timeframe,
#                 self.test.begin,
#                 self.test.end,
#             )
#             self.current_asset.chart(timeframe)._setHeadIndex(0)
#
#     # }}}
#     def __setCurrentAsset(self, asset):  # {{{
#         self.current_asset = asset
#
#     # }}}
#     def __setTime(self):  # {{{
#         self.time = self.test.begin
#         self.total_time = (self.test.end - self.test.begin).total_seconds()
#         self.progress.emit(0)
#         self.last_emit = now()
#
#     # }}}
#     def __startTest(self):  # {{{
#         logger.info(f"Start test {self.current_asset.ticker}")
#         self.strategy.start()
#         self.__setTime()
#         while self.time <= self.test.end:
#             self.__processStrategy()
#             self.__processSignals()
#             self.__processOpenPositions()
#             self.__removeClosedPositions()
#             self.__emitProgress()
#             self.__nextTime()
#
#     # }}}
#     def __processStrategy(self):  # {{{
#         self.strategy.process(self.current_asset)
#
#     # }}}
#     def __processSignals(self):  # {{{
#         while len(self.signals) > 0:
#             signal = self.signals[0]
#             self.analytic.process(signal)
#             self.market.process(signal)
#             self.risk.process(signal)
#             self.ruler.process(signal)
#             self.adviser.process(signal)
#             pos = self.__openPosition(signal)
#             if pos is not None:
#                 self.portfolio.add(pos)
#             self.signals.pop(0)
#
#     # }}}
#     def __processOpenPositions(self):  # {{{
#         for pos in self.portfolio.positions:
#             bar = pos.signal.asset.chart("1M").now
#             self.__checkStopLoss(pos, bar)
#             self.__checkTakeProfit(pos, bar)
#             self.__checkCloseCondition(pos, bar)
#             if pos.status == Position.Status.CLOSE:
#                 pos.signal.status = Signal.Status.CLOSE
#                 trade = Signal.toTrade(pos.signal)
#                 self.test.tlist.add(trade)
#
#     # }}}
#     def __removeClosedPositions(self):  # {{{
#         i = 0
#         while i < len(self.portfolio.positions):
#             pos = self.portfolio.positions[i]
#             if pos.status == Position.Status.CLOSE:
#                 self.portfolio.positions.pop(i)
#             else:
#                 i += 1
#
#     # }}}
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
#     def __clearAll(self):  # {{{
#         self.test = None
#         self.strategy = None
#         self.portfolio = None
#         self.analytic = None
#         self.market = None
#         self.risk = None
#         self.ruler = None
#         self.current_asset = None
#         self.signals.clear()
#
#     # }}}
#     def __receiveSignal(self, signal: Signal):  # {{{
#         logger.debug("Tester.__receiveSignal()")
#         logger.info(str(signal))
#         signal.status = Signal.Status.NEW
#         self.signals.append(signal)
#
#     # }}}
#     def setTest(self, test):  # {{{
#         self.__clearAll()
#         self.test = test
#         self.test.status = Test.Status.PROCESS
#
#     # }}}
#     def runTest(self):  # {{{
#         logger.info("Test run")
#         self.test.clear()
#         self.__loadStrategy()
#         self.__loadPortfolio()
#         self.__loadTeam()
#         for asset in self.test.alist:
#             self.__setCurrentAsset(asset)
#             self.__loadChart()
#             self.__startTest()
#             self.__finishTest()
#         self.test.status = Test.Status.COMPLETE
#         self.__createReport()
#         self.__saveTest()
#         logger.info(f"Test '{self.test.name}' complete!")
#         self.__clearAll()
#
#     # }}}
#
#
#

if __name__ == "__main__":
    ...
