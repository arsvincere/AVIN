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
    Summary,
    TradeList,
    logger,
)
from gui.tester.thread import Thread


class TradeListItem(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0
        Profit = 1
        Accuracy = 2
        Trades = 3
        Win = 4
        Loss = 5
        Ratio = 6
        Avg = 7
        GrossProfit = 8
        GrossLoss = 9
        WSeq = 10
        LSeq = 11
        AvgWin = 12
        AvgLoss = 13
        MaxWin = 14
        MaxLoss = 15

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
        name = trade_list.subname if has_parent else trade_list.name
        self.setText(self.Column.Name, name)

        # # text align
        # right = Qt.AlignmentFlag.AlignRight
        # self.setTextAlignment(self.Column.Trades, right)
        # self.setTextAlignment(self.Column.Win, right)
        # self.setTextAlignment(self.Column.Loss, right)

        self.__calcSummary()
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
    def anyOfFilterList(self, filter_list: FilterList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.selectFilter()")

        child = Thread.anyOfFilterList(self.trade_list, filter_list)
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

    def __calcSummary(self):  # {{{
        summary = Summary(self.trade_list)

        self.setText(self.Column.Profit, str(summary.profit))
        self.setText(self.Column.Accuracy, str(summary.accuracy))
        self.setText(self.Column.Trades, str(summary.trades))
        self.setText(self.Column.Win, str(summary.win))
        self.setText(self.Column.Loss, str(summary.loss))
        self.setText(self.Column.Ratio, str(summary.ratio))
        self.setText(self.Column.Avg, str(summary.avg))
        self.setText(self.Column.GrossProfit, str(summary.gross_profit))
        self.setText(self.Column.GrossLoss, str(summary.gross_loss))
        self.setText(self.Column.WSeq, str(summary.wseq))
        self.setText(self.Column.LSeq, str(summary.lseq))
        self.setText(self.Column.AvgWin, str(summary.avg_win))
        self.setText(self.Column.AvgLoss, str(summary.avg_loss))
        self.setText(self.Column.MaxWin, str(summary.max_win))
        self.setText(self.Column.MaxLoss, str(summary.max_loss))

    # }}}
    def __createChilds(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createChilds()")

        for child_list in self.trade_list.childs:
            item = TradeListItem(child_list)
            self.addChild(item)

    # }}}


# }}}


if __name__ == "__main__":
    ...
