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
from avin.utils import logger, now
from gui.chart.gchart import GChart, ViewType
from gui.chart.gtest import GTradeList
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
        self.__tlist = None

    # }}}

    def setAsset(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setAsset()")

        self.__asset = asset
        self.toolbar.setAsset(asset)
        self.__drawChart()

    # }}}
    def setTradeList(self, tlist: TradeList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setTradeList()")

        # FIX: в базе остаются трейды со статусом INITIAL и тп
        # после тестера, надо сделать чтобы сама стратегия их
        # удаляла когда они не актуальны, а потом еще
        # тестер в конце теста подчищает все такое безобразие
        # и выдает какую то сводку, мол тест окончен, еще
        # столько то трейдов висело незавершенных - они выкинуты
        # или сложнее... INITIAL трейды тоже можно сохранять
        # но надо их корректно обрабатывать, у них нет result()
        # и тп...
        # Пока ставлю заглушку - пропускаю все трейды кроме CLOSED
        # tlist = tlist.selectStatus(Trade.Status.CLOSED)

        test = tlist.owner
        assert isinstance(test, Test)
        gtrade_list = GTradeList.fromSelected(test, tlist)
        asset = test.asset

        self.toolbar.setFirstTimeFrame(TimeFrame("D"))
        self.toolbar.resetSecondTimeFrames()

        self.scene.setGTradeList(gtrade_list)
        self.view.centerOnFirst()

        # FIX:
        # во первых надо сохранять то что сейчас активен GTradeList
        # чтобы работала смена таймфрейма
        # во вторых при создании GTradeList надо использовать
        # таймфрейм
        # возможно стоит в тест вообще вернуть таймфрейм
        # думать думать думать
        self.__tlist = tlist
        self.__asset = asset
        self.toolbar.setAsset(asset)

    # }}}
    def showTrade(self, trade: Trade):  # {{{
        logger.debug(f"{self.__class__.__name__}.showTrade()")

        self.view.centerOnTrade(trade)

    # }}}
    def clearAll(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.clearAll()")

        self.scene.removeGChart()
        self.scene.removeGTrades()
        # self.scene.removeIndicator()
        # self.scene.removeMark()
        self.view.resetTransform()

        self.__tlist = None
        self.__asset = None
        self.toolbar.setAsset(None)

    # }}}

    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("AVIN")
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
        self.toolbar.barViewSelected.connect(self.__onBarView)
        self.toolbar.cundleViewSelected.connect(self.__onCundleView)

    # }}}
    def __drawChart(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawChart()")

        timeframe = self.toolbar.firstTimeFrame()
        end = now()
        begin = now() - timeframe * Chart.DEFAULT_BARS_COUNT
        chart = Thread.loadChart(self.__asset, timeframe, begin, end)
        gchart = GChart(chart)

        self.scene.setGChart(gchart)
        self.view.centerOnLast()

    # }}}
    @QtCore.pyqtSlot(TimeFrame)  # __onTimeframe1  # {{{
    def __onTimeframe1(self, timeframe: TimeFrame):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe1()")

        if self.__asset is None:
            return

        self.__drawChart()

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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ChartWidget()
    w.show()
    sys.exit(app.exec())
