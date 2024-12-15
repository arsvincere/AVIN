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
from gui.custom import Theme


class GTrade(QtWidgets.QGraphicsItemGroup):  # {{{
    OPEN_WIDTH = 1
    STOP_WIDTH = 1
    TAKE_WIDTH = 1

    __open_pen = QtGui.QPen()
    __open_pen.setWidth(OPEN_WIDTH)
    __open_pen.setColor(Theme.Chart.OPEN)
    __stop_pen = QtGui.QPen()
    __stop_pen.setWidth(STOP_WIDTH)
    __stop_pen.setColor(Theme.Chart.STOP)
    __take_pen = QtGui.QPen()
    __take_pen.setWidth(TAKE_WIDTH)
    __take_pen.setColor(Theme.Chart.TAKE)

    def __init__(self, trade: Trade, gchart: GChart, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.trade = trade
        self.gchart = gchart

        self.__calcCoordinates()
        self.__createTradeShape()
        self.__createOpenItem()
        self.__createStopLossItem()
        self.__createTakeProfitItem()

    # }}}

    def showAnnotation(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.showAnnotation()")

        self.__createAnnotation()
        self.annotation.show()

    # }}}
    def hideAnnotation(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.hideAnnotation()")

        self.annotation.hide()

    # }}}

    def __calcCoordinates(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__calcCoordinates()")

        gchart = self.gchart
        trade = self.trade
        self.x_opn = gchart.xFromDatetime(trade.openDateTime())
        self.x_cls = gchart.xFromDatetime(trade.closeDateTime())
        gbar = gchart.barFromDatetime(trade.openDateTime())
        y_hgh = gbar.high_pos.y()
        self.y0 = y_hgh - 50
        self.trade_pos = QtCore.QPointF(self.x_opn, self.y0)

    # }}}
    def __createTradeShape(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createTradeShape()")

        x0 = self.x_opn
        x1 = x0 + GBar.WIDTH
        x_center = (x0 + x1) / 2
        y0 = self.y0
        y1 = y0 - GBar.WIDTH

        if self.trade.isLong():
            p1 = QtCore.QPointF(x0, y0)
            p2 = QtCore.QPointF(x1, y0)
            p3 = QtCore.QPointF(x_center, y1)
            triangle = QtGui.QPolygonF([p1, p2, p3])
        else:
            p1 = QtCore.QPointF(x0, y1)
            p2 = QtCore.QPointF(x1, y1)
            p3 = QtCore.QPointF(x_center, y0)
            triangle = QtGui.QPolygonF([p1, p2, p3])
        triangle = QtWidgets.QGraphicsPolygonItem(triangle)

        if self.trade.isWin():
            triangle.setPen(Theme.Chart.TRADE_WIN)
            triangle.setBrush(Theme.Chart.TRADE_WIN)
        else:
            triangle.setPen(Theme.Chart.TRADE_LOSS)
            triangle.setBrush(Theme.Chart.TRADE_LOSS)

        self.addToGroup(triangle)

    # }}}
    def __createOpenItem(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createOpenItem()")

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

        self.y_stop = self.__gchart.yFromPrice(stop_loss_price)
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

        self.y_take = self.__gchart.yFromPrice(take_profit_price)
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

        local_time = Usr.localTime(self.trade.dt)
        text = (
            "<div style='background-color:#333333;'>"
            f"{local_time}<br>"
            f"Result: {self.trade.result()}<br>"
            f"Days: {self.trade.holdingDays()}<br>"
            f"PPD: {self.trade.percentPerDay()}% "
            "</div>"
        )
        self.annotation = QtWidgets.QGraphicsTextItem()
        self.annotation.setHtml(text)
        self.annotation.setPos(self.x_opn, self.y0 - 100)
        self.annotation.hide()
        self.addToGroup(self.annotation)

    # }}}


# }}}
class GTradeList(QtWidgets.QGraphicsItemGroup):  # {{{
    def __init__(self, test: Test, trade_list, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.test = test
        self.trade_list = trade_list

        self.__createGChart()
        self.__createGTrades()

    # }}}

    @classmethod  # fromTest  # {{{
    def fromTest(cls, test: Test) -> GTradeList:
        logger.debug(f"{cls.__name__}.fromTest()")

        gtrade_list = cls(test, test.trade_list)
        return gtrade_list

    # }}}
    @classmethod  # fromSelected  # {{{
    def fromSelected(
        cls, test: Test, selected_trades: TradeList
    ) -> GTradeList:
        logger.debug(f"{cls.__name__}.fromSelected()")

        gtrade_list = cls(test, selected_trades)
        return gtrade_list

    # }}}

    def __createGChart(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createGChart()")

        begin = datetime.combine(self.test.begin, time(0, 0, tzinfo=UTC))
        end = datetime.combine(self.test.end, time(0, 0, tzinfo=UTC))

        chart = Thread.loadChart(
            self.test.asset,
            TimeFrame("D"),
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
