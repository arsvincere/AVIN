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

from avin import TradeList, logger
from gui.custom import Css, Menu
from gui.trade.dialog_trade_info import TradeInfoDialog
from gui.trade.item import TradeItem


class TradeTree(QtWidgets.QTreeWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__config()
        self.__createMenus()
        self.__connect()

        self.__current_item = None

    # }}}

    def mouseDoubleClickEvent(self, e: QtGui.QMouseEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.mouseDoubleClickEvent(e)")

        trade = self.currentItem().trade
        dial = TradeInfoDialog()
        dial.showTradeInfo(trade)

        return e.ignore()

    # }}}
    def contextMenuEvent(self, e: QtGui.QContextMenuEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent(e)")

        self.__current_item = self.itemAt(e.pos())
        self.menu.setVisibleActions(self.__current_item)
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
        self.setColumnWidth(TradeItem.Column.Date, 160)
        self.setColumnWidth(TradeItem.Column.Type, 60)
        self.setColumnWidth(TradeItem.Column.Ticker, 60)
        self.setColumnWidth(TradeItem.Column.Status, 70)
        self.setColumnWidth(TradeItem.Column.Result, 70)
        self.setColumnWidth(TradeItem.Column.PPD, 60)
        self.setMinimumWidth(500)

    # }}}
    def __createMenus(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenus()")

        self.menu = _TradeMenu(self)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.menu.info.triggered.connect(self.__onInfo)

    # }}}

    @QtCore.pyqtSlot()  # __onInfo# {{{
    def __onInfo(self):
        logger.debug(f"{self.__class__.__name__}.__onInfo()")

        trade = self.__current_item.trade
        dial = TradeInfoDialog()
        dial.showTradeInfo(trade)

    # }}}


# }}}
class _TradeMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Menu.__init__(self, parent=parent)

        self.info = QtGui.QAction("Info", self)

        self.addAction(self.info)

    # }}}
    def setVisibleActions(self, item):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")

        # disable all actions
        for i in self.actions():
            i.setEnabled(False)

        # # enable availible for this item
        if item is None:
            self.info.setEnabled(False)
        elif isinstance(item, TradeItem):
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
