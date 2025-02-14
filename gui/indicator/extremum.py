#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from avin.core import TimeFrame
from avin.utils import logger
from gui.chart.gchart import GBar, GChart, Thread
from gui.custom import Css, Icon, Label, Theme, ToolButton
from gui.indicator.item import IndicatorItem
from gui.marker import GShape
from usr.lib import Extremum, ExtremumList, Move, Term, Trend


class ExtremumIndicator:  # {{{
    name = "Extremum"

    def __init__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.gitem = None
        self.__item = None
        self.__label = None
        self.__settings = None

    # }}}

    def item(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.item()")

        if self.__item is None:
            self.__item = IndicatorItem(self)

        return self.__item

    # }}}
    def label(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.label()")

        if self.__label is None:
            self.__label = _ExtremumLabel(self)

        return self.__label

    # }}}
    def graphics(self, gchart: GChart):  # {{{
        logger.debug(f"{self.__class__.__name__}.graphics()")

        self.gitem = _ExtremumGraphics(gchart)

        if self.__settings is None:
            self.__settings = _ExtremumSettings(self)

        self.__settings.configureSilent(self.gitem)
        return self.gitem

    # }}}
    def configure(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.configure()")

        if self.__settings is None:
            self.__settings = _ExtremumSettings(self)

        self.__settings.configure(self.gitem)

    # }}}


# }}}


class _GExtremum(QtWidgets.QGraphicsItemGroup):  # {{{
    def __init__(  # {{{
        self, gchart: GChart, extr: Extremum, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.gchart = gchart
        self.extr = extr

        self.__calcCoordinates()
        self.__createPointShape()

    # }}}

    def __calcCoordinates(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__calcCoordinates()")

        # (x, y)   - epos - точка экстремума на графике
        # (x0, y0) - spos - точка графической метки экстремума
        x0 = self.gchart.xFromDatetime(self.extr.dt)
        x = x0 + GBar.WIDTH / 2
        y = self.gchart.yFromPrice(self.extr.price)
        y0 = y * 0.98 if self.extr.isMax() else y * 1.02

        self.epos = QtCore.QPointF(x, y)
        self.spos = QtCore.QPointF(x0, y0)

    # }}}
    def __createPointShape(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createPointShape()")

        # select size and color
        if self.extr.isLongterm():
            size = GShape.Size.BIG
            color = GShape.Color.VIOLET
        elif self.extr.isMidterm():
            size = GShape.Size.NORMAL
            color = GShape.Color.BLUE
        elif self.extr.isShortterm():
            size = GShape.Size.SMALL
            color = GShape.Color.CYAN

        # create shape
        shape = GShape(GShape.Type.SQARE, size, color)
        shape.setPos(self.spos)

        self.addToGroup(shape)

    # }}}


# }}}
class _GTrend(QtWidgets.QGraphicsItemGroup):  # {{{
    SHORTTERM_WIDTH = 1
    MIDTERM_WIDTH = 2
    LONGTERM_WIDTH = 3

    COLOR_5M = Theme.Chart.TREND_5M
    COLOR_1H = Theme.Chart.TREND_1H
    COLOR_D = Theme.Chart.TREND_D

    def __init__(  # {{{
        self, gchart: GChart, trend: Trend, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.gchart = gchart
        self.trend = trend

        self.__calcCoordinates()
        self.__createLine()

    # }}}

    def getTextInfo(self) -> str:  # {{{
        logger.debug(f"{self.__class__.__name__}.getTextInfo()")

        t = self.trend
        volume = t.volume()
        vol_str = f"{(t.volume() / 1_000_000):.2f}m"

        string = (
            f"{str(t.timeframe):<2} "
            f"{t.term.name[0:2]:<2} "
            f"{t.type.name} "
            f"p={t.period():<3} "
            f"d={t.deltaPercent():<6} "
            f"s={t.speedPercent():<6} "
            f"v={vol_str} "
            f"{t.strength.name[0:1]} "
        )
        return string

    # }}}
    def setPen(self, pen: QtGui.QPen):  # {{{
        self.line.setPen(pen)

    # }}}

    def __calcCoordinates(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__calcCoordinates()")

        # begin pos
        x0 = self.gchart.xFromDatetime(self.trend.begin.dt)
        x = x0 + GBar.WIDTH / 2
        y = self.gchart.yFromPrice(self.trend.begin.price)
        self.begin_pos = QtCore.QPointF(x, y)

        # end pos
        x0 = self.gchart.xFromDatetime(self.trend.end.dt)
        x = x0 + GBar.WIDTH / 2
        y = self.gchart.yFromPrice(self.trend.end.price)
        self.end_pos = QtCore.QPointF(x, y)

    # }}}
    def __createLine(self):  # {{{
        match str(self.trend.timeframe):
            case "D":
                color = self.COLOR_D
            case "1H":
                color = self.COLOR_1H
            case "5M":
                color = self.COLOR_5M

        match self.trend.term:
            case Term.STERM:
                width = self.SHORTTERM_WIDTH
            case Term.MTERM:
                width = self.MIDTERM_WIDTH
            case Term.LTERM:
                width = self.LONGTERM_WIDTH

        self.line = QtWidgets.QGraphicsLineItem(
            self.begin_pos.x(),
            self.begin_pos.y(),
            self.end_pos.x(),
            self.end_pos.y(),
        )
        pen = QtGui.QPen(color, width)
        self.line.setPen(pen)

        self.addToGroup(self.line)

    # }}}


# }}}
class _GMove(QtWidgets.QGraphicsItemGroup):  # {{{
    SHORTTERM_WIDTH = 1
    MIDTERM_WIDTH = 2
    LONGTERM_WIDTH = 3

    COLOR_BEAR = Theme.Chart.VAWE_BEAR
    COLOR_BULL = Theme.Chart.VAWE_BULL

    def __init__(  # {{{
        self, gchart: GChart, move: Move, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.gchart = gchart
        self.move = move

        self.__createLines()

    # }}}

    def __createLines(self):  # {{{
        match str(self.move.type.name):
            case "BEAR":
                color = self.COLOR_BEAR
            case "BULL":
                color = self.COLOR_BULL

        match self.move.term:
            case Term.STERM:
                width = self.SHORTTERM_WIDTH
            case Term.MTERM:
                width = self.MIDTERM_WIDTH
            case Term.LTERM:
                width = self.LONGTERM_WIDTH

        for trend in self.move.getTrends():
            gtrend = _GTrend(self.gchart, trend)
            gtrend.setPen(QtGui.QPen(color, width))
            self.addToGroup(gtrend)

    # }}}


# }}}
class _GExtremumList(QtWidgets.QGraphicsItemGroup):  # {{{
    def __init__(  # {{{
        self, gchart: GChart, elist: ExtremumList, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.gchart = gchart
        self.elist = elist

        self.__createInside()
        self.__createOutside()
        self.__createGExtrs()
        self.__createGTrends()
        self.__createGMoves()

    # }}}

    def getInfo(self, x):  # {{{
        string = ""

        # TODO: binary search

        for line in self.gs_trends.childItems():
            if self.__xInLine(x, line):
                string += line.getTextInfo()

        for line in self.gm_trends.childItems():
            if self.__xInLine(x, line):
                string += "\n"
                string += line.getTextInfo()

        for line in self.gl_trends.childItems():
            if self.__xInLine(x, line):
                string += "\n"
                string += line.getTextInfo()

        return string

    # }}}

    def __createInside(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createInside()")

        self.inside_marks = QtWidgets.QGraphicsItemGroup()
        gbars = self.gchart.gbars
        for gbar in gbars:
            bar = gbar.bar
            if bar.isInside():
                shape = self.__createInsideShape(gbar)
                self.inside_marks.addToGroup(shape)

        self.addToGroup(self.inside_marks)

    # }}}
    def __createInsideShape(self, gbar):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createInsideShape()")

        x = gbar.X0
        y = gbar.y_low
        w = gbar.WIDTH
        h = gbar.full_height

        rect = QtWidgets.QGraphicsRectItem(x, y, w, h)
        color = QtGui.QColor("#CC000000")
        rect.setPen(color)
        rect.setBrush(color)

        return rect

    # }}}
    def __createOutside(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createOutside()")

        self.outside_marks = QtWidgets.QGraphicsItemGroup()
        gbars = self.gchart.gbars
        for gbar in gbars:
            bar = gbar.bar
            if bar.isOutside():
                shape = self.__createOutsideShape(gbar)
                self.outside_marks.addToGroup(shape)

        self.addToGroup(self.outside_marks)

    # }}}
    def __createOutsideShape(self, gbar):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createOutsideShape()")

        x = gbar.X0
        y = gbar.y_low
        w = gbar.WIDTH
        h = gbar.full_height

        rect = QtWidgets.QGraphicsRectItem(x, y, w, h)
        color = QtGui.QColor("#33FFFFFF")
        rect.setPen(color)
        rect.setBrush(color)

        return rect

    # }}}
    def __createGExtrs(self):  # {{{
        self.gs_extrs = QtWidgets.QGraphicsItemGroup()
        for extr in self.elist.sterm:
            gextr = _GExtremum(self.gchart, extr)
            self.gs_extrs.addToGroup(gextr)

        self.gm_extrs = QtWidgets.QGraphicsItemGroup()
        for extr in self.elist.mterm:
            gextr = _GExtremum(self.gchart, extr)
            self.gm_extrs.addToGroup(gextr)

        self.gl_extrs = QtWidgets.QGraphicsItemGroup()
        for extr in self.elist.lterm:
            gextr = _GExtremum(self.gchart, extr)
            self.gl_extrs.addToGroup(gextr)

        self.addToGroup(self.gs_extrs)
        self.addToGroup(self.gm_extrs)
        self.addToGroup(self.gl_extrs)

    # }}}
    def __createGTrends(self):  # {{{
        self.gs_trends = QtWidgets.QGraphicsItemGroup()
        self.s_trends = self.elist.getAllTrends(Term.STERM)
        for trend in self.s_trends:
            gtrend = _GTrend(self.gchart, trend)
            self.gs_trends.addToGroup(gtrend)

        self.gm_trends = QtWidgets.QGraphicsItemGroup()
        self.m_trends = self.elist.getAllTrends(Term.MTERM)
        for trend in self.m_trends:
            gtrend = _GTrend(self.gchart, trend)
            self.gm_trends.addToGroup(gtrend)

        self.gl_trends = QtWidgets.QGraphicsItemGroup()
        self.l_trends = self.elist.getAllTrends(Term.LTERM)
        for trend in self.l_trends:
            gtrend = _GTrend(self.gchart, trend)
            self.gl_trends.addToGroup(gtrend)

        self.addToGroup(self.gs_trends)
        self.addToGroup(self.gm_trends)
        self.addToGroup(self.gl_trends)

    # }}}
    def __createGMoves(self):  # {{{
        self.gs_moves = QtWidgets.QGraphicsItemGroup()
        self.s_moves = self.elist.getAllMoves(Term.STERM)
        for move in self.s_moves:
            gmove = _GMove(self.gchart, move)
            self.gs_moves.addToGroup(gmove)

        self.gm_moves = QtWidgets.QGraphicsItemGroup()
        self.m_moves = self.elist.getAllMoves(Term.MTERM)
        for move in self.m_moves:
            gmove = _GMove(self.gchart, move)
            self.gm_moves.addToGroup(gmove)

        self.gl_moves = QtWidgets.QGraphicsItemGroup()
        self.l_moves = self.elist.getAllMoves(Term.LTERM)
        for move in self.l_moves:
            gmove = _GMove(self.gchart, move)
            self.gl_moves.addToGroup(gmove)

        self.addToGroup(self.gs_moves)
        self.addToGroup(self.gm_moves)
        self.addToGroup(self.gl_moves)

    # }}}
    def __xInLine(self, x, line: _GTrend):  # {{{
        logger.debug(f"{self.__class__.__name__}.__xInTrend()")

        if line.begin_pos.x() < x < line.end_pos.x():
            return True

        return False

    # }}}


# }}}


class _ExtremumGraphics(QtWidgets.QGraphicsItemGroup):  # {{{
    def __init__(self, gchart: GChart, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.gchart = gchart
        self.chart = gchart.chart

        self.gelist_5m = None
        self.gelist_1h = None
        self.gelist_d = None

        self.__createGraphics()

    # }}}

    # def showInside(self, value: bool):  # {{{
    #     self.gelist.inside_marks.setVisible(value)
    #
    # # }}}
    # def showOutside(self, value: bool):  # {{{
    #     self.gelist.outside_marks.setVisible(value)
    #
    # # }}}

    def showShortShapes5M(self, value: bool):  # {{{
        if self.gelist_5m is None:
            return

        self.gelist_5m.gs_extrs.setVisible(value)

    # }}}
    def showShortShapes1H(self, value: bool):  # {{{
        if self.gelist_1h is None:
            return

        self.gelist_1h.gs_extrs.setVisible(value)

    # }}}
    def showShortShapesD(self, value: bool):  # {{{
        if self.gelist_d is None:
            return

        self.gelist_d.gs_extrs.setVisible(value)

    # }}}
    def showMidShapes5M(self, value: bool):  # {{{
        if self.gelist_5m is None:
            return

        self.gelist_5m.gm_extrs.setVisible(value)

    # }}}
    def showMidShapes1H(self, value: bool):  # {{{
        if self.gelist_1h is None:
            return

        self.gelist_1h.gm_extrs.setVisible(value)

    # }}}
    def showMidShapesD(self, value: bool):  # {{{
        if self.gelist_d is None:
            return

        self.gelist_d.gm_extrs.setVisible(value)

    # }}}
    def showLongShapes5M(self, value: bool):  # {{{
        if self.gelist_5m is None:
            return

        self.gelist_5m.gl_extrs.setVisible(value)

    # }}}
    def showLongShapes1H(self, value: bool):  # {{{
        if self.gelist_1h is None:
            return

        self.gelist_1h.gl_extrs.setVisible(value)

    # }}}
    def showLongShapesD(self, value: bool):  # {{{
        if self.gelist_d is None:
            return

        self.gelist_d.gl_extrs.setVisible(value)

    # }}}

    def showShortLines5M(self, value: bool):  # {{{
        if self.gelist_5m is None:
            return

        self.gelist_5m.gs_trends.setVisible(value)

    # }}}
    def showShortLines1H(self, value: bool):  # {{{
        if self.gelist_1h is None:
            return

        self.gelist_1h.gs_trends.setVisible(value)

    # }}}
    def showShortLinesD(self, value: bool):  # {{{
        if self.gelist_d is None:
            return

        self.gelist_d.gs_trends.setVisible(value)

    # }}}
    def showMidLines5M(self, value: bool):  # {{{
        if self.gelist_5m is None:
            return

        self.gelist_5m.gm_trends.setVisible(value)

    # }}}
    def showMidLines1H(self, value: bool):  # {{{
        if self.gelist_1h is None:
            return

        self.gelist_1h.gm_trends.setVisible(value)

    # }}}
    def showMidLinesD(self, value: bool):  # {{{
        if self.gelist_d is None:
            return

        self.gelist_d.gm_trends.setVisible(value)

    # }}}
    def showLongLines5M(self, value: bool):  # {{{
        if self.gelist_5m is None:
            return

        self.gelist_5m.gl_trends.setVisible(value)

    # }}}
    def showLongLines1H(self, value: bool):  # {{{
        if self.gelist_1h is None:
            return

        self.gelist_1h.gl_trends.setVisible(value)

    # }}}
    def showLongLinesD(self, value: bool):  # {{{
        if self.gelist_d is None:
            return

        self.gelist_d.gl_trends.setVisible(value)

    # }}}

    def showShortMoves5M(self, value: bool):  # {{{
        if self.gelist_5m is None:
            return

        self.gelist_5m.gs_moves.setVisible(value)

    # }}}
    def showShortMoves1H(self, value: bool):  # {{{
        if self.gelist_1h is None:
            return

        self.gelist_1h.gs_moves.setVisible(value)

    # }}}
    def showShortMovesD(self, value: bool):  # {{{
        if self.gelist_d is None:
            return

        self.gelist_d.gs_moves.setVisible(value)

    # }}}
    def showMidMoves5M(self, value: bool):  # {{{
        if self.gelist_5m is None:
            return

        self.gelist_5m.gm_moves.setVisible(value)

    # }}}
    def showMidMoves1H(self, value: bool):  # {{{
        if self.gelist_1h is None:
            return

        self.gelist_1h.gm_moves.setVisible(value)

    # }}}
    def showMidMovesD(self, value: bool):  # {{{
        if self.gelist_d is None:
            return

        self.gelist_d.gm_moves.setVisible(value)

    # }}}
    def showLongMoves5M(self, value: bool):  # {{{
        if self.gelist_5m is None:
            return

        self.gelist_5m.gl_moves.setVisible(value)

    # }}}
    def showLongMoves1H(self, value: bool):  # {{{
        if self.gelist_1h is None:
            return

        self.gelist_1h.gl_moves.setVisible(value)

    # }}}
    def showLongMovesD(self, value: bool):  # {{{
        if self.gelist_d is None:
            return

        self.gelist_d.gl_moves.setVisible(value)

    # }}}

    def __createGraphics(self):  # {{{
        if self.chart.timeframe <= TimeFrame("5M"):
            self.chart_5m = Thread.loadChart(
                self.chart.instrument,
                TimeFrame("5M"),
                self.chart.first.dt,
                self.chart.last.dt,
            )
            self.gchart_5m = GChart(self.chart_5m)
            self.elist_5m = ExtremumList(self.chart_5m)
            self.gelist_5m = _GExtremumList(self.gchart, self.elist_5m)
            self.addToGroup(self.gelist_5m)

        if self.chart.timeframe <= TimeFrame("1H"):
            self.chart_1h = Thread.loadChart(
                self.chart.instrument,
                TimeFrame("1H"),
                self.chart.first.dt,
                self.chart.last.dt,
            )
            self.gchart_1h = GChart(self.chart_1h)
            self.elist_1h = ExtremumList(self.chart_1h)
            self.gelist_1h = _GExtremumList(self.gchart, self.elist_1h)
            self.addToGroup(self.gelist_1h)

        if self.chart.timeframe <= TimeFrame("D"):
            self.chart_d = Thread.loadChart(
                self.chart.instrument,
                TimeFrame("D"),
                self.chart.first.dt,
                self.chart.last.dt,
            )
            self.gchart_d = GChart(self.chart_d)
            self.elist_d = ExtremumList(self.chart_d)
            self.gelist_d = _GExtremumList(self.gchart, self.elist_d)
            self.addToGroup(self.gelist_d)


# }}}


# }}}
class _ExtremumLabel(QtWidgets.QWidget):  # {{{
    def __init__(self, indicator, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__indicator = indicator
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

    # }}}

    @property  # indicator  # {{{
    def indicator(self):
        return self.__indicator

    # }}}

    def setGChart(self, gchart):  # {{{
        self.gchart = gchart

    # }}}
    def update(self, x):  # {{{
        # 5M S p=5/BIG  d=15.5/NORMAL  s=3.1/SMALL  v=1000/VERY_BIG
        # 5M M p=5/BIG  d=15.5/NORMAL  s=3.1/SMALL  v=1000/VERY_BIG
        # 5M L p=5/BIG  d=15.5/NORMAL  s=3.1/SMALL  v=1000/VERY_BIG
        # 1H S p=5/BIG  d=15.5/NORMAL  s=3.1/SMALL  v=1000/VERY_BIG
        # 1H ...

        self.gitem = self.__indicator.gitem

        if self.gitem.gelist_5m is not None:
            string = self.gitem.gelist_5m.getInfo(x)
            self.info_5m.setText(string)

        if self.gitem.gelist_1h is not None:
            string = self.gitem.gelist_1h.getInfo(x)
            self.info_1h.setText(string)

        if self.gitem.gelist_d is not None:
            string = self.gitem.gelist_d.getInfo(x)
            self.info_d.setText(string)

    # }}}

    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.label_name = QtWidgets.QLabel("Extremum")
        self.btn_hide = ToolButton(Icon.HIDE)
        self.btn_settings = ToolButton(Icon.CONFIG)
        self.btn_delete = ToolButton(Icon.DELETE)

        self.info_5m = Label("5M")
        self.info_1h = Label("1H")
        self.info_d = Label("D")

        self.info_5m.setStyleSheet(Css.CHART_LABEL)
        self.info_1h.setStyleSheet(Css.CHART_LABEL)
        self.info_d.setStyleSheet(Css.CHART_LABEL)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.label_name)
        hbox.addWidget(self.btn_hide)
        hbox.addWidget(self.btn_settings)
        hbox.addWidget(self.btn_delete)
        hbox.addStretch()
        hbox.setContentsMargins(0, 0, 0, 0)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.info_5m)
        vbox.addWidget(self.info_1h)
        vbox.addWidget(self.info_d)

        self.setLayout(vbox)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.btn_settings.clicked.connect(self.__onSettings)

    # }}}

    @QtCore.pyqtSlot()  # __onSettings  # {{{
    def __onSettings(self):
        logger.debug(f"{self.__class__.__name__}.__onSettings()")

        self.indicator.configure()

    # }}}


# }}}
class _ExtremumSettings(QtWidgets.QDialog):  # {{{
    def __init__(self, indicator, parent=None):  # {{{
        QtWidgets.QDialog.__init__(self, parent)
        self.__indicator = indicator

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__initUI()

    # }}}

    @property  # indicator  # {{{
    def indicator(self):
        return self.__indicator

    # }}}

    def configureSilent(self, gextr: _ExtremumGraphics):  # {{{
        logger.debug(f"{self.__class__.__name__}.configure")

        # gextr.showInside(self.inside_checkbox.isChecked())
        # gextr.showOutside(self.outside_checkbox.isChecked())

        gextr.showShortShapes5M(self.spoint_5m_checkbox.isChecked())
        gextr.showShortShapes1H(self.spoint_1h_checkbox.isChecked())
        gextr.showShortShapesD(self.spoint_d_checkbox.isChecked())
        gextr.showMidShapes5M(self.mpoint_5m_checkbox.isChecked())
        gextr.showMidShapes1H(self.mpoint_1h_checkbox.isChecked())
        gextr.showMidShapesD(self.mpoint_d_checkbox.isChecked())
        gextr.showLongShapes5M(self.lpoint_5m_checkbox.isChecked())
        gextr.showLongShapes1H(self.lpoint_1h_checkbox.isChecked())
        gextr.showLongShapesD(self.lpoint_d_checkbox.isChecked())

        gextr.showShortLines5M(self.sline_5m_checkbox.isChecked())
        gextr.showShortLines1H(self.sline_1h_checkbox.isChecked())
        gextr.showShortLinesD(self.sline_d_checkbox.isChecked())
        gextr.showMidLines5M(self.mline_5m_checkbox.isChecked())
        gextr.showMidLines1H(self.mline_1h_checkbox.isChecked())
        gextr.showMidLinesD(self.mline_d_checkbox.isChecked())
        gextr.showLongLines5M(self.lline_5m_checkbox.isChecked())
        gextr.showLongLines1H(self.lline_1h_checkbox.isChecked())
        gextr.showLongLinesD(self.lline_d_checkbox.isChecked())

        gextr.showShortMoves5M(self.smove_5m_checkbox.isChecked())
        gextr.showShortMoves1H(self.smove_1h_checkbox.isChecked())
        gextr.showShortMovesD(self.smove_d_checkbox.isChecked())
        gextr.showMidMoves5M(self.mmove_5m_checkbox.isChecked())
        gextr.showMidMoves1H(self.mmove_1h_checkbox.isChecked())
        gextr.showMidMovesD(self.mmove_d_checkbox.isChecked())
        gextr.showLongMoves5M(self.lmove_5m_checkbox.isChecked())
        gextr.showLongMoves1H(self.lmove_1h_checkbox.isChecked())
        gextr.showLongMovesD(self.lmove_d_checkbox.isChecked())

    # }}}
    def configure(self, gextr):  # {{{
        logger.debug(f"{self.__class__.__name__}.showSettings")

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return

        if gextr is None:
            return

        self.configureSilent(gextr)

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowTitle("AVIN")
        self.setStyleSheet(Css.DIALOG)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.title_label = Label("| Extremum settings:", parent=self)
        self.title_label.setStyleSheet(Css.TITLE)

        self.inside_checkbox = QtWidgets.QCheckBox("Inside")
        self.outside_checkbox = QtWidgets.QCheckBox("Outside")

        self.spoint_5m_checkbox = QtWidgets.QCheckBox("5M")
        self.mpoint_5m_checkbox = QtWidgets.QCheckBox("5M")
        self.lpoint_5m_checkbox = QtWidgets.QCheckBox("5M")
        self.spoint_1h_checkbox = QtWidgets.QCheckBox("1H")
        self.mpoint_1h_checkbox = QtWidgets.QCheckBox("1H")
        self.lpoint_1h_checkbox = QtWidgets.QCheckBox("1H")
        self.spoint_d_checkbox = QtWidgets.QCheckBox("D")
        self.mpoint_d_checkbox = QtWidgets.QCheckBox("D")
        self.lpoint_d_checkbox = QtWidgets.QCheckBox("D")

        self.sline_5m_checkbox = QtWidgets.QCheckBox("5M")
        self.mline_5m_checkbox = QtWidgets.QCheckBox("5M")
        self.lline_5m_checkbox = QtWidgets.QCheckBox("5M")
        self.sline_1h_checkbox = QtWidgets.QCheckBox("1H")
        self.mline_1h_checkbox = QtWidgets.QCheckBox("1H")
        self.lline_1h_checkbox = QtWidgets.QCheckBox("1H")
        self.sline_d_checkbox = QtWidgets.QCheckBox("D")
        self.mline_d_checkbox = QtWidgets.QCheckBox("D")
        self.lline_d_checkbox = QtWidgets.QCheckBox("D")

        self.smove_5m_checkbox = QtWidgets.QCheckBox("5M")
        self.mmove_5m_checkbox = QtWidgets.QCheckBox("5M")
        self.lmove_5m_checkbox = QtWidgets.QCheckBox("5M")
        self.smove_1h_checkbox = QtWidgets.QCheckBox("1H")
        self.mmove_1h_checkbox = QtWidgets.QCheckBox("1H")
        self.lmove_1h_checkbox = QtWidgets.QCheckBox("1H")
        self.smove_d_checkbox = QtWidgets.QCheckBox("D")
        self.mmove_d_checkbox = QtWidgets.QCheckBox("D")
        self.lmove_d_checkbox = QtWidgets.QCheckBox("D")

        self.ok_btn = ToolButton(Icon.OK)
        self.cancel_btn = ToolButton(Icon.CANCEL)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox_btn = QtWidgets.QHBoxLayout()
        hbox_btn.addWidget(self.title_label)
        hbox_btn.addStretch()
        hbox_btn.addWidget(self.ok_btn)
        hbox_btn.addWidget(self.cancel_btn)

        hbox_days = QtWidgets.QHBoxLayout()
        hbox_days.addWidget(Label("Days: "))
        hbox_days.addWidget(self.inside_checkbox)
        hbox_days.addWidget(self.outside_checkbox)

        hbox_points_s = QtWidgets.QHBoxLayout()
        hbox_points_s.addWidget(Label("Points S: "))
        hbox_points_s.addWidget(self.spoint_5m_checkbox)
        hbox_points_s.addWidget(self.spoint_1h_checkbox)
        hbox_points_s.addWidget(self.spoint_d_checkbox)
        hbox_points_m = QtWidgets.QHBoxLayout()
        hbox_points_m.addWidget(Label("Points M: "))
        hbox_points_m.addWidget(self.mpoint_5m_checkbox)
        hbox_points_m.addWidget(self.mpoint_1h_checkbox)
        hbox_points_m.addWidget(self.mpoint_d_checkbox)
        hbox_points_l = QtWidgets.QHBoxLayout()
        hbox_points_l.addWidget(Label("Points L: "))
        hbox_points_l.addWidget(self.lpoint_5m_checkbox)
        hbox_points_l.addWidget(self.lpoint_1h_checkbox)
        hbox_points_l.addWidget(self.lpoint_d_checkbox)

        hbox_lines_s = QtWidgets.QHBoxLayout()
        hbox_lines_s.addWidget(Label("Lines S: "))
        hbox_lines_s.addWidget(self.sline_5m_checkbox)
        hbox_lines_s.addWidget(self.sline_1h_checkbox)
        hbox_lines_s.addWidget(self.sline_d_checkbox)
        hbox_lines_m = QtWidgets.QHBoxLayout()
        hbox_lines_m.addWidget(Label("Lines M: "))
        hbox_lines_m.addWidget(self.mline_5m_checkbox)
        hbox_lines_m.addWidget(self.mline_1h_checkbox)
        hbox_lines_m.addWidget(self.mline_d_checkbox)
        hbox_lines_l = QtWidgets.QHBoxLayout()
        hbox_lines_l.addWidget(Label("Lines L: "))
        hbox_lines_l.addWidget(self.lline_5m_checkbox)
        hbox_lines_l.addWidget(self.lline_1h_checkbox)
        hbox_lines_l.addWidget(self.lline_d_checkbox)

        hbox_moves_s = QtWidgets.QHBoxLayout()
        hbox_moves_s.addWidget(Label("Moves S: "))
        hbox_moves_s.addWidget(self.smove_5m_checkbox)
        hbox_moves_s.addWidget(self.smove_1h_checkbox)
        hbox_moves_s.addWidget(self.smove_d_checkbox)
        hbox_moves_m = QtWidgets.QHBoxLayout()
        hbox_moves_m.addWidget(Label("Moves M: "))
        hbox_moves_m.addWidget(self.mmove_5m_checkbox)
        hbox_moves_m.addWidget(self.mmove_1h_checkbox)
        hbox_moves_m.addWidget(self.mmove_d_checkbox)
        hbox_moves_l = QtWidgets.QHBoxLayout()
        hbox_moves_l.addWidget(Label("Moves L: "))
        hbox_moves_l.addWidget(self.lmove_5m_checkbox)
        hbox_moves_l.addWidget(self.lmove_1h_checkbox)
        hbox_moves_l.addWidget(self.lmove_d_checkbox)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(hbox_btn)
        vbox.addLayout(hbox_days)
        vbox.addSpacing(20)
        vbox.addLayout(hbox_points_s)
        vbox.addLayout(hbox_points_m)
        vbox.addLayout(hbox_points_l)
        vbox.addSpacing(20)
        vbox.addLayout(hbox_lines_s)
        vbox.addLayout(hbox_lines_m)
        vbox.addLayout(hbox_lines_l)
        vbox.addSpacing(20)
        vbox.addLayout(hbox_moves_s)
        vbox.addLayout(hbox_moves_m)
        vbox.addLayout(hbox_moves_l)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    # }}}
    def __initUI(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")

        # self.inside_checkbox.setChecked(False)
        # self.outside_checkbox.setChecked(False)

        # self.sshape_checkbox.setChecked(False)
        # self.mshape_checkbox.setChecked(False)
        # self.lshape_checkbox.setChecked(False)

    # }}}


# }}}


# class _ExtremumGraphicsLabel(QtWidgets.QGraphicsItemGroup):  # {{{
#     def __init__(self, indicator, parent=None):  # {{{
#         logger.debug(f"{self.__class__.__name__}.__init__()")
#         QtWidgets.QGraphicsItemGroup.__init__(self, parent)
#
#         hide_icon = Icon.CLOSE
#         pixmap = hide_icon.pixmap(32)
#         self.gitem = QtWidgets.QGraphicsPixmapItem(pixmap)
#
#         self.gitem.setPos(100, 100)
#         self.addToGroup(self.gitem)
#
#     # }}}
#
#     def mousePressEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent):
#         logger.debug(f"{self.__class__.__name__}.mousePressEvent()")
#         super().mousePressEvent(e)
#
#         # Dialog.info("Hello")
#         print("xxxx")
#
#         # return e.accept()
#         return e.ignore()
#
#     def mouseReleaseEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent):
#         logger.debug(f"{self.__class__.__name__}.mouseReleaseEvent()")
#
#         super().mouseReleaseEvent(e)
#         return e.ignore()
#
#
# # }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    indicator = ExtremumIndicator()
    w = _ExtremumSettings(indicator)
    w.show()
    sys.exit(app.exec())
