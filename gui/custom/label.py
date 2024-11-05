#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from PyQt6 import QtWidgets

from gui.custom.css import Css
from gui.custom.font import Font


class Label(QtWidgets.QLabel):
    def __init__(self, string: str, parent=None):
        QtWidgets.QLineEdit.__init__(self, parent)

        if string:
            self.setText(string)

        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(Css.STYLE)
        self.setFont(Font.MONO)


if __name__ == "__main__":
    ...
