#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from avin.analytic import ExtremumList
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


class _ExtremumGraphics(QtWidgets.QGraphicsItemGroup):  # {{{
    LONGTERM_LINE_WIDTH = 4
    MIDTERM_LINE_WIDTH = 2
    SHORTTERM_LINE_WIDTH = 1

    __LPEN = QtGui.QPen()
    __LPEN.setWidth(LONGTERM_LINE_WIDTH)
    __LPEN.setColor(Theme.Chart.LONGTERM)
    __MPEN = QtGui.QPen()
    __MPEN.setWidth(MIDTERM_LINE_WIDTH)
    __MPEN.setColor(Theme.Chart.MIDTERM)
    __SPEN = QtGui.QPen()
    __SPEN.setWidth(SHORTTERM_LINE_WIDTH)
    __SPEN.setColor(Theme.Chart.SHORTTERM)

    def __init__(self, gchart: GChart, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.gchart = gchart
        self.chart = gchart.chart
        self.elist = ExtremumList(self.chart)

        self.s_points = self.__createPoints(self.elist.sterm)
        self.m_points = self.__createPoints(self.elist.mterm)
        self.l_points = self.__createPoints(self.elist.lterm)

        self.s_lines = self.__createLines(self.s_points, self.__SPEN)
        self.m_lines = self.__createLines(self.m_points, self.__MPEN)
        self.l_lines = self.__createLines(self.l_points, self.__LPEN)

        self.s_speeds = self.__createSpeedLabels(self.s_points)
        self.m_speeds = self.__createSpeedLabels(self.m_points)
        self.l_speeds = self.__createSpeedLabels(self.l_points)

        self.inside_marks = self.__createInside()
        self.outside_marks = self.__createOutside()

        self.addToGroup(self.s_points)
        self.addToGroup(self.m_points)
        self.addToGroup(self.l_points)
        self.addToGroup(self.s_lines)
        self.addToGroup(self.m_lines)
        self.addToGroup(self.l_lines)
        self.addToGroup(self.s_speeds)
        self.addToGroup(self.m_speeds)
        self.addToGroup(self.l_speeds)
        self.addToGroup(self.inside_marks)
        self.addToGroup(self.outside_marks)

    # }}}

    def showInside(self, value: bool):  # {{{
        items = self.inside_marks.childItems()
        for item in items:
            item.setVisible(value)

    # }}}
    def showOutside(self, value: bool):  # {{{
        items = self.outside_marks.childItems()
        for item in items:
            item.setVisible(value)

    # }}}
    def showShortShapes(self, value: bool):  # {{{
        items = self.s_points.childItems()
        for item in items:
            item.setVisible(value)

    # }}}
    def showMidShapes(self, value: bool):  # {{{
        items = self.m_points.childItems()
        for item in items:
            item.setVisible(value)

    # }}}
    def showLongShapes(self, value: bool):  # {{{
        items = self.l_points.childItems()
        for item in items:
            item.setVisible(value)

    # }}}
    def showShortLines(self, value: bool):  # {{{
        items = self.s_lines.childItems()
        for item in items:
            item.setVisible(value)

    # }}}
    def showMidLines(self, value: bool):  # {{{
        items = self.m_lines.childItems()
        for item in items:
            item.setVisible(value)

    # }}}
    def showLongLines(self, value: bool):  # {{{
        items = self.l_lines.childItems()
        for item in items:
            item.setVisible(value)

    # }}}
    def showShortSpeeds(self, value: bool):  # {{{
        items = self.s_speeds.childItems()
        for item in items:
            item.setVisible(value)

    # }}}
    def showMidSpeeds(self, value: bool):  # {{{
        items = self.m_speeds.childItems()
        for item in items:
            item.setVisible(value)

    # }}}
    def showLongSpeeds(self, value: bool):  # {{{
        items = self.l_speeds.childItems()
        for item in items:
            item.setVisible(value)

    # }}}

    def __createPoints(self, extr_list):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createPoints()")

        points = QtWidgets.QGraphicsItemGroup()
        for e in extr_list:
            shape = self.__createPointShape(e)
            points.addToGroup(shape)
        return points

    # }}}
    def __createPointShape(self, extr):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createPointShape()")

        # select size and color
        if extr.isLongterm():
            size = GShape.Size.BIG
            color = GShape.Color.VIOLET
        elif extr.isMidterm():
            size = GShape.Size.NORMAL
            color = GShape.Color.BLUE
        elif extr.isShortterm():
            size = GShape.Size.SMALL
            color = GShape.Color.CYAN

        # calc coordinate
        # (x, y)   - epos - точка экстремума на графике
        # (x0, y0) - spos - точка графической метки экстремума
        x0 = self.gchart.xFromDatetime(extr.dt)
        x = x0 + GBar.WIDTH / 2
        y = self.gchart.yFromPrice(extr.price)
        y0 = y * 0.98 if extr.isMax() else y * 1.02
        epos = QtCore.QPointF(x, y)
        spos = QtCore.QPointF(x0, y0)

        # create shape
        shape = GShape(GShape.Type.SQARE, size, color)
        shape.setPos(spos)
        shape.info["epos"] = epos
        shape.info["spos"] = spos
        shape.info["extr"] = extr

        return shape

    # }}}
    def __createLines(  # {{{
        self, points_group: QtWidgets.QGraphicsItemGroup, pen
    ):
        logger.debug(f"{self.__class__.__name__}.__createLines()")
        points = points_group.childItems()
        if len(points) < 2:
            return None

        lines = QtWidgets.QGraphicsItemGroup()
        i = 0
        while i < len(points) - 1:
            e1 = points[i].info["epos"]
            e2 = points[i + 1].info["epos"]
            l = QtWidgets.QGraphicsLineItem(e1.x(), e1.y(), e2.x(), e2.y())
            l.setPen(pen)
            lines.addToGroup(l)
            i += 1

        return lines

    # }}}
    def __createSpeedLabels(self, points_group):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createSpeedLabels()")

        points = points_group.childItems()
        if len(points) < 2:
            return None

        flags = QtWidgets.QGraphicsItem.GraphicsItemFlag
        glabels = QtWidgets.QGraphicsItemGroup()
        i = 0
        while i < len(points) - 1:
            e1 = points[i].info["extr"]
            e2 = points[i + 1].info["extr"]
            speed = ExtremumList.speedPercent(e1, e2)
            delta = ExtremumList.deltaPercent(e1, e2)

            e2_x = points[i + 1].info["spos"].x()
            e2_y = points[i + 1].info["spos"].y()
            y = e2_y * 0.98 if e2.isMax() else e2_y * 1.01
            label_pos = QtCore.QPointF(e2_x, y)

            label = QtWidgets.QLabel(f"{delta} / {speed}")
            label.setStyleSheet(Css.SPEED_LABEL)
            glabel = QtWidgets.QGraphicsProxyWidget()
            glabel.setWidget(label)
            glabel.setPos(label_pos)
            glabel.setFlag(flags.ItemIgnoresTransformations, True)
            glabels.addToGroup(glabel)

            i += 1

        return glabels

    # }}}
    def __createInside(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createInside()")

        inside_marks = QtWidgets.QGraphicsItemGroup()
        gbars = self.gchart.gbars
        for gbar in gbars:
            bar = gbar.bar
            if bar.isInside():
                shape = self.__createInsideShape(gbar)
                inside_marks.addToGroup(shape)

        return inside_marks

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

        outside_marks = QtWidgets.QGraphicsItemGroup()
        gbars = self.gchart.gbars
        for gbar in gbars:
            bar = gbar.bar
            if bar.isOutside():
                shape = self.__createOutsideShape(gbar)
                outside_marks.addToGroup(shape)

        return outside_marks

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
        gextr.showShortSpeeds(self.sspeed_checkbox.isChecked())
        gextr.showMidSpeeds(self.mspeed_checkbox.isChecked())
        gextr.showLongSpeeds(self.lspeed_checkbox.isChecked())

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
        self.sspeed_checkbox = QtWidgets.QCheckBox("Short-term speed")
        self.mspeed_checkbox = QtWidgets.QCheckBox("Mid-term speed")
        self.lspeed_checkbox = QtWidgets.QCheckBox("Long-term speed")

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
        vbox.addSpacing(20)

        vbox.addWidget(self.sspeed_checkbox)
        vbox.addWidget(self.mspeed_checkbox)
        vbox.addWidget(self.lspeed_checkbox)

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
        self.mline_checkbox.setChecked(True)
        self.lline_checkbox.setChecked(True)

        self.sspeed_checkbox.setChecked(False)
        self.mspeed_checkbox.setChecked(False)
        self.lspeed_checkbox.setChecked(False)

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
