#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc """
import sys
sys.path.append("/usr/lib/python3.12/site-packages")
sys.path.append("/home/alex/.local/lib/python3.12/site-packages/tinkoff/")
sys.path.append("/home/alex/yandex/avin-dev/")
import enum
import json
import logging
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from avin.const import MSK_TIME_DIF, STRATEGY_DIR, TEST_DIR
from avin.core import TimeFrame, Asset, Trade, TradeList, Test, Strategy
from avin.company import Tester
from avin.utils import Cmd
from avin.gui.custom import Palette, Font, Icon, ProgressBar, Dialog
import avin.gui as gui
logger = logging.getLogger("LOGGER")

class ITrade(Trade, QtWidgets.QTreeWidgetItem):
    def __init__(self, info: dict, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Trade.__init__(self, info, parent)
        self.__config()
        self.gtrade = None  # link to GTrade

    def __config(self):
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        dt = self.dt + MSK_TIME_DIF
        dt = dt.strftime("%Y-%m-%d  %H:%M")
        self.setText(TradeTree.Column.Date, dt)
        self.setText(TradeTree.Column.Result, str(self.result))


class ITradeList(TradeList, QtWidgets.QTreeWidgetItem):
    def __init__(self, name, trades=None, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        TradeList.__init__(self, name, trades, parent)
        self.__config()
        self.updateText()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setTextAlignment(
            TestTree.Column.Trades,
            Qt.AlignmentFlag.AlignRight
            )
        self.setTextAlignment(
            TestTree.Column.Block,
            Qt.AlignmentFlag.AlignRight
            )
        self.setTextAlignment(
            TestTree.Column.Allow,
            Qt.AlignmentFlag.AlignRight
            )

    def _createChild(self, trades, suffix):
        logger.debug(f"{self.__class__.__name__}.__createChild()")
        child_name = "-" + self.name.replace("tlist", "") + f" {suffix}"
        child = ITradeList(
            name = child_name,
            trades = trades,
            parent = self
            )
        child._asset = self.asset
        self._childs.append(child)
        return child

    @staticmethod  #load
    def load(file_path, parent=None):
        logger.debug(f"{__class__.__name__}.load()")
        name = Cmd.name(file_path)
        obj = Cmd.loadJSON(file_path)
        itlist = ITradeList(name, parent=parent)
        for info in obj:
            itrade = ITrade(info)
            itlist.add(itrade)
        itlist.updateText()
        return itlist

    def updateText(self):
        logger.debug(f"{self.__class__.__name__}.__updateText()")
        self.setText(TestTree.Column.Name, self.name)
        self.setText(TestTree.Column.Trades, str(self.count))

    def selectAsset(self, asset: Asset):
        logger.debug(f"{self.__class__.__name__}.selectAsset()")
        selected = list()
        for trade in self._trades:
            if trade.asset.figi == asset.figi:
                selected.append(trade)
        child = self._createChild(selected, asset.ticker)
        child._asset = asset
        return child

    def selectLong(self):
        logger.debug(f"{self.__class__.__name__}.selectLong()")
        selected = list()
        for trade in self._trades:
            if trade.isLong():
                selected.append(trade)
        child = self._createChild(selected, "long")
        return child

    def selectShort(self):
        logger.debug(f"{self.__class__.__name__}.selectShort()")
        selected = list()
        for trade in self._trades:
            if trade.isShort():
                selected.append(trade)
        child = self._createChild(selected, "short")
        return child

    def selectWin(self):
        logger.debug(f"{self.__class__.__name__}.selectWin()")
        selected = list()
        for trade in self._trades:
            if trade.isWin():
                selected.append(trade)
        child = self._createChild(selected, "win")
        return child

    def selectLoss(self):
        logger.debug(f"{self.__class__.__name__}.selectLoss()")
        selected = list()
        for trade in self._trades:
            if trade.isLoss():
                selected.append(trade)
        child = self._createChild(selected, "loss")
        return child

    def selectYear(self, year):
        logger.debug(f"{self.__class__.__name__}.selectYear()")
        selected = list()
        for trade in self._trades:
            trade_year = trade.dt.year
            if trade_year == year:
                selected.append(trade)
        child = self._createChild(selected, year)
        return child

    def selectBack(self):
        logger.debug(f"{self.__class__.__name__}.selectBack()")
        selected = list()
        for trade in self._trades:
            if trade.isBack():
                selected.append(trade)
        child = self._createChild(selected, "back")
        return child

    def selectForward(self):
        logger.debug(f"{self.__class__.__name__}.selectForward()")
        selected = list()
        for trade in self._trades:
            if trade.isForward():
                selected.append(trade)
        child = self._createChild(selected, "forward")
        return child


class ITest(Test, QtWidgets.QTreeWidgetItem):
    def __init__(self, name, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Test.__init__(self, name)
        self.__parent = parent
        self.__createProgressBar()
        self.__config()
        self.updateText()

    def __createProgressBar(self):
        logger.debug(f"{self.__class__.__name__}.__createProgressBar()")
        self.progress_bar = ProgressBar()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )

    def __createSubgroups(self):
        logger.debug(f"{self.__class__.__name__}.__createSubgroups()")
        for asset in self.alist:
            self.tlist.selectAsset(asset)

    def _loadTrades(self):
        logger.debug(f"{self.__class__.__name__}._loadTrades()")
        file_path = Cmd.join(self.dir_path, "tlist.tl")
        if Cmd.isExist(file_path):
            self._tlist = ITradeList.load(file_path, parent=self)
            return True
        else:
            self._tlist = ITradeList(name="tlist", parent=self)
            return False

    @staticmethod  #load
    def load(dir_path: str):
        if not Cmd.isExist(dir_path):
            logger.error(
                f"{__class__.__name__}.load:"
                f"directory not found: '{dir_path}'"
                )
            return None
        name = Cmd.name(dir_path)
        itest = ITest(name)
        itest._loadConfig()
        itest._loadAssetList()
        itest._loadTrades()
        itest._loadStatus()
        itest._loadReport()
        itest.__createSubgroups()
        itest.updateText()
        itest.updateProgressBar()
        return itest

    @staticmethod  #rename
    def rename(test, new_name):
        Test.rename(test, new_name)
        test.updateText()
        test.updateProgressBar()

    def parent(self):
        return self.__parent

    def setParent(self, parent):
        self.__parent = parent

    def updateText(self):
        self.setText(TestTree.Column.Name, self.name)

    def updateProgressBar(self):
        logger.debug(f"{self.__class__.__name__}.updateProgressBar()")
        if self.status == Test.Status.UNDEFINE:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Undefine")
        elif self.status == Test.Status.NEW:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("New")
        elif self.status == Test.Status.EDITED:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Edited")
        elif self.status == Test.Status.PROCESS:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("%p%")
        elif self.status == Test.Status.COMPLETE:
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Complete")
        tree = self.parent()
        if tree:
            tree.setItemWidget(
                self,
                TestTree.Column.Progress,
                self.progress_bar
                )


class TestTree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Name =      0
        Progress =  1
        Trades =    2
        Block =     3
        Allow =     4

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createTestActions()
        self.__createTestMenu()
        self.__createYearActions()
        self.__createYearMenu()
        self.__createTradeListActions()
        self.__createTradeListMenu()
        self.__connect()
        self.constructor = Editor()
        self.thread = None

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setSortingEnabled(True)
        self.sortByColumn(self.Column.Name, Qt.SortOrder.AscendingOrder)
        self.setColumnWidth(self.Column.Name, 200)
        self.setColumnWidth(self.Column.Progress, 80)
        self.setColumnWidth(self.Column.Trades, 55)
        self.setColumnWidth(self.Column.Block, 50)
        self.setColumnWidth(self.Column.Allow, 50)
        self.setFont(Font.MONO)

    def __createTestActions(self):
        self.action_run =      QtGui.QAction("Run", self)
        self.action_pause =    QtGui.QAction("Pause", self)
        self.action_stop =     QtGui.QAction("Stop", self)
        self.action_new =      QtGui.QAction("New", self)
        self.action_copy =     QtGui.QAction("Copy", self)
        self.action_edit =     QtGui.QAction("Edit", self)
        self.action_rename =   QtGui.QAction("Rename", self)
        self.action_delete =   QtGui.QAction("Delete", self)

    def __createTestMenu(self):
        self.test_menu = QtWidgets.QMenu(self)
        self.test_menu.addAction(self.action_run)
        self.test_menu.addAction(self.action_pause)
        self.test_menu.addAction(self.action_stop)
        self.test_menu.addSeparator()
        self.test_menu.addAction(self.action_new)
        self.test_menu.addAction(self.action_copy)
        self.test_menu.addAction(self.action_edit)
        self.test_menu.addAction(self.action_rename)
        self.test_menu.addAction(self.action_delete)

    def __createYearActions(self):
        self.action_select_2018 = QtGui.QAction("Select 2018", self)
        self.action_select_2019 = QtGui.QAction("Select 2019", self)
        self.action_select_2020 = QtGui.QAction("Select 2020", self)
        self.action_select_2021 = QtGui.QAction("Select 2021", self)
        self.action_select_2022 = QtGui.QAction("Select 2022", self)
        self.action_select_2023 = QtGui.QAction("Select 2023", self)
        self.action_select_2024 = QtGui.QAction("Select 2024", self)

    def __createYearMenu(self):
        self.year_menu = QtWidgets.QMenu("Select year...")
        self.year_menu.addAction(self.action_select_2018)
        self.year_menu.addAction(self.action_select_2019)
        self.year_menu.addAction(self.action_select_2020)
        self.year_menu.addAction(self.action_select_2021)
        self.year_menu.addAction(self.action_select_2022)
        self.year_menu.addAction(self.action_select_2023)
        self.year_menu.addAction(self.action_select_2024)

    def __createTradeListActions(self):
        self.action_select_long =    QtGui.QAction("Select long", self)
        self.action_select_short =   QtGui.QAction("Select short", self)
        self.action_select_win =     QtGui.QAction("Select win", self)
        self.action_select_loss =    QtGui.QAction("Select loss", self)
        self.action_select_filter =  QtGui.QAction("Select filter", self)

    def __createTradeListMenu(self):
        self.trade_list_menu = QtWidgets.QMenu(self)
        self.trade_list_menu.addAction(self.action_select_long)
        self.trade_list_menu.addAction(self.action_select_short)
        self.trade_list_menu.addAction(self.action_select_win)
        self.trade_list_menu.addAction(self.action_select_loss)
        self.trade_list_menu.addAction(self.action_select_filter)
        self.trade_list_menu.addMenu(self.year_menu)

    def __connect(self):
        self.action_run.triggered.connect(self.__onRun)
        self.action_pause.triggered.connect(self.__onPause)
        self.action_stop.triggered.connect(self.__onStop)
        self.action_new.triggered.connect(self.__onNew)
        self.action_copy.triggered.connect(self.__onCopy)
        self.action_edit.triggered.connect(self.__onEdit)
        self.action_rename.triggered.connect(self.__onRename)
        self.action_delete.triggered.connect(self.__onDelete)
        self.action_select_long.triggered.connect(self.__onSelectLong)
        self.action_select_short.triggered.connect(self.__onSelectShort)
        self.action_select_win.triggered.connect(self.__onSelectWin)
        self.action_select_loss.triggered.connect(self.__onSelectLoss)
        self.action_select_filter.triggered.connect(self.__onSelectFilter)

    def __resetActions(self):
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        for i in self.actions():
            i.setEnabled(False)

    def __setVisibleActions(self, item):
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            self.__new.setEnabled(True)
        elif isinstance(item, ITest):
            self.__run.setEnabled(True)
            self.__pause.setEnabled(True)
            self.__stop.setEnabled(True)
            self.__new.setEnabled(True)
            self.__copy.setEnabled(True)
            self.__edit.setEnabled(True)
            self.__rename.setEnabled(True)
            self.__delete.setEnabled(True)
        elif isinstance(item, ITradeList):
            self.__select_year.setEnabled(True)
            self.__select_long.setEnabled(True)
            self.__select_short.setEnabled(True)
            self.__select_win.setEnabled(True)
            self.__select_loss.setEnabled(True)
            self.__select_filter.setEnabled(True)

    def __reloadTest(self):
        logger.debug(f"{self.__class__.__name__}.__reloadTest()")
        itest = self.thread.test
        index = self.indexFromItem(itest).row()
        self.takeTopLevelItem(index)
        path = itest.dir_path
        reloaded = ITest.load(path)
        self.addTest(reloaded)

    def __updateProgressBar(self, val):
        self.thread.test.progress_bar.setValue(val)

    @QtCore.pyqtSlot()  #__onRun
    def __onRun(self):
        logger.debug(f"{self.__class__.__name__}.__onRun()")
        if self.thread is not None:
            Dialog.info("Tester is busy now, wait for complete test")
            return
        itest = self.currentItem()
        tester = Tester()
        tester.progress.connect(self.__updateProgressBar)
        self.thread = Thread(tester, itest)
        self.thread.finished.connect(self.__threadFinished)
        itest.updateProgressBar()
        self.thread.start()

    @QtCore.pyqtSlot()  #__onPause
    def __onPause(self):
        logger.debug(f"{self.__class__.__name__}.__onPause()")

    @QtCore.pyqtSlot()  #__onStop
    def __onStop(self):
        logger.debug(f"{self.__class__.__name__}.__onStop()")

    @QtCore.pyqtSlot()  #__threadFinished
    def __threadFinished(self):
        logger.debug(f"{self.__class__.__name__}.__threadFinished()")
        self.__reloadTest()
        self.thread = None

    @QtCore.pyqtSlot()  #__onNew
    def __onNew(self):
        logger.debug(f"{self.__class__.__name__}.__onNew()")
        test = self.constructor.newTest()
        if test:
            self.addTest(test)

    @QtCore.pyqtSlot()  #__onCopy
    def __onCopy(self):
        logger.debug(f"{self.__class__.__name__}.__onCopy()")
        itest = self.currentItem()
        new_name = Dialog.name(default=itest.name)
        if new_name:
            path = Cmd.join(TEST_DIR, new_name)
            Cmd.copyDir(itest.dir_path, path)
            copy = ITest.load(path)
            copy.name = new_name
            self.addTopLevelItem(copy)

    @QtCore.pyqtSlot()  #__onEdit
    def __onEdit(self):
        logger.debug(f"{self.__class__.__name__}.__onEdit()")
        itest: ITest = self.currentItem()
        edited = self.constructor.editTest(itest)
        if edited:
            self.removeTest(itest)
            self.addTest(edited)

    @QtCore.pyqtSlot()  #__onRename
    def __onRename(self):
        logger.debug(f"{self.__class__.__name__}.__onRename()")
        itest: ITest = self.currentItem()
        new_name = Dialog.name(default=itest.name)
        if new_name:
            ITest.rename(itest, new_name)

    @QtCore.pyqtSlot()  #__onDelete
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.delete()")
        result = Dialog.confirm()
        if result:
            itest = self.currentItem()
            logger.info(f"Delete test '{itest.name}'")
            Test.delete(itest)
            self.removeTest(itest)
        else:
            logger.info(f"Cancel delete")

    @QtCore.pyqtSlot()  #__onSelectLong
    def __onSelectLong(self):
        logger.debug(f"{self.__class__.__name__}.selectLong()")
        itlist = self.currentItem()
        itlist.selectLong()

    @QtCore.pyqtSlot()  #__onSelectShort
    def __onSelectShort(self):
        logger.debug(f"{self.__class__.__name__}.selectShort()")
        itlist = self.currentItem()
        itlist.selectShort()

    @QtCore.pyqtSlot()  #__onSelectWin
    def __onSelectWin(self):
        logger.debug(f"{self.__class__.__name__}.selectWin()")
        itlist = self.currentItem()
        itlist.selectWin()

    @QtCore.pyqtSlot()  #__onSelectLoss
    def __onSelectLoss(self):
        logger.debug(f"{self.__class__.__name__}.selectWin()")
        itlist = self.currentItem()
        itlist.selectLoss()

    @QtCore.pyqtSlot()  #__onSelectFilter
    def __onSelectFilter(self):
        logger.debug(f"{self.__class__.__name__}.selectWin()")
        itlist = self.currentItem()
        itlist.selectFilter()

    def contextMenuEvent(self, e: QtGui.QContextMenuEvent):
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent(e)")
        item = self.itemAt(e.pos())
        # if item is None:
        #     self.test_menu.exec()
        if isinstance(item, ITest):
            self.test_menu.exec(QtGui.QCursor.pos())
        elif isinstance(item, ITradeList):
            self.trade_list_menu.exec(QtGui.QCursor.pos())
        return e.ignore()

    def addTest(self, itest: ITest):
        logger.debug(f"{self.__class__.__name__}.addTest()")
        self.addTopLevelItem(itest)
        itest.setParent(self)
        itest.updateProgressBar()

    def removeTest(self, itest):
        logger.debug(f"{self.__class__.__name__}.removeTest()")
        index = self.indexFromItem(itest).row()
        self.takeTopLevelItem(index)



class TradeTree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Date =      0
        Result =    1

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createMenu()
        self.__connect()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setSortingEnabled(True)
        self.sortByColumn(TradeTree.Column.Date, Qt.SortOrder.AscendingOrder)
        self.setColumnWidth(TradeTree.Column.Date, 170)
        self.setColumnWidth(TradeTree.Column.Result, 100)
        self.setFont(Font.MONO)

    def __createMenu(self):
        self.action_info =     QtGui.QAction("Info", self)
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.action_info)

    def __connect(self):
        self.action_info.triggered.connect(self.__onInfo)

    def __resetActions(self):
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        for i in self.menu.actions():
            i.setEnabled(False)

    def __setVisibleActions(self, item):
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            self.action_info.setEnabled(False)
        elif isinstance(item, ITrade):
            self.action_info.setEnabled(True)

    @QtCore.pyqtSlot()  #__onInfo
    def __onInfo(self):
        logger.debug(f"{self.__class__.__name__}.__onInfo()")
        itrade: ITrade = self.currentItem()
        Dialog.info(str(itrade))

    def contextMenuEvent(self, e: QtGui.QContextMenuEvent):
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent(e)")
        item = self.itemAt(e.pos())
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()


class Thread(QtCore.QThread):
    def __init__(self, tester: Tester, test: ITest, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.tester = tester
        self.test = test
        self.tester.setTest(self.test)

    def run(self):
        self.tester.runTest()


class Editor(QtWidgets.QDialog):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__createForm()
        self.__configButton()
        self.__connect()
        self.__config()
        self.__loadUserStrategy()
        self.__loadUserTimeframes()
        self.__initUI()

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.lineedit_testname = QtWidgets.QLineEdit()
        self.combobox_strategy = QtWidgets.QComboBox()
        self.combobox_version = QtWidgets.QComboBox()
        self.combobox_timeframe = QtWidgets.QComboBox()
        self.dblspinbox_deposit = QtWidgets.QDoubleSpinBox()
        self.dblspinbox_commission = QtWidgets.QDoubleSpinBox()
        self.begin = QtWidgets.QDateEdit()
        self.end = QtWidgets.QDateEdit()
        self.description = QtWidgets.QPlainTextEdit()
        self.btn_alist = QtWidgets.QToolButton()
        self.btn_save = QtWidgets.QToolButton()
        self.btn_cancel = QtWidgets.QToolButton()

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        self.hbox_btn = QtWidgets.QHBoxLayout()
        self.hbox_btn.addStretch()
        self.hbox_btn.addWidget(self.btn_save)
        self.hbox_btn.addWidget(self.btn_cancel)
        self.hbox_alist = QtWidgets.QHBoxLayout()
        self.hbox_alist.addStretch()
        self.hbox_alist.addWidget(self.btn_alist)

    def __createForm(self):
        logger.debug(f"{self.__class__.__name__}.__createForm()")
        form = QtWidgets.QFormLayout()
        form.addRow("Test name",        self.lineedit_testname)
        form.addRow("Strategy",         self.combobox_strategy)
        form.addRow("Version",          self.combobox_version)
        form.addRow("Timeframe",        self.combobox_timeframe)
        form.addRow("Asset list",       self.hbox_alist)
        form.addRow("Deposit",          self.dblspinbox_deposit)
        form.addRow("Commission %",     self.dblspinbox_commission)
        form.addRow("Begin date",       self.begin)
        form.addRow("End date",         self.end)
        form.addRow(QtWidgets.QLabel("Description"))
        form.addRow(self.description)
        form.addRow(self.hbox_btn)
        self.setLayout(form)

    def __configButton(self):
        logger.debug(f"{self.__class__.__name__}.__configButton()")
        self.btn_alist.setIcon(Icon.ASSET)
        self.btn_alist.setFixedSize(32, 32)
        self.btn_alist.setIconSize(QtCore.QSize(30, 30))
        self.btn_save.setIcon(Icon.SAVE)
        self.btn_save.setFixedSize(32, 32)
        self.btn_save.setIconSize(QtCore.QSize(30, 30))
        self.btn_cancel.setIcon(Icon.CANCEL)
        self.btn_cancel.setFixedSize(32, 32)
        self.btn_cancel.setIconSize(QtCore.QSize(30, 30))

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.combobox_strategy.currentTextChanged.connect(self.__loadVersions)
        self.btn_alist.clicked.connect(self.__editAssetList)
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def __loadUserStrategy(self):
        logger.debug(f"{self.__class__.__name__}.__loadUserStrategy()")
        dirs = Cmd.getDirs(STRATEGY_DIR)
        for name in dirs:
            self.combobox_strategy.addItem(name)

    def __loadVersions(self):
        logger.debug(f"{self.__class__.__name__}.__loadVersions()")
        name = self.combobox_strategy.currentText()
        versions = Strategy.versions(name)
        self.combobox_version.clear()
        self.combobox_version.addItems(versions)

    def __loadUserTimeframes(self):
        logger.debug(f"{self.__class__.__name__}.__loadUserTimeframes()")
        for timeframe in TimeFrame.ALL:
            self.combobox_timeframe.addItem(str(timeframe))

    def __initUI(self):
        self.combobox_timeframe.setCurrentText("1M")
        self.lineedit_testname.setText("unnamed")
        self.dblspinbox_deposit.setMinimum(0.0)
        self.dblspinbox_deposit.setMaximum(1_000_000_000.0)
        self.dblspinbox_deposit.setValue(100_000.0)
        self.dblspinbox_commission.setMinimum(0.0)
        self.dblspinbox_commission.setMaximum(1.0)
        self.dblspinbox_commission.setValue(0.05)
        self.begin.setDate(QtCore.QDate(2018, 1, 1))
        self.end.setDate(QtCore.QDate(2023, 1, 1))

    def __editAssetList(self):
        editor = gui.asset.Editor()
        editor.editAssetList(self.alist)

    def __writeTestConfig(self, test):
        test.name =         self.lineedit_testname.text()
        test.description =  self.description.toPlainText()
        test.strategy =     self.combobox_strategy.currentText()
        test.version =      self.combobox_version.currentText()
        test.timeframe =    TimeFrame(self.combobox_timeframe.currentText())
        test.alist =        self.alist
        test.deposit =      self.dblspinbox_deposit.value()
        test.commission =   self.dblspinbox_commission.value() / 100
        test.begin =        str(self.begin.date().toPyDate())
        test.end =          str(self.end.date().toPyDate())
        test.updateText()
        return test

    def __readTestConfig(self, test):
        self.lineedit_testname.setText(test.name)
        self.combobox_strategy.setCurrentText(test.strategy)
        self.combobox_version.setCurrentText(test.version)
        self.combobox_timeframe.setCurrentText(str(test.timeframe))
        self.dblspinbox_deposit.setValue(test.deposit)
        self.dblspinbox_commission.setValue(test.commission * 100)
        self.begin.setDate(test.begin.date())
        self.end.setDate(test.end.date())
        self.description.setPlainText(test.description)

    def newTest(self):
        new_test = ITest(name="")
        self.alist = gui.asset.IAssetList(".tmp", parent=new_test)
        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            self.__writeTestConfig(new_test)
            ITest.save(new_test)
            logger.info(f"New test '{new_test.name}' created")
            return new_test
        else:
            logger.info(f"Cancel new test")
            return False

    def editTest(self, itest):
        self.__readTestConfig(itest)
        self.alist = itest.alist
        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            ITest.delete(itest)
            edited = ITest(name="")
            edited = self.__writeTestConfig(edited)
            edited.status = Test.Status.EDITED
            ITest.save(edited)
            logger.info(f"Test edited")
            return edited
        else:
            logger.info(f"Cancel edit test")
            return False


class TestWidget(QtWidgets.QWidget):
    """ Signal """
    testChanged = QtCore.pyqtSignal(ITest)
    tlistChanged = QtCore.pyqtSignal(ITradeList)
    tradeChanged = QtCore.pyqtSignal(ITrade)

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__loadUserTests()

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.test_tree = TestTree(self)
        self.trade_tree = TradeTree(self)
        self.vsplit = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical, self)
        self.vsplit.addWidget(self.test_tree)
        self.vsplit.addWidget(self.trade_tree)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.vsplit)
        self.setLayout(vbox)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.test_tree.clicked.connect(self.__onTestTreeClicked)
        self.trade_tree.clicked.connect(self.__onTradeTreeClicked)

    def __loadUserTests(self):
        logger.debug(f"{self.__class__.__name__}.__loadUserTests()")
        dirs = Cmd.getDirs(TEST_DIR, full_path=True)
        for dir_path in dirs:
            dir_name = Cmd.name(dir_path)
            if dir_name.startswith("."):
                continue
            itest = ITest.load(dir_path)
            self.test_tree.addTest(itest)

    @QtCore.pyqtSlot()  #__onTestTreeClicked
    def __onTestTreeClicked(self):
        logger.debug(f"{self.__class__.__name__}.__onTestTreeClicked()")
        item = self.test_tree.currentItem()
        if   isinstance(item, ITest):
            while self.trade_tree.takeTopLevelItem(0): pass
            self.testChanged.emit(item)
        elif isinstance(item, ITradeList):
            while self.trade_tree.takeTopLevelItem(0): pass
            self.trade_tree.addTopLevelItems(item)
            self.tlistChanged.emit(item)

    @QtCore.pyqtSlot()  #__onTradeTreeClicked
    def __onTradeTreeClicked(self):
        logger.debug(f"{self.__class__.__name__}.__onTradeTreeClicked()")
        itrade = self.trade_tree.currentItem()
        self.tradeChanged.emit(itrade)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = TestWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.showMaximized()
    w.show()
    sys.exit(app.exec())

