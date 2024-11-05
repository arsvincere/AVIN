#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtWidgets

from gui.custom.css import Css


class PushButton(QtWidgets.QPushButton):
    def __init__(self, text, height=32, parent=None):
        QtWidgets.QPushButton.__init__(self, parent)

        if text:
            self.setText(text)

        self.setFixedHeight(height)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(Css.PUSH_BUTTON)


if __name__ == "__main__":
    ...
