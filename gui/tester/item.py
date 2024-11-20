#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from avin.const import MSK_TIME_DIF
from avin.core import Asset, Test, Trade, TradeList
from avin.gui.custom import ProgressBar
from avin.utils import Cmd, logger


class ITrade(Trade, QtWidgets.QTreeWidgetItem):  # {{{
    def __init__(self, info: dict, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Trade.__init__(self, info, parent)
        self.__config()
        self.gtrade = None  # link to GTrade

    # }}}
    def __config(self):  # {{{
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        )
        dt = self.dt + MSK_TIME_DIF
        dt = dt.strftime("%Y-%m-%d  %H:%M")
        self.setText(TradeTree.Column.Date, dt)
        self.setText(TradeTree.Column.Result, str(self.result))


# }}}
# }}}
class ITradeList(TradeList, QtWidgets.QTreeWidgetItem):  # {{{
    def __init__(self, name, trades=None, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        TradeList.__init__(self, name, trades, parent)
        self.__config()
        self.updateText()

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        )
        self.setTextAlignment(
            TestTree.Column.Trades, Qt.AlignmentFlag.AlignRight
        )
        self.setTextAlignment(
            TestTree.Column.Block, Qt.AlignmentFlag.AlignRight
        )
        self.setTextAlignment(
            TestTree.Column.Allow, Qt.AlignmentFlag.AlignRight
        )

    # }}}
    def _createChild(self, trades, suffix):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createChild()")
        child_name = "-" + self.name.replace("tlist", "") + f" {suffix}"
        child = ITradeList(name=child_name, trades=trades, parent=self)
        child._asset = self.asset
        self._childs.append(child)
        return child

    # }}}
    @staticmethod  # load# {{{
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

    # }}}
    def updateText(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__updateText()")
        self.setText(TestTree.Column.Name, self.name)
        self.setText(TestTree.Column.Trades, str(self.count))

    # }}}
    def selectAsset(self, asset: Asset):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectAsset()")
        selected = list()
        for trade in self._trades:
            if trade.asset.figi == asset.figi:
                selected.append(trade)
        child = self._createChild(selected, asset.ticker)
        child._asset = asset
        return child

    # }}}
    def selectLong(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectLong()")
        selected = list()
        for trade in self._trades:
            if trade.isLong():
                selected.append(trade)
        child = self._createChild(selected, "long")
        return child

    # }}}
    def selectShort(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectShort()")
        selected = list()
        for trade in self._trades:
            if trade.isShort():
                selected.append(trade)
        child = self._createChild(selected, "short")
        return child

    # }}}
    def selectWin(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectWin()")
        selected = list()
        for trade in self._trades:
            if trade.isWin():
                selected.append(trade)
        child = self._createChild(selected, "win")
        return child

    # }}}
    def selectLoss(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectLoss()")
        selected = list()
        for trade in self._trades:
            if trade.isLoss():
                selected.append(trade)
        child = self._createChild(selected, "loss")
        return child

    # }}}
    def selectYear(self, year):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectYear()")
        selected = list()
        for trade in self._trades:
            trade_year = trade.dt.year
            if trade_year == year:
                selected.append(trade)
        child = self._createChild(selected, year)
        return child

    # }}}
    def selectBack(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectBack()")
        selected = list()
        for trade in self._trades:
            if trade.isBack():
                selected.append(trade)
        child = self._createChild(selected, "back")
        return child

    # }}}
    def selectForward(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.selectForward()")
        selected = list()
        for trade in self._trades:
            if trade.isForward():
                selected.append(trade)
        child = self._createChild(selected, "forward")
        return child


# }}}
# }}}
class ITest(Test, QtWidgets.QTreeWidgetItem):  # {{{
    def __init__(self, name, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Test.__init__(self, name)
        self.__parent = parent
        self.__createProgressBar()
        self.__config()
        self.updateText()

    # }}}
    def __createProgressBar(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createProgressBar()")
        self.progress_bar = ProgressBar()

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        )

    # }}}
    def __createSubgroups(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createSubgroups()")
        for asset in self.alist:
            self.tlist.selectAsset(asset)

    # }}}
    def _loadTrades(self):  # {{{
        logger.debug(f"{self.__class__.__name__}._loadTrades()")
        file_path = Cmd.join(self.dir_path, "tlist.tl")
        if Cmd.isExist(file_path):
            self._tlist = ITradeList.load(file_path, parent=self)
            return True
        else:
            self._tlist = ITradeList(name="tlist", parent=self)
            return False

    # }}}
    @staticmethod  # load# {{{
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

    # }}}
    @staticmethod  # rename# {{{
    def rename(test, new_name):
        Test.rename(test, new_name)
        test.updateText()
        test.updateProgressBar()

    # }}}
    def parent(self):  # {{{
        return self.__parent

    # }}}
    def setParent(self, parent):  # {{{
        self.__parent = parent

    # }}}
    def updateText(self):  # {{{
        self.setText(TestTree.Column.Name, self.name)

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
# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TestWidget()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
