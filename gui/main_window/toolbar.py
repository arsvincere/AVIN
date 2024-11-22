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
from gui.custom import Css, Icon, Spacer


class LeftToolBar(QtWidgets.QToolBar):
    __ICON_SIZE = QtCore.QSize(32, 32)

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)

        self.__config()
        self.__createActions()
        self.__configButtons()
        self.__connect()

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setIconSize(self.__ICON_SIZE)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(Css.STYLE)

    # }}}
    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        self.data = QtGui.QAction(Icon.DATA, "Data", self)
        self.asset = QtGui.QAction(Icon.LIST, "Asset", self)
        self.filter = QtGui.QAction(Icon.CHART, "Filter", self)
        self.analytic = QtGui.QAction(Icon.CHART, "Analytic", self)
        self.strategy = QtGui.QAction(Icon.STRATEGY, "Strategy", self)
        self.note = QtGui.QAction(Icon.NO, "Note", self)
        self.test = QtGui.QAction(Icon.TEST, "Test", self)
        self.summary = QtGui.QAction(Icon.SUMMARY, "Summary", self)

        self.console = QtGui.QAction(Icon.CONSOLE, "Console", self)
        self.config = QtGui.QAction(Icon.CONFIG, "Config", self)
        self.shutdown = QtGui.QAction(Icon.SHUTDOWN, "Shutdown", self)

        self.addAction(self.data)
        self.addAction(self.asset)
        self.addAction(self.filter)
        self.addAction(self.analytic)
        self.addAction(self.strategy)
        self.addAction(self.note)
        self.addAction(self.test)
        self.addAction(self.summary)

        # self.addWidget(Spacer(parent=self))
        self.addAction(self.console)
        self.addAction(self.config)
        self.addAction(self.shutdown)

    # }}}
    def __configButtons(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        for action in self.actions():
            btn = self.widgetForAction(action)
            btn.setCheckable(True)
            btn.setStyleSheet(Css.TOOL_BUTTON)

    # }}}
    def __connect(self):  # {{{
        self.actionTriggered.connect(self.__onTriggered)

    # }}}
    def __onTriggered(self, action: QtGui.QAction):  # {{{
        btn = self.widgetForAction(action)
        state = btn.isChecked()
        btn.setChecked(not state)


# }}}


class RightToolBar(QtWidgets.QToolBar):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)
        self.__config()
        self.__createActions()
        self.__configButtons()
        self.__connect()

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setIconSize(QtCore.QSize(32, 32))
        p = self.palette()
        p.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor("#484848"))
        self.setPalette(p)

    # }}}
    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.broker = QtGui.QAction(Icon.BROKER, "Broker", self)
        self.account = QtGui.QAction(Icon.ACCOUNT, "Account", self)
        self.order = QtGui.QAction(Icon.ORDER, "Order", self)
        self.analytic = QtGui.QAction(Icon.ANALYTIC, "Analytic", self)
        self.sandbox = QtGui.QAction(Icon.SANDBOX, "Sandbox", self)
        self.general = QtGui.QAction(Icon.GENERAL, "General", self)
        self.keeper = QtGui.QAction(Icon.KEEPER, "Keeper", self)
        self.addAction(self.broker)
        self.addAction(self.account)
        self.addAction(self.order)
        self.addAction(self.analytic)
        self.addAction(self.sandbox)
        self.addAction(self.general)
        self.addAction(self.keeper)

    # }}}
    def __configButtons(self):  # {{{
        for i in self.actions():
            self.widgetForAction(i).setCheckable(True)
        self.addWidget(Spacer(self))

    # }}}
    def __connect(self):  # {{{
        self.actionTriggered.connect(self.__onTriggered)

    # }}}
    def __onTriggered(self, action: QtGui.QAction):  # {{{
        btn = self.widgetForAction(action)
        state = btn.isChecked()
        btn.setChecked(not state)


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = LeftToolBar()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
