#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys
from datetime import UTC, datetime

from PyQt6 import QtCore, QtWidgets

from avin.const import ONE_DAY
from avin.core import Asset, Chart, TimeFrame
from avin.utils import logger, now
from gui.chart.gchart import GChart
from gui.chart.scene import ChartScene
from gui.chart.thread import Thread
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
    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("AVIN  -  Ars  Vincere")
        self.setStyleSheet(Css.STYLE)

    # }}}
    def __createWidgets(self):  # {{{
        self.view = ChartView(self)
        self.scene = ChartScene(self)
        self.view.setScene(self.scene)
        self.btn_asset = QtWidgets.QPushButton("ASSET")
        self.combobox_timeframe1 = QtWidgets.QComboBox()
        self.combobox_timeframe2 = QtWidgets.QComboBox()
        self.dateedit_begin = QtWidgets.QDateEdit()
        self.dateedit_end = QtWidgets.QDateEdit(now().date())
        self.btn_indicator = QtWidgets.QPushButton("Indicator")
        self.btn_mark = QtWidgets.QPushButton("Mark")

    # }}}
    def __createLayots(self):  # {{{
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.btn_asset)
        hbox1.addWidget(self.combobox_timeframe1)
        hbox1.addWidget(self.combobox_timeframe2)
        hbox1.addWidget(self.dateedit_begin)
        hbox1.addWidget(QtWidgets.QLabel("-"))
        hbox1.addWidget(self.dateedit_end)
        hbox1.addWidget(self.btn_indicator)
        hbox1.addWidget(self.btn_mark)
        hbox1.addStretch()
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addLayout(hbox1)
        vbox.addWidget(self.view)
        self.setLayout(vbox)

    # }}}
    def __connect(self):  # {{{
        self.combobox_timeframe1.currentTextChanged.connect(
            self.__onTimeframe1Changed
        )
        self.combobox_timeframe2.currentTextChanged.connect(
            self.__onTimeframe2Changed
        )
        self.dateedit_begin.dateChanged.connect(self.__onBeginDateChanged)
        self.dateedit_end.dateChanged.connect(self.__onEndDateChanged)
        self.btn_asset.clicked.connect(self.__onButtonAsset)
        self.btn_indicator.clicked.connect(self.__onButtonIndicator)
        self.btn_mark.clicked.connect(self.__onButtonMark)

    # }}}
    def __initUI(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")

        for timeframe in TimeFrame.ALL:
            self.combobox_timeframe1.addItem(str(timeframe))
            self.combobox_timeframe2.addItem(str(timeframe))
        self.combobox_timeframe1.setCurrentIndex(4)
        self.combobox_timeframe2.setCurrentIndex(5)

        self.dateedit_begin.setMinimumDate(QtCore.QDate(2018, 1, 1))
        self.dateedit_begin.setMaximumDate(now().date() - ONE_DAY)

        self.dateedit_end.setMinimumDate(QtCore.QDate(2018, 1, 1))
        self.dateedit_end.setMaximumDate(now().date())

    # }}}
    def __readBeginDate(self):  # {{{
        date = self.dateedit_begin.date()
        year, month, day = date.year(), date.month(), date.day()
        return datetime(year, month, day, tzinfo=UTC)

    # }}}
    def __readEndDate(self):  # {{{
        date = self.dateedit_end.date()
        year, month, day = date.year(), date.month(), date.day()
        return datetime(year, month, day, tzinfo=UTC)

    # }}}
    def __readTimeframe1(self):  # {{{
        text = self.combobox_timeframe1.currentText()
        return TimeFrame(text)

    # }}}
    def __readTimeframe2(self):  # {{{
        text = self.combobox_timeframe2.currentText()
        return TimeFrame(text)

    # }}}
    def __setBegin(self, dt):  # {{{
        self.dateedit_begin.setDate(dt.date())

    # }}}
    def __setEnd(self, dt):  # {{{
        self.dateedit_end.setDate(dt.date())

    # }}}
    def __setTimeframe1(self, timeframe):  # {{{
        assert isinstance(timeframe, TimeFrame)
        self.combobox_timeframe1.setCurrentText(str(timeframe))

    # }}}
    def __setTimeframe2(self, timeframe):  # {{{
        assert isinstance(timeframe, TimeFrame)
        self.combobox_timeframe2.setCurrentText(str(timeframe))

    # }}}
    @QtCore.pyqtSlot()  # __onButtonAsset{{{
    def __onButtonAsset(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonAsset()")
        ...

    # }}}
    @QtCore.pyqtSlot()  # __onButtonIndicator{{{
    def __onButtonIndicator(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonIndicator()")
        indicators = self.indicator_dial.chooseIndicator()
        current_chart = self.scene.currentChart()
        if indicators and current_chart:
            for i in indicators:
                gindicator = i.createGItem(current_chart)
                self.scene.addIndicator(gindicator)

    # }}}
    @QtCore.pyqtSlot()  # __onButtonMark{{{
    def __onButtonMark(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonMark()")
        ...

    # }}}
    @QtCore.pyqtSlot()  # __onTimeframe1Changed{{{
    def __onTimeframe1Changed(self):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe1Changed()")
        text = self.combobox_timeframe1.currentText()
        self.__timeframe1 = TimeFrame(text)

    # }}}
    @QtCore.pyqtSlot()  # __onTimeframe2Changed{{{
    def __onTimeframe2Changed(self):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe2Changed()")
        text = self.combobox_timeframe2.currentText()
        self.__timeframe2 = TimeFrame(text)

    # }}}
    @QtCore.pyqtSlot()  # __onBeginDateChanged{{{
    def __onBeginDateChanged(self):
        logger.debug(f"{self.__class__.__name__}.__onBeginDateChanged()")
        ...

    # }}}
    @QtCore.pyqtSlot()  # __onEndDateChanged{{{
    def __onEndDateChanged(self):
        logger.debug(f"{self.__class__.__name__}.__onEndDateChanged()")
        ...

    # }}}
    def setAsset(self, asset: Asset):  # {{{
        logger.debug(f"{self.__class__.__name__}.setAsset()")

        timeframe = self.__readTimeframe1()
        end = now()
        begin = now() - timeframe * Chart.DEFAULT_BARS_COUNT
        chart = Thread.loadChart(asset, timeframe, begin, end)
        gchart = GChart(chart)

        self.scene.setGChart(gchart)
        self.view.centerOnLast()
        self.btn_asset.setText(asset.ticker)

    # }}}
    def showTradeList(self, itlist):  # {{{
        logger.debug(f"{self.__class__.__name__}.showTradeList()")
        if itlist.asset is None:
            self.scene.removeGTradeList()
            return
        gtlist = GTradeList(itlist)
        self.__setTimeframe1(TimeFrame("D"))
        self.__setTimeframe2(TimeFrame("5M"))
        self.__setBegin(gtlist.begin)
        self.__setEnd(gtlist.end)
        self.scene.setGTradeList(gtlist)
        self.view.centerOnFirst()

    # }}}
    def showTrade(self, itrade):  # {{{
        gtrade = itrade.gtrade
        if gtrade:
            self.view.centerOnTrade(gtrade)

    # }}}
    def clearAll(self):  # {{{
        logger.debug("ChartWidget.clearAll()")
        self.scene.removeChart()
        self.scene.removeTradeList()
        self.scene.removeIndicator()
        self.scene.removeMark()
        self.view.resetTransform()


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ChartWidget()
    w.show()
    sys.exit(app.exec())
