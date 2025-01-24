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

from avin import Test
from avin.utils import logger
from gui.custom import Css
from gui.summary.thread import TLoadTrades
from gui.summary.tree import TradeListTree


class SummaryDockWidget(QtWidgets.QDockWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDockWidget.__init__(self, "Summary", parent)

        self.widget = SummaryWidget(self)
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

    def setTest(self, test: Test) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setTest()")

        self.widget.setTest(test)

    # }}}


# }}}
class SummaryWidget(QtWidgets.QWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

        self.__test = None
        self.__thread = None

    # }}}

    def setTest(self, test) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setTest()")

        self.__test = test
        if test.trade_list is not None:
            self.__showSummary()
        else:
            self.__showButtonLoadTrades()

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Css.STYLE)
        self.setWindowTitle("AVIN")

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__tree = TradeListTree(self)
        self.__load_btn = QtWidgets.QPushButton("Load trades")

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.__tree)
        vbox.addWidget(self.__load_btn)
        self.setLayout(vbox)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__load_btn.clicked.connect(self.__loadTradeList)

    # }}}
    def __showSummary(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__showSummary()")

        self.__load_btn.hide()
        self.__tree.show()

        self.__tree.setTradeList(self.__test.trade_list)

    # }}}
    def __showButtonLoadTrades(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__showButtonLoadTrades()")

        self.__load_btn.show()
        self.__tree.hide()

    # }}}
    def __loadTradeList(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadTradeList()")

        if self.__test is None:
            return

        if self.__test.trade_list is not None:
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


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = SummaryWidget()
    w.show()
    sys.exit(app.exec())
