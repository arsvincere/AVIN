#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtWidgets


class TestProgressBar(QtWidgets.QProgressBar):
    def __init__(self, parent=None):
        QtWidgets.QProgressBar.__init__(self, parent)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setMaximumHeight(20)


if __name__ == "__main__":
    ...
