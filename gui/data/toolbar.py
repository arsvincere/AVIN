#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from avin.utils import logger
from gui.custom import Css, Icon


class DataToolBar(QtWidgets.QToolBar):
    ICON_SIZE = QtCore.QSize(32, 32)

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)

        self.__createActions()
        self.__config()

    # }}}
    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")

        self.download = QtGui.QAction(Icon.DOWNLOAD, "Download", self)
        self.convert = QtGui.QAction(Icon.CONVERT, "Convert", self)
        self.delete = QtGui.QAction(Icon.THRASH, "Delete", self)
        self.view = QtGui.QAction(Icon.THRASH, "View", self)
        self.update = QtGui.QAction(Icon.UPDATE, "Update", self)

        self.addAction(self.download)
        self.addAction(self.convert)
        self.addAction(self.delete)
        self.addAction(self.view)
        self.addAction(self.update)

        actions = self.actions()
        for i in actions:
            btn = self.widgetForAction(i)
            btn.setStyleSheet(Css.TOOL_BUTTON)

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setIconSize(self.ICON_SIZE)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(Css.STYLE)

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = DataToolBar()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
