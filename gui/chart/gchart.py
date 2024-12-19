#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum

from PyQt6 import QtCore, QtWidgets

from avin.config import Cfg
from avin.const import ONE_DAY, ONE_HOUR, ONE_WEEK
from avin.core import (
    Bar,
    Chart,
    TimeFrame,
)
from avin.utils import find_left, logger, next_month
from gui.chart.gmark import Marker, Shape
from gui.custom import Theme


class ViewType(enum.Enum):  # {{{
    BAR = 1
    CUNDLE = 2


# }}}
class GBar(QtWidgets.QGraphicsItemGroup):  # {{{
    WIDTH = Cfg.Chart.BAR_WIDTH
    HEIGHT = Cfg.Chart.BAR_HEIGHT
    CUNDLE_INDENT = Cfg.Chart.CUNDLE_INDENT
    BAR_INDENT = Cfg.Chart.BAR_INDENT
    SHADOW_WIDTH = Cfg.Chart.SHADOW_WIDTH

    def __init__(self, bar: Bar, n: int, gchart: GChart):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, gchart)

        self.bar = bar
        self.n = n
        self.gchart = gchart
        self.shapes = list()

        self.__calcCoordinates()
        self.__setColor()
        self.__createShadowLine()
        self.__createBody()
        self.__createOpenLine()
        self.__createCloseLine()
        self.updateView()

    # }}}

    def addShape(self, shape: Shape) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.addShape()")

        self.shapes.append(shape)

        x = self.X0
        y = self.y_hgh - 20 * len(self.shapes)

        shape.setPos(x, y)
        self.addToGroup(shape)

    # }}}
    def clearShapes(self) -> None:
        logger.debug(f"{self.__class__.__name__}.clearShapes()")

        for item in self.shapes:
            item.setVisible(False)
            self.removeFromGroup(item)

        self.shapes.clear()

    def updateView(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.updateView()")

        view_type = self.gchart.viewType()
        match view_type:
            case ViewType.BAR:
                self.open_line.show()
                self.close_line.show()
                self.body.hide()
            case ViewType.CUNDLE:
                self.open_line.hide()
                self.close_line.hide()
                self.body.show()

    # }}}

    def __calcCoordinates(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__calcCoordinates()")

        gchart = self.gchart

        # for bar view - without indent
        self.X0 = gchart.xFromNumber(self.n)
        self.X1 = self.X0 + self.WIDTH

        self.x_center = (self.X0 + self.X1) / 2
        self.x0_bar = self.X0 + self.BAR_INDENT
        self.x1_bar = self.X1 - self.BAR_INDENT
        self.x0_cundle = self.X0 + self.CUNDLE_INDENT
        self.x1_cundle = self.X1 - self.CUNDLE_INDENT

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

        self.shadow = QtWidgets.QGraphicsLineItem(
            self.x_center, self.y_low, self.x_center, self.y_hgh
        )
        self.shadow.setPen(self.color)
        self.addToGroup(self.shadow)

    # }}}
    def __createOpenLine(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createOpenLine()")

        self.open_line = QtWidgets.QGraphicsLineItem(
            self.x0_bar, self.y_opn, self.x_center, self.y_opn
        )
        self.open_line.setPen(self.color)
        self.addToGroup(self.open_line)

    # }}}
    def __createCloseLine(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createCloseLine()")

        self.close_line = QtWidgets.QGraphicsLineItem(
            self.x_center, self.y_cls, self.x1_bar, self.y_cls
        )
        self.close_line.setPen(self.color)
        self.addToGroup(self.close_line)

    # }}}
    def __createBody(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createBody()")

        width = self.x1_cundle - self.x0_cundle
        height = abs(self.y_opn - self.y_cls)
        y0 = self.y_cls if self.bar.isBull() else self.y_opn
        x0 = self.x_center - width / 2

        self.body = QtWidgets.QGraphicsRectItem(x0, y0, width, height)
        self.body.setPen(self.color)
        self.body.setBrush(self.color)

        self.addToGroup(self.body)

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
        self.x0 = gchart.xFromDatetime(first.dt)
        self.x1 = gchart.xFromDatetime(last.dt) + GBar.WIDTH
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
        body.setPen(self.color)
        body.setBrush(self.color)

        self.addToGroup(body)

    # }}}


# }}}
class GChart(QtWidgets.QGraphicsItemGroup):  # {{{
    __VIEW_TYPE = ViewType.BAR

    def __init__(self, chart: Chart, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.chart = chart
        self.gbars = list()
        self.behind_1H = list()
        self.behind_D = list()
        self.behind_W = list()
        self.behind_M = list()

        self.__createSceneRect()
        self.__createGBars()

    # }}}

    @property  # first  # {{{
    def first(self) -> GBar:
        assert len(self.gbars)

        return self.gbars[0]

    # }}}
    @property  # last  # {{{
    def last(self) -> GBar:
        assert len(self.gbars)

        return self.gbars[-1]

    # }}}

    def addMarker(self, marker: Marker) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.addMarker()")

        chart = self.chart
        f = marker.filter
        chart.setHeadIndex(0)
        while chart.nextHead():
            if f.check(chart):
                dt = chart.now.dt
                gbar = self.barFromDatetime(dt)
                gbar.addShape(marker.shape)

    # }}}
    def clearMarkers(self):
        logger.debug(f"{self.__class__.__name__}.addMarker()")

        for gbar in self.gbars:
            gbar.clearShapes()

    def viewType(self) -> ViewType:  # {{{
        logger.debug(f"{self.__class__.__name__}.viewType()")

        return GChart.__VIEW_TYPE

    # }}}
    def setViewType(self, t: ViewType) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setViewType()")

        GChart.__VIEW_TYPE = t
        for gbar in self.gbars:
            gbar.updateView()

    # }}}
    def drawBack(self, timeframe: TimeFrame) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.drawBack()")

        assert len(self.gbars) > 0

        match timeframe:
            case "1H":
                self.__drawBack_1H()
            case "D":
                self.__drawBack_D()
            case "W":
                self.__drawBack_W()
            case "M":
                self.__drawBack_M()

    # }}}
    def clearBack(self, timeframe: TimeFrame) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clearBack()")

        assert len(self.gbars) > 0

        match str(timeframe):
            case "1H":
                self.__clearBack_1H()
            case "D":
                self.__clearBack_D()
            case "W":
                self.__clearBack_W()
            case "M":
                self.__clearBack_M()

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
        return gbar.X0

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

        first = self.chart.first.dt
        last = self.chart.last.dt

        current = first
        while current <= last:
            bars = self.chart.getBarsOfHour(current)

            if bars:
                gbar_behind = GBarBehind(bars, self)
                self.behind_1H.append(gbar_behind)
                self.addToGroup(gbar_behind)

            current += ONE_HOUR

    # }}}
    def __drawBack_D(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawBack_D()")

        first = self.chart.first.dt
        last = self.chart.last.dt

        day = first
        while day <= last:
            bars = self.chart.getBarsOfDay(day)

            if bars:
                gbar_behind = GBarBehind(bars, self)
                self.behind_D.append(gbar_behind)
                self.addToGroup(gbar_behind)

            day += ONE_DAY

    # }}}
    def __drawBack_W(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawBack_W()")

        first = self.chart.first.dt
        last = self.chart.last.dt

        current = first
        while current <= last:
            bars = self.chart.getBarsOfWeek(current)

            if bars:
                gbar_behind = GBarBehind(bars, self)
                self.behind_W.append(gbar_behind)
                self.addToGroup(gbar_behind)

            current += ONE_WEEK

    # }}}
    def __drawBack_M(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawBack_M()")

        first = self.chart.first.dt
        last = self.chart.last.dt

        current = first
        while current <= last:
            bars = self.chart.getBarsOfMonth(current)

            if bars:
                gbar_behind = GBarBehind(bars, self)
                self.behind_M.append(gbar_behind)
                self.addToGroup(gbar_behind)

            current = next_month(current)

    # }}}
    def __clearBack_1H(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__clearBack_1H()")

        for gbar_behind in self.behind_1H:
            gbar_behind.setVisible(False)  # NOTE: иначе не удаляются...
            self.removeFromGroup(gbar_behind)

    # }}}
    def __clearBack_D(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__clearBack_D()")

        for gbar_behind in self.behind_D:
            gbar_behind.setVisible(False)  # NOTE: иначе не удаляются...
            self.removeFromGroup(gbar_behind)

    # }}}
    def __clearBack_W(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__clearBack_W()")

        for gbar_behind in self.behind_W:
            gbar_behind.setVisible(False)  # NOTE: иначе не удаляются...
            self.removeFromGroup(gbar_behind)

    # }}}
    def __clearBack_M(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__clearBack_M()")

        for gbar_behind in self.behind_M:
            gbar_behind.setVisible(False)  # NOTE: иначе не удаляются...
            self.removeFromGroup(gbar_behind)

    # }}}


# }}}


if __name__ == "__main__":
    ...
