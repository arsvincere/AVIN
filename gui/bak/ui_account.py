#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc """
import sys
sys.path.append("/usr/lib/python3.12/site-packages")
sys.path.append("/home/alex/.local/lib/python3.12/site-packages/tinkoff/")
sys.path.append("/home/alex/yandex/avin-dev/")
import logging
from datetime import datetime, date, time
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from avin.company import Account
from avin.gui.custom import Palette
from avin.gui.portfolio import PortfolioWidget
from avin.gui.operation import OperationWidget
from avin.gui.order import OrderWidget
logger = logging.getLogger("LOGGER")

class IAccount(Account, QtWidgets.QTreeWidgetItem):
    def __init__(self, broker, account_info, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Account.__init__(self, broker, account_info)
        self.__config()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.type = Tree.Type.ACCOUNT
        self.setText(Tree.Column.Broker, self.name.title())

    def portfolio(self):
        logger.debug(f"{self.__class__.__name__}.portfolio()")
        p = super().portfolio()
        iportfolio = IPortfolio.fromPortfolio(self, p, parent=None)
        return iportfolio

    def operations(self, begin=None, end=None):
        logger.debug(f"{self.__class__.__name__}.operations")
        operations = super().operations(begin, end)
        items = list()
        for op in operations:
            iop = IOperation.fromOperation(op, parent=None)
            items.append(iop)
        return items

    def orders(self):
        logger.debug(f"{self.__class__.__name__}.orders")
        orders = super().orders()
        items = list()
        for i in orders:
            iorder = IOrder.fromOrder(i, parent=None)
            items.append(iorder)
        return items


class AccountWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        QtWidgets.QTabWidget.__init__(self, parent)
        self.__createWidgets()
        self.setContentsMargins(0, 0, 0, 0)

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.portfolio = PortfolioWidget(self)
        self.operation = OperationWidget(self)
        self.order = OrderWidget(self)
        self.addTab(self.portfolio, "Portfolio")
        self.addTab(self.operation, "Operation")
        self.addTab(self.order, "Order")

    def connectAccount(self, acc):
        logger.debug(f"{self.__class__.__name__}.connectAccount()")
        self.__current_account = acc
        self.portfolio.setAccount(acc)
        self.operation.setAccount(acc)
        self.order.setAccount(acc)

    def currentAccount(self):
        logger.debug(f"{self.__class__.__name__}.currentAccount()")
        return self.__current_account



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = AccountWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())

