#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtWidgets

from avin.utils import logger
from gui.chart.gchart import GChart
from gui.chart.glabels import BarInfo, ChartLabels, VolumeInfo
from gui.chart.gtrade import GTradeList
from gui.custom import Theme
from gui.indicator.extremum import ExtremumHandler


class ChartScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsScene.__init__(self, parent)
        self.__config()
        self.__createWidgets()
        self.__createChartGroup()
        self.__createTListGroup()
        self.__createIndicatorGroup()

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setBackgroundBrush(Theme.Chart.BG)

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.labels = self.addWidget(ChartLabels())
        self.bar_info = BarInfo()
        self.vol_info = VolumeInfo()
        eh = ExtremumHandler()
        self.extr_label = eh.getLabel()
        self.labels.widget().add(self.bar_info)
        self.labels.widget().add(self.vol_info)
        self.labels.widget().add(self.extr_label)

    # }}}
    def __createChartGroup(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createChartGroup()")
        self.__has_chart = False
        self.gchart = None

    # }}}
    def __createTListGroup(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createTListGroup()")
        self.__has_gtlist = False
        self.gtlist = None

    # }}}
    def __createIndicatorGroup(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createIndicatorGroup()")
        self.indicators = QtWidgets.QGraphicsItemGroup()
        self.addItem(self.indicators)

    # }}}
    def mouseMoveEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent):  # {{{
        # print(e.pos())
        # print(e.scenePos())
        # print(e.screenPos())
        # print("l", e.lastPos())
        # print("l", e.lastScenePos())
        # print("l", e.lastScreenPos())
        # print("p", e.buttonDownPos(QtCore.Qt.MouseButton.LeftButton))
        # print("p", e.buttonDownScenePos(QtCore.Qt.MouseButton.LeftButton))
        # print("p", e.buttonDownScreenPos(QtCore.Qt.MouseButton.LeftButton))
        if not self.__has_chart:
            return e.ignore()
        bar = self.gchart.barAt(e.scenePos().x())
        if not bar:
            return e.ignore()
        self.bar_info.set(bar)
        self.vol_info.set(bar)
        return e.ignore()

    # }}}
    def mousePressEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent):  # {{{
        pos = e.scenePos()
        items = self.items(pos)
        for i in items:
            if isinstance(i, QtWidgets.QGraphicsProxyWidget):
                self.extr_label.mousePressEventtt()
        # return e.ignore()

    # }}}
    def mouseReleaseEvent(self, e):  # {{{
        view = self.views()[0]
        p = view.mapToScene(0, 0)
        self.labels.setPos(p)
        return e.ignore()

    # }}}
    def mouseDoubleClickEvent(self, e):  # {{{
        """
        загрузить новый график, именно за этот период (бар)
        стереть станый график.
        нарисовать главный график до выделенного бара
        нарисовать раскрытый бар
        продолжить рисовать главный график.
        """
        # if self.chart is None:
        #     return e.ignore()
        # n = self._nFromPos(e.scenePos())
        # bar_items = self.gchart.childItems()
        # zoom_bar = bar_items[n].bar
        # ID = self.chart.ID
        # begin = zoom_bar.dt
        # end = zoom_bar.dt + self.chart.timeframe
        # self.zoom_chart = Chart(ID, TimeFrame("5M"), begin, end)
        # ###
        # self.removeChart()
        # ###
        # scene_x0 = 0
        # n1 = self.chart.getBarsCount() - 1
        # n2 = self.zoom_chart.getBarsCount()
        # scene_x1 = (n1 + n2) * self.SCALE_X
        # scene_y0 = 0
        # scene_y1 = self.chart.highestHigh() * self.SCALE_Y
        # height = scene_y1 - scene_y0 #+ 2 * self.SCENE_INDENT
        # width = scene_x1 - scene_x0 #+ 2 * self.SCENE_INDENT
        # self.setSceneRect(0, 0, width, height)
        # ###
        # i = 0
        # for big_bar in self.chart:
        #     if big_bar.dt != zoom_bar.dt:
        #         bar_item = GraphicsBarItem(big_bar, i, self)
        #         self.gchart.addToGroup(bar_item)
        #         i += 1
        #     else:
        #         bar_item = GraphicsBarItem(big_bar, i, self)
        #         self.gchart.addToGroup(bar_item)
        #         i += 1
        #         for small_bar in self.zoom_chart:
        #             bar_item = GraphicsZoomBarItem(small_bar, i, self)
        #             self.gchart.addToGroup(bar_item)
        #             i += 1

    # }}}
    def setGChart(self, gchart: GChart):  # {{{
        logger.debug(f"{self.__class__.__name__}.setGChart()")
        self.removeGChart()
        self.setSceneRect(gchart.rect)
        self.addItem(gchart)
        self.gchart = gchart
        self.__has_chart = True
        return True

    # }}}
    def setGTradeList(self, gtlist: GTradeList):  # {{{
        logger.debug(f"{self.__class__.__name__}.setGTradeList()")
        self.removeGTradeList()
        self.gchart = gtlist.gchart
        self.gtlist = gtlist
        self.__has_chart = True
        self.__has_gtlist = True
        self.setSceneRect(self.gchart.rect)
        self.addItem(self.gchart)
        self.addItem(self.gtlist)

    # }}}
    def addIndicator(self, gi):  # {{{
        logger.debug(f"{self.__class__.__name__}.addIndicator()")
        self.indicators.addToGroup(gi)

    # }}}
    def removeGChart(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.removeGChart()")
        if self.__has_chart:
            self.removeItem(self.gchart)
            self.__has_chart = False

    # }}}
    def removeGTradeList(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.removeGTradeList()")
        if self.__has_chart:
            self.removeItem(self.gchart)
            self.__has_chart = False
        if self.__has_gtlist:
            self.removeItem(self.gtlist)
            self.__has_gtlist = False

    # }}}
    def currentChart(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.currentChart()")
        return self.gchart


# }}}


if __name__ == "__main__":
    ...
