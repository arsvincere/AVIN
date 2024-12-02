#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum
import sys

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin.analytic import ExtremumList
from avin.utils import logger
from gui.chart.gchart import GChart
from gui.custom import Icon, Theme, ToolButton


class Tree(QtWidgets.QTreeWidget):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0

    # }}}
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setSortingEnabled(True)
        self.sortByColumn(Tree.Column.Name, Qt.SortOrder.AscendingOrder)
        self.setColumnWidth(Tree.Column.Name, 250)
        self.setFont(Font.MONO)


# }}}


# }}}


class ExtremumHandler:  # {{{
    def __init__(self):  # {{{
        self.item = ExtremumItem(self)
        self.label = ExtremumLabel(self)
        self.settings = ExtremumSettings(self)
        self.indicator = ExtremumList
        self.graphics = ExtremumGraphics

    # }}}
    def createGItem(self, gchart):  # {{{
        logger.debug(f"{self.__class__.__name__}.createGItem()")
        graphics_item_group = self.graphics(gchart)
        return graphics_item_group

    # }}}
    def showSettings(self):  # {{{
        self.settings.exec()

    # }}}
    def getLabel(self):  # {{{
        return self.label


# }}}


# }}}
class ExtremumItem(QtWidgets.QTreeWidgetItem):  # {{{
    def __init__(self, handler, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.__handler = handler
        self.__config()

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.setCheckState(Tree.Column.Name, Qt.CheckState.Unchecked)
        self.setText(Tree.Column.Name, "Extremum")

    # }}}
    @property  # handler{{{
    def handler(self):
        return self.__handler


# }}}


# }}}
class ExtremumGraphics(QtWidgets.QGraphicsItemGroup):  # {{{
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

    """ Data index """
    EXTR_POS = 0
    SHAPE_POS = 1

    def __init__(self, gchart: GChart, parent=None):  # {{{
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)
        self.gchart = gchart
        self.elist = ExtremumList(self.gchart)
        self.s_points = self.__createPoints(self.elist.sterm)
        self.m_points = self.__createPoints(self.elist.mterm)
        self.l_points = self.__createPoints(self.elist.lterm)
        self.s_lines = self.__createLines(self.s_points, self.__SPEN)
        self.m_lines = self.__createLines(self.m_points, self.__MPEN)
        self.l_lines = self.__createLines(self.l_points, self.__LPEN)
        self.addToGroup(self.s_points)
        self.addToGroup(self.m_points)
        self.addToGroup(self.l_points)
        self.addToGroup(self.s_lines)
        self.addToGroup(self.m_lines)
        self.addToGroup(self.l_lines)

    # }}}
    def __createPoints(self, extr_list):  # {{{
        points = QtWidgets.QGraphicsItemGroup()
        for e in extr_list:
            shape = self.__createPointShape(e)
            points.addToGroup(shape)
        return points

    # }}}
    def __createPointShape(self, extr):  # {{{
        """
        (x, y)   - epos - точка экстремума на графике
        (x0, y0) - spos - точка начала QGraphicsEllipseItem, графической
                   метки экстремума
        """
        shape = QtWidgets.QGraphicsItemGroup()
        x0 = self.gchart.xFromDatetime(extr.dt)
        y = self.gchart.yFromPrice(extr.price)
        x = x0 + GBar.WIDTH / 2
        y0 = y * 0.98 if extr.isMax() else y * 1.02
        epos = QtCore.QPointF(x, y)
        spos = QtCore.QPointF(x0, y0)
        width = height = GBar.WIDTH
        shape.setData(ExtremumGraphics.EXTR_POS, epos)
        shape.setData(ExtremumGraphics.SHAPE_POS, spos)
        if extr.isLongterm():
            circle = QtWidgets.QGraphicsEllipseItem(x0, y0, width, height)
            circle.setPen(Theme.Chart.LONGTERM)
            circle.setBrush(Theme.Chart.LONGTERM)
            shape.addToGroup(circle)
        elif extr.isMidterm():
            circle = QtWidgets.QGraphicsEllipseItem(x0, y0, width, height)
            circle.setPen(Theme.Chart.MIDTERM)
            circle.setBrush(Theme.Chart.MIDTERM)
            shape.addToGroup(circle)
        else:
            # для short-term-extremum метку не рисуем
            pass
        return shape

    # }}}
    def __createLines(
        self, points_group: QtWidgets.QGraphicsItemGroup, pen
    ):  # {{{
        lines = QtWidgets.QGraphicsItemGroup()
        points = points_group.childItems()
        if len(points) < 2:
            return
        i = 0
        while i < len(points) - 1:
            e1 = points[i].data(ExtremumGraphics.EXTR_POS)
            e2 = points[i + 1].data(ExtremumGraphics.EXTR_POS)
            l = QtWidgets.QGraphicsLineItem(e1.x(), e1.y(), e2.x(), e2.y())
            l.setPen(pen)
            lines.addToGroup(l)
            i += 1
        return lines


