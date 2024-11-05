#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtWidgets


class Spacer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )


class HLine(QtWidgets.QFrame):
    def __init__(self, parent=None):
        QtWidgets.QFrame.__init__(self, parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)


class VLine(QtWidgets.QFrame):
    def __init__(self, parent=None):
        QtWidgets.QFrame.__init__(self, parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)


if __name__ == "__main__":
    ...
