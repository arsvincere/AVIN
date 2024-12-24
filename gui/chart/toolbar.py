#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from PyQt6 import QtCore, QtGui, QtWidgets

from avin.core import Asset, TimeFrame, TimeFrameList
from avin.utils import DateTime, logger
from gui.chart.dialog_period import ChartPeriodDialog
from gui.chart.gchart import ViewType
from gui.custom import (
    Css,
    Icon,
    Label,
    Menu,
    ToolButton,
    VLine,
)
from gui.marker import MarkerWidget, MarkList


class ChartToolBar(QtWidgets.QToolBar):  # {{{
    firstTimeFrameChanged = QtCore.pyqtSignal(TimeFrame)
    secondTimeFrameChanged = QtCore.pyqtSignal(TimeFrame, bool)
    barViewSelected = QtCore.pyqtSignal()
    cundleViewSelected = QtCore.pyqtSignal()
    markListChanged = QtCore.pyqtSignal(MarkList)
    periodChanged = QtCore.pyqtSignal(DateTime, DateTime)

    __ICON_SIZE = QtCore.QSize(32, 32)

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)

        self.__config()
        self.__createButtons()
        self.__createMenus()
        self.__connect()

        self.__marker_widget = None

    # }}}

    def firstTimeFrame(self) -> TimeFrame:  # {{{
        logger.debug(f"{self.__class__.__name__}.firstTimeFrame()")

        text = self.__first_tf_btn.text()
        timeframe = TimeFrame(text)
        return timeframe

    # }}}
    def setFirstTimeFrame(self, timeframe: TimeFrame) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setFirstTimeFrame()")

        self.__first_tf_btn.setText(str(timeframe))

    # }}}
    def secondTimeFrames(self) -> TimeFrameList:  # {{{
        logger.debug(f"{self.__class__.__name__}.secondTimeFrames()")

        # TODO: it
        assert False

    # }}}
    def resetSecondTimeFrames(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.resetSecondTimeFrames()")

        self.__second_1H.setChecked(False)
        self.__second_D.setChecked(False)
        self.__second_W.setChecked(False)
        self.__second_M.setChecked(False)

    # }}}
    def setAsset(self, asset: Asset | None) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setAsset()")

        if asset is None:
            self.__asset_btn.setText("ASSET")
            return

        self.__asset_btn.setText(asset.ticker)

    # }}}

    def __createButtons(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        # asset
        self.__asset_btn = ToolButton(text="ASSET", width=64, parent=self)
        self.__current_asset = None

        # first timeframe
        self.__first_tf_btn = ToolButton(text="D", parent=self)

        # back timeframe
        self.__second_1H = ToolButton(text="1H", parent=self)
        self.__second_D = ToolButton(text="D", parent=self)
        self.__second_W = ToolButton(text="W", parent=self)
        self.__second_M = ToolButton(text="M", parent=self)
        self.__second_1H.setCheckable(True)
        self.__second_D.setCheckable(True)
        self.__second_W.setCheckable(True)
        self.__second_M.setCheckable(True)

        # bar / cundle
        self.__bar_btn = ToolButton(icon=Icon.BAR, parent=self)
        self.__bar_btn.setCheckable(True)
        self.__bar_btn.setChecked(True)
        self.__cundle_btn = ToolButton(icon=Icon.CUNDLE, parent=self)
        self.__cundle_btn.setCheckable(True)
        self.__current_view = ViewType.BAR

        # indicator
        self.__indicator_btn = ToolButton(
            text="Indicator", width=96, parent=self
        )

        # marker
        self.__marker_btn = ToolButton(text="Marker", width=70, parent=self)
        self.__marker_btn.setCheckable(True)

        # period
        self.__period_btn = ToolButton(text="Period", width=70, parent=self)
        self.__period_dialog = None

        # add widgets
        self.addWidget(self.__asset_btn)
        self.addWidget(self.__first_tf_btn)
        self.addWidget(VLine(width=10))
        self.addWidget(Label(" Background:", self))
        self.addWidget(self.__second_1H)
        self.addWidget(self.__second_D)
        self.addWidget(self.__second_W)
        self.addWidget(self.__second_M)
        self.addWidget(VLine(width=10))
        self.addWidget(self.__bar_btn)
        self.addWidget(self.__cundle_btn)
        self.addWidget(VLine(width=10))
        self.addWidget(self.__indicator_btn)
        self.addWidget(self.__marker_btn)
        self.addWidget(self.__period_btn)

    # }}}
    def __createMenus(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenus()")

        self.__first_tf_menu = _FirstTFMenu(parent=self)
        self.__first_tf_btn.setMenu(self.__first_tf_menu)
        self.__first_tf_btn.setPopupMode(
            QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup
        )

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setIconSize(self.__ICON_SIZE)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(Css.TOOL_BAR)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__first_tf_menu.triggered.connect(self.__onFirstTF)
        self.__second_1H.clicked.connect(self.__onSecond_1H)
        self.__second_D.clicked.connect(self.__onSecond_D)
        self.__second_W.clicked.connect(self.__onSecond_W)
        self.__second_M.clicked.connect(self.__onSecond_M)
        self.__bar_btn.clicked.connect(self.__onBarBtn)
        self.__cundle_btn.clicked.connect(self.__onCundleBtn)
        self.__marker_btn.clicked.connect(self.__onMarkerBtn)
        self.__period_btn.clicked.connect(self.__onPeriodBtn)

    # }}}

    @QtCore.pyqtSlot(QtGui.QAction)  # __onFirstTF  # {{{
    def __onFirstTF(self, action: QtGui.QAction):
        logger.debug(f"{self.__class__.__name__}.__onFirstTF()")

        timeframe = action.data()
        if self.__first_tf_btn.text() != str(timeframe):
            self.__first_tf_btn.setText(str(timeframe))
            self.firstTimeFrameChanged.emit(timeframe)

    # }}}
    @QtCore.pyqtSlot(bool)  # __onSecond_1H  # {{{
    def __onSecond_1H(self, checked: bool):
        logger.debug(f"{self.__class__.__name__}.__onSecond_1H()")

        self.secondTimeFrameChanged.emit(TimeFrame("1H"), checked)

    # }}}
    @QtCore.pyqtSlot(bool)  # __onSecond_D  # {{{
    def __onSecond_D(self, checked: bool):
        logger.debug(f"{self.__class__.__name__}.__onSecond_D()")

        self.secondTimeFrameChanged.emit(TimeFrame("D"), checked)

    # }}}
    @QtCore.pyqtSlot(bool)  # __onSecond_W  # {{{
    def __onSecond_W(self, checked: bool):
        logger.debug(f"{self.__class__.__name__}.__onSecond_W()")

        self.secondTimeFrameChanged.emit(TimeFrame("W"), checked)

    # }}}
    @QtCore.pyqtSlot(bool)  # __onSecond_M  # {{{
    def __onSecond_M(self, checked: bool):
        logger.debug(f"{self.__class__.__name__}.__onSecond_M()")

        self.secondTimeFrameChanged.emit(TimeFrame("M"), checked)

    # }}}
    @QtCore.pyqtSlot()  # __onBarBtn  # {{{
    def __onBarBtn(self):
        logger.debug(f"{self.__class__.__name__}.__onBarBtn()")

        if self.__current_view == ViewType.BAR:
            return

        self.__current_view = ViewType.BAR
        self.__bar_btn.setChecked(True)
        self.__cundle_btn.setChecked(False)

        self.barViewSelected.emit()

    # }}}
    @QtCore.pyqtSlot()  # __onCundleBtn  # {{{
    def __onCundleBtn(self):
        logger.debug(f"{self.__class__.__name__}.__onCundleBtn()")

        if self.__current_view == ViewType.CUNDLE:
            return

        self.__current_view = ViewType.CUNDLE
        self.__cundle_btn.setChecked(True)
        self.__bar_btn.setChecked(False)

        self.cundleViewSelected.emit()

    # }}}
    @QtCore.pyqtSlot()  # __onMarkerBtn  # {{{
    def __onMarkerBtn(self):
        logger.debug(f"{self.__class__.__name__}.__onMarkerBtn()")

        if self.__marker_widget is None:
            self.__marker_widget = MarkerWidget()

        mark_list = self.__marker_widget.selectMarks()
        if mark_list is not None:
            self.markListChanged.emit(mark_list)

    # }}}
    @QtCore.pyqtSlot()  # __onPeriodBtn  # {{{
    def __onPeriodBtn(self):
        logger.debug(f"{self.__class__.__name__}.__onPeriodBtn()")

        if self.__period_dialog is None:
            self.__period_dialog = ChartPeriodDialog()

        begin, end = self.__period_dialog.selectPeriod()
        if begin and end:
            self.periodChanged.emit(begin, end)

    # }}}


# }}}


class _FirstTFMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init()")
        Menu.__init__(self, parent=parent)

        self.__config()
        self.__createActions()

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setFixedWidth(64)

    # }}}
    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        self.t_1M = QtGui.QAction("1M", self)
        self.t_5M = QtGui.QAction("5M", self)
        self.t_10M = QtGui.QAction("10M", self)
        self.t_1H = QtGui.QAction("1H", self)
        self.t_D = QtGui.QAction("D", self)
        self.t_W = QtGui.QAction("W", self)
        self.t_M = QtGui.QAction("M", self)

        self.t_1M.setData(TimeFrame("1M"))
        self.t_5M.setData(TimeFrame("5M"))
        self.t_10M.setData(TimeFrame("10M"))
        self.t_1H.setData(TimeFrame("1H"))
        self.t_D.setData(TimeFrame("D"))
        self.t_W.setData(TimeFrame("W"))
        self.t_M.setData(TimeFrame("M"))

        self.addAction(self.t_1M)
        self.addAction(self.t_5M)
        self.addAction(self.t_10M)
        self.addAction(self.t_1H)
        self.addAction(self.t_D)
        self.addAction(self.t_W)
        self.addAction(self.t_M)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    w = ChartToolBar()
    w.setWindowTitle("AVIN")
    w.show()
    app.exec()
