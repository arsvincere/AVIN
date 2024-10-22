#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc """
import sys
sys.path.append("/usr/lib/python3.12/site-packages")
sys.path.append("/home/alex/.local/lib/python3.12/site-packages/tinkoff/")
sys.path.append("/home/alex/yandex/avin-dev/")
import os
import enum
import logging
import time as timer
from datetime import datetime, date, time
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from avin.core import Order, Asset
from avin.gui.custom import Palette, Font
logger = logging.getLogger("LOGGER")

class IOrder(Order, QtWidgets.QTreeWidgetItem):
    def __init__(
            self,
            signal,
            TYPE,
            direction,
            asset,
            lots,
            price,
            exec_price=None,
            timeout=None,
            status=Order.Status.NEW,
            ID=None,
            commission=None,
            parent=None
        ):
        logger.debug(f"{__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Order.__init__(
            self, signal, TYPE, direction, asset, lots, price,
            exec_price, timeout, status, ID, commission
            )
        self.__config()

    def __config(self):
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(Tree.Column.Signal,      "TODO")
        self.setText(Tree.Column.Type,        self.type.name)
        self.setText(Tree.Column.Direction,   self.direction.name)
        self.setText(Tree.Column.Asset,       self.asset.ticker)
        self.setText(Tree.Column.Lots,        str(self.lots))
        self.setText(Tree.Column.Price,       str(self.price))
        self.setText(Tree.Column.ExecPrice,   str(self.exec_price))
        self.setText(Tree.Column.Timeout,     str(self.timeout))
        self.setText(Tree.Column.Status,      str(self.status.name))
        self.setText(Tree.Column.ID,          str(self.ID))
        self.setText(Tree.Column.Commission,  str(self.commission))

    @staticmethod  #fromOrder
    def fromOrder(order: Order, parent=None):
        iorder = IOrder(
            signal=         order.signal,
            TYPE=           order.type,
            direction=      order.direction,
            asset=          order.asset,
            lots=           order.lots,
            price=          order.price,
            exec_price=     order.exec_price,
            timeout=        order.timeout,
            status=         order.status,
            ID=             order.ID,
            commission=     order.commission,
            parent=         parent
            )
        return iorder


class Tree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Signal =     0
        Type =       1
        Direction =  2
        Asset =      3
        Lots =       4
        Price =      5
        ExecPrice =  6
        Amount =     7
        Commission = 8
        Timeout =    9
        Status =     10
        ID =         11

    def __init__(self, parent=None):
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
        self.setSortingEnabled(True)
        self.sortByColumn(self.Column.Type, Qt.SortOrder.DescendingOrder)
        # self.setColumnWidth(self.Column.Datetime, 150)
        self.setFont(Font.MONO)
        self.setItemsExpandable(True)

    def __createActions(self):
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.action_update = QtGui.QAction("Update")
        self.action_edit = QtGui.QAction("Edit")
        self.action_remove = QtGui.QAction("Remove")

    def __createMenu(self):
        logger.debug(f"{self.__class__.__name__}.__createMenu()")
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.action_update)
        self.menu.addSeparator()
        self.menu.addAction(self.action_edit)
        self.menu.addAction(self.action_remove)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.action_update.triggered.connect(self.__onUpdate)
        self.action_edit.triggered.connect(self.__onEdit)
        self.action_remove.triggered.connect(self.__onRemove)

    def __resetActions(self):
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        for i in self.actions():
            i.setEnabled(False)

    def __setVisibleActions(self, item):
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            self.action_update.setEnabled(True)
        elif isinstance(item, IOrder):
            self.action_update.setEnabled(True)
            self.action_edit.setEnabled(True)
            self.action_remove.setEnabled(True)

    @QtCore.pyqtSlot()  #__onUpdate
    def __onUpdate(self):
        logger.debug(f"{self.__class__.__name__}.__onUpdate()")
        order_widget = self.parent()
        order_widget.updateWidget()

    @QtCore.pyqtSlot()  #__onEdit
    def __onEdit(self):
        logger.debug(f"{self.__class__.__name__}.__onUpdate()")
        ...

    @QtCore.pyqtSlot()  #__onRemove
    def __onRemove(self):
        logger.debug(f"{self.__class__.__name__}.__onRemove()")
        iorder = self.currentItem()
        acc: IAccount = self.parent().currentAccount()
        acc.cancel(iorder)

    def contextMenuEvent(self, e):
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")
        item = self.currentItem()
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()


class OrderWidget(QtWidgets.QWidget):
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
            orders = self.__current_account.orders()
            self.tree.clear()
            self.tree.addTopLevelItems(orders)

    def currentAccount(self):
        logger.debug(f"{self.__class__.__name__}.currentAccount()")
        return self.__current_account



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = OrderWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())

