#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets

from avin.core import Asset, Chart, TimeFrame, Trade, TradeList
from avin.utils import logger, now
from gui.chart.gchart import GChart
from gui.chart.scene import ChartScene
from gui.chart.thread import Thread
from gui.chart.toolbar import ChartToolBar
from gui.chart.view import ChartView
from gui.custom import Css


class ChartWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

        self.__asset = None

    # }}}

    def setAsset(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setAsset()")

        self.__asset = asset
        self.__drawChart()

    # }}}
    def setTradeList(self, tlist: TradeList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setTradeList()")

        # if itlist.asset is None:
        #     self.scene.removeGTradeList()
        #     return
        #
        # gtlist = GTradeList(itlist)
        # self.__setTimeframe1(TimeFrame("D"))
        # self.__setTimeframe2(TimeFrame("5M"))
        # self.__setBegin(gtlist.begin)
        # self.__setEnd(gtlist.end)
        #
        # self.scene.setGTradeList(gtlist)
        # self.view.centerOnFirst()

    # }}}
    def showTrade(self, trade: Trade):  # {{{
        logger.debug(f"{self.__class__.__name__}.showTrade()")

        # gtrade = itrade.gtrade
        # if gtrade:
        #     self.view.centerOnTrade(gtrade)

    # }}}
    def clearAll(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.clearAll()")

        self.scene.removeChart()
        self.scene.removeTradeList()
        self.scene.removeIndicator()
        self.scene.removeMark()
        self.view.resetTransform()

    # }}}

    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("AVIN  -  Ars  Vincere")
        self.setStyleSheet(Css.STYLE)

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.toolbar = ChartToolBar(self)
        self.view = ChartView(self)
        self.scene = ChartScene(self)
        self.view.setScene(self.scene)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.view)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.toolbar.firstTimeFrameChanged.connect(self.__onTimeframe1)
        self.toolbar.secondTimeFrameChanged.connect(self.__onTimeframe2)

    # }}}
    def __drawChart(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawChart()")

        timeframe = self.toolbar.firstTimeFrame()
        end = now()
        begin = now() - timeframe * Chart.DEFAULT_BARS_COUNT
        chart = Thread.loadChart(self.__asset, timeframe, begin, end)
        gchart = GChart(chart)

        self.scene.setGChart(gchart)
        self.view.centerOnLast()

    # }}}

    @QtCore.pyqtSlot(TimeFrame)  # __onTimeframe1{{{
    def __onTimeframe1(self, timeframe: TimeFrame):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe1()")

        if self.__asset is None:
            return

        self.__drawChart()

    # }}}
    @QtCore.pyqtSlot(TimeFrame, bool)  # __onTimeframe2{{{
    def __onTimeframe2(self, timeframe: TimeFrame, endbled: bool):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe2()")

        gchart = self.scene.currentChart()
        if gchart is None:
            return

        if endbled:
            gchart.drawBack(timeframe)
        else:
            gchart.clearBack(timeframe)

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ChartWidget()
    w.show()
    sys.exit(app.exec())
