#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from PyQt6 import QtCore, QtGui, QtWidgets

from avin.core import (
    Bar,
    Chart,
)
from avin.utils import find_left, logger
from gui.custom import Theme


class GBar(QtWidgets.QGraphicsItemGroup):  # {{{
    DRAW_BODY = True
    WIDTH = 8
    HEIGHT = 10  # 10px на 1% цены
    INDENT = 2
    SHADOW_WIDTH = 1

    def __init__(self, bar: Bar, n: int, gchart: GChart):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, gchart)

        self.bar = bar
        self.n = n
        self.gchart = gchart

        self.__createGraphicsItem()

    # }}}
    def __createGraphicsItem(self):  # {{{
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
    def __calcCoordinates(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__calcCoordinates()")

        gchart = self.gchart
        self.x = gchart.xFromNumber(self.n)
        self.x0 = self.x + self.INDENT
        self.x1 = self.x + self.WIDTH - self.INDENT
        self.x_center = int((self.x0 + self.x1) / 2)

        self.y_opn = gchart.yFromPrice(self.bar.open)
        self.y_cls = gchart.yFromPrice(self.bar.close)
        self.y_hgh = gchart.yFromPrice(self.bar.high)
        self.y_low = gchart.yFromPrice(self.bar.low)

        self.open_pos = QtCore.QPointF(self.x_center, self.y_opn)
        self.close_pos = QtCore.QPointF(self.x_center, self.y_cls)
        self.high_pos = QtCore.QPointF(self.x_center, self.y_hgh)
        self.low_pos = QtCore.QPointF(self.x_center, self.y_low)

    # }}}
    def __setColor(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setColor()")
        if self.bar.isBull():
            self.color = Theme.Chart.BULL
        elif self.bar.isBear():
            self.color = Theme.Chart.BEAR
        else:
            self.color = Theme.Chart.UNDEFINE

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
    def __createBody(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createBody()")
        width = self.x1 - self.x0
        height = abs(self.y_opn - self.y_cls)
        y0 = self.y_cls if self.bar.isBull() else self.y_opn
        x0 = self.x_center - width / 2
        body = QtWidgets.QGraphicsRectItem(x0, y0, width, height)
        body.setPen(self.color)
        body.setBrush(self.color)
        self.addToGroup(body)

    # }}}


# }}}
class GChart(QtWidgets.QGraphicsItemGroup):  # {{{
    def __init__(self, chart: Chart, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.chart = chart
        self.gbars = list()

        self.__createSceneRect()
        self.__createGBars()

    # }}}

    def barFromDatetime(self, dt):  # {{{
        logger.debug(f"{self.__class__.__name__}.barFromDatetime()")

        index = find_left(self._bars, dt, key=lambda x: x.dt)
        assert index is not None
        gbar = self._bars[index]
        return gbar

    # }}}
    def xFromNumber(self, n):  # {{{
        logger.debug(f"{self.__class__.__name__}.xFromNumber()")

        return int(n * GBar.WIDTH)

    # }}}
    def xFromDatetime(self, dt):  # {{{
        logger.debug(f"{self.__class__.__name__}.xFromDatetime()")

        gbar = self.barFromDatetime(dt)
        return gbar.x

    # }}}
    def yFromPrice(self, price):  # {{{
        logger.debug(f"{self.__class__.__name__}.yFromPrice()")

        y = self.rect.height() - price * self.SCALE_Y + self.y_indent
        return y

    # }}}
    def nFromX(self, x):  # {{{
        logger.debug(f"{self.__class__.__name__}.nFromX()")

        n = int(x / GBar.WIDTH)
        return n

    # }}}
    def barAt(self, x):  # {{{
        logger.debug(f"{self.__class__.__name__}.barAt()")

        if x < 0:
            return None

        n = self.nFromX(x)
        if n < len(self.gbars):
            return self.gbars[n]
        else:
            return None

    # }}}

    def __createSceneRect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createSceneRect()")

        # Масштаб по оси Y расчитывается так чтобы изменение цены
        # на 1% занимало GBar.HEIGHT = 10px
        # Не зависимо от того сколько стоит актив 20р штука или 5000р штука
        # бар у которого тело 20.0-20.2 будет занимать 10px на экране
        # и бар с телом 5000-5050 тоже будет занимать 10px на экране
        last_price = self.chart.last.close  # 1000
        self.SCALE_Y = GBar.HEIGHT / last_price * 100

        x0 = 0
        y0 = 0
        x1 = len(self.chart) * GBar.WIDTH
        y1 = int(self.chart.highestHigh() * self.SCALE_Y)

        self.x_indent = (x1 - x0) * 0.2  # доп.отступ 20%
        self.y_indent = (y1 - y0) * 0.1  # доп.отступ 10%

        height = y1 - y0 + self.y_indent
        width = x1 - x0 + self.x_indent
        self.rect = QtCore.QRectF(0, 0, width, height)

    # }}}
    def __createGBars(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createGBars()")

        for n, bar in enumerate(self.chart, 0):
            gbar = GBar(bar, n, self)
            self.gbars.append(gbar)
            self.addToGroup(gbar)

    # }}}


# }}}


if __name__ == "__main__":
    ...
