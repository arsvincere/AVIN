#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from avin.analytic import Extremum, ExtremumList, Term, Trend
from avin.utils import logger
from gui.chart.gchart import GBar, GChart
from gui.custom import Css, Icon, Label, Theme, ToolButton
from gui.indicator.item import IndicatorItem
from gui.marker import GShape


class ExtremumIndicator:  # {{{
    name = "Extremum"

    def __init__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.__item = None
        self.__gitem = None
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

        self.__gitem = _ExtremumGraphics(gchart)

        if self.__settings is None:
            self.__settings = _ExtremumSettings(self)

        self.__settings.configureSilent(self.__gitem)
        return self.__gitem

    # }}}
    def configure(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.configure()")

        if self.__settings is None:
            self.__settings = _ExtremumSettings(self)

        self.__settings.configure(self.__gitem)

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
        match str(self.gchart.chart.timeframe):
            case "D":
                color = self.COLOR_D
            case "1H":
                color = self.COLOR_1H
            case "5M":
                color = self.COLOR_5M

        match self.trend.term:
            case Term.SHORTTERM:
                width = self.SHORTTERM_WIDTH
            case Term.MIDTERM:
                width = self.MIDTERM_WIDTH
            case Term.LONGTERM:
                width = self.LONGTERM_WIDTH

        line = QtWidgets.QGraphicsLineItem(
            self.begin_pos.x(),
            self.begin_pos.y(),
            self.end_pos.x(),
            self.end_pos.y(),
        )
        pen = QtGui.QPen(color, width)
        line.setPen(pen)

        self.addToGroup(line)

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

        self.__createPoints()
        self.__createLines()
        self.__createInside()
        self.__createOutside()

    # }}}
    def __createPoints(self):  # {{{
        self.s_points = QtWidgets.QGraphicsItemGroup()
        for extr in self.elist.sterm:
            gextr = _GExtremum(self.gchart, extr)
            self.s_points.addToGroup(gextr)

        self.m_points = QtWidgets.QGraphicsItemGroup()
        for extr in self.elist.mterm:
            gextr = _GExtremum(self.gchart, extr)
            self.m_points.addToGroup(gextr)

        self.l_points = QtWidgets.QGraphicsItemGroup()
        for extr in self.elist.lterm:
            gextr = _GExtremum(self.gchart, extr)
            self.l_points.addToGroup(gextr)

        self.addToGroup(self.s_points)
        self.addToGroup(self.m_points)
        self.addToGroup(self.l_points)

    # }}}
    def __createLines(self):  # {{{
        self.s_lines = QtWidgets.QGraphicsItemGroup()
        self.s_trends = self.elist.getAllSTrends()
        for trend in self.s_trends:
            gtrend = _GTrend(self.gchart, trend)
            self.s_lines.addToGroup(gtrend)

        self.m_lines = QtWidgets.QGraphicsItemGroup()
        self.m_trends = self.elist.getAllMTrends()
        for trend in self.m_trends:
            gtrend = _GTrend(self.gchart, trend)
            self.m_lines.addToGroup(gtrend)

        self.l_lines = QtWidgets.QGraphicsItemGroup()
        self.l_trends = self.elist.getAllLTrends()
        for trend in self.l_trends:
            gtrend = _GTrend(self.gchart, trend)
            self.l_lines.addToGroup(gtrend)

        self.addToGroup(self.s_lines)
        self.addToGroup(self.m_lines)
        self.addToGroup(self.l_lines)

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


# }}}


class _ExtremumGraphics(QtWidgets.QGraphicsItemGroup):  # {{{
    def __init__(self, gchart: GChart, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.gchart = gchart
        self.chart = gchart.chart
        self.elist = ExtremumList(self.chart)
        self.gelist = _GExtremumList(self.gchart, self.elist)
        self.addToGroup(self.gelist)

    # }}}

    def showInside(self, value: bool):  # {{{
        self.gelist.inside_marks.setVisible(value)

    # }}}
    def showOutside(self, value: bool):  # {{{
        self.gelist.outside_marks.setVisible(value)

    # }}}
    def showShortShapes(self, value: bool):  # {{{
        self.gelist.s_points.setVisible(value)

    # }}}
    def showMidShapes(self, value: bool):  # {{{
        self.gelist.m_points.setVisible(value)

    # }}}
    def showLongShapes(self, value: bool):  # {{{
        self.gelist.l_points.setVisible(value)

    # }}}
    def showShortLines(self, value: bool):  # {{{
        self.gelist.s_lines.setVisible(value)

    # }}}
    def showMidLines(self, value: bool):  # {{{
        self.gelist.m_lines.setVisible(value)

    # }}}
    def showLongLines(self, value: bool):  # {{{
        self.gelist.l_lines.setVisible(value)

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

    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.label_name = QtWidgets.QLabel("Extremum")
        self.btn_hide = ToolButton(Icon.HIDE)
        self.btn_settings = ToolButton(Icon.CONFIG)
        self.btn_delete = ToolButton(Icon.DELETE)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        hbox = QtWidgets.QHBoxLayout(self)
        hbox.addWidget(self.label_name)
        hbox.addWidget(self.btn_hide)
        hbox.addWidget(self.btn_settings)
        hbox.addWidget(self.btn_delete)
        hbox.addStretch()
        hbox.setContentsMargins(0, 0, 0, 0)

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

        gextr.showInside(self.inside_checkbox.isChecked())
        gextr.showOutside(self.outside_checkbox.isChecked())
        gextr.showShortShapes(self.sshape_checkbox.isChecked())
        gextr.showMidShapes(self.mshape_checkbox.isChecked())
        gextr.showLongShapes(self.lshape_checkbox.isChecked())
        gextr.showShortLines(self.sline_checkbox.isChecked())
        gextr.showMidLines(self.mline_checkbox.isChecked())
        gextr.showLongLines(self.lline_checkbox.isChecked())

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

        self.inside_checkbox = QtWidgets.QCheckBox("Inside days")
        self.outside_checkbox = QtWidgets.QCheckBox("Outside days")
        self.sshape_checkbox = QtWidgets.QCheckBox("Short-term extremum")
        self.mshape_checkbox = QtWidgets.QCheckBox("Mid-term extremum")
        self.lshape_checkbox = QtWidgets.QCheckBox("Long-term extremum")
        self.sline_checkbox = QtWidgets.QCheckBox("Short-term line")
        self.mline_checkbox = QtWidgets.QCheckBox("Mid-term line")
        self.lline_checkbox = QtWidgets.QCheckBox("Long-term line")

        self.ok_btn = ToolButton(Icon.OK)
        self.cancel_btn = ToolButton(Icon.CANCEL)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.title_label)
        hbox.addStretch()
        hbox.addWidget(self.ok_btn)
        hbox.addWidget(self.cancel_btn)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(hbox)
        vbox.addWidget(self.inside_checkbox)
        vbox.addWidget(self.outside_checkbox)
        vbox.addSpacing(20)

        vbox.addWidget(self.sshape_checkbox)
        vbox.addWidget(self.mshape_checkbox)
        vbox.addWidget(self.lshape_checkbox)
        vbox.addSpacing(20)

        vbox.addWidget(self.sline_checkbox)
        vbox.addWidget(self.mline_checkbox)
        vbox.addWidget(self.lline_checkbox)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    # }}}
    def __initUI(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")

        self.inside_checkbox.setChecked(False)
        self.outside_checkbox.setChecked(False)

        self.sshape_checkbox.setChecked(False)
        self.mshape_checkbox.setChecked(False)
        self.lshape_checkbox.setChecked(False)

        self.sline_checkbox.setChecked(True)
        self.mline_checkbox.setChecked(False)
        self.lline_checkbox.setChecked(False)

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
