#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets

from avin.utils import logger
from gui.custom import Css
from gui.data.download_dialog import DataDownloadDialog
from gui.data.thread import Thread
from gui.data.toolbar import DataToolBar
from gui.data.tree import DataInfoTree


class DataWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__thread = None

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

        self.tool_bar.download.triggered.connect(self.__onDownload)
        self.tool_bar.delete.triggered.connect(self.__onDelete)
        self.tool_bar.update.triggered.connect(self.__onUpdate)

    # }}}
    def __initUI(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")

        self.__updateTree()

    # }}}
    @QtCore.pyqtSlot()  # __updateTree  # {{{
    def __updateTree(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__updateTree()")

        data_info = Thread.info()
        self.data_tree.clear()
        self.data_tree.add(data_info)

    # }}}
    @QtCore.pyqtSlot()  # __onDownload  # {{{
    def __onDownload(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onDownload()")

        dialog = DataDownloadDialog()
        dialog.exec()

    # }}}
    @QtCore.pyqtSlot()  # __onDelete  # {{{
    def __onDelete(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onDelete()")

        data_info = self.data_tree.selectedData()
        Thread.delete(data_info)

    # }}}
    @QtCore.pyqtSlot()  # __onUpdate  # {{{
    def __onUpdate(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onUpdate()")

        data_info = self.data_tree.selectedData()
        Thread.update(data_info)

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = DataWidget()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
