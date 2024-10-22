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
import time as timer
from datetime import datetime, date, time
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from tinkoff.invest import (
    Client,
    AsyncClient,
    )

from tinkoff.invest.services import (
    Services
    )

from tinkoff.invest.constants import (
    INVEST_GRPC_API,
    INVEST_GRPC_API_SANDBOX,
    )

from avin.const import BROKER_DIR
from avin.core import Portfolio
from avin.company import Broker, Sandbox, Tinkoff, Account
from avin.utils import Cmd
from avin.gui.custom import Palette, Font
from avin.gui.account import IAccount
logger = logging.getLogger("LOGGER")

class IToken(QtWidgets.QTreeWidgetItem):
    def __init__(self, name, token, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.__name = name
        self.__type = Tree.Type.TOKEN
        self.__token = token
        self.__config()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(Tree.Column.Broker, self.__name)

    @property  #name
    def name(self):
        return self.__name

    @property  #type
    def type(self):
        return self.__type

    @property  #token
    def token(self):
        return self.__token


class ISandbox(Sandbox, QtWidgets.QTreeWidgetItem):
    def __init__(self, path: str, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Sandbox.__init__(self)
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.__path = path
        self.__name = Cmd.name(self.__path)
        self.__type = Tree.Type.BROKER
        self.__config()
        self.__createChilds()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(Tree.Column.Broker, self.__name.title())

    def __createChilds(self):
        logger.debug(f"{self.__class__.__name__}.__createChilds()")
        dir_path = self.__path
        files = Cmd.getFiles(dir_path, full_path=True)
        files = Cmd.select(files, ".txt")
        for file in files:
            name = Cmd.name(file, extension=False)
            token = Cmd.read(file).strip()
            itoken = IToken(name, token, self)

    @property  #name
    def name(self):
        return self.__name

    @property  #type
    def type(self):
        return self.__type

    @property  #path
    def path(self):
        return self.__path


class ITinkoff(Tinkoff, QtWidgets.QTreeWidgetItem):
    def __init__(self, path: str, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Tinkoff.__init__(self)
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.__path = path
        self.__name = Cmd.name(self.__path)
        self.__type = Tree.Type.BROKER
        self.__config()
        self.__createChilds()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(Tree.Column.Broker, self.__name.title())

    def __createChilds(self):
        logger.debug(f"{self.__class__.__name__}.__createChilds()")
        dir_path = self.__path
        files = Cmd.getFiles(dir_path, full_path=True)
        files = Cmd.select(files, ".txt")
        for file in files:
            name = Cmd.name(file, extension=False)
            token = Cmd.read(file).strip()
            itoken = IToken(name, token, self)

    @property  #name
    def name(self):
        return self.__name

    @property  #type
    def type(self):
        return self.__type

    @property  #path
    def path(self):
        return self.__path



class TConnect(QtCore.QThread):
    """ Signal """
    brokerConnected = QtCore.pyqtSignal(Services)

    def __init__(self, ibroker, itoken, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.ibroker = ibroker
        self.itoken = itoken
        self.iaccount = None
        self.work = True

    def run(self):
        token = self.itoken.token
        target = self.ibroker.TARGET
        with Client(token, target=target) as client:
            self.brokerConnected.emit(client)
            while self.work:
                timer.sleep(1)
                pass

    def closeConnection(self):
        self.work = False



class Tree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Broker = 0

    class Type(enum.Enum):
        BROKER =   enum.auto()
        TOKEN =    enum.auto()
        ACCOUNT =  enum.auto()

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createActions()
        self.__createMenu()
        self.__connect()
        self.thread = None
        self.current_itoken = None
        self.current_iaccount = None
        self.current_ibroker = None

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setFont(Font.MONO)
        self.setSortingEnabled(True)
        self.sortByColumn(self.Column.Broker, Qt.SortOrder.AscendingOrder)
        self.setItemsExpandable(True)
        self.setColumnWidth(Tree.Column.Broker, 250)

    def __createActions(self):
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.action_connect = QtGui.QAction("Connect")
        self.action_set_account = QtGui.QAction("Set account")
        self.action_disconnect = QtGui.QAction("Disconnect")

    def __createMenu(self):
        logger.debug(f"{self.__class__.__name__}.__createMenu()")
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.action_connect)
        self.menu.addAction(self.action_disconnect)
        self.menu.addSeparator()
        self.menu.addAction(self.action_set_account)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.action_connect.triggered.connect(self.__onConnect)
        self.action_set_account.triggered.connect(self.__onSetAccount)
        self.action_disconnect.triggered.connect(self.__onDisconnect)

    def __resetActions(self):
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        self.action_connect.setEnabled(False)
        self.action_set_account.setEnabled(False)
        self.action_disconnect.setEnabled(False)

    def __setVisibleActions(self, item):
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            pass
        elif item.type == Tree.Type.TOKEN:
            self.action_connect.setEnabled(True)
            self.action_disconnect.setEnabled(True)
        elif item.type == Tree.Type.ACCOUNT:
            self.action_set_account.setEnabled(True)

    @QtCore.pyqtSlot()  #__onConnect
    def __onConnect(self):
        logger.debug(f"{self.__class__.__name__}.__onConnect()")
        self.current_itoken = self.currentItem()
        self.current_ibroker = self.current_itoken.parent()
        self.thread = TConnect(self.current_ibroker, self.current_itoken)
        self.thread.brokerConnected.connect(self.__threadBrokerConnected)
        self.thread.finished.connect(self.__threadFinish)
        self.thread.start()
        logger.info(f"Connection enabled: '{self.current_ibroker.name}'")

    @QtCore.pyqtSlot()  #__onSetAccount
    def __onSetAccount(self):
        logger.debug(f"{self.__class__.__name__}.__onSetAccount()")
        self.current_iaccount = self.currentItem()
        broker_widget = self.parent()
        broker_widget.accountSetUp.emit(
            self.current_iaccount,
            )
        logger.info(
            f"Broker '{self.current_ibroker.name}' "
            f"account '{self.current_iaccount.name}' is active, "
            f"account_id={self.current_iaccount.ID}"
            )

    @QtCore.pyqtSlot()  #__onDisconnect
    def __onDisconnect(self):
        logger.debug(f"{self.__class__.__name__}.__onDisconnect()")
        self.thread.work = False

    @QtCore.pyqtSlot(Services)  #__threadBrokerConnected
    def __threadBrokerConnected(self, client):
        logger.debug(f"{self.__class__.__name__}.__onBrokerConnected()")
        self.current_ibroker.activate(client)
        accounts = self.current_ibroker.getAllAccounts()
        for acc in accounts:
            iaccount = IAccount(self.current_ibroker, acc)
            self.current_itoken.addChild(iaccount)
        broker_widget = self.parent()
        broker_widget.connectEnabled.emit(
            self.current_ibroker,
            )

    @QtCore.pyqtSlot()  #__threadFinish
    def __threadFinish(self):
        logger.debug(f"{self.__class__.__name__}.__onFinish()")
        logger.info(
            f"Connection disabled: broker '{self.current_ibroker.name}'"
            )
        broker_widget = self.parent()
        broker_widget.connectDisabled.emit(self.current_ibroker)
        while self.current_itoken.takeChild(0):
            pass
        self.current_ibroker = None
        self.current_itoken = None
        self.current_iaccount = None

    def contextMenuEvent(self, e):
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")
        item = self.currentItem()
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()


class BrokerWidget(QtWidgets.QWidget):
    """ Signal """
    connectEnabled = QtCore.pyqtSignal(Broker)
    accountSetUp = QtCore.pyqtSignal(IAccount)
    connectDisabled = QtCore.pyqtSignal(Broker)

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__loadBrokers()
        self.__current_broker = None
        self.__current_account = None

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.tree = Tree(self)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.tree)
        self.setLayout(vbox)

    def __loadBrokers(self):
        logger.debug(f"{self.__class__.__name__}.__loadBrokers()")
        dirs = Cmd.getDirs(BROKER_DIR, full_path=True)
        for d in dirs:
            name = Cmd.name(d)
            if name == "Sandbox":
                ibroker = ISandbox(d)
            if name == "Tinkoff":
                ibroker = ITinkoff(d)
            self.tree.addTopLevelItem(ibroker)
        self.tree.expandAll()

    def currentToken(self):
        logger.debug(f"{self.__class__.__name__}.currentToken()")
        return self.tree.current_itoken

    def currentBroker(self):
        logger.debug(f"{self.__class__.__name__}.currentBroker()")
        return self.tree.current_ibroker

    def currentAccount(self):
        logger.debug(f"{self.__class__.__name__}.currentBroker()")
        return self.tree.current_account




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = BrokerWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())

