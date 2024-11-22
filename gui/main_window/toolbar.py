#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from gui.custom import Icon, Spacer


class LeftToolBar(QtWidgets.QToolBar):
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
        self.data = QtGui.QAction(Icon.DATA, "Data", self)
        self.asset = QtGui.QAction(Icon.LIST, "Asset", self)
        self.chart = QtGui.QAction(Icon.CHART, "Chart", self)
        self.strategy = QtGui.QAction(Icon.STRATEGY, "Strategy", self)
        self.test = QtGui.QAction(Icon.TEST, "Test", self)
        self.report = QtGui.QAction(Icon.REPORT, "Report", self)
        self.console = QtGui.QAction(Icon.CONSOLE, "Console", self)
        self.shutdown = QtGui.QAction(Icon.SHUTDOWN, "Shutdown", self)
        self.addAction(self.data)
        self.addAction(self.asset)
        self.addAction(self.chart)
        self.addAction(self.strategy)
        self.addAction(self.test)
        self.addAction(self.report)
        self.addAction(self.console)
        self.addWidget(Spacer(self))
        self.addAction(self.shutdown)

    # }}}
    def __configButtons(self):  # {{{
        self.widgetForAction(self.data).setCheckable(True)
        self.widgetForAction(self.asset).setCheckable(True)
        self.widgetForAction(self.chart).setCheckable(True)
        self.widgetForAction(self.strategy).setCheckable(True)
        self.widgetForAction(self.test).setCheckable(True)
        self.widgetForAction(self.report).setCheckable(True)
        self.widgetForAction(self.console).setCheckable(True)
        self.widgetForAction(self.shutdown).setCheckable(True)

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
