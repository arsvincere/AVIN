#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

"""Doc"""

import sys

sys.path.append("/usr/lib/python3.12/site-packages")
sys.path.append("/home/alex/.local/lib/python3.12/site-packages/tinkoff/")
sys.path.append("/home/alex/yandex/avin-dev/")
import logging

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin.core import Asset
from avin.gui.account import AccountWidget, IAccount
from avin.gui.asset import AssetWidget, IShare
from avin.gui.broker import BrokerWidget, ISandbox
from avin.gui.chart import ChartWidget
from avin.gui.console import ConsoleWidget
from avin.gui.custom import Icon, Palette, Spacer
from avin.gui.data import DataWidget
from avin.gui.general import GeneralWidget
from avin.gui.order_dialog import OrderDialog
from avin.gui.report import ReportWidget
from avin.gui.strategy import StrategyWidget
from avin.gui.test import ITrade, ITradeList, TestWidget

logger = logging.getLogger("LOGGER")


class ToolLeft(QtWidgets.QToolBar):
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


class ToolRight(QtWidgets.QToolBar):
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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):  # {{{
        QtWidgets.QMainWindow.__init__(self, parent)
        # self.__createMdiArea()
        # self.__configMdiArea()
        self.__createToolBar()
        self.__createLeftWidgets()
        self.__createCenterWidgets()
        self.__createRightWidgets()
        self.__createSplitter()
        self.__setWidgetSize()
        self.__connect()
        self.__config()
        self.__initUI()

    # }}}
    # def __createMdiArea(self):{{{
    #     self.area = QtWidgets.QMdiArea(self)
    #     self.tab1 = QtWidgets.QMdiSubWindow(self.area)
    #     self.tab2 = QtWidgets.QMdiSubWindow(self.area)
    #     self.tab3 = QtWidgets.QMdiSubWindow(self.area)
    #     self.tab4 = QtWidgets.QMdiSubWindow(self.area)
    #     self.tab5 = QtWidgets.QMdiSubWindow(self.area)
    #     self.area.addSubWindow(self.tab1)
    #     self.area.addSubWindow(self.tab2)
    #     self.area.addSubWindow(self.tab3)
    #     self.area.addSubWindow(self.tab4)
    #     self.area.addSubWindow(self.tab5)
    #     self.tab1.setWindowTitle("Tester")
    #     self.tab2.setWindowTitle("Sandbox")
    #     self.tab3.setWindowTitle("General")
    #     self.tab4.setWindowTitle("Terminal")
    #     self.tab5.setWindowTitle("Documentation")
    #
    # def __configMdiArea(self):
    #     self.area.setViewMode(QtWidgets.QMdiArea.ViewMode.TabbedView)
    #     self.area.setTabsMovable(True)
    #     self.area.setTabsClosable(False)
    #     self.area.setActiveSubWindow(self.tab1)
    #
    def __createToolBar(self):
        self.ltool = ToolLeft(self)
        self.ltool.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.ltool)
        self.rtool = ToolRight(self)
        self.rtool.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.rtool)

    # }}}
    def __createLeftWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLeftWidgets()")
        self.widget_data = DataWidget(self)
        self.widget_data.hide()
        self.widget_asset = AssetWidget(self)
        self.widget_asset.hide()
        self.widget_strategy = StrategyWidget(self)
        self.widget_strategy.hide()
        self.widget_test = TestWidget(self)
        self.widget_test.hide()

    # }}}
    def __createCenterWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createCenterWidgets()")
        self.widget_chart = ChartWidget(self)
        self.widget_chart.hide()
        self.widget_report = ReportWidget(self)
        self.widget_report.hide()
        self.widget_console = ConsoleWidget(self)
        self.widget_console.hide()
        self.widget_account = AccountWidget(self)
        self.widget_account.hide()

    # }}}
    def __createRightWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createRightWidgets()")
        self.widget_broker = BrokerWidget(self)
        self.widget_broker.hide()
        self.widget_order = OrderDialog(self)
        self.widget_order.hide()
        self.widget_general = GeneralWidget(self)
        self.widget_general.hide()

    # }}}
    def __createSplitter(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createSplitter()")
        # left
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.widget_data)
        self.splitter.addWidget(self.widget_asset)
        self.splitter.addWidget(self.widget_strategy)
        self.splitter.addWidget(self.widget_test)
        # center
        self.vsplit = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.vsplit.addWidget(self.widget_chart)
        self.vsplit.addWidget(self.widget_account)
        self.vsplit.addWidget(self.widget_report)
        self.vsplit.addWidget(self.widget_console)
        self.splitter.addWidget(self.vsplit)
        # right
        self.splitter.addWidget(self.widget_general)
        self.splitter.addWidget(self.widget_order)
        self.splitter.addWidget(self.widget_broker)

    # }}}
    def __setWidgetSize(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setWidgetSize()")
        self.splitter.setStretchFactor(0, 10)  # data
        self.splitter.setStretchFactor(1, 5)  # asset
        self.splitter.setStretchFactor(2, 5)  # strategy
        self.splitter.setStretchFactor(3, 10)  # test
        self.splitter.setStretchFactor(4, 13)  # central widgets
        self.vsplit.setStretchFactor(0, 10)  # chart
        self.vsplit.setStretchFactor(1, 2)  # account
        self.vsplit.setStretchFactor(2, 1)  # report
        self.vsplit.setStretchFactor(3, 1)  # console
        self.splitter.setStretchFactor(5, 5)  # order
        self.splitter.setStretchFactor(6, 5)  # broker

    # }}}
    def __connect(self):  # {{{
        # left tools
        self.ltool.data.triggered.connect(self.__onData)
        self.ltool.asset.triggered.connect(self.__onAsset)
        self.ltool.chart.triggered.connect(self.__onChart)
        self.ltool.strategy.triggered.connect(self.__onStrategy)
        self.ltool.test.triggered.connect(self.__onTest)
        self.ltool.report.triggered.connect(self.__onReport)
        self.ltool.console.triggered.connect(self.__onConsole)
        self.ltool.shutdown.triggered.connect(self.__onShutdown)
        # right tools
        self.rtool.broker.triggered.connect(self.__onBroker)
        self.rtool.account.triggered.connect(self.__onAccount)
        self.rtool.order.triggered.connect(self.__onOrder)
        self.rtool.general.triggered.connect(self.__onGeneral)
        # widget signals
        self.widget_asset.assetChanged.connect(self.__onAssetChanged)
        self.widget_test.tlistChanged.connect(self.__onTradeListChanged)
        self.widget_test.tradeChanged.connect(self.__onTradeChanged)
        self.widget_broker.connectEnabled.connect(self.__onConnect)
        self.widget_broker.connectDisabled.connect(self.__onDisconnect)
        self.widget_broker.accountSetUp.connect(self.__onAccountSetUp)

    # }}}
    def __config(self):  # {{{
        self.setWindowTitle("AVIN  -  Ars  Vincere")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.showMaximized()
        self.setCentralWidget(self.splitter)
        self.splitter.setContentsMargins(5, 5, 5, 5)
        self.splitter.setHandleWidth(10)
        self.vsplit.setHandleWidth(10)

    # }}}
    def __initUI(self):  # {{{
        self.ltool.data.trigger()
        self.ltool.chart.trigger()
        # self.ltool.test.trigger()
        self.ltool.console.trigger()
        # self.rtool.broker.trigger()
        # self.rtool.account.trigger()
        # self.rtool.order.trigger()
        # iasset = self.widget_asset.currentAsset()
        # self.widget_chart.showChart(iasset)
        # self.widget_order.setAsset(iasset)

    # }}}
    @QtCore.pyqtSlot()  # __onData# {{{
    def __onData(self):
        logger.debug(f"{self.__class__.__name__}.__onData()")
        state = self.widget_data.isVisible()
        self.widget_data.setVisible(not state)

    # }}}
    @QtCore.pyqtSlot()  # __onAsset# {{{
    def __onAsset(self):
        logger.debug(f"{self.__class__.__name__}.__onAsset()")
        state = self.widget_asset.isVisible()
        self.widget_asset.setVisible(not state)

    # }}}
    @QtCore.pyqtSlot()  # __onChart# {{{
    def __onChart(self):
        logger.debug(f"{self.__class__.__name__}.__onChart()")
        state = self.widget_chart.isVisible()
        self.widget_chart.setVisible(not state)

    # }}}
    @QtCore.pyqtSlot()  # __onStrategy# {{{
    def __onStrategy(self):
        logger.debug(f"{self.__class__.__name__}.__onStrategy()")
        state = self.widget_strategy.isVisible()
        self.widget_strategy.setVisible(not state)

    # }}}
    @QtCore.pyqtSlot()  # __onTest# {{{
    def __onTest(self):
        logger.debug(f"{self.__class__.__name__}.__onTest()")
        state = self.widget_test.isVisible()
        self.widget_test.setVisible(not state)

    # }}}
    @QtCore.pyqtSlot()  # __onReport# {{{
    def __onReport(self):
        logger.debug(f"{self.__class__.__name__}.__onReport()")
        state = self.widget_report.isVisible()
        self.widget_report.setVisible(not state)

    # }}}
    @QtCore.pyqtSlot()  # __onConsole# {{{
    def __onConsole(self):
        logger.debug(f"{self.__class__.__name__}.__onConsole()")
        state = self.widget_console.isVisible()
        self.widget_console.setVisible(not state)

    # }}}
    @QtCore.pyqtSlot()  # __onShutdown# {{{
    def __onShutdown(self):
        logger.debug(f"{self.__class__.__name__}.__onShutdown()")
        QtWidgets.QApplication.instance().quit()

    # }}}
    @QtCore.pyqtSlot()  # __onBroker# {{{
    def __onBroker(self):
        logger.debug(f"{self.__class__.__name__}.__onBroker()")
        state = self.widget_broker.isVisible()
        self.widget_broker.setVisible(not state)

    # }}}
    @QtCore.pyqtSlot()  # __onAccount# {{{
    def __onAccount(self):
        logger.debug(f"{self.__class__.__name__}.__onAccount()")
        state = self.widget_account.isVisible()
        self.widget_account.setVisible(not state)

    # }}}
    @QtCore.pyqtSlot()  # __onOrder# {{{
    def __onOrder(self):
        logger.debug(f"{self.__class__.__name__}.__onOrder()")
        state = self.widget_order.isVisible()
        self.widget_order.setVisible(not state)

    # }}}
    @QtCore.pyqtSlot()  # __onGeneral# {{{
    def __onGeneral(self):
        logger.debug(f"{self.__class__.__name__}.__onGeneral()")
        state = self.widget_general.isVisible()
        self.widget_general.setVisible(not state)

    # }}}
    @QtCore.pyqtSlot(Asset)  # __onAssetChanged# {{{
    def __onAssetChanged(self, iasset: Asset):
        logger.debug(f"{self.__class__.__name__}.__onAssetChanged()")
        assert isinstance(iasset, IShare)
        self.widget_chart.showChart(iasset)
        self.widget_order.setAsset(iasset)

    # }}}
    @QtCore.pyqtSlot(ITradeList)  # __onTradeListChanged# {{{
    def __onTradeListChanged(self, itlist: ITradeList):
        logger.debug(f"{self.__class__.__name__}.__onTradeListChanged()")
        self.widget_chart.showTradeList(itlist)
        self.widget_report.showSummary(itlist)

    # }}}
    @QtCore.pyqtSlot(ITrade)  # __onTradeChanged# {{{
    def __onTradeChanged(self, itrade: ITrade):
        logger.debug(f"{self.__class__.__name__}.__onTradeChanged()")
        self.widget_chart.showTrade(itrade)

    # }}}
    @QtCore.pyqtSlot(ISandbox)  # __onConnect# {{{
    def __onConnect(self, ibroker: ISandbox):
        logger.debug(f"{self.__class__.__name__}.__onConnect()")
        ...

    # }}}
    @QtCore.pyqtSlot(IAccount)  # __onAccountSetUp# {{{
    def __onAccountSetUp(self, iaccount: IAccount):
        logger.debug(f"{self.__class__.__name__}.__onAccountSetUp()")
        self.widget_order.connectAccount(iaccount)
        self.widget_account.connectAccount(iaccount)

    # }}}
    @QtCore.pyqtSlot(ISandbox)  # __onDisconnect# {{{
    def __onDisconnect(self, iaccount: ISandbox):
        logger.debug(f"{self.__class__.__name__}.__onDisconnect()")
        self.widget_order.disconnectAccount(iaccount)


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = MainWindow()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())
