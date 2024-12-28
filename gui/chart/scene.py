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
        self.__createGraphicsWidgets()
        self.__createChartGroup()
        self.__createTListGroup()
        self.__createIgnoreScaleList()

    # }}}

    def mouseMoveEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.mouseMoveEvent()")
        # super().mouseMoveEvent(e)

        if not self.__has_chart:
            return e.ignore()

        bar = self.gchart.gbarOnX(e.scenePos().x())
        if not bar:
            return e.ignore()

        self.bar_info.set(bar)
        self.vol_info.set(bar)

        return e.ignore()

    # }}}
    # def mousePressEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent):  # {{{
    #     logger.debug(f"{self.__class__.__name__}.mousePressEvent()")
    #     super().mousePressEvent(e)
    #
    #     return e.ignore()
    #
    # # }}}
    # def mouseReleaseEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent):  # {{{
    #     logger.debug(f"{self.__class__.__name__}.mouseReleaseEvent()")
    #     super().mouseReleaseEvent(e)
    #
    #     return e.ignore()
    #
    # # }}}
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
    def removeGChart(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.removeGChart()")

        if self.__has_chart:
            self.removeItem(self.gchart)
            self.__has_chart = False

    # }}}
    def currentGChart(self) -> GChart:  # {{{
        logger.debug(f"{self.__class__.__name__}.currentChart()")

        return self.gchart

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
    def removeGTrades(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.removeGTrades()")

        if self.__has_gtrades:
            self.removeItem(self.gtrades)
            self.__has_gtrades = False

    # }}}

    def setIndList(self, ind_list) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setIndList()")

        for i in ind_list:
            label = i.label()
            self.labels.widget().add(label)

    # }}}
    def removeIndicators(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.removeIndicators()")

        # пересоздаем график виджеты в левом верхнем углу
        self.__createGraphicsWidgets()

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
    def __createGraphicsWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createGraphicsWidgets()")

        # create widgets
        self.bar_info = BarInfo()
        self.vol_info = VolumeInfo()

        # create QtWidgets.QGraphicsProxyWidget
        self.labels = self.addWidget(ChartLabels())

        # add
        self.labels.widget().add(self.bar_info)
        self.labels.widget().add(self.vol_info)

        ####
        # TODO: del it, debug...
        from gui.indicator.extremum import (
            ExtremumIndicator,
            _ExtremumGraphicsLabel,
        )

        ind = ExtremumIndicator
        lbl = _ExtremumGraphicsLabel(ind)
        self.addItem(lbl)
        ####

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
    def __createIgnoreScaleList(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createIgnoreScaleList()")

        # TODO: Ахтунг! Оказывается есть специальный флаг для QGraphicsItem
        # QGraphicsItem::ItemIgnoresTransformations
        # почитай еще раз доку и переделай свой велосипед с трансформацией
        self.ignore_scale = list()

    # }}}


if __name__ == "__main__":
    ...
