#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets

from avin.const import TEST_DIR
from avin.utils import Cmd, logger


class TestWidget(QtWidgets.QWidget):  # {{{
    """Signal"""  # {{{

    testChanged = QtCore.pyqtSignal(ITest)
    tlistChanged = QtCore.pyqtSignal(ITradeList)
    tradeChanged = QtCore.pyqtSignal(ITrade)

    # }}}
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__loadUserTests()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.test_tree = TestTree(self)
        self.trade_tree = TradeTree(self)
        self.vsplit = QtWidgets.QSplitter(
            QtCore.Qt.Orientation.Vertical, self
        )
        self.vsplit.addWidget(self.test_tree)
        self.vsplit.addWidget(self.trade_tree)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.vsplit)
        self.setLayout(vbox)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.test_tree.clicked.connect(self.__onTestTreeClicked)
        self.trade_tree.clicked.connect(self.__onTradeTreeClicked)

    # }}}
    def __loadUserTests(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadUserTests()")
        dirs = Cmd.getDirs(TEST_DIR, full_path=True)
        for dir_path in dirs:
            dir_name = Cmd.name(dir_path)
            if dir_name.startswith("."):
                continue
            itest = ITest.load(dir_path)
            self.test_tree.addTest(itest)

    # }}}
    @QtCore.pyqtSlot()  # __onTestTreeClicked# {{{
    def __onTestTreeClicked(self):
        logger.debug(f"{self.__class__.__name__}.__onTestTreeClicked()")
        item = self.test_tree.currentItem()
        if isinstance(item, ITest):
            while self.trade_tree.takeTopLevelItem(0):
                pass
            self.testChanged.emit(item)
        elif isinstance(item, ITradeList):
            while self.trade_tree.takeTopLevelItem(0):
                pass
            self.trade_tree.addTopLevelItems(item)
            self.tlistChanged.emit(item)

    # }}}
    @QtCore.pyqtSlot()  # __onTradeTreeClicked# {{{
    def __onTradeTreeClicked(self):
        logger.debug(f"{self.__class__.__name__}.__onTradeTreeClicked()")
        itrade = self.trade_tree.currentItem()
        self.tradeChanged.emit(itrade)


# }}}
# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TestWidget()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
