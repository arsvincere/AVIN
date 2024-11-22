#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt, pyqtSlot

from avin.core import Account, Asset, Broker, Trade, TradeList
from avin.utils import logger
from gui.asset import AssetListWidget
from gui.console import ConsoleWidget
from gui.custom import Css
from gui.data import DataWidget
from gui.main_window.toolbar import LeftToolBar, RightToolBar
from gui.strategy import StrategyWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QMainWindow.__init__(self, parent)

        # HACK: хз че за херня, но если тут тоже не вызвать заставку
        # то в hyprland она не отображается. Ее нужно в 2 местах
        # вызвать здесь и в main.py
        # Причем настройки тянутся именно из main.py и заставка
        # от сюда по факту не отображается, но без этого вызова .show()
        # никак. Наверное дело в цикле событий. Нужно как то
        # принудительно сначала вывести заставку а потом грузить дальше
        # но пример из доков Qt с вызовом app.processEvents() не
        # срабатывает.
        # Возможно баг в hyprland, в xfce4 вроде работало из main.py
        # без проблем
        splash = QtWidgets.QSplashScreen()
        splash.show()

        # create main window
        self.__config()
        # self.__createMdiArea()
        # self.__configMdiArea()
        self.__createToolBars()
        self.__createWidgets()
        # self.__createSplitter()
        # self.__setWidgetSize()
        self.__connect()
        self.__initUI()

    # }}}
    # def __createMdiArea(self):  # {{{
    #     logger.debug(f"{self.__class__.__name__}.__createMdiArea()")
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
    #     self.area.setViewMode(QtWidgets.QMdiArea.ViewMode.TabbedView)
    #     self.area.setTabsMovable(True)
    #     self.area.setTabsClosable(False)
    #     self.area.setActiveSubWindow(self.tab1)
    #
    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setStyleSheet(Css.STYLE)
        self.setWindowTitle("AVIN  -  Ars  Vincere")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.showMaximized()

    # }}}
    def __createToolBars(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createToolBars()")

        self.ltool = LeftToolBar(self)
        self.ltool.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.ltool)

        self.rtool = RightToolBar(self)
        self.rtool.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.rtool)

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLeftWidgets()")

        self.data_widget = None
        self.asset_widget = None
        self.strategy_widget = None
        self.tester_widget = None

        self.console_widget = None

        # self.widget_chart = ChartWidget(self)
        # self.widget_chart.hide()
        # self.widget_report = ReportWidget(self)
        # self.widget_report.hide()
        # self.widget_account = AccountWidget(self)
        # self.widget_account.hide()

        # self.widget_broker = BrokerWidget(self)
        # self.widget_broker.hide()
        # self.widget_order = OrderDialog(self)
        # self.widget_order.hide()
        # self.widget_general = GeneralWidget(self)
        # self.widget_general.hide()

    # }}}
    def __createSplitter(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createSplitter()")

        # left
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.widget_data)
        self.splitter.addWidget(self.widget_asset)
        self.splitter.addWidget(self.widget_strategy)
        self.splitter.addWidget(self.widget_tester)
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

        self.setCentralWidget(self.splitter)
        self.splitter.setContentsMargins(5, 5, 5, 5)
        self.splitter.setHandleWidth(10)
        self.vsplit.setHandleWidth(10)

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
        logger.debug(f"{self.__class__.__name__}.__connect()")

        # left tools
        self.ltool.data.triggered.connect(self.__onData)
        self.ltool.asset.triggered.connect(self.__onAsset)
        # self.ltool.filter.triggered.connect(self.__onFilter)
        # self.ltool.analytic.triggered.connect(self.__onAnalytic)
        self.ltool.strategy.triggered.connect(self.__onStrategy)
        # self.ltool.note.triggered.connect(self.__onNote)
        self.ltool.tester.triggered.connect(self.__onTester)
        # self.ltool.summary.triggered.connect(self.__onSummary)
        self.ltool.console.triggered.connect(self.__onConsole)
        # self.ltool.config.triggered.connect(self.__onConfig)
        self.ltool.shutdown.triggered.connect(self.__onShutdown)
        # right tools
        # self.rtool.broker.triggered.connect(self.__onBroker)
        # self.rtool.chart.triggered.connect(self.__onChart)
        # self.rtool.book.triggered.connect(self.__onBook)
        # self.rtool.tic.triggered.connect(self.__onTic)
        # self.rtool.order.triggered.connect(self.__onOrder)
        # self.rtool.account.triggered.connect(self.__onAccount)
        # self.rtool.trader.triggered.connect(self.__onTrader)
        # self.rtool.report.triggered.connect(self.__onReport)
        # widget signals
        # AssetListWidget.assetChanged.connect(self.__onAssetChanged)
        # TesterWidget.tlistChanged.connect(self.__onTradeListChanged)
        # TesterWidget.tradeChanged.connect(self.__onTradeChanged)
        # self.widget_broker.connectEnabled.connect(self.__onConnect)
        # self.widget_broker.connectDisabled.connect(self.__onDisconnect)
        # self.widget_broker.accountSetUp.connect(self.__onAccountSetUp)

    # }}}
    def __initUI(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")

        # self.ltool.data.trigger()
        # self.ltool.chart.trigger()
        # self.ltool.test.trigger()
        # self.ltool.console.trigger()
        # self.rtool.broker.trigger()
        # self.rtool.account.trigger()
        # self.rtool.order.trigger()
        # iasset = self.widget_asset.currentAsset()
        # self.widget_chart.showChart(iasset)
        # self.widget_order.setAsset(iasset)

    # }}}
    @pyqtSlot()  # __onData  # {{{
    def __onData(self):
        logger.debug(f"{self.__class__.__name__}.__onData()")

        if self.data_widget is None:
            self.data_widget = DataWidget(self)
            self.data_dock_widget = QtWidgets.QDockWidget(self)
            self.data_dock_widget.setWidget(self.data_widget)

            feat = QtWidgets.QDockWidget.DockWidgetFeature
            self.data_dock_widget.setFeatures(
                feat.DockWidgetMovable | feat.DockWidgetVerticalTitleBar
            )

            area = Qt.DockWidgetArea.LeftDockWidgetArea
            self.addDockWidget(area, self.data_dock_widget)
            return

    # }}}
    @pyqtSlot()  # __onAsset  # {{{
    def __onAsset(self):
        logger.debug(f"{self.__class__.__name__}.__onAsset()")

        if self.asset_widget is None:
            self.asset_widget = AssetListWidget(self)
            self.asset_dock_widget = QtWidgets.QDockWidget(self)
            self.asset_dock_widget.setWidget(self.asset_widget)

            feat = QtWidgets.QDockWidget.DockWidgetFeature
            self.asset_dock_widget.setFeatures(
                feat.DockWidgetMovable | feat.DockWidgetVerticalTitleBar
            )

            area = Qt.DockWidgetArea.LeftDockWidgetArea
            self.addDockWidget(area, self.asset_dock_widget)
            return

    # }}}
    @pyqtSlot()  # __onStrategy  # {{{
    def __onStrategy(self):
        logger.debug(f"{self.__class__.__name__}.__onStrategy()")

        if self.strategy_widget is None:
            self.strategy_widget = StrategyWidget(self)
            self.strategy_dock_widget = QtWidgets.QDockWidget(self)
            self.strategy_dock_widget.setWidget(self.strategy_widget)

            feat = QtWidgets.QDockWidget.DockWidgetFeature
            self.strategy_dock_widget.setFeatures(
                feat.DockWidgetMovable | feat.DockWidgetVerticalTitleBar
            )

            area = Qt.DockWidgetArea.RightDockWidgetArea
            self.addDockWidget(area, self.strategy_dock_widget)
            return

    # }}}
    @pyqtSlot()  # __onTester  # {{{
    def __onTester(self):
        logger.debug(f"{self.__class__.__name__}.__onTester()")

        if self.tester_widget is None:
            self.tester_widget = StrategyWidget(self)
            self.tester_dock_widget = QtWidgets.QDockWidget(self)
            self.tester_dock_widget.setWidget(self.tester_widget)

            feat = QtWidgets.QDockWidget.DockWidgetFeature
            self.tester_dock_widget.setFeatures(
                feat.DockWidgetMovable | feat.DockWidgetVerticalTitleBar
            )

            area = Qt.DockWidgetArea.RightDockWidgetArea
            self.addDockWidget(area, self.tester_dock_widget)
            return

    # }}}
    @pyqtSlot()  # __onSummary  # {{{
    def __onSummary(self):
        logger.debug(f"{self.__class__.__name__}.__onSummary()")

    # }}}
    @pyqtSlot()  # __onConsole  # {{{
    def __onConsole(self):
        logger.debug(f"{self.__class__.__name__}.__onConsole()")

        if self.console_widget is None:
            self.console_widget = ConsoleWidget(self)
            self.console_dock_widget = QtWidgets.QDockWidget(self)
            self.console_dock_widget.setWidget(self.console_widget)

            feat = QtWidgets.QDockWidget.DockWidgetFeature
            self.console_dock_widget.setFeatures(
                feat.DockWidgetMovable | feat.DockWidgetVerticalTitleBar
            )

            area = Qt.DockWidgetArea.BottomDockWidgetArea
            self.addDockWidget(area, self.console_dock_widget)
            return

    # }}}
    @pyqtSlot()  # __onShutdown  # {{{
    def __onShutdown(self):
        logger.debug(f"{self.__class__.__name__}.__onShutdown()")

        QtWidgets.QApplication.instance().quit()

    # }}}

    @pyqtSlot()  # __onBroker  # {{{
    def __onBroker(self):
        logger.debug(f"{self.__class__.__name__}.__onBroker()")
        state = self.widget_broker.isVisible()
        self.widget_broker.setVisible(not state)

    # }}}
    @pyqtSlot()  # __onChart  # {{{
    def __onChart(self):
        logger.debug(f"{self.__class__.__name__}.__onChart()")
        state = self.widget_chart.isVisible()
        self.widget_chart.setVisible(not state)

    # }}}
    @pyqtSlot()  # __onAccount  # {{{
    def __onAccount(self):
        logger.debug(f"{self.__class__.__name__}.__onAccount()")
        state = self.widget_account.isVisible()
        self.widget_account.setVisible(not state)

    # }}}
    @pyqtSlot()  # __onOrder  # {{{
    def __onOrder(self):
        logger.debug(f"{self.__class__.__name__}.__onOrder()")
        state = self.widget_order.isVisible()
        self.widget_order.setVisible(not state)

    # }}}
    @pyqtSlot()  # __onGeneral  # {{{
    def __onGeneral(self):
        logger.debug(f"{self.__class__.__name__}.__onGeneral()")
        state = self.widget_general.isVisible()
        self.widget_general.setVisible(not state)

    # }}}
    @pyqtSlot(Asset)  # __onAssetChanged  # {{{
    def __onAssetChanged(self, iasset: Asset):
        logger.debug(f"{self.__class__.__name__}.__onAssetChanged()")
        assert isinstance(iasset, IShare)
        self.widget_chart.showChart(iasset)
        self.widget_order.setAsset(iasset)

    # }}}
    @pyqtSlot(TradeList)  # __onTradeListChanged # {{{
    def __onTradeListChanged(self, tlist: TradeList):
        logger.debug(f"{self.__class__.__name__}.__onTradeListChanged()")
        self.widget_chart.showTradeList(tlist)
        self.widget_report.showSummary(tlist)

    # }}}
    @pyqtSlot(Trade)  # __onTradeChanged  # {{{
    def __onTradeChanged(self, trade: Trade):
        logger.debug(f"{self.__class__.__name__}.__onTradeChanged()")
        self.widget_chart.showTrade(trade)

    # }}}
    @pyqtSlot(Broker)  # __onConnect  # {{{
    def __onConnect(self, broker: Broker):
        logger.debug(f"{self.__class__.__name__}.__onConnect()")
        ...

    # }}}
    @pyqtSlot(Account)  # __onAccountSetUp  # {{{
    def __onAccountSetUp(self, account: Account):
        logger.debug(f"{self.__class__.__name__}.__onAccountSetUp()")
        self.widget_order.connectAccount(account)
        self.widget_account.connectAccount(account)

    # }}}
    @pyqtSlot(Broker)  # __onDisconnect  # {{{
    def __onDisconnect(self, broker: Broker):
        logger.debug(f"{self.__class__.__name__}.__onDisconnect()")
        # self.widget_order.disconnectAccount(iaccount)


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.showMaximized()
    w.show()
    sys.exit(app.exec())
