#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum

from PyQt6 import QtCore, QtGui, QtWidgets

from avin.core import TimeFrame
from avin.utils import logger
from gui.custom import (
    Css,
    Icon,
    Menu,
    ToolButton,
)


class ChartToolBar(QtWidgets.QToolBar):  # {{{
    firstTimeFrameChanged = QtCore.pyqtSignal(TimeFrame)
    secondTimeFrameChanged = QtCore.pyqtSignal(TimeFrame)
    barViewSelected = QtCore.pyqtSignal()
    cundleViewSelected = QtCore.pyqtSignal()

    __ICON_SIZE = QtCore.QSize(32, 32)

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)

        self.__config()
        self.__createButtons()
        self.__createMenus()
        self.__connect()

    # }}}

    def firstTimeFrame(self) -> TimeFrame:
        logger.debug(f"{self.__class__.__name__}.firstTimeFrame()")

        text = self.__first_tf_btn.text()
        timeframe = TimeFrame(text)
        return timeframe

    def secondTimeFrame(self) -> TimeFrame:
        logger.debug(f"{self.__class__.__name__}.secondTimeFrame()")

        text = self.__second_tf_btn.text()
        timeframe = TimeFrame(text)
        return timeframe

    def __createButtons(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        self.__asset_btn = ToolButton(text="ASSET", width=64, parent=self)
        self.__current_asset = None

        self.__first_tf_btn = ToolButton(parent=self)
        self.__first_tf_btn.setText("5M")
        self.__second_tf_btn = ToolButton(parent=self)
        self.__second_tf_btn.setText("D")

        self.__bar_btn = ToolButton(icon=Icon.BAR, parent=self)
        self.__bar_btn.setCheckable(True)
        self.__cundle_btn = ToolButton(icon=Icon.CUNDLE, parent=self)
        self.__cundle_btn.setCheckable(True)
        self.__cundle_btn.setChecked(True)
        self.__current_view = _ViewType.CUNDLE

        self.__indicator_btn = ToolButton(
            text="Indicator", width=96, parent=self
        )

        self.addWidget(self.__asset_btn)
        self.addWidget(self.__first_tf_btn)
        self.addWidget(self.__second_tf_btn)
        self.addWidget(self.__bar_btn)
        self.addWidget(self.__cundle_btn)
        self.addWidget(self.__indicator_btn)

    # }}}
    def __createMenus(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenus()")

        self.__first_tf_menu = _FirstTFMenu(parent=self)
        self.__first_tf_btn.setMenu(self.__first_tf_menu)
        self.__first_tf_btn.setPopupMode(
            QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup
        )

        self.__second_tf_menu = _SecondTFMenu(self)
        self.__second_tf_btn.setMenu(self.__second_tf_menu)
        self.__second_tf_btn.setPopupMode(
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
        self.__second_tf_menu.triggered.connect(self.__onSecondTF)
        self.__bar_btn.clicked.connect(self.__onBarBtn)
        self.__cundle_btn.clicked.connect(self.__onCundleBtn)

    # }}}

    @QtCore.pyqtSlot(QtGui.QAction)  # __onFirstTF  # {{{
    def __onFirstTF(self, action: QtGui.QAction):
        logger.debug(f"{self.__class__.__name__}.__onFirstTF()")

        timeframe = action.data()
        if self.__first_tf_btn.text() != str(timeframe):
            self.__first_tf_btn.setText(str(timeframe))
            self.firstTimeFrameChanged.emit(timeframe)

    # }}}
    @QtCore.pyqtSlot(QtGui.QAction)  # __onSecondTF  # {{{
    def __onSecondTF(self, action: QtGui.QAction):
        logger.debug(f"{self.__class__.__name__}.__onSecondTF()")

        timeframe = action.data()
        if self.__second_tf_btn.text() != str(timeframe):
            self.__second_tf_btn.setText(str(timeframe))
            self.secondTimeFrameChanged.emit(timeframe)

    # }}}
    @QtCore.pyqtSlot()  # __onBarBtn  # {{{
    def __onBarBtn(self):
        logger.debug(f"{self.__class__.__name__}.__onBarBtn()")

        if self.__current_view == _ViewType.BAR:
            return

        self.__current_view = _ViewType.BAR
        self.__bar_btn.setChecked(True)
        self.__cundle_btn.setChecked(False)

        self.barViewSelected.emit()

    # }}}
    @QtCore.pyqtSlot()  # __onCundleBtn  # {{{
    def __onCundleBtn(self):
        logger.debug(f"{self.__class__.__name__}.__onCundleBtn()")

        if self.__current_view == _ViewType.CUNDLE:
            return

        self.__current_view = _ViewType.CUNDLE
        self.__cundle_btn.setChecked(True)
        self.__bar_btn.setChecked(False)

        self.cundleViewSelected.emit()

    # }}}


# }}}


class _ViewType(enum.Enum):  # {{{
    BAR = 1
    CUNDLE = 2


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
class _SecondTFMenu(Menu):  # {{{
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

        self.t_1M.setCheckable(True)
        self.t_5M.setCheckable(True)
        self.t_10M.setCheckable(True)
        self.t_1H.setCheckable(True)
        self.t_D.setCheckable(True)
        self.t_W.setCheckable(True)
        self.t_M.setCheckable(True)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    w = ChartToolBar()
    w.setWindowTitle("AVIN")
    w.show()
    app.exec()
