#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets

from avin.core import Strategy
from avin.utils import logger
from gui.custom import Css
from gui.strategy.item import StrategyItem
from gui.strategy.tree import StrategySetTree, StrategyTree


class StrategyWidget(QtWidgets.QWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__loadUserStrategy()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__tree = StrategyTree(self)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.__tree)
        self.setLayout(vbox)

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setStyleSheet(Css.STYLE)

    # }}}
    def __loadUserStrategy(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadUserStrategy()")

        strategy_names = Strategy.requestAll()
        for name in strategy_names:
            item = StrategyItem(name)
            item.loadConfig()
            item.loadVersions(checkable=False)
            self.__tree.addTopLevelItem(item)

    # }}}


# }}}
class StrategySetWidget(QtWidgets.QWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__createWidgets()
        self.__createLayots()
        self.__config()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__tree = StrategySetTree(self)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.__tree)
        self.setLayout(vbox)

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setStyleSheet(Css.STYLE)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = StrategySetWidget()
    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
