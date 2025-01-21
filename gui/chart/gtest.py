#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from datetime import UTC, datetime, time

from PyQt6 import QtCore, QtGui, QtWidgets

from avin.config import Usr
from avin.core import TimeFrame, Trade, TradeList
from avin.tester import Test
from avin.utils import logger
from gui.chart.gchart import GBar, GChart
from gui.chart.thread import Thread
from gui.custom import Css, Theme
from gui.marker import GShape


class GTrade(QtWidgets.QGraphicsItemGroup):  # {{{
    __open_pen = QtGui.QPen(Theme.Chart.OPEN)
    __stop_pen = QtGui.QPen(Theme.Chart.STOP)
    __take_pen = QtGui.QPen(Theme.Chart.TAKE)

    def __init__(self, trade: Trade, gchart: GChart, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.trade = trade
        self.gchart = gchart
        self.annotation = None

        self.__calcCoordinates()
        self.__createTradeGShape()
        self.__createOpenItem()
        self.__createStopLossItem()
        self.__createTakeProfitItem()

    # }}}

    def showAnnotation(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.showAnnotation()")

        if self.annotation is None:
            self.__createAnnotation()

        self.annotation.show()

    # }}}
    def hideAnnotation(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.hideAnnotation()")

        if self.annotation is not None:
            self.annotation.hide()

    # }}}

    def __calcCoordinates(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__calcCoordinates()")

        gchart = self.gchart
        trade = self.trade

        match trade.status:
            case Trade.Status.CLOSED:
                self.x_init = gchart.xFromDatetime(trade.dt)
                self.x_opn = gchart.xFromDatetime(trade.openDateTime())
                self.x_cls = gchart.xFromDatetime(trade.closeDateTime())
                gbar = gchart.barFromDatetime(trade.openDateTime())
                y_hgh = gbar.high_pos.y()
                self.y0 = y_hgh - 50
                self.trade_pos = QtCore.QPointF(self.x_opn, self.y0)
            case _:
                self.x_init = gchart.xFromDatetime(trade.dt)
                self.x_opn = self.x_init
                self.x_cls = self.x_init
                gbar = gchart.barFromDatetime(trade.dt)
                y_hgh = gbar.high_pos.y()
                self.y0 = y_hgh - 50
                self.trade_pos = QtCore.QPointF(self.x_opn, self.y0)

    # }}}
    def __createTradeGShape(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createTradeGShape()")

        # choose form
        if self.trade.isLong():
            typ = GShape.Type.TRIANGLE_UP
        else:
            typ = GShape.Type.TRIANGLE_DOWN

        # choose color
        if self.trade.status != Trade.Status.CLOSED:
            color = GShape.Color.WHITE
        elif self.trade.isWin():
            color = GShape.Color.GREEN
        else:
            color = GShape.Color.RED

        # create shape
        shape = GShape(typ, GShape.Size.NORMAL, color)

        # set position
        shape.setPos(self.x_opn, self.y0)

        self.addToGroup(shape)

    # }}}
    def __createOpenItem(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createOpenItem()")

        if self.trade.status != Trade.Status.CLOSED:
            return

        open_price = self.trade.openPrice()
        self.y_opn = self.gchart.yFromPrice(open_price)

        open_item = QtWidgets.QGraphicsLineItem(
            self.x_opn, self.y_opn, self.x_cls + GBar.WIDTH, self.y_opn
        )
        open_item.setPen(self.__open_pen)

        self.addToGroup(open_item)

    # }}}
    def __createStopLossItem(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createStopLossItem()")

        stop_loss_price = self.trade.stopPrice()
        if stop_loss_price is None:
            return

        self.y_stop = self.gchart.yFromPrice(stop_loss_price)
        stop_loss = QtWidgets.QGraphicsLineItem(
            self.x_opn,
            self.y_stop,
            self.x_cls + GBar.WIDTH,
            self.y_stop,
        )
        stop_loss.setPen(self.__stop_pen)
        self.addToGroup(stop_loss)

    # }}}
    def __createTakeProfitItem(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createTakeProfitItem()")

        take_profit_price = self.trade.takePrice()
        if take_profit_price is None:
            return

        self.y_take = self.gchart.yFromPrice(take_profit_price)
        take_profit = QtWidgets.QGraphicsLineItem(
            self.x_opn,
            self.y_take,
            self.x_cls + GBar.WIDTH,
            self.y_take,
        )
        take_profit.setPen(self.__take_pen)
        self.addToGroup(take_profit)

    # }}}
    def __createAnnotation(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createAnnotation()")

        self.annotation = GTradeAnnotation(self)
        self.addToGroup(self.annotation)

    # }}}


# }}}
class GTradeAnnotation(QtWidgets.QGraphicsProxyWidget):  # {{{
    def __init__(self, gtrade: GTrade, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsProxyWidget.__init__(self, parent)

        local_time = Usr.localTime(gtrade.trade.dt)
        status = gtrade.trade.status.name
        match gtrade.trade.status:
            case Trade.Status.CLOSED:
                days = gtrade.trade.holdingDays()
                result = gtrade.trade.result()
                p = gtrade.trade.percent()
                ppd = gtrade.trade.percentPerDay()
                text = f"""
                    <table>
                      <tbody>
                        <tr>
                          <td><b>{local_time}  </b></td>
                          <th>{status}</th>
                        </tr>
                        <tr>
                          <td>Days:</td>
                          <td>{days}</td>
                        </tr>
                        <tr>
                        <td>Result:</td>
                          <td>{result}</td>
                        </tr>
                        <tr>
                          <td>P/PPD:</td>
                          <td>{p} / {ppd}%</td>
                        </tr>
                      </tbody>
                    </table>
                    """
                y0 = gtrade.y0 - 100
            case _:
                text = f"""
                    <table>
                      <tbody>
                        <tr>
                          <td><b>{local_time}  </b></td>
                          <th>{status}</th>
                        </tr>
                      </tbody>
                    </table>
                    """
                y0 = gtrade.y0 - 50

        label = QtWidgets.QLabel(text)
        label.setStyleSheet(Css.TRADE_LABEL)

        self.setWidget(label)
        self.setPos(gtrade.x_opn, y0)

    # }}}


# }}}
class GTradeList(QtWidgets.QGraphicsItemGroup):  # {{{
    def __init__(  # {{{
        self,
        test: Test,
        trade_list: TradeList,
        timeframe: TimeFrame,
        parent=None,
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.test = test
        self.trade_list = trade_list
        self.timeframe = timeframe

        self.__createGChart()
        self.__createGTrades()

    # }}}

    @classmethod  # fromSelected  # {{{
    def fromSelected(
        cls,
        test: Test,
        selected_trades: TradeList,
        timeframe: TimeFrame,
    ) -> GTradeList:
        logger.debug(f"{cls.__name__}.fromSelected()")

        gtrade_list = cls(test, selected_trades, timeframe)
        return gtrade_list

    # }}}

    def __createGChart(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createGChart()")

        begin = datetime.combine(self.test.begin, time(0, 0, tzinfo=UTC))
        end = datetime.combine(self.test.end, time(0, 0, tzinfo=UTC))

        chart = Thread.loadChart(
            self.test.asset,
            self.timeframe,
            begin,
            end,
        )

        self.gchart = GChart(chart)

    # }}}
    def __createGTrades(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createGTrades()")

        self.gtrades = QtWidgets.QGraphicsItemGroup()
        for trade in self.trade_list:
            gtrade = GTrade(trade, self.gchart)
            self.gtrades.addToGroup(gtrade)

    # }}}


# }}}


if __name__ == "__main__":
    ...
