#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from PyQt6 import QtCore, QtWidgets

from avin.const import ONE_DAY
from avin.core import (
    Bar,
    Chart,
    TimeFrame,
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
        shadow.setPen(self.color)
        self.addToGroup(shadow)

    # }}}
    def __createOpenLine(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createOpenLine()")

        opn = QtWidgets.QGraphicsLineItem(
            self.x0, self.y_opn, self.x_center, self.y_opn
        )
        opn.setPen(self.color)
        self.addToGroup(opn)

    # }}}
    def __createCloseLine(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createCloseLine()")

        cls = QtWidgets.QGraphicsLineItem(
            self.x_center, self.y_cls, self.x1, self.y_cls
        )
        cls.setPen(self.color)
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
class GBarBehind(QtWidgets.QGraphicsItemGroup):  # {{{
    def __init__(self, bars: list[Bar], gchart: GChart):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, gchart)

        self.bars = bars
        self.gchart = gchart

        self.__calcCoordinates()
        self.__setColor()
        self.__createGraphics()

    # }}}
    def __calcCoordinates(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__calcCoordinates()")

        first = self.bars[0]
        last = self.bars[-1]
        low_bar = min(self.bars, key=lambda x: x.low)
        high_bar = max(self.bars, key=lambda x: x.high)

        gchart = self.gchart
        self.x0 = gchart.xFromDatetime(first.dt) + GBar.INDENT
        self.x1 = gchart.xFromDatetime(last.dt) - GBar.WIDTH - GBar.INDENT
        self.y0 = gchart.yFromPrice(low_bar.low)
        self.y1 = gchart.yFromPrice(high_bar.high)

    # }}}
    def __setColor(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setColor()")

        open_price = self.bars[0].open
        close_price = self.bars[-1].close

        if close_price > open_price:
            self.color = Theme.Chart.BULL_BEHIND
        elif close_price < open_price:
            self.color = Theme.Chart.BEAR_BEHIND
        else:
            self.color = Theme.Chart.UNDEFINE_BEHIND

    # }}}
    def __createGraphics(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createGraphics()")

        width = self.x1 - self.x0
        height = self.y1 - self.y0

        body = QtWidgets.QGraphicsRectItem(self.x0, self.y0, width, height)
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
        self.gbars_behind = list()

        self.__createSceneRect()
        self.__createGBars()

    # }}}

    def drawBack(self, timeframe: TimeFrame) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.drawBack()")

        assert timeframe in (TimeFrame("1H"), TimeFrame("D"))
        assert len(self.gbars) > 0

        if timeframe == TimeFrame("1H"):
            self.__drawBack_1H()

        if timeframe == TimeFrame("D"):
            self.__drawBack_D()

    # }}}
    def clearBack(self, timeframe: TimeFrame) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clearBack()")

        assert timeframe in (TimeFrame("1H"), TimeFrame("D"))
        assert len(self.gbars) > 0

        # clear old graphic bars behind
        for gbar_behind in self.gbars_behind:
            gbar_behind.setVisible(False)  # NOTE: иначе не удаляются...
            self.removeFromGroup(gbar_behind)

    # }}}

    def nFromX(self, x) -> int:  # {{{
        logger.debug(f"{self.__class__.__name__}.nFromX()")

        n = int(x / GBar.WIDTH)
        return n

    # }}}
    def barFromDatetime(self, dt) -> GBar:  # {{{
        logger.debug(f"{self.__class__.__name__}.barFromDatetime()")

        index = find_left(self.gbars, dt, key=lambda x: x.bar.dt)
        assert index is not None
        gbar = self.gbars[index]

        return gbar

    # }}}
    def barAt(self, x) -> GBar:  # {{{
        logger.debug(f"{self.__class__.__name__}.barAt()")

        if x < 0:
            return None

        n = self.nFromX(x)
        if n < len(self.gbars):
            return self.gbars[n]
        else:
            return None

    # }}}
    def xFromNumber(self, n) -> float:  # {{{
        logger.debug(f"{self.__class__.__name__}.xFromNumber()")

        return int(n * GBar.WIDTH)

    # }}}
    def xFromDatetime(self, dt) -> float:  # {{{
        logger.debug(f"{self.__class__.__name__}.xFromDatetime()")

        gbar = self.barFromDatetime(dt)
        return gbar.x

    # }}}
    def yFromPrice(self, price) -> float:  # {{{
        logger.debug(f"{self.__class__.__name__}.yFromPrice()")

        y = self.rect.height() - price * self.SCALE_Y + self.y_indent
        return y

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
    def __drawBack_1H(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawBack_1H()")

    # }}}
    def __drawBack_D(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawBack_D()")

        first_day = self.chart.first.dt.date()
        last_day = self.chart.last.dt.date()

        day = first_day
        while day <= last_day:
            bars = self.chart.getBarsOfDate(day)

            if bars:
                gbar_behind = GBarBehind(bars, self)
                self.gbars_behind.append(gbar_behind)
                self.addToGroup(gbar_behind)

            day += ONE_DAY

    # }}}


# }}}


if __name__ == "__main__":
    ...
