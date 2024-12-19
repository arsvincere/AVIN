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
import logging
from datetime import datetime, date, time
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from avin.core import Portfolio
from avin.gui.custom import Palette, Font
logger = logging.getLogger("LOGGER")

class ICash(Portfolio.Cash, QtWidgets.QTreeWidgetItem):
    def __init__(self, pos, parent):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Portfolio.Cash.__init__(
            self,
            pos.currency,
            pos.value,
            pos.block,
            )
        self.__config()

    def __config(self):
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(Tree.Column.Name, self.currency)
        self.setText(Tree.Column.Balance, str(self.value))
        self.setText(Tree.Column.Block, str(self.block))


class IShare(Portfolio.Share, QtWidgets.QTreeWidgetItem):
    def __init__(self, pos, parent):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Portfolio.Share.__init__(
            self,
            pos.share,
            pos.balance,
            pos.block,
            pos.ID,
            pos.full_responce,
            )
        self.__config()

    def __config(self):
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(Tree.Column.Name, self.share.ticker)
        self.setText(Tree.Column.Balance, str(self.balance))
        self.setText(Tree.Column.Block, str(self.block))
        self.setText(Tree.Column.ID, self.ID)


class IBound(Portfolio.Bound, QtWidgets.QTreeWidgetItem):
    def __init__(self, pos, parent):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Portfolio.Bound.__init__(self)
        self.__config()

    def __config(self):
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(Tree.Column.Name, "WRITE_ME")


class IFuture(Portfolio.Future, QtWidgets.QTreeWidgetItem):
    def __init__(self, pos, parent):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Portfolio.Future.__init__(self)
        self.__config()

    def __config(self):
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(Tree.Column.Name, "WRITE_ME")


class IOption(Portfolio.Option, QtWidgets.QTreeWidgetItem):
    def __init__(self, pos, parent):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Portfolio.Option.__init__(self)
        self.__config()

    def __config(self):
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(Tree.Column.Name, "WRITE_ME")


class IPortfolio(Portfolio, QtWidgets.QTreeWidgetItem):
    def __init__(
            self,
            account: object,
            money: list,
            shares: list,
            bounds: list,
            futures: list,
            options: list,
            parent=None
            ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Portfolio.__init__(
            self, money, shares, bounds, futures, options
            )
        self.__account = account
        self.__config()
        self.__createChilds()
        self.setExpanded(True)

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        title = f"{self.__account.name} (id={self.__account.ID})"
        self.setText(Tree.Column.Name, title)

    def __createChilds(self):
        logger.debug(f"{self.__class__.__name__}.__createChilds()")
        self.__createMoney()
        self.__createShares()
        self.__createBounds()
        self.__createFutures()
        self.__createOptions()

    def __createMoney(self):
        logger.debug(f"{self.__class__.__name__}.__createMoney()")
        money_group = QtWidgets.QTreeWidgetItem(self)
        money_group.setText(Tree.Column.Name, "Money")
        for pos in self.money:
            item = IPortfolio.ICash(pos, parent=money_group)

    def __createShares(self):
        logger.debug(f"{self.__class__.__name__}.__createMoney()")
        group = QtWidgets.QTreeWidgetItem(self)
        group.setText(Tree.Column.Name, "Shares")
        for pos in self.shares:
            item = IPortfolio.IShare(pos, parent=group)

    def __createBounds(self):
        logger.debug(f"{self.__class__.__name__}.__createMoney()")
        group = QtWidgets.QTreeWidgetItem(self)
        group.setText(Tree.Column.Name, "Bounds")
        for pos in self.bounds:
            item = IPortfolio.IBound(pos, parent=group)

    def __createFutures(self):
        logger.debug(f"{self.__class__.__name__}.__createMoney()")
        group = QtWidgets.QTreeWidgetItem(self)
        group.setText(Tree.Column.Name, "Futures")
        for pos in self.futures:
            item = IPortfolio.IFuture(pos, parent=group)

    def __createOptions(self):
        logger.debug(f"{self.__class__.__name__}.__createMoney()")
        group = QtWidgets.QTreeWidgetItem(self)
        group.setText(Tree.Column.Name, "Options")
        for pos in self.options:
            item = IPortfolio.IOption(pos, parent=group)

    @staticmethod  #fromPortfolio
    def fromPortfolio(iaccount, portfolio, parent=None):
        item = IPortfolio(
            account=iaccount,
            money=portfolio.money,
            shares=portfolio.shares,
            bounds=portfolio.bounds,
            futures=portfolio.futures,
            options=portfolio.options,
            parent=parent,
            )
        return item



class Tree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Name =      0
        Balance =   1
        Block =     2
        ID =        3

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createActions()
        self.__createMenu()
        self.__connect()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        # self.setSortingEnabled(True)
        # self.sortByColumn(self.Column.Name, Qt.SortOrder.AscendingOrder)
        self.setColumnWidth(self.Column.Name, 150)
        self.setColumnWidth(self.Column.Balance, 100)
        self.setColumnWidth(self.Column.Block, 100)
        self.setColumnWidth(self.Column.ID, 100)
        self.setFont(Font.MONO)
        self.setItemsExpandable(True)

    def __createActions(self):
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.action_update = QtGui.QAction("Update")

    def __createMenu(self):
        logger.debug(f"{self.__class__.__name__}.__createMenu()")
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.action_update)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.action_update.triggered.connect(self.__onUpdate)

    def __resetActions(self):
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        self.action_update.setEnabled(False)

    def __setVisibleActions(self, item):
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        # if item is None:
        #     self.action_update.setEnabled(True)
        self.action_update.setEnabled(True)

    @QtCore.pyqtSlot()  #__onUpdate
    def __onUpdate(self):
        operation_widget = self.parent()
        operation_widget.updateWidget()

    def contextMenuEvent(self, e):
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")
        item = self.currentItem()
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()


class PortfolioWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__current_account = None

    def __createWidgets(self):
        self.tree = Tree(self)

    def __createLayots(self):
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.tree)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

    def setAccount(self, acc):
        self.__current_account = acc
        self.updateWidget()

    def updateWidget(self):
        if self.__current_account:
            p = self.__current_account.portfolio()
            self.tree.clear()
            self.tree.addTopLevelItem(p)
            self.tree.expandAll()




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = PortfolioWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())

