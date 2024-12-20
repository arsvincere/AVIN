#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

"""Doc"""

import sys

sys.path.append("/usr/lib/python3.12/site-packages")
sys.path.append("/home/alex/.local/lib/python3.12/site-packages/tinkoff/")
sys.path.append("/home/alex/yandex/avin-dev/")
import asyncio
import logging

from PyQt6 import QtCore, QtWidgets

from avin.company import General
from avin.gui.custom import Palette

logger = logging.getLogger("LOGGER")


class TGeneral(QtCore.QThread):
    def __init__(self, general, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.general = general

    def run(self):
        self.loop = asyncio.new_event_loop()
        self.general.initialize()
        self.loop.run_until_complete(self.general.initialize())
        self.loop.run_until_complete(self.general.start())


class GeneralWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.thread = None

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.btn_BABLO = QtWidgets.QPushButton("-= Б А Б Л О =-")
        self.btn_BABLO.setCheckable(True)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.btn_BABLO)
        self.setLayout(vbox)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")

    @QtCore.pyqtSlot()  # __threadFinished
    def __threadFinished(self):
        self.thread = None
        self.btn_BABLO.setEnabled(True)

    @QtCore.pyqtSlot()  # __onBABLO
    def __onBABLO(self):
        logger.debug(f"{self.__class__.__name__}.__onBABLO()")
        self.general = General()
        self.thread = TGeneral(self.general)
        self.thread.finished.connect(self.__threadFinished)
        self.thread.start()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = GeneralWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.showMaximized()
    w.show()
    sys.exit(app.exec())
