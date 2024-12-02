#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from avin.utils import logger
from gui.custom import Css, Icon


class LeftToolBar(QtWidgets.QToolBar):  # {{{
    __ICON_SIZE = QtCore.QSize(32, 32)

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, "Left Tool Bar", parent)

        self.__config()
        self.__createActions()
        self.__configButtons()
        self.__connect()

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setIconSize(self.__ICON_SIZE)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(Css.TOOL_BAR)

    # }}}
    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        self.data = QtGui.QAction(Icon.DATA, "Data", self)
        self.asset = QtGui.QAction(Icon.LIST, "Asset", self)
        self.note = QtGui.QAction(Icon.NOTE, "Note", self)
        self.analytic = QtGui.QAction(Icon.ANALYTIC, "Analytic", self)
        self.filter = QtGui.QAction(Icon.FILTER, "Filter", self)
        self.strategy = QtGui.QAction(Icon.STRATEGY, "Strategy", self)
        self.tester = QtGui.QAction(Icon.TESTER, "Tester", self)
        self.summary = QtGui.QAction(Icon.SUMMARY, "Summary", self)

        self.console = QtGui.QAction(Icon.CONSOLE, "Console", self)
        self.config = QtGui.QAction(Icon.CONFIG, "Config", self)
        self.shutdown = QtGui.QAction(Icon.SHUTDOWN, "Shutdown", self)

        self.addAction(self.data)
        self.addAction(self.asset)
        self.addAction(self.note)
        self.addAction(self.analytic)
        self.addAction(self.filter)
        self.addAction(self.strategy)
        self.addAction(self.tester)
        self.addAction(self.summary)

        # self.addWidget(Spacer(parent=self))
        self.addAction(self.console)
        self.addAction(self.config)
        self.addAction(self.shutdown)

    # }}}
    def __configButtons(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__configButtons()")

        for action in self.actions():
            btn = self.widgetForAction(action)
            btn.setCheckable(True)
            btn.setStyleSheet(Css.TOOL_BUTTON)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.actionTriggered.connect(self.__onTriggered)

    # }}}
    def __onTriggered(self, action: QtGui.QAction):  # {{{
        logger.debug(f"{self.__class__.__name__}.__onTriggered()")

        btn = self.widgetForAction(action)
        state = btn.isChecked()
        btn.setChecked(not state)

    # }}}


# }}}
class RightToolBar(QtWidgets.QToolBar):  # {{{
    __ICON_SIZE = QtCore.QSize(32, 32)

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, "Right Tool Bar", parent)

        self.__config()
        self.__createActions()
        self.__configButtons()
        self.__connect()

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setIconSize(self.__ICON_SIZE)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(Css.TOOL_BAR)

    # }}}
    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        self.broker = QtGui.QAction(Icon.BROKER, "Broker", self)
        self.chart = QtGui.QAction(Icon.CHART, "Chart", self)
        self.book = QtGui.QAction(Icon.CHART, "Book", self)
        self.tic = QtGui.QAction(Icon.CHART, "Tic", self)
        self.order = QtGui.QAction(Icon.ORDER, "Order", self)
        self.account = QtGui.QAction(Icon.ACCOUNT, "Account", self)
        self.trader = QtGui.QAction(Icon.TRADER, "Trader", self)
        self.report = QtGui.QAction(Icon.KEEPER, "Report", self)

        self.informer = QtGui.QAction(Icon.NO, "Informer", self)

        self.addAction(self.broker)
        self.addAction(self.chart)
        self.addAction(self.book)
        self.addAction(self.tic)
        self.addAction(self.order)
        self.addAction(self.account)
        self.addAction(self.trader)
        self.addAction(self.report)

        self.addAction(self.informer)

    # }}}
    def __configButtons(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__configButtons()")

        for action in self.actions():
            btn = self.widgetForAction(action)
            btn.setCheckable(True)
            btn.setStyleSheet(Css.TOOL_BUTTON)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.actionTriggered.connect(self.__onTriggered)

    # }}}
    def __onTriggered(self, action: QtGui.QAction):  # {{{
        logger.debug(f"{self.__class__.__name__}.__onTriggered()")

        btn = self.widgetForAction(action)
        state = btn.isChecked()
        btn.setChecked(not state)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = RightToolBar()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
