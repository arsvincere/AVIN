#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtWidgets

from gui.custom.css import Css


class Menu(QtWidgets.QMenu):
    def __init__(self, title=None, parent=None):
        QtWidgets.QMenu.__init__(self, parent)

        if title:
            self.setTitle(title)

        self.setStyleSheet(Css.MENU)


if __name__ == "__main__":
    ...
