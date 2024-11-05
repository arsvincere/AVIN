#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""Doc"""

import logging
import sys

from PyQt6 import QtCore, QtWidgets

logger = logging.getLogger("LOGGER")


class ProgressBar(QtWidgets.QProgressBar):
    def __init__(self, parent=None):
        QtWidgets.QProgressBar.__init__(self, parent)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setMaximumHeight(20)
        self.setFont(Font.MONO)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = UOrderType()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.showMaximized()
    w.show()
    sys.exit(app.exec())
