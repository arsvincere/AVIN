#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtCore, QtWidgets

from avin.utils import logger
from gui.chart.gchart import GChart
from gui.chart.glabels import BarInfo, ChartLabels, VolumeInfo
from gui.chart.gtest import GTradeList
from gui.custom import Theme


class ChartScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsScene.__init__(self, parent)

        self.__config()
        self.__createEmpyRect()
        self.__createWidgets()
        self.__createChartGroup()
        self.__createTListGroup()
        self.__createIndicatorGroup()
        self.__createIgnoreScaleList()

    # }}}

    def mouseMoveEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.mouseMoveEvent()")

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
        logger.debug(f"{self.__class__.__name__}.mousePressEvent()")

        pos = e.scenePos()
        items = self.items(pos)
        for i in items:
            if isinstance(i, QtWidgets.QGraphicsProxyWidget):
                self.extr_label.mousePressEventtt()

        return e.ignore()

    # }}}
    def mouseReleaseEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.mouseReleaseEvent()")

        return e.ignore()

    # }}}
    def mouseDoubleClickEvent(  # {{{
        self, e: QtWidgets.QGraphicsSceneMouseEvent
    ):
        logger.debug(f"{self.__class__.__name__}.mouseReleaseEvent()")
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

    def setGChart(self, gchart: GChart) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setGChart()")

        self.removeGChart()
        self.setSceneRect(gchart.rect)
        self.addItem(gchart)
        self.gchart = gchart
        self.__has_chart = True

    # }}}
    def currentGChart(self) -> GChart:  # {{{
        logger.debug(f"{self.__class__.__name__}.currentChart()")

        return self.gchart

    # }}}
    def removeGChart(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.removeGChart()")

        if self.__has_chart:
            self.removeItem(self.gchart)
            self.__has_chart = False

    # }}}

    def setGTradeList(self, gtrade_list: GTradeList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setGTradeList()")

        self.setGChart(gtrade_list.gchart)

        self.removeGTrades()
        self.gtrades = gtrade_list.gtrades
        self.addItem(self.gtrades)
        self.__has_gtrades = True

        # TODO: это порно код, подумай как лучше сделать
        view = self.views()[0]
        view.resetCurrentGTrade()

    # }}}
    def removeGTrades(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.removeGTrades()")

        if self.__has_gtrades:
            self.removeItem(self.gtrades)
            self.__has_gtrades = False

    # }}}

    def addIndicator(self, gi):  # {{{
        logger.debug(f"{self.__class__.__name__}.addIndicator()")

        # TODO: it
        assert False

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setBackgroundBrush(Theme.Chart.BG)

    # }}}
    def __createEmpyRect(self):  # {{{
        """Инициализируем сцену произвольным прямоугольником

        Просто для того чтобы потом scene.labels нормально в верхнем
        углу расположить.
        """
        logger.debug(f"{self.__class__.__name__}.__createEmpyRect()")

        rect = QtCore.QRectF(0, 0, 800, 600)
        self.setSceneRect(rect)

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        # create widgets
        self.bar_info = BarInfo()
        self.vol_info = VolumeInfo()

        # create QtWidgets.QGraphicsProxyWidget
        self.labels = self.addWidget(ChartLabels())

        # add
        self.labels.widget().add(self.bar_info)
        self.labels.widget().add(self.vol_info)

    # }}}
    def __createChartGroup(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createChartGroup()")

        self.__has_chart = False
        self.gchart = None

    # }}}
    def __createTListGroup(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createTListGroup()")

        self.__has_gtrades = False
        self.gtrades = None

    # }}}
    def __createIndicatorGroup(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createIndicatorGroup()")

        self.indicators = QtWidgets.QGraphicsItemGroup()
        self.addItem(self.indicators)

    # }}}
    def __createIgnoreScaleList(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createIgnoreScaleList()")

        self.ignore_scale = list()

    # }}}


if __name__ == "__main__":
    ...
