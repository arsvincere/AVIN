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
from avin.tester import Test
from avin.utils import DateTime, logger, now
from gui.chart.gchart import GChart, ViewType
from gui.chart.gtest import GTradeList
from gui.chart.scene import ChartScene
from gui.chart.thread import Thread
from gui.chart.toolbar import ChartToolBar
from gui.chart.view import ChartView
from gui.custom import Css
from gui.marker import GMarker


class ChartWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

        self.__asset = None
        self.__trade_list = None
        self.__markers: list[GMarker] = list()

    # }}}

    def setAsset(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setAsset()")

        self.clearAll()
        self.__asset = asset
        self.toolbar.setAsset(asset)
        self.__drawChart()

    # }}}
    def setTradeList(self, trade_list: TradeList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setTradeList()")

        self.clearAll()
        self.__trade_list = trade_list
        self.__drawTradeList()

    # }}}
    def showTrade(self, trade: Trade) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.showTrade()")

        self.view.centerOnTrade(trade)

    # }}}
    def clearAll(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clearAll()")

        self.scene.removeGChart()
        self.scene.removeGTrades()
        # self.scene.removeIndicator()
        # self.scene.removeMark()
        self.view.resetTransform()

        self.__trade_list = None
        self.__asset = None
        self.__markers: list[GMarker] = list()
        self.toolbar.setAsset(None)
        self.toolbar.setFirstTimeFrame(TimeFrame("D"))
        self.toolbar.resetSecondTimeFrames()

    # }}}

    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("AVIN")
        self.setStyleSheet(Css.STYLE)

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.toolbar = ChartToolBar(self)
        self.view = ChartView(self)
        self.scene = ChartScene(self)

        self.view.setScene(self.scene)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.view)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.toolbar.firstTimeFrameChanged.connect(self.__onTimeframe1)
        self.toolbar.secondTimeFrameChanged.connect(self.__onTimeframe2)
        self.toolbar.barViewSelected.connect(self.__onBarView)
        self.toolbar.cundleViewSelected.connect(self.__onCundleView)
        self.toolbar.newGMarker.connect(self.__onNewGMarker)
        self.toolbar.periodChanged.connect(self.__onPeriod)

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
    def __drawTradeList(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawTradeList()")

        trade_list = self.__trade_list
        test = trade_list.owner
        assert isinstance(test, Test)
        asset = test.asset
        timeframe = self.toolbar.firstTimeFrame()
        gtrade_list = GTradeList.fromSelected(test, trade_list, timeframe)

        self.toolbar.resetSecondTimeFrames()
        self.toolbar.setAsset(asset)
        self.scene.setGTradeList(gtrade_list)
        self.view.centerOnFirst()

        self.__asset = asset

    # }}}

    @QtCore.pyqtSlot(TimeFrame)  # __onTimeframe1  # {{{
    def __onTimeframe1(self, timeframe: TimeFrame):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe1()")

        if self.__trade_list is not None:
            self.__drawTradeList()
            return

        if self.__asset is not None:
            self.__drawChart()
            return

    # }}}
    @QtCore.pyqtSlot(TimeFrame, bool)  # __onTimeframe2  # {{{
    def __onTimeframe2(self, timeframe: TimeFrame, endbled: bool):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe2()")

        gchart = self.scene.currentGChart()
        if gchart is None:
            return

        if endbled:
            gchart.drawBack(timeframe)
        else:
            gchart.clearBack(timeframe)

    # }}}
    @QtCore.pyqtSlot()  # __onBarView  # {{{
    def __onBarView(self):
        logger.debug(f"{self.__class__.__name__}.__onBarView()")

        gchart = self.scene.currentGChart()
        if gchart is None:
            return

        gchart.setViewType(ViewType.BAR)

    # }}}
    @QtCore.pyqtSlot()  # __onCundleView  # {{{
    def __onCundleView(self):
        logger.debug(f"{self.__class__.__name__}.__onCundleView()")

        gchart = self.scene.currentGChart()
        if gchart is None:
            return

        gchart.setViewType(ViewType.CUNDLE)

    # }}}
    @QtCore.pyqtSlot(GMarker)  # __onNewGMarker  # {{{
    def __onNewGMarker(self, marker: GMarker):
        logger.debug(f"{self.__class__.__name__}.__onNewGMarker()")

        if self.__asset is None:
            return

        self.__markers.append(marker)

        gchart = self.scene.currentGChart()
        gchart.addGMarker(marker)

    # }}}
    @QtCore.pyqtSlot(DateTime, DateTime)  # __onPeriod  # {{{
    def __onPeriod(self, begin: DateTime, end: DateTime):
        logger.debug(f"{self.__class__.__name__}.__onPeriod()")

        # NOTE:
        # если перерисовать трейд лист - трейды поедут по датам
        # пока эта функция особо не нужна для трейд листов
        # так что работать будет только если на виджете
        # отображается только график, установлен только ассет
        if self.__trade_list is not None:
            return
        if self.__asset is None:
            return

        timeframe = self.toolbar.firstTimeFrame()
        chart = Thread.loadChart(self.__asset, timeframe, begin, end)
        gchart = GChart(chart)

        self.scene.setGChart(gchart)
        self.view.centerOnLast()

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ChartWidget()
    w.show()
    sys.exit(app.exec())
