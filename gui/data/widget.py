#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import asyncio
import sys

from PyQt6 import QtCore, QtWidgets

from avin.data import Data, DataInfo
from avin.utils import logger
from gui.custom import Css
from gui.data.download_dialog import DataDownloadDialog
from gui.data.toolbar import DataToolBar
from gui.data.tree import DataInfoTree


class _TInfo(QtCore.QThread):  # {{{
    info = QtCore.pyqtSignal(DataInfo)

    def __init__(  # {{{
        self, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")
        asyncio.run(self.__ainfo())

    # }}}
    async def __ainfo(self):  # {{{
        data_info = await Data.info()
        self.info.emit(data_info)

    # }}}


# }}}


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

    # }}}
    def __initUI(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")

        self.__updateTree()

    # }}}
    def __isBusy(self) -> bool:  # {{{
        logger.debug(f"{self.__class__.__name__}.__isBusy()")

        if self.__thread is not None:
            Dialog.info("Data manager is busy now, wait for complete task")
            return True

        return False

    # }}}
    @QtCore.pyqtSlot()  # __updateTree  # {{{
    def __updateTree(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__updateTree()")

        if self.__isBusy():
            return

        self.__thread = _TInfo(parent=self)
        self.__thread.info.connect(self.__onInfo)
        self.__thread.finished.connect(self.__onThreadFinished)
        self.__thread.start()

    # }}}
    @QtCore.pyqtSlot(DataInfo)  # __onInfo  # {{{
    def __onInfo(self, data_info: DataInfo) -> None:
        logger.debug(f"{self.__class__.__name__}.__onInfo()")

        self.data_tree.clear()
        self.data_tree.add(data_info)

    # }}}
    @QtCore.pyqtSlot()  # __onDownload  # {{{
    def __onDownload(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onDownload()")

        dialog = DataDownloadDialog()
        dialog.setWindowTitle("AVIN  -  Widget")
        dialog.exec()

    # }}}
    @QtCore.pyqtSlot()  # __onThreadFinished  # {{{
    def __onThreadFinished(self):
        logger.debug(f"{self.__class__.__name__}.__onThreadFinished()")

        del self.__thread
        self.__thread = None

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = DataWidget()
    w.setWindowTitle("AVIN  -  Widget")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
