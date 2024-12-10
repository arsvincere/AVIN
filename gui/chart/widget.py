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
        self.__initUI()

    # }}}

    def setAsset(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setAsset()")

        timeframe = self.toolbar.firstTimeFrame()
        end = now()
        begin = now() - timeframe * Chart.DEFAULT_BARS_COUNT
        chart = Thread.loadChart(asset, timeframe, begin, end)
        gchart = GChart(chart)

        self.scene.setGChart(gchart)
        self.view.centerOnLast()

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

    # }}}
    def __initUI(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")

    # }}}
    def __readBeginDate(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__readBeginDate()")

    # }}}
    def __readEndDate(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__readEndDate()")

    # }}}
    def __setBegin(self, dt):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setBegin()")

    # }}}
    def __setEnd(self, dt):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setEnd()")

    # }}}
    def __setTimeframe1(self, timeframe):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setTimeframe1()")
        assert isinstance(timeframe, TimeFrame)

    # }}}
    def __setTimeframe2(self, timeframe):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setTimeframe2()")
        assert isinstance(timeframe, TimeFrame)

    # }}}

    @QtCore.pyqtSlot()  # __onButtonAsset{{{
    def __onButtonAsset(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonAsset()")

    # }}}
    @QtCore.pyqtSlot()  # __onButtonIndicator{{{
    def __onButtonIndicator(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonIndicator()")

        # indicators = self.indicator_dial.chooseIndicator()
        # current_chart = self.scene.currentChart()
        # if indicators and current_chart:
        #     for i in indicators:
        #         gindicator = i.createGItem(current_chart)
        #         self.scene.addIndicator(gindicator)

    # }}}
    @QtCore.pyqtSlot()  # __onButtonMark{{{
    def __onButtonMark(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonMark()")

    # }}}
    @QtCore.pyqtSlot()  # __onTimeframe1Changed{{{
    def __onTimeframe1Changed(self):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe1Changed()")

    # }}}
    @QtCore.pyqtSlot()  # __onTimeframe2Changed{{{
    def __onTimeframe2Changed(self):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe2Changed()")

    # }}}
    @QtCore.pyqtSlot()  # __onBeginDateChanged{{{
    def __onBeginDateChanged(self):
        logger.debug(f"{self.__class__.__name__}.__onBeginDateChanged()")

    # }}}
    @QtCore.pyqtSlot()  # __onEndDateChanged{{{
    def __onEndDateChanged(self):
        logger.debug(f"{self.__class__.__name__}.__onEndDateChanged()")

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ChartWidget()
    w.show()
    sys.exit(app.exec())