# }}}


# }}}
class ExtremumLabel(QtWidgets.QWidget):  # {{{
    def __init__(self, handler, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__handler = handler
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.label_name = QtWidgets.QLabel("Extremum")
        self.btn_hide = ToolButton(Icon.HIDE)
        self.btn_settings = ToolButton(Icon.CONFIG)
        self.btn_delete = ToolButton(Icon.DELETE)
        self.btn_other = ToolButton(Icon.OTHER)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        hbox = QtWidgets.QHBoxLayout(self)
        hbox.addWidget(self.label_name)
        hbox.addWidget(self.btn_hide)
        hbox.addWidget(self.btn_settings)
        hbox.addWidget(self.btn_delete)
        hbox.addWidget(self.btn_other)
        hbox.addStretch()
        hbox.setContentsMargins(0, 0, 0, 0)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.btn_settings.clicked.connect(self.__onSettings)

    # }}}
    @QtCore.pyqtSlot()  # __onSettings{{{
    def __onSettings(self):
        logger.debug(f"{self.__class__.__name__}.__onSettings()")
        self.handler.showSettings()

    # }}}
    def mousePressEventtt(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.mousePressEvent()")
        self.__onSettings()  # TODO: сделать нормальную кликабельную кнопку
        # даже если надо будет не виджеты делать а график итем груп
        # для каждого индикатора

    # }}}
    @property  # handler{{{
    def handler(self):
        return self.__handler


# }}}


# }}}
class ExtremumSettings(QtWidgets.QDialog):  # {{{
    def __init__(self, handler, parent=None):  # {{{
        QtWidgets.QDialog.__init__(self, parent)
        self.__handler = handler
        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    # }}}
    def __createWidgets(self):  # {{{
        self.__message_label = QtWidgets.QLabel()
        self.checkbox_inside = QtWidgets.QCheckBox("Inside days")
        self.checkbox_outside = QtWidgets.QCheckBox("Outside days")
        self.checkbox_sterm = QtWidgets.QCheckBox("Short-term extremum")
        self.checkbox_mterm = QtWidgets.QCheckBox("Mid-term extremum")
        self.checkbox_lterm = QtWidgets.QCheckBox("Long-term extremum")
        self.btn_apply = ToolButton(Icon.OK)
        self.btn_cancel = ToolButton(Icon.CANCEL)

    # }}}
    def __createLayots(self):  # {{{
        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(self.btn_apply)
        btn_box.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(btn_box)
        vbox.addWidget(self.checkbox_inside)
        vbox.addWidget(self.checkbox_outside)
        vbox.addWidget(self.checkbox_sterm)
        vbox.addWidget(self.checkbox_mterm)
        vbox.addWidget(self.checkbox_lterm)

    # }}}
    def __config(self):  # {{{
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    # }}}
    def __connect(self):  # {{{
        self.btn_apply.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    # }}}
    # def confirm(self, message):{{{
    #     self.__message_label.setText(message)
    #     result = self.exec()
    #     if result == QtWidgets.QDialog.DialogCode.Accepted:
    #         return True
    #     else:
    #         return False
    # }}}
    @property  # handler{{{
    def handler(self):
        return self.__handler


# }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ChartWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
