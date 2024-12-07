#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin.core import TradeList
from avin.tester import Test
from avin.utils import logger
from gui.custom import Css, Menu
from gui.tester.dialog_edit import TestEditDialog
from gui.tester.item import TestItem, TradeItem, TradeListItem


class TestTree(QtWidgets.QTreeWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__config()
        self.__createMenus()
        self.__connect()

    # }}}

    def contextMenuEvent(self, e: QtGui.QContextMenuEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent(e)")

        item = self.itemAt(e.pos())
        if item is None:
            self.test_menu.exec(QtGui.QCursor.pos())
        if isinstance(item, TestItem):
            self.test_menu.exec(QtGui.QCursor.pos())
        elif isinstance(item, TradeListItem):
            self.trade_list_menu.exec(QtGui.QCursor.pos())
        return e.ignore()

    # }}}
    def addTest(self, test: Test):  # {{{
        logger.debug(f"{self.__class__.__name__}.addTest()")

        item = TestItem(test)
        self.addTopLevelItem(item)

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        # config header
        labels = list()
        for l in TestItem.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.header().setStyleSheet(Css.TREE_HEADER)

        # config sorting
        self.setSortingEnabled(True)
        self.sortByColumn(TestItem.Column.Name, Qt.SortOrder.AscendingOrder)

        # config width
        self.setColumnWidth(TestItem.Column.Name, 200)
        self.setColumnWidth(TestItem.Column.Status, 80)
        self.setColumnWidth(TestItem.Column.Trades, 60)
        self.setColumnWidth(TestItem.Column.Win, 50)
        self.setColumnWidth(TestItem.Column.Loss, 50)
        self.setMinimumWidth(460)

        # config style
        self.setStyleSheet(Css.TREE)
        self.setContentsMargins(0, 0, 0, 0)

    # }}}
    def __createMenus(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenus()")

        self.test_menu = _TestMenu(self)
        self.tlist_menu = _TradeListMenu(self)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.test_menu.run.triggered.connect(self.__onRun)
        self.test_menu.pause.triggered.connect(self.__onPause)
        self.test_menu.stop.triggered.connect(self.__onStop)
        self.test_menu.new.triggered.connect(self.__onNew)
        self.test_menu.copy.triggered.connect(self.__onCopy)
        self.test_menu.edit.triggered.connect(self.__onEdit)
        self.test_menu.rename.triggered.connect(self.__onRename)
        self.test_menu.delete.triggered.connect(self.__onDelete)

        self.tlist_menu.filter.triggered.connect(self.__onSelectFilter)
        self.tlist_menu.strategy.triggered.connect(self.__onSelectStrategy)
        self.tlist_menu.long.triggered.connect(self.__onSelectLong)
        self.tlist_menu.short.triggered.connect(self.__onSelectShort)
        self.tlist_menu.win.triggered.connect(self.__onSelectWin)
        self.tlist_menu.loss.triggered.connect(self.__onSelectLoss)
        self.tlist_menu.assets.triggered.connect(self.__onSelectAssets)
        self.tlist_menu.years.triggered.connect(self.__onSelectYears)

    # }}}
    def __reloadTest(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__reloadTest()")

        # FIX: write me!
        assert False

    # }}}
    def __removeTest(self, test: Test):  # {{{
        logger.debug(f"{self.__class__.__name__}.removeTest()")
        index = self.indexFromItem(itest).row()
        self.takeTopLevelItem(index)

    # }}}
    @QtCore.pyqtSlot()  # __threadFinished# {{{
    def __threadFinished(self):
        logger.debug(f"{self.__class__.__name__}.__threadFinished()")
        self.__reloadTest()
        self.thread = None

    # }}}

    @QtCore.pyqtSlot()  # __onRun# {{{
    def __onRun(self):
        logger.debug(f"{self.__class__.__name__}.__onRun()")
        # if self.thread is not None:
        #     Dialog.info("Tester is busy now, wait for complete test")
        #     return
        # itest = self.currentItem()
        # tester = Tester()
        # tester.progress.connect(self.__updateProgressBar)
        # self.thread = Thread(tester, itest)
        # self.thread.finished.connect(self.__threadFinished)
        # itest.updateProgressBar()
        # self.thread.start()

    # }}}
    @QtCore.pyqtSlot()  # __onPause# {{{
    def __onPause(self):
        logger.debug(f"{self.__class__.__name__}.__onPause()")

    # }}}
    @QtCore.pyqtSlot()  # __onStop# {{{
    def __onStop(self):
        logger.debug(f"{self.__class__.__name__}.__onStop()")

    # }}}
    @QtCore.pyqtSlot()  # __onNew# {{{
    def __onNew(self):
        logger.debug(f"{self.__class__.__name__}.__onNew()")

        dial = TestEditDialog()
        test = dial.newTest()
        if test:
            self.addTest(test)

    # }}}
    @QtCore.pyqtSlot()  # __onCopy# {{{
    def __onCopy(self):
        logger.debug(f"{self.__class__.__name__}.__onCopy()")

        # itest = self.currentItem()
        # new_name = Dialog.name(default=itest.name)
        # if new_name:
        #     path = Cmd.join(TEST_DIR, new_name)
        #     Cmd.copyDir(itest.dir_path, path)
        #     copy = ITest.load(path)
        #     copy.name = new_name
        #     self.addTopLevelItem(copy)

    # }}}
    @QtCore.pyqtSlot()  # __onEdit# {{{
    def __onEdit(self):
        logger.debug(f"{self.__class__.__name__}.__onEdit()")

        # itest: ITest = self.currentItem()
        # edited = self.constructor.editTest(itest)
        # if edited:
        #     self.removeTest(itest)
        #     self.addTest(edited)

    # }}}
    @QtCore.pyqtSlot()  # __onRename# {{{
    def __onRename(self):
        logger.debug(f"{self.__class__.__name__}.__onRename()")

        # itest: ITest = self.currentItem()
        # new_name = Dialog.name(default=itest.name)
        # if new_name:
        #     ITest.rename(itest, new_name)

    # }}}
    @QtCore.pyqtSlot()  # __onDelete# {{{
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.delete()")

        # result = Dialog.confirm()
        # if result:
        #     itest = self.currentItem()
        #     logger.info(f"Delete test '{itest.name}'")
        #     Test.delete(itest)
        #     self.removeTest(itest)
        # else:
        #     logger.info("Cancel delete")

    # }}}

    @QtCore.pyqtSlot()  # __onSelectFilter# {{{
    def __onSelectFilter(self):
        logger.debug(f"{self.__class__.__name__}.__onSelectFilter()")

        # itlist = self.currentItem()
        # itlist.selectFilter()

    # }}}
    @QtCore.pyqtSlot()  # __onSelectStrategy# {{{
    def __onSelectStrategy(self):
        logger.debug(f"{self.__class__.__name__}.__onSelectStrategy()")

        # itlist = self.currentItem()
        # itlist.selectFilter()

    # }}}
    @QtCore.pyqtSlot()  # __onSelectLong# {{{
    def __onSelectLong(self):
        logger.debug(f"{self.__class__.__name__}.__onSelectLong()")

        # itlist = self.currentItem()
        # itlist.selectLong()

    # }}}
    @QtCore.pyqtSlot()  # __onSelectShort# {{{
    def __onSelectShort(self):
        logger.debug(f"{self.__class__.__name__}.__onSelectShort()")

        # itlist = self.currentItem()
        # itlist.selectShort()

    # }}}
    @QtCore.pyqtSlot()  # __onSelectWin# {{{
    def __onSelectWin(self):
        logger.debug(f"{self.__class__.__name__}.__onSelectWin()")

        # itlist = self.currentItem()
        # itlist.selectWin()

    # }}}
    @QtCore.pyqtSlot()  # __onSelectLoss# {{{
    def __onSelectLoss(self):
        logger.debug(f"{self.__class__.__name__}.__onSelectLoss()")

        # itlist = self.currentItem()
        # itlist.selectLoss()

    # }}}
    @QtCore.pyqtSlot()  # __onSelectAssets# {{{
    def __onSelectAssets(self):
        logger.debug(f"{self.__class__.__name__}.__onSelectAssets()")

    # }}}
    @QtCore.pyqtSlot()  # __onSelectYears# {{{
    def __onSelectYears(self):
        logger.debug(f"{self.__class__.__name__}.__onSelectYears()")

    # }}}


# }}}
class _TestMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Menu.__init__(self, parent=parent)

        self.run = QtGui.QAction("Run", self)
        self.pause = QtGui.QAction("Pause", self)
        self.stop = QtGui.QAction("Stop", self)
        self.new = QtGui.QAction("New", self)
        self.copy = QtGui.QAction("Copy", self)
        self.edit = QtGui.QAction("Edit", self)
        self.rename = QtGui.QAction("Rename", self)
        self.delete = QtGui.QAction("Delete", self)

        self.addTextSeparator("Execute")
        self.addAction(self.run)
        self.addAction(self.pause)
        self.addAction(self.stop)
        self.addTextSeparator("Test")
        self.addAction(self.new)
        self.addAction(self.copy)
        self.addAction(self.edit)
        self.addAction(self.rename)
        self.addAction(self.delete)

    # }}}


# }}}
class _TradeListMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Menu.__init__(self, parent=parent)

        self.filter = QtGui.QAction("Filter ...", self)
        self.strategy = QtGui.QAction("Strategy", self)
        self.long = QtGui.QAction("Long", self)
        self.short = QtGui.QAction("Short", self)
        self.win = QtGui.QAction("Win", self)
        self.loss = QtGui.QAction("Loss", self)
        self.assets = QtGui.QAction("Assets", self)
        self.years = QtGui.QAction("Years", self)

        self.addAction(self.filter)
        self.addTextSeparator("Select")
        self.addAction(self.strategy)
        self.addAction(self.long)
        self.addAction(self.short)
        self.addAction(self.win)
        self.addAction(self.loss)
        self.addAction(self.assets)
        self.addAction(self.years)

    # }}}


# }}}


class TradeTree(QtWidgets.QTreeWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__config()
        self.__createMenus()
        self.__connect()

    # }}}
    def contextMenuEvent(self, e: QtGui.QContextMenuEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent(e)")

        item = self.itemAt(e.pos())
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()

    # }}}
    def setTradeList(self, tlist: TradeList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setTradeList()")

        self.clearTrades()
        for trade in tlist:
            item = TradeItem(trade)
            self.addTopLevelItem(item)

    # }}}
    def clearTrades(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clearTrades()")

        while self.takeTopLevelItem(0):
            pass

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        # config style
        self.setStyleSheet(Css.TREE)
        self.setContentsMargins(0, 0, 0, 0)

        # config header
        labels = list()
        for l in TradeItem.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.header().setStyleSheet(Css.TREE_HEADER)

        # config sorting
        self.setSortingEnabled(True)
        self.sortByColumn(TradeItem.Column.Date, Qt.SortOrder.AscendingOrder)

        # config width
        self.setColumnWidth(TradeItem.Column.Date, 180)
        self.setColumnWidth(TradeItem.Column.Type, 100)
        self.setColumnWidth(TradeItem.Column.Ticker, 100)
        self.setColumnWidth(TradeItem.Column.Result, 100)
        self.setColumnWidth(TradeItem.Column.PPD, 100)
        self.setMinimumWidth(600)

    # }}}
    def __createMenus(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenus()")

        self.menu = _TradeMenu(self)

    # }}}
    def __connect(self):  # {{{
        self.menu.show_chart.triggered.connect(self.__onShowChart)
        self.menu.info.triggered.connect(self.__onInfo)

    # }}}
    @QtCore.pyqtSlot()  # __onShowChart# {{{
    def __onShowChart(self):
        logger.debug(f"{self.__class__.__name__}.__onShowChart()")

    # }}}
    @QtCore.pyqtSlot()  # __onInfo# {{{
    def __onInfo(self):
        logger.debug(f"{self.__class__.__name__}.__onInfo()")

    # }}}


# }}}
class _TradeMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Menu.__init__(self, parent=parent)

        self.show_chart = QtGui.QAction("Show on chart", self)
        self.info = QtGui.QAction("Info", self)

        self.addAction(self.show_chart)
        self.addAction(self.info)

    # }}}
    def __setVisibleActions(self, item):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")

        # disable all actions
        for i in self.actions():
            i.setEnabled(False)

        # # enable availible for this item
        if item is None:
            self.info.setEnabled(False)
        elif isinstance(item, ITrade):
            self.info.setEnabled(True)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TradeTree()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
