#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from avin import Filter, FilterList, Summary, TradeList, logger
from gui.custom import Css, Menu
from gui.filter.dialog_select import FilterSelectDialog
from gui.summary.item import TradeListItem


class TradeListTree(QtWidgets.QTreeWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__config()
        self.__createMenus()
        self.__connect()

        self.thread = None
        self.filter_select_dialog = None

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
            pass
        elif isinstance(self.__current_item, TradeListItem):
            self.tlist_menu.exec(QtGui.QCursor.pos())

        return e.ignore()

    # }}}
    def setTradeList(self, trade_list: TradeList):  # {{{
        logger.debug(f"{self.__class__.__name__}.setTradeList()")

        self.clear()
        item = TradeListItem(trade_list)
        self.addTopLevelItem(item)

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        # config header
        labels = Summary.header()
        self.setHeaderLabels(labels)
        self.header().setStyleSheet(Css.TREE_HEADER)

        # config sorting
        # self.setSortingEnabled(True)
        # self.sortByColumn(TestItem.Column.Name, Qt.SortOrder.AscendingOrder)

        # config width
        self.setColumnWidth(0, 400)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 60)
        self.setColumnWidth(3, 50)
        self.setColumnWidth(4, 50)
        self.setColumnWidth(5, 50)
        self.setColumnWidth(6, 50)
        self.setColumnWidth(7, 70)
        self.setColumnWidth(8, 100)
        self.setColumnWidth(9, 100)
        self.setColumnWidth(10, 50)
        self.setColumnWidth(11, 50)
        self.setColumnWidth(12, 80)
        self.setColumnWidth(13, 80)
        self.setColumnWidth(14, 80)
        self.setColumnWidth(15, 80)

        # config style
        self.setStyleSheet(Css.TREE)
        self.setContentsMargins(0, 0, 0, 0)

    # }}}
    def __createMenus(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenus()")

        self.tlist_menu = _TradeListMenu(self)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.tlist_menu.filter.triggered.connect(self.__onSelectFilter)
        self.tlist_menu.any_of.triggered.connect(self.__onAnyOf)
        self.tlist_menu.strategy.triggered.connect(self.__onSelectStrategy)
        self.tlist_menu.long_short.triggered.connect(self.__onSelectLongShort)
        self.tlist_menu.win_loss.triggered.connect(self.__onSelectWinLoss)
        self.tlist_menu.assets.triggered.connect(self.__onSelectAssets)
        self.tlist_menu.years.triggered.connect(self.__onSelectYears)
        self.tlist_menu.clear.triggered.connect(self.__onClearChilds)

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
    w = TradeListTree()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
