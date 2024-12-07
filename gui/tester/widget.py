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

from avin.core import Trade, TradeList
from avin.tester import Test
from avin.utils import logger
from gui.custom import Css
from gui.tester.thread import Thread
from gui.tester.tree import TestTree, TradeTree


class TesterDockWidget(QtWidgets.QDockWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        QtWidgets.QDockWidget.__init__(self, "Tester", parent)

        widget = TesterWidget(self)
        self.setWidget(widget)
        self.setStyleSheet(Css.DOCK_WIDGET)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        feat = QtWidgets.QDockWidget.DockWidgetFeature
        self.setFeatures(
            feat.DockWidgetMovable
            | feat.DockWidgetClosable
            | feat.DockWidgetFloatable
        )

        # }}}


# }}}
class TesterWidget(QtWidgets.QWidget):  # {{{
    testChanged = QtCore.pyqtSignal(Test)
    tlistChanged = QtCore.pyqtSignal(TradeList)
    tradeChanged = QtCore.pyqtSignal(Trade)

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__loadUserTests()

    # }}}
    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setStyleSheet(Css.STYLE)

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.test_tree = TestTree(self)
        self.trade_tree = TradeTree(self)

        vertical = QtCore.Qt.Orientation.Vertical
        self.vsplit = QtWidgets.QSplitter(vertical, self)
        self.vsplit.addWidget(self.test_tree)
        self.vsplit.addWidget(self.trade_tree)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.vsplit)
        self.setLayout(vbox)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.test_tree.clicked.connect(self.__onTestTreeClicked)
        self.trade_tree.clicked.connect(self.__onTradeTreeClicked)

    # }}}
    def __loadUserTests(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadUserTests()")

        all_names = Thread.requestAllTest()
        for name in all_names:
            test = Thread.loadTest(name)
            self.test_tree.addTest(test)

    # }}}
    @QtCore.pyqtSlot()  # __onTestTreeClicked# {{{
    def __onTestTreeClicked(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onTestTreeClicked()")

        item = self.test_tree.currentItem()
        class_name = item.__class__.__name__
        match class_name:
            case "TestItem":
                test = item.test
                self.trade_tree.setTradeList(test.trade_list)
                self.testChanged.emit(test)
            case "TradeListItem":
                tlist = item.tlist
                self.trade_tree.setTradeList(tlist)
                self.tlistChanged.emit(tlist)

    # }}}
    @QtCore.pyqtSlot()  # __onTradeTreeClicked# {{{
    def __onTradeTreeClicked(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onTradeTreeClicked()")

        item = self.trade_tree.currentItem()
        self.tradeChanged.emit(item.trade)


# }}}
# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TestWidget()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
