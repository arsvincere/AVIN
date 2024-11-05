#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets
from qasync import asyncSlot

from avin.data import Data
from avin.utils import logger
from gui.custom import Css
from gui.data.toolbar import DataToolBar
from gui.data.tree import DataInfoTree


class DataWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        super().__init__()

        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()
        self.__initUI()

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.tool_bar = DataToolBar(self)
        self.data_tree = DataInfoTree(self)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.tool_bar)
        vbox.addWidget(self.data_tree)
        vbox.setContentsMargins(0, 0, 0, 0)

    # }}}
    def __config(self):  # {{{
        self.setStyleSheet(Css.STYLE)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

    # }}}
    @asyncSlot()  # {{{
    async def __initUI(self):
        logger.debug(f"{self.__class__.__name__}.__initUI()")

        info = await Data.info()
        self.data_tree.add(info)

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = DataWidget()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
