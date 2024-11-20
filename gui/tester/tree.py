#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum
import sys

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin.company import Tester
from avin.const import TEST_DIR
from avin.core import Test
from avin.gui.custom import Dialog, Font
from avin.utils import Cmd, logger


class TestTree(QtWidgets.QTreeWidget):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0
        Progress = 1
        Trades = 2
        Block = 3
        Allow = 4

    # }}}
    def __init__(self, parent=None):  # {{{
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

    # }}}
    def __config(self):  # {{{
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

    # }}}
    def __createTestActions(self):  # {{{
        self.action_run = QtGui.QAction("Run", self)
        self.action_pause = QtGui.QAction("Pause", self)
        self.action_stop = QtGui.QAction("Stop", self)
        self.action_new = QtGui.QAction("New", self)
        self.action_copy = QtGui.QAction("Copy", self)
        self.action_edit = QtGui.QAction("Edit", self)
        self.action_rename = QtGui.QAction("Rename", self)
        self.action_delete = QtGui.QAction("Delete", self)

    # }}}
    def __createTestMenu(self):  # {{{
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

    # }}}
    def __createYearActions(self):  # {{{
        self.action_select_2018 = QtGui.QAction("Select 2018", self)
        self.action_select_2019 = QtGui.QAction("Select 2019", self)
        self.action_select_2020 = QtGui.QAction("Select 2020", self)
        self.action_select_2021 = QtGui.QAction("Select 2021", self)
        self.action_select_2022 = QtGui.QAction("Select 2022", self)
        self.action_select_2023 = QtGui.QAction("Select 2023", self)
        self.action_select_2024 = QtGui.QAction("Select 2024", self)

    # }}}
    def __createYearMenu(self):  # {{{
        self.year_menu = QtWidgets.QMenu("Select year...")
        self.year_menu.addAction(self.action_select_2018)
        self.year_menu.addAction(self.action_select_2019)
        self.year_menu.addAction(self.action_select_2020)
        self.year_menu.addAction(self.action_select_2021)
        self.year_menu.addAction(self.action_select_2022)
        self.year_menu.addAction(self.action_select_2023)
        self.year_menu.addAction(self.action_select_2024)

    # }}}
    def __createTradeListActions(self):  # {{{
        self.action_select_long = QtGui.QAction("Select long", self)
        self.action_select_short = QtGui.QAction("Select short", self)
        self.action_select_win = QtGui.QAction("Select win", self)
        self.action_select_loss = QtGui.QAction("Select loss", self)
        self.action_select_filter = QtGui.QAction("Select filter", self)

    # }}}
    def __createTradeListMenu(self):  # {{{
        self.trade_list_menu = QtWidgets.QMenu(self)
        self.trade_list_menu.addAction(self.action_select_long)
        self.trade_list_menu.addAction(self.action_select_short)
        self.trade_list_menu.addAction(self.action_select_win)
        self.trade_list_menu.addAction(self.action_select_loss)
        self.trade_list_menu.addAction(self.action_select_filter)
        self.trade_list_menu.addMenu(self.year_menu)

    # }}}
    def __connect(self):  # {{{
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

    # }}}
    def __resetActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        for i in self.actions():
            i.setEnabled(False)

    # }}}
    def __setVisibleActions(self, item):  # {{{
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

    # }}}
    def __reloadTest(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__reloadTest()")
        itest = self.thread.test
        index = self.indexFromItem(itest).row()
        self.takeTopLevelItem(index)
        path = itest.dir_path
        reloaded = ITest.load(path)
        self.addTest(reloaded)

    # }}}
    def __updateProgressBar(self, val):  # {{{
        self.thread.test.progress_bar.setValue(val)

    # }}}
    @QtCore.pyqtSlot()  # __onRun# {{{
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

    # }}}
    @QtCore.pyqtSlot()  # __onPause# {{{
    def __onPause(self):
        logger.debug(f"{self.__class__.__name__}.__onPause()")

    # }}}
    @QtCore.pyqtSlot()  # __onStop# {{{
    def __onStop(self):
        logger.debug(f"{self.__class__.__name__}.__onStop()")

    # }}}
    @QtCore.pyqtSlot()  # __threadFinished# {{{
    def __threadFinished(self):
        logger.debug(f"{self.__class__.__name__}.__threadFinished()")
        self.__reloadTest()
        self.thread = None

    # }}}
    @QtCore.pyqtSlot()  # __onNew# {{{
    def __onNew(self):
        logger.debug(f"{self.__class__.__name__}.__onNew()")
        test = self.constructor.newTest()
        if test:
            self.addTest(test)

    # }}}
    @QtCore.pyqtSlot()  # __onCopy# {{{
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

    # }}}
    @QtCore.pyqtSlot()  # __onEdit# {{{
    def __onEdit(self):
        logger.debug(f"{self.__class__.__name__}.__onEdit()")
        itest: ITest = self.currentItem()
        edited = self.constructor.editTest(itest)
        if edited:
            self.removeTest(itest)
            self.addTest(edited)

    # }}}
    @QtCore.pyqtSlot()  # __onRename# {{{
    def __onRename(self):
        logger.debug(f"{self.__class__.__name__}.__onRename()")
        itest: ITest = self.currentItem()
        new_name = Dialog.name(default=itest.name)
        if new_name:
            ITest.rename(itest, new_name)

    # }}}
    @QtCore.pyqtSlot()  # __onDelete# {{{
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.delete()")
        result = Dialog.confirm()
        if result:
            itest = self.currentItem()
            logger.info(f"Delete test '{itest.name}'")
            Test.delete(itest)
            self.removeTest(itest)
        else:
            logger.info("Cancel delete")

    # }}}
    @QtCore.pyqtSlot()  # __onSelectLong# {{{
    def __onSelectLong(self):
        logger.debug(f"{self.__class__.__name__}.selectLong()")
        itlist = self.currentItem()
        itlist.selectLong()

    # }}}
    @QtCore.pyqtSlot()  # __onSelectShort# {{{
    def __onSelectShort(self):
        logger.debug(f"{self.__class__.__name__}.selectShort()")
        itlist = self.currentItem()
        itlist.selectShort()

    # }}}
    @QtCore.pyqtSlot()  # __onSelectWin# {{{
    def __onSelectWin(self):
        logger.debug(f"{self.__class__.__name__}.selectWin()")
        itlist = self.currentItem()
        itlist.selectWin()

    # }}}
    @QtCore.pyqtSlot()  # __onSelectLoss# {{{
    def __onSelectLoss(self):
        logger.debug(f"{self.__class__.__name__}.selectWin()")
        itlist = self.currentItem()
        itlist.selectLoss()

    # }}}
    @QtCore.pyqtSlot()  # __onSelectFilter# {{{
    def __onSelectFilter(self):
        logger.debug(f"{self.__class__.__name__}.selectWin()")
        itlist = self.currentItem()
        itlist.selectFilter()

    # }}}
    def contextMenuEvent(self, e: QtGui.QContextMenuEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent(e)")
        item = self.itemAt(e.pos())
        # if item is None:
        #     self.test_menu.exec()
        if isinstance(item, ITest):
            self.test_menu.exec(QtGui.QCursor.pos())
        elif isinstance(item, ITradeList):
            self.trade_list_menu.exec(QtGui.QCursor.pos())
        return e.ignore()

    # }}}
    def addTest(self, itest: ITest):  # {{{
        logger.debug(f"{self.__class__.__name__}.addTest()")
        self.addTopLevelItem(itest)
        itest.setParent(self)
        itest.updateProgressBar()

    # }}}
    def removeTest(self, itest):  # {{{
        logger.debug(f"{self.__class__.__name__}.removeTest()")
        index = self.indexFromItem(itest).row()
        self.takeTopLevelItem(index)


# }}}


# }}}
class TradeTree(QtWidgets.QTreeWidget):  # {{{
    class Column(enum.IntEnum):  # {{{
        Date = 0
        Result = 1

    # }}}
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createMenu()
        self.__connect()

    # }}}
    def __config(self):  # {{{
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

    # }}}
    def __createMenu(self):  # {{{
        self.action_info = QtGui.QAction("Info", self)
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.action_info)

    # }}}
    def __connect(self):  # {{{
        self.action_info.triggered.connect(self.__onInfo)

    # }}}
    def __resetActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        for i in self.menu.actions():
            i.setEnabled(False)

    # }}}
    def __setVisibleActions(self, item):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            self.action_info.setEnabled(False)
        elif isinstance(item, ITrade):
            self.action_info.setEnabled(True)

    # }}}
    @QtCore.pyqtSlot()  # __onInfo# {{{
    def __onInfo(self):
        logger.debug(f"{self.__class__.__name__}.__onInfo()")
        itrade: ITrade = self.currentItem()
        Dialog.info(str(itrade))

    # }}}
    def contextMenuEvent(self, e: QtGui.QContextMenuEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent(e)")
        item = self.itemAt(e.pos())
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()


# }}}
# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TestWidget()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
