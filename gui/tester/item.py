#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from avin import (
    Asset,
    Filter,
    FilterList,
    Test,
    Trade,
    TradeList,
    Usr,
    logger,
)
from gui.tester.progress_bar import TestProgressBar
from gui.tester.thread import Thread


class TestItem(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0
        Status = 1
        Trades = 2

    # }}}

    def __init__(self, test: Test, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.test = test
        self.progress_bar = TestProgressBar()
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        )

        self.updateText()
        self.__createTradeListChild()

    # }}}

    def updateText(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.update()")

        self.setText(self.Column.Name, self.test.name)
        self.setText(self.Column.Status, self.test.status.name)
        self.setText(self.Column.Trades, str(len(self.test.trade_list)))

    # }}}
    def updateProgressBar(self):  # {{{
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
                self, TestTree.Column.Progress, self.progress_bar
            )

    # }}}

    def __createTradeListChild(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createTradeListChild()")

        if self.test.status != Test.Status.COMPLETE:
            return

        tlist_item = TradeListItem(self.test.trade_list)
        self.addChild(tlist_item)

    # }}}


# }}}
class TradeListItem(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0
        _ = 1
        Trades = 2
        Win = 3
        Loss = 4

    # }}}

    def __init__(self, trade_list: TradeList, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.trade_list = trade_list

        # flags
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        )

        # text
        has_parent = trade_list.parent_list is not None
        name = trade_list.subname if has_parent else "trades"
        self.setText(self.Column.Name, name)
        self.setText(self.Column.Trades, str(len(trade_list)))
        self.setText(self.Column.Win, "???")
        self.setText(self.Column.Loss, "???")

        # text align
        right = Qt.AlignmentFlag.AlignRight
        self.setTextAlignment(self.Column.Trades, right)
        self.setTextAlignment(self.Column.Win, right)
        self.setTextAlignment(self.Column.Loss, right)

        self.__createChilds()

    # }}}

    def selectFilter(self, f: Filter) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectFilter()")

        child = Thread.selectFilter(self.trade_list, f)
        child_item = TradeListItem(child)
        self.addChild(child_item)

    # }}}
    def selectFilterList(self, filter_list: FilterList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectFilter()")

        child = Thread.selectFilterList(self.trade_list, filter_list)
        child_item = TradeListItem(child)
        self.addChild(child_item)
        self.setExpanded(True)

    # }}}
    def selectStrategy(self, name: str, version: str) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectStrategy()")

        child = self.trade_list.selectStrategy(name, version)
        child_item = TradeListItem(child)
        self.addChild(child_item)

    # }}}
    def selectStrategys(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectStrategys()")

        childs = self.trade_list.selectStrategys()
        for child in childs:
            child_item = TradeListItem(child)
            self.addChild(child_item)

    # }}}
    def selectLong(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectLong()")

        child = self.trade_list.selectLong()
        child_item = TradeListItem(child)
        self.addChild(child_item)

    # }}}
    def selectShort(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectShort()")

        child = self.trade_list.selectShort()
        child_item = TradeListItem(child)
        self.addChild(child_item)

    # }}}
    def selectWin(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectWin()")

        child = self.trade_list.selectWin()
        child_item = TradeListItem(child)
        self.addChild(child_item)

    # }}}
    def selectLoss(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectLoss()")

        child = self.trade_list.selectLoss()
        child_item = TradeListItem(child)
        self.addChild(child_item)

    # }}}
    def selectAsset(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectAsset()")

        child = self.trade_list.selectAsset(asset)
        child_item = TradeListItem(child)
        self.addChild(child_item)

    # }}}
    def selectAssets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectAsset()")

        childs = self.trade_list.selectAssets()
        for child in childs:
            child_item = TradeListItem(child)
            self.addChild(child_item)

    # }}}
    def selectYear(self, year: int) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectYear()")

        child = self.trade_list.selectYear(year)
        child_item = TradeListItem(child)
        self.addChild(child_item)

    # }}}
    def clearChilds(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clearChilds()")

        self.trade_list.clearChilds()
        while self.takeChild(0):
            pass

    # }}}

    def __createChilds(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createChilds()")

        for child_list in self.trade_list.childs:
            item = TradeListItem(child_list)
            self.addChild(item)

    # }}}


# }}}
class TradeItem(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):  # {{{
        Date = 0
        Type = 1
        Ticker = 2
        Status = 3
        Result = 4
        PPD = 5

    # }}}
    def __init__(self, trade: Trade, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.trade = trade

        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        )

        dt = trade.dt + Usr.TIME_DIF
        dt = dt.strftime("%Y-%m-%d  %H:%M")
        self.setText(self.Column.Date, dt)
        self.setText(self.Column.Type, trade.type.name)
        self.setText(self.Column.Ticker, trade.instrument.ticker)
        self.setText(self.Column.Status, trade.status.name)

        if trade.status == Trade.Status.CLOSED:
            self.setText(self.Column.Result, str(trade.result()))
            self.setText(self.Column.PPD, str(trade.percentPerDay()))

    # }}}


# }}}


if __name__ == "__main__":
    ...
