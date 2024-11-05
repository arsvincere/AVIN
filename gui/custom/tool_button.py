#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtCore, QtWidgets

from gui.custom.css import Css
from gui.custom.icon import Icon


class ToolButton(QtWidgets.QToolButton):
    def __init__(
        self, icon: Icon = None, text="", width=32, height=32, parent=None
    ):
        QtWidgets.QToolButton.__init__(self, parent)

        if icon:
            self.setIcon(icon)
            self.setIconSize(QtCore.QSize(height, height))

        if text:
            self.setText(text)

        self.setFixedSize(QtCore.QSize(width, height))
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(Css.TOOL_BUTTON)


if __name__ == "__main__":
    ...
