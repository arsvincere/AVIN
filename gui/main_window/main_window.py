#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from avin.core import Asset
from gui.asset import AssetListWidget
from gui.data import DataWidget
from gui.strategy import StrategyWidget
from gui.test import TestWidget


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
        self.widget_asset = AssetListWidget(self)
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
