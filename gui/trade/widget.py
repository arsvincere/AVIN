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

from avin import Trade, TradeList
from avin.utils import logger
from gui.custom import Css, Dialog
from gui.summary.thread import TLoadTrades
from gui.trade.tree import TradeTree


class TradeDockWidget(QtWidgets.QDockWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDockWidget.__init__(self, "Trades", parent)

        self.widget = TradeWidget(self)
        self.setWidget(self.widget)
        self.setStyleSheet(Css.DOCK_WIDGET)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
            | Qt.DockWidgetArea.BottomDockWidgetArea
        )

        feat = QtWidgets.QDockWidget.DockWidgetFeature
        self.setFeatures(
            feat.DockWidgetMovable
            | feat.DockWidgetClosable
            | feat.DockWidgetFloatable
        )

        # }}}

    def setTradeList(self, trade_list: TradeList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setTest()")

        self.widget.setTradeList(trade_list)

    # }}}


# }}}
class TradeWidget(QtWidgets.QWidget):  # {{{
    tradeChanged = QtCore.pyqtSignal(Trade)

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

        self.__trade_list = None

    # }}}

    def setTradeList(self, trade_list: TradeList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setTradeList()")

        self.__trade_list = trade_list
        self.__tree.setTradeList(trade_list)

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Css.STYLE)
        self.setWindowTitle("AVIN")

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__tree = TradeTree(self)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.__tree)
        self.setLayout(vbox)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__tree.clicked.connect(self.__onTreeClicked)

    # }}}
    def __loadTradeList(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadTradeList()")

        if self.__test is None:
            return

        # если трейды уже загружены - ничего не делать
        if self.__test.trade_list is not None:
            return

        if self.__thread is not None:
            Dialog.error(
                "Loading trades already runing,\n"
                "Wait for loading the previous trade list."
            )
            return

        logger.info(f":: Loading trades {self.__test}")
        self.__thread = TLoadTrades(self.__test)
        self.__thread.finished.connect(self.__onLoaded)
        self.__thread.start()

    # }}}

    @QtCore.pyqtSlot()  # __onLoaded# {{{
    def __onLoaded(self):
        logger.debug(f"{self.__class__.__name__}.__onLoaded()")

        self.__thread = None
        self.__showSummary()

    # }}}
    @QtCore.pyqtSlot()  # __onTreeClicked# {{{
    def __onTreeClicked(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onTreeClicked()")

        item = self.__tree.currentItem()
        trade = item.trade
        self.tradeChanged.emit(trade)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TradeWidget()
    w.show()
    sys.exit(app.exec())
