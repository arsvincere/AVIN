#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtCore, QtGui, QtWidgets

from avin.config import Usr
from avin.core import (
    TimeFrame,
    TradeList,
)
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

    def __init__(self, itrade, parent):  # {{{
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        itrade.gtrade = self  # link to GTrade in ITrade item
        self.itrade = itrade  #  link to ITrade in GTrade item
        self.__parent = parent
        self.__gchart = parent.gchart
        self.__calcCoordinates()
        self.__crateTradeShape()
        self.__createOpenItem()
        self.__createStopLossItem()
        self.__createTakeProfitItem()

    # }}}
    def __calcCoordinates(self):  # {{{
        gchart = self.__gchart
        self.x_opn = gchart.xFromDatetime(self.open_dt)
        self.x_cls = gchart.xFromDatetime(self.close_dt)
        gbar = gchart.barFromDatetime(self.open_dt)
        y_hgh = gbar.high_pos.y()
        self.y0 = y_hgh - 50
        self.trade_pos = QtCore.QPointF(self.x_opn, self.y0)

    # }}}
    def __crateTradeShape(self):  # {{{
        x0 = self.x_opn
        x1 = x0 + GBar.WIDTH
        x_center = (x0 + x1) / 2
        y0 = self.y0
        y1 = y0 - GBar.WIDTH
        if self.isLong():
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
        if self.isWin():
            triangle.setPen(Theme.Chart.TRADE_WIN)
            triangle.setBrush(Theme.Chart.TRADE_WIN)
        else:
            triangle.setPen(Theme.Chart.TRADE_LOSS)
            triangle.setBrush(Theme.Chart.TRADE_LOSS)
        self.addToGroup(triangle)

    # }}}
    def __createOpenItem(self):  # {{{
        open_price = self.strategy["open_price"]
        self.y_opn = self.__gchart.yFromPrice(open_price)
        open_item = QtWidgets.QGraphicsLineItem(
            self.x_opn, self.y_opn, self.x_cls + GBar.WIDTH, self.y_opn
        )
        open_item.setPen(self.__open_pen)
        self.addToGroup(open_item)

    # }}}
    def __createStopLossItem(self):  # {{{
        stop_loss_price = self.strategy["stop_price"]
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
        take_profit_price = self.strategy["take_price"]
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
        msk_dt = self.dt + Usr.TIME_DIF
        str_dt = msk_dt.strftime("%Y-%m-%d  %H:%M")
        text = (
            "<div style='background-color:#333333;'>"
            f"{str_dt}<br>"
            f"Result: {self.result}<br>"
            f"Days: {self.holding}<br>"
            f"Profitability: {self.percent_per_day}% "
            "</div>"
        )
        self.annotation = QtWidgets.QGraphicsTextItem()
        self.annotation.setHtml(text)
        self.annotation.setPos(self.x_opn, self.y0 - 200)
        self.annotation.hide()
        self.addToGroup(self.annotation)

    # }}}
    def parent(self):  # {{{
        return self.__parent

    # }}}
    def showAnnotation(self):  # {{{
        self.__createAnnotation()
        self.annotation.show()

    # }}}
    def hideAnnotation(self):  # {{{
        self.annotation.hide()


# }}}


# }}}
class GTest(TradeList, QtWidgets.QGraphicsItemGroup):  # {{{
    def __init__(self, itlist, parent=None):  # {{{
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)
        TradeList.__init__(self, itlist.name, parent=itlist)
        self.__createGChart()
        self.__createGTrades()

    # }}}
    def __createGChart(self):  # {{{
        if self.asset is None:
            self.gchart = None
            return
        self.gchart = GChart(
            self.asset,
            TimeFrame("D"),
            self.begin,
            self.end,
        )

    # }}}
    def __createGTrades(self):  # {{{
        if self.gchart is None:
            return
        for t in self.parent():
            gtrade = GTrade(t, parent=self)
            self.add(gtrade)  # Trade.add
            self.addToGroup(gtrade)  # QGraphicsItemGroup.addToGroup

    # }}}
    @property  # begin{{{
    def begin(self):
        return self.test.begin

    # }}}
    @property  # end{{{
    def end(self):
        return self.test.end


# }}}


# }}}


if __name__ == "__main__":
    ...
