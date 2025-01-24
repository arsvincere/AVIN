#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from avin import Filter, FilterList, Test, TestList, logger
from gui.custom import Css, Dialog, Menu
from gui.filter.dialog_select import FilterSelectDialog
from gui.tester.dialog_test_edit import TestEditDialog
from gui.tester.dialog_test_select import TestSelectDialog
from gui.tester.item import TestItem, TestListItem
from gui.tester.thread import Thread, TRunTest


class TestTree(QtWidgets.QTreeWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__config()
        self.__createMenus()
        self.__connect()

        self.thread = None
        self.filter_select_dialog = None
        self.test_select_dialog = None

    # }}}
    def __iter__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__iter__()")

        all_items = list()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            all_items.append(item)

        return iter(all_items)

    # }}}

    def contextMenuEvent(self, e: QtGui.QContextMenuEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent(e)")

        self.__current_item = self.itemAt(e.pos())

        if self.__current_item is None:
            self.test_menu.setVisibleActions(self.__current_item)
            self.test_menu.exec(QtGui.QCursor.pos())
        if isinstance(self.__current_item, TestItem):
            self.test_menu.setVisibleActions(self.__current_item)
            self.test_menu.exec(QtGui.QCursor.pos())

        return e.ignore()

    # }}}
    def addTest(self, test: Test) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.addTest()")

        item = TestItem(test)
        self.addTopLevelItem(item)

    # }}}
    def addTestList(self, test_list: TestList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.addTest()")

        item = TestListItem(test_list)
        self.addTopLevelItem(item)

    # }}}
    def removeTest(self, test: Test) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.removeTest()")

        for item in self:
            if item.test.name == test.name:
                index = self.indexFromItem(item).row()
                self.takeTopLevelItem(index)

    # }}}
    def removeTestList(self, test_list: TestList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.removeTestList()")

        for item in self:
            if item.test_list.name == test_list.name:
                index = self.indexFromItem(item).row()
                self.takeTopLevelItem(index)

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
        # self.setSortingEnabled(True)
        # self.sortByColumn(TestItem.Column.Name, Qt.SortOrder.AscendingOrder)

        # config width
        self.setColumnWidth(TestItem.Column.Name, 250)
        self.setColumnWidth(TestItem.Column.Status, 80)
        self.setMinimumWidth(350)

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
        self.test_menu.load.triggered.connect(self.__onLoad)
        self.test_menu.copy.triggered.connect(self.__onCopy)
        self.test_menu.edit.triggered.connect(self.__onEdit)
        self.test_menu.rename.triggered.connect(self.__onRename)
        self.test_menu.delete.triggered.connect(self.__onDelete)

        self.tlist_menu.filter.triggered.connect(self.__onSelectFilter)
        self.tlist_menu.any_of.triggered.connect(self.__onAnyOf)
        self.tlist_menu.strategy.triggered.connect(self.__onSelectStrategy)
        self.tlist_menu.long_short.triggered.connect(self.__onSelectLongShort)
        self.tlist_menu.win_loss.triggered.connect(self.__onSelectWinLoss)
        self.tlist_menu.assets.triggered.connect(self.__onSelectAssets)
        self.tlist_menu.years.triggered.connect(self.__onSelectYears)
        self.tlist_menu.clear.triggered.connect(self.__onClearChilds)

    # }}}

    def __isBusy(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__isBusy()")

        if self.thread is not None:
            Dialog.info("Tester is busy now, wait for complete test")
            return True

        return False

    # }}}
    @QtCore.pyqtSlot()  # __onTestComplete# {{{
    def __onTestComplete(self):
        logger.debug(f"{self.__class__.__name__}.__onTestComplete()")

        # find and update test item text
        test = self.thread.test
        # for item in self:
        #     if item.test.name == test.name:
        #         item.updateText()

        # reload test
        self.removeTest(test)
        test = Thread.loadTest(test.name)
        self.addTest(test)

        self.thread = None

    # }}}

    @QtCore.pyqtSlot()  # __onRun# {{{
    def __onRun(self):
        logger.debug(f"{self.__class__.__name__}.__onRun()")

        if self.__isBusy():
            return

        if self.__current_item is None:
            return

        test = self.__current_item.test

        self.thread = TRunTest(test)
        self.thread.finished.connect(self.__onTestComplete)
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

    @QtCore.pyqtSlot()  # __onNew# {{{
    def __onNew(self):
        logger.debug(f"{self.__class__.__name__}.__onNew()")

        dial = TestEditDialog()
        test = dial.newTest()
        if test:
            self.addTest(test)

    # }}}
    @QtCore.pyqtSlot()  # __onLoad# {{{
    def __onLoad(self):
        logger.debug(f"{self.__class__.__name__}.__onLoad()")

        if self.test_select_dialog is None:
            self.test_select_dialog = TestSelectDialog()

        name = self.test_select_dialog.selectTestListName()
        if name is None:
            return

        test_list = Thread.loadTestList(name)
        self.removeTestList(test_list)  # если его уже грузили, передобавить
        self.addTestList(test_list)

    # }}}
    @QtCore.pyqtSlot()  # __onCopy# {{{
    def __onCopy(self):
        logger.debug(f"{self.__class__.__name__}.__onCopy()")

        test = self.__current_item.test

        new_name = Dialog.name(test.name)
        if not new_name:
            return

        test = self.__current_item.test

        new_test = Thread.copyTest(test, new_name)
        if new_test:
            new_item = TestItem(new_test)
            self.addTopLevelItem(new_item)
            self.setCurrentItem(new_item)

    # }}}
    @QtCore.pyqtSlot()  # __onEdit# {{{
    def __onEdit(self):
        logger.debug(f"{self.__class__.__name__}.__onEdit()")

        item = self.__current_item
        test = item.test

        dial = TestEditDialog()
        edited = dial.editTest(test)
        if edited:
            self.removeTest(test)
            self.addTest(edited)

    # }}}
    @QtCore.pyqtSlot()  # __onRename# {{{
    def __onRename(self):
        logger.debug(f"{self.__class__.__name__}.__onRename()")

        # get current test
        item = self.__current_item
        test = self.__current_item.test

        # enter new name
        new_name = Dialog.name(f"{test.name}")
        if not new_name:
            return

        # try rename test
        renamed_test = Thread.renameTest(test, new_name)
        if not renamed_test:
            return

        # delete old item from tree, add renamed test
        self.removeTest(test)
        self.addTest(renamed_test)

    # }}}
    @QtCore.pyqtSlot()  # __onDelete# {{{
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.delete()")

        if not Dialog.confirm():
            return

        test = self.__current_item.test

        # delete test
        Thread.deleteTest(test)

        # delete item from tree
        self.removeTest(test)

    # }}}

    @QtCore.pyqtSlot()  # __onSelectFilter# {{{
    def __onSelectFilter(self):
        logger.debug(f"{self.__class__.__name__}.__onSelectFilter()")

        if self.filter_select_dialog is None:
            self.filter_select_dialog = FilterSelectDialog()

        f = self.filter_select_dialog.selectFilter()
        if f is None:
            return

        trade_list_item = self.__current_item
        if isinstance(f, Filter):
            trade_list_item.selectFilter(f)
        elif isinstance(f, FilterList):
            trade_list_item.selectFilterList(f)

    # }}}
    @QtCore.pyqtSlot()  # __onAnyOf# {{{
    def __onAnyOf(self):
        logger.debug(f"{self.__class__.__name__}.__onAnyOf()")

        if self.filter_select_dialog is None:
            self.filter_select_dialog = FilterSelectDialog()

        f = self.filter_select_dialog.selectFilter()
        if f is None:
            return

        trade_list_item = self.__current_item
        if isinstance(f, Filter):
            logger.error("Select FilterList, not simple Filter")
        elif isinstance(f, FilterList):
            trade_list_item.anyOfFilterList(f)

    # }}}
    @QtCore.pyqtSlot()  # __onSelectStrategy# {{{
    def __onSelectStrategy(self):
        logger.debug(f"{self.__class__.__name__}.__onSelectStrategy()")

        trade_list_item = self.__current_item
        trade_list_item.selectStrategys()

    # }}}
    @QtCore.pyqtSlot()  # __onSelectLongShort# {{{
    def __onSelectLongShort(self):
        logger.debug(f"{self.__class__.__name__}.__onSelectLongShort()")

        trade_list_item = self.__current_item
        trade_list_item.selectLong()
        trade_list_item.selectShort()

    # }}}
    @QtCore.pyqtSlot()  # __onSelectWinLoss# {{{
    def __onSelectWinLoss(self):
        logger.debug(f"{self.__class__.__name__}.__onSelectWinLoss()")

        trade_list_item = self.__current_item
        trade_list_item.selectWin()
        trade_list_item.selectLoss()

    # }}}
    @QtCore.pyqtSlot()  # __onSelectAssets# {{{
    def __onSelectAssets(self):
        logger.debug(f"{self.__class__.__name__}.__onSelectAssets()")

        trade_list_item = self.__current_item
        trade_list_item.selectAssets()

    # }}}
    @QtCore.pyqtSlot()  # __onSelectYears# {{{
    def __onSelectYears(self):
        logger.debug(f"{self.__class__.__name__}.__onSelectYears()")

        item = self.__current_item
        trade_list = item.trade_list
        test = trade_list.owner
        for year in range(test.begin.year, test.end.year):
            item.selectYear(year)

    # }}}
    @QtCore.pyqtSlot()  # __onClearChilds# {{{
    def __onClearChilds(self):
        logger.debug(f"{self.__class__.__name__}.__onClearChilds()")

        trade_list_item = self.__current_item
        trade_list_item.clearChilds()

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
        self.load = QtGui.QAction("Load", self)
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
        self.addAction(self.load)
        self.addAction(self.copy)
        self.addAction(self.edit)
        self.addAction(self.rename)
        self.addAction(self.delete)

    # }}}

    def setVisibleActions(self, item):  # {{{
        logger.debug(f"{self.__class__.__name__}.setVisibleActions()")

        # disable all actions
        for i in self.actions():
            i.setEnabled(False)

        # # enable availible for this item
        if item is None:
            self.new.setEnabled(True)
            self.load.setEnabled(True)
        elif isinstance(item, TestItem):
            self.run.setEnabled(True)
            self.pause.setEnabled(True)
            self.stop.setEnabled(True)
            self.new.setEnabled(True)
            self.load.setEnabled(True)
            self.copy.setEnabled(True)
            self.edit.setEnabled(True)
            self.rename.setEnabled(True)
            self.delete.setEnabled(True)

    # }}}


# }}}
class _TradeListMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Menu.__init__(self, parent=parent)

        self.filter = QtGui.QAction("Filter ...", self)
        self.any_of = QtGui.QAction("Any of ...", self)
        self.strategy = QtGui.QAction("Strategy", self)
        self.long_short = QtGui.QAction("Long/Short", self)
        self.win_loss = QtGui.QAction("Win/Loss", self)
        self.assets = QtGui.QAction("Assets", self)
        self.years = QtGui.QAction("Years", self)
        self.clear = QtGui.QAction("Clear childs", self)

        self.addAction(self.filter)
        self.addAction(self.any_of)
        self.addTextSeparator("Select")
        self.addAction(self.strategy)
        self.addAction(self.long_short)
        self.addAction(self.win_loss)
        self.addAction(self.assets)
        self.addAction(self.years)
        self.addAction(self.clear)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TradeTree()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
