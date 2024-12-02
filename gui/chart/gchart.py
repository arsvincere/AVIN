#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from datetime import datetime

from PyQt6 import QtCore, QtGui, QtWidgets

from avin.core import (
    Asset,
    Bar,
    Chart,
    TimeFrame,
)
from avin.utils import find_left
from gui.custom import Color


class GBar(Bar, QtWidgets.QGraphicsItemGroup):  # {{{
    # DRAW_BODY =         False
    DRAW_BODY = True
    WIDTH = 16
    # INDENT =            1
    INDENT = 4
    SHADOW_WIDTH = 1

    def __init__(self, dt, o, h, l, c, v, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)
        Bar.__init__(self, dt, o, h, l, c, v, parent)
        self.n = None

    # }}}
    def __calcCoordinates(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__calcCoordinates()")
        gchart = self.parent()
        self.x = gchart.xFromNumber(self.n)
        self.x0 = self.x + self.INDENT
        self.x1 = self.x + self.WIDTH - self.INDENT
        self.x_center = int((self.x0 + self.x1) / 2)
        self.y_opn = gchart.yFromPrice(self.open)
        self.y_cls = gchart.yFromPrice(self.close)
        self.y_hgh = gchart.yFromPrice(self.high)
        self.y_low = gchart.yFromPrice(self.low)
        self.open_pos = QtCore.QPointF(self.x_center, self.y_opn)
        self.close_pos = QtCore.QPointF(self.x_center, self.y_cls)
        self.high_pos = QtCore.QPointF(self.x_center, self.y_hgh)
        self.low_pos = QtCore.QPointF(self.x_center, self.y_low)

    # }}}
    def __setColor(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setColor()")
        if self.isBull():
            self.color = Color.BULL
        elif self.isBear():
            self.color = Color.BEAR
        else:
            self.color = Color.UNDEFINE

    # }}}
    def __createOpenLine(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createOpenLine()")
        opn = QtWidgets.QGraphicsLineItem(
            self.x0, self.y_opn, self.x_center, self.y_opn
        )
        pen = QtGui.QPen()
        pen.setColor(self.color)
        pen.setWidth(GBar.SHADOW_WIDTH)
        opn.setPen(pen)
        self.addToGroup(opn)

    # }}}
    def __createCloseLine(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createCloseLine()")
        cls = QtWidgets.QGraphicsLineItem(
            self.x_center, self.y_cls, self.x1, self.y_cls
        )
        pen = QtGui.QPen()
        pen.setColor(self.color)
        pen.setWidth(GBar.SHADOW_WIDTH)
        cls.setPen(pen)
        self.addToGroup(cls)

    # }}}
    def __createShadowLine(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createShadowLine()")
        shadow = QtWidgets.QGraphicsLineItem(
            self.x_center, self.y_low, self.x_center, self.y_hgh
        )
        pen = QtGui.QPen()
        pen.setColor(self.color)
        pen.setWidth(GBar.SHADOW_WIDTH)
        shadow.setPen(pen)
        self.addToGroup(shadow)

    # }}}
    def __createBody(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createBody()")
        width = self.x1 - self.x0
        height = abs(self.y_opn - self.y_cls)
        y0 = self.y_cls if self.isBull() else self.y_opn
        x0 = self.x_center - width / 2
        body = QtWidgets.QGraphicsRectItem(x0, y0, width, height)
        body.setPen(self.color)
        body.setBrush(self.color)
        self.addToGroup(body)

    # }}}
    @staticmethod  # fromCSV{{{
    def fromCSV(bar_str, parent):
        code = f"GBar({bar_str}, parent)"
        bar = eval(code)
        return bar

    # }}}
    def createGraphicsItem(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.createGraphicsItem()")
        self.__calcCoordinates()
        self.__setColor()
        self.__createShadowLine()
        if self.DRAW_BODY:
            self.__createBody()
        else:
            self.__createOpenLine()
            self.__createCloseLine()


# }}}


# }}}
class GChart(Chart, QtWidgets.QGraphicsItemGroup):  # {{{
    def __init__(  # {{{
        self,
        asset: Asset,
        timeframe: TimeFrame,
        begin: datetime,
        end: datetime,
        constructor=GBar.fromCSV,
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self)
        Chart.__init__(self, asset, timeframe, begin, end, constructor)
        # self.__createIndicatorGroup()
        self.__numerateBars()
        self.__createSceneRect()
        self.__createGBars()

    # }}}
    def __numerateBars(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__numerateBars()")
        for n, bar in enumerate(self._bars, 0):
            bar.n = n

    # }}}
    def __createSceneRect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createSceneRect()")
        self.SCALE_Y = 10
        self.step = self.asset.min_price_step
        x0 = 0
        y0 = 0
        x1 = len(self._bars) * GBar.WIDTH
        y1 = int(self.highestHigh() / self.step / self.SCALE_Y)
        self.x_indent = (x1 - x0) * 0.05
        self.y_indent = (y1 - y0) * 0.05
        height = y1 - y0 + self.y_indent
        width = x1 - x0 + self.x_indent
        self.rect = QtCore.QRectF(0, 0, width, height)

    # }}}
    def __createGBars(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createGBars()")
        for bar in self._bars:
            # TODO чарт имеет список self._gbars
            # GBar содержит ссылку на бар и номер
            # GBar это график итем гроуп
            # созданные итемы помещаются в self._gbars
            # self.getGrapthics - возвращает группу всей графики
            # тогда даже наследовать график итем гроуп не надо.
            bar.createGraphicsItem()

    # }}}
    def barFromDatetime(self, dt):  # {{{
        index = find_left(self._bars, dt, key=lambda x: x.dt)
        assert index is not None
        gbar = self._bars[index]
        return gbar

    # }}}
    def xFromNumber(self, n):  # {{{
        return int(n * GBar.WIDTH)

    # }}}
    def xFromDatetime(self, dt):  # {{{
        gbar = self.barFromDatetime(dt)
        return gbar.x

    # }}}
    def yFromPrice(self, price):  # {{{
        y = int(
            self.rect.height()
            - price / self.step / self.SCALE_Y
            + self.y_indent
        )
        return y

    # }}}
    def nFromX(self, x):  # {{{
        n = int(x / GBar.WIDTH)
        return n

    # }}}
    def barAt(self, x):  # {{{
        if x < 0:
            return None
        n = self.nFromX(x)
        if n < len(self._bars):
            return self._bars[n]
        else:
            return None


# }}}


# }}}


if __name__ == "__main__":
    ...
