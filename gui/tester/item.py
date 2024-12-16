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

from avin.config import Usr
from avin.core import Asset, Trade, TradeList
from avin.tester import Test
from avin.utils import logger
from gui.tester.progress_bar import TestProgressBar


class TestItem(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0
        Status = 1
        Trades = 2
        Win = 3
        Loss = 4

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

    def __createTradeListChild(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__createTradeListChild()")

        if self.test.status != Test.Status.COMPLETE:
            return

        tlist_item = TradeListItem(self.test.trade_list)
        self.addChild(tlist_item)


# }}}
class TradeListItem(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0
        _ = 1
        Trades = 2
        Win = 3
        Loss = 4

    # }}}

    def __init__(self, tlist: TradeList, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.tlist = tlist

        # flags
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        )

        # text
        has_parent = tlist.parent_tlist is not None
        name = tlist.subname if has_parent else "trades"
        self.setText(self.Column.Name, name)
        self.setText(self.Column.Trades, str(len(tlist)))
        self.setText(self.Column.Win, "???")
        self.setText(self.Column.Loss, "???")

        # text align
        right = Qt.AlignmentFlag.AlignRight
        self.setTextAlignment(self.Column.Trades, right)
        self.setTextAlignment(self.Column.Win, right)
        self.setTextAlignment(self.Column.Loss, right)

    # }}}

    def selectStrategy(self, name: str, version: str) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectStrategy()")

        child = self.tlist.selectStrategy(name, version)
        child_item = TradeListItem(child)
        self.addChild(child_item)

    # }}}
    def selectLong(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectLong()")

        child = self.tlist.selectLong()
        child_item = TradeListItem(child)
        self.addChild(child_item)

    # }}}
    def selectShort(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectShort()")

        child = self.tlist.selectShort()
        child_item = TradeListItem(child)
        self.addChild(child_item)

    # }}}
    def selectWin(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectWin()")

        child = self.tlist.selectWin()
        child_item = TradeListItem(child)
        self.addChild(child_item)

    # }}}
    def selectLoss(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectLoss()")

        child = self.tlist.selectLoss()
        child_item = TradeListItem(child)
        self.addChild(child_item)

    # }}}
    def selectAsset(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectAsset()")

        child = self.tlist.selectAsset(asset)
        child_item = TradeListItem(child)
        self.addChild(child_item)

    # }}}
    def selectYear(self, year: int) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectYear()")

        child = self.tlist.selectYear(year)
        child_item = TradeListItem(child)
        self.addChild(child_item)

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
            self.setText(self.Column.PPD, str(trade.percentPerDay()) + "%")

    # }}}


# }}}


if __name__ == "__main__":
    ...
