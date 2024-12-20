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
from avin.core import Operation
from avin.gui.custom import Palette, Font
logger = logging.getLogger("LOGGER")


class IOperation(Operation, QtWidgets.QTreeWidgetItem):
    def __init__(
            self,
            signal,
            dt,
            direction,
            asset,
            lots,
            price,
            quantity,
            amount,
            commission,
            broker_info=None,
            parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Operation.__init__(
            self, signal, dt, direction,
            asset, lots, price, quantity, amount, commission, broker_info,
            )
        self.config()

    def fromOperation(op, parent=None):
        item = IOperation(
            signal=op.signal,
            dt=op.dt,
            direction=op.direction,
            asset=op.asset,
            lots=op.lots,
            price=op.price,
            quantity=op.quantity,
            amount=op.amount,
            commission=op.commission,
            broker_info=op.broker_info,
            parent=parent,
            )
        return item

    def config(self):
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        msk_dt = self.dt + const.MSK_TIME_DIF
        str_dt = msk_dt.strftime("%Y-%m-%d  %H:%M")
        self.setText(Tree.Column.Signal,      "TODO")
        self.setText(Tree.Column.Datetime,    str_dt)
        self.setText(Tree.Column.Direction,   self.direction.name)
        self.setText(Tree.Column.Asset,       self.asset.ticker)
        self.setText(Tree.Column.Lots,        str(self.lots))
        self.setText(Tree.Column.Price,       str(self.price))
        self.setText(Tree.Column.Quantity,    str(self.quantity))
        self.setText(Tree.Column.Amount,      str(self.amount))
        self.setText(Tree.Column.Commission,  str(self.commission))


class Tree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Signal =     0
        Datetime =   1
        Direction =  2
        Asset =      3
        Lots =       4
        Price =      5
        Quantity =   6
        Amount =     7
        Commission = 8

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
        self.sortByColumn(self.Column.Datetime, Qt.SortOrder.DescendingOrder)
        self.setColumnWidth(self.Column.Datetime, 150)
        # self.setColumnWidth(self.Column.Balance, 100)
        # self.setColumnWidth(self.Column.Block, 100)
        # self.setColumnWidth(self.Column.ID, 100)
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


class OperationWidget(QtWidgets.QWidget):
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
            op = self.__current_account.operations()
            self.tree.clear()
            self.tree.addTopLevelItems(op)




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = OperationWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())

